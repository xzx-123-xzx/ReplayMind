"""
Growth API Routes
成长中心 API
"""

from typing import List
from uuid import UUID
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from common import logger
from infrastructure.db.postgres import get_db
from domain.repositories.report_repo import ScoreRepository
from domain.models.growth import GrowthRecord
from pydantic import BaseModel


router = APIRouter()


class GrowthRecordResponse(BaseModel):
    """成长记录响应"""
    id: UUID
    created_at: str
    score: int
    category: str
    insight: str


class GrowthListResponse(BaseModel):
    """成长记录列表响应"""
    total: int
    records: List[GrowthRecordResponse]


@router.get("", response_model=GrowthListResponse)
async def list_growth_records(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """
    获取成长记录列表

    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        db: 数据库会话

    Returns:
        GrowthListResponse: 成长记录列表
    """
    from domain.repositories.report_repo import (
        ReportRepository,
        ScoreRepository,
        RecommendationRepository,
    )

    report_repo = ReportRepository(db)
    score_repo = ScoreRepository(db)
    rec_repo = RecommendationRepository(db)

    reports = await report_repo.get_multi(skip=skip, limit=limit)
    total = await report_repo.count()

    records = []

    for report in reports:
        score = await score_repo.get_by_report(report.id)
        recommendations = await rec_repo.get_by_report(report.id, priority=2)

        if not score and not recommendations:
            continue

        record_score = score.replay_score if score else 0
        category = "technical"
        insight = report.summary if report.summary else (
            recommendations[0].content if recommendations else "完成了一次复盘"
        )

        if score:
            score_map = {
                "operation": score.operation_score,
                "awareness": score.awareness_score,
                "decision": score.decision_score,
                "teamwork": score.teamwork_score,
            }
            max_key = max(score_map, key=lambda k: score_map[k])
            category_map = {
                "operation": "technical",
                "awareness": "strategy",
                "decision": "decision",
                "teamwork": "teamwork",
            }
            category = category_map.get(max_key, "technical")

        records.append(
            GrowthRecordResponse(
                id=report.id,
                created_at=report.created_at.isoformat(),
                score=record_score,
                category=category,
                insight=insight,
            )
        )

    return GrowthListResponse(total=total, records=records)


class RadarData(BaseModel):
    """雷达图数据"""
    operation: float
    awareness: float
    decision: float
    teamwork: float


class TrendDataPoint(BaseModel):
    """趋势数据点"""
    date: str
    score: float


class GrowthOverview(BaseModel):
    """成长概览"""
    total_replays: int
    avg_replay_score: float
    recent_trend: str  # "up", "down", "stable"
    ability_radar: RadarData


class GrowthTrendsResponse(BaseModel):
    """成长趋势响应"""
    period: str
    data_points: List[TrendDataPoint]


class GrowthRadarResponse(BaseModel):
    """能力雷达图响应"""
    current: RadarData
    previous: RadarData
    improvement: RadarData


@router.get("/overview", response_model=GrowthOverview)
async def get_growth_overview(
    db: AsyncSession = Depends(get_db),
):
    """
    获取成长概览

    Args:
        db: 数据库会话

    Returns:
        GrowthOverview: 成长概览
    """
    from sqlalchemy import func, select
    from domain.models.report import Report, Score

    result = await db.execute(
        select(
            func.avg(Score.operation_score).label("avg_operation"),
            func.avg(Score.awareness_score).label("avg_awareness"),
            func.avg(Score.decision_score).label("avg_decision"),
            func.avg(Score.teamwork_score).label("avg_teamwork"),
            func.avg(Score.replay_score).label("avg_replay"),
            func.count(Score.id).label("total_scores"),
        )
    )
    row = result.one()

    total_replays = int(row.total_scores or 0)
    if total_replays == 0:
        return GrowthOverview(
            total_replays=0,
            avg_replay_score=0,
            recent_trend="stable",
            ability_radar=RadarData(
                operation=0,
                awareness=0,
                decision=0,
                teamwork=0,
            ),
        )

    return GrowthOverview(
        total_replays=total_replays,
        avg_replay_score=round(float(row.avg_replay or 0), 2),
        recent_trend="stable",
        ability_radar=RadarData(
            operation=round(float(row.avg_operation or 0), 2),
            awareness=round(float(row.avg_awareness or 0), 2),
            decision=round(float(row.avg_decision or 0), 2),
            teamwork=round(float(row.avg_teamwork or 0), 2),
        ),
    )


@router.get("/trends", response_model=GrowthTrendsResponse)
async def get_growth_trends(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
):
    """
    获取成长趋势
    
    Args:
        days: 统计天数
        db: 数据库会话
        
    Returns:
        GrowthTrendsResponse: 成长趋势
    """
    # 生成趋势数据点（简化实现）
    data_points = []
    today = date.today()
    
    for i in range(days):
        current_date = today - timedelta(days=i)
        # 模拟数据
        data_points.append(TrendDataPoint(
            date=current_date.isoformat(),
            score=70 + (days - i) * 0.5,
        ))
    
    return GrowthTrendsResponse(
        period=f"last_{days}_days",
        data_points=list(reversed(data_points)),
    )


@router.get("/radar", response_model=GrowthRadarResponse)
async def get_growth_radar(
    db: AsyncSession = Depends(get_db),
):
    """
    获取能力雷达图数据

    Args:
        db: 数据库会话

    Returns:
        GrowthRadarResponse: 能力雷达图数据
    """
    from sqlalchemy import func, select
    from domain.models.report import Score

    result = await db.execute(
        select(
            func.avg(Score.operation_score).label("avg_operation"),
            func.avg(Score.awareness_score).label("avg_awareness"),
            func.avg(Score.decision_score).label("avg_decision"),
            func.avg(Score.teamwork_score).label("avg_teamwork"),
            func.avg(Score.replay_score).label("avg_replay"),
            func.count(Score.id).label("total_scores"),
        )
    )
    row = result.one()
    total = int(row.total_scores or 0)

    if total == 0:
        current = RadarData(operation=0, awareness=0, decision=0, teamwork=0)
    else:
        current = RadarData(
            operation=round(float(row.avg_operation or 0), 2),
            awareness=round(float(row.avg_awareness or 0), 2),
            decision=round(float(row.avg_decision or 0), 2),
            teamwork=round(float(row.avg_teamwork or 0), 2),
        )

    previous = RadarData(
        operation=65,
        awareness=68,
        decision=70,
        teamwork=66,
    )

    improvement = RadarData(
        operation=current.operation - previous.operation,
        awareness=current.awareness - previous.awareness,
        decision=current.decision - previous.decision,
        teamwork=current.teamwork - previous.teamwork,
    )

    return GrowthRadarResponse(
        current=current,
        previous=previous,
        improvement=improvement,
    )
