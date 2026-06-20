"""
Reports API Routes
复盘报告 API
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from common import logger
from infrastructure.db.postgres import get_db
from domain.repositories.report_repo import ReportRepository, ScoreRepository, RecommendationRepository
from pydantic import BaseModel


router = APIRouter()


class ScoreResponse(BaseModel):
    """评分响应"""
    operation_score: int
    awareness_score: int
    decision_score: int
    teamwork_score: int
    replay_score: int
    score_details: dict


class RecommendationResponse(BaseModel):
    """建议响应"""
    id: UUID
    category: str
    content: str
    priority: int
    is_actionable: bool


class ReportResponse(BaseModel):
    """报告响应"""
    id: UUID
    video_id: UUID
    title: str
    summary: Optional[str]
    scores: Optional[ScoreResponse]
    recommendations: List[RecommendationResponse]
    created_at: str


class ReportListResponse(BaseModel):
    """报告列表响应"""
    total: int
    reports: List[ReportResponse]


@router.get("", response_model=ReportListResponse)
async def list_reports(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """
    获取报告列表
    
    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        db: 数据库会话
        
    Returns:
        ReportListResponse: 报告列表
    """
    repo = ReportRepository(db)
    reports = await repo.get_multi(skip=skip, limit=limit)
    total = await repo.count()
    
    result = []
    for report in reports:
        # 获取评分
        score_repo = ScoreRepository(db)
        score = await score_repo.get_by_report(report.id)
        
        # 获取建议
        rec_repo = RecommendationRepository(db)
        recommendations = await rec_repo.get_by_report(report.id)
        
        result.append(ReportResponse(
            id=report.id,
            video_id=report.video_id,
            title=report.title,
            summary=report.summary,
            scores=ScoreResponse(**score.__dict__) if score else None,
            recommendations=[
                RecommendationResponse(
                    id=r.id,
                    category=r.category,
                    content=r.content,
                    priority=r.priority,
                    is_actionable=bool(r.is_actionable),
                )
                for r in recommendations
            ],
            created_at=report.created_at.isoformat(),
        ))
    
    return ReportListResponse(total=total, reports=result)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    获取报告详情
    
    Args:
        report_id: 报告ID
        db: 数据库会话
        
    Returns:
        ReportResponse: 报告详情
    """
    repo = ReportRepository(db)
    report = await repo.get(report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # 获取评分
    score_repo = ScoreRepository(db)
    score = await score_repo.get_by_report(report_id)
    
    # 获取建议
    rec_repo = RecommendationRepository(db)
    recommendations = await rec_repo.get_by_report(report_id)
    
    return ReportResponse(
        id=report.id,
        video_id=report.video_id,
        title=report.title,
        summary=report.summary,
        scores=ScoreResponse(**score.__dict__) if score else None,
        recommendations=[
            RecommendationResponse(
                id=r.id,
                category=r.category,
                content=r.content,
                priority=r.priority,
                is_actionable=bool(r.is_actionable),
            )
            for r in recommendations
        ],
        created_at=report.created_at.isoformat(),
    )


@router.get("/{report_id}/content")
async def get_report_content(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    获取报告完整内容（Markdown）
    
    Args:
        report_id: 报告ID
        db: 数据库会话
        
    Returns:
        dict: 报告内容
    """
    repo = ReportRepository(db)
    report = await repo.get(report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return {
        "id": str(report.id),
        "title": report.title,
        "content": report.markdown_content,
        "created_at": report.created_at.isoformat(),
    }
