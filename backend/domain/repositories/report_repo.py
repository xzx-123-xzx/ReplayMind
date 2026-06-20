"""
Report Repository
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.models.report import Report, Score, Recommendation
from domain.repositories.base import BaseRepository


class ReportRepository(BaseRepository[Report]):
    """报告仓储"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Report, session)
    
    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Report]:
        """获取用户的报告列表"""
        result = await self.session.execute(
            select(Report)
            .where(Report.user_id == user_id)
            .order_by(Report.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_video(self, video_id: UUID) -> Optional[Report]:
        """根据视频获取报告"""
        result = await self.session.execute(
            select(Report).where(Report.video_id == video_id)
        )
        return result.scalar_one_or_none()
    
    async def get_with_scores(self, report_id: UUID) -> Optional[Report]:
        """获取报告及评分"""
        result = await self.session.execute(
            select(Report)
            .where(Report.id == report_id)
        )
        return result.scalar_one_or_none()


class ScoreRepository(BaseRepository[Score]):
    """评分仓储"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Score, session)
    
    async def get_by_report(self, report_id: UUID) -> Optional[Score]:
        """根据报告获取评分"""
        result = await self.session.execute(
            select(Score).where(Score.report_id == report_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_avg_scores(
        self,
        user_id: UUID,
    ) -> Optional[dict]:
        """获取用户的平均评分"""
        from sqlalchemy import func, exists
        from domain.models.report import Report
        
        # 子查询获取用户的所有报告
        subquery = select(Report.id).where(Report.user_id == user_id).subquery()
        
        result = await self.session.execute(
            select(
                func.avg(Score.operation_score).label("avg_operation"),
                func.avg(Score.awareness_score).label("avg_awareness"),
                func.avg(Score.decision_score).label("avg_decision"),
                func.avg(Score.teamwork_score).label("avg_teamwork"),
                func.avg(Score.replay_score).label("avg_replay"),
                func.count(Score.id).label("total_scores"),
            )
            .where(Score.report_id.in_(select(subquery)))
        )
        
        row = result.one()
        
        if row.total_scores == 0:
            return None
        
        return {
            "operation_score": round(float(row.avg_operation or 0), 2),
            "awareness_score": round(float(row.avg_awareness or 0), 2),
            "decision_score": round(float(row.avg_decision or 0), 2),
            "teamwork_score": round(float(row.avg_teamwork or 0), 2),
            "replay_score": round(float(row.avg_replay or 0), 2),
            "total_scores": row.total_scores,
        }


class RecommendationRepository(BaseRepository[Recommendation]):
    """建议仓储"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Recommendation, session)
    
    async def get_by_report(
        self,
        report_id: UUID,
        priority: Optional[int] = None,
    ) -> List[Recommendation]:
        """获取报告的建议"""
        query = select(Recommendation).where(Recommendation.report_id == report_id)
        
        if priority is not None:
            query = query.where(Recommendation.priority <= priority)
        
        query = query.order_by(Recommendation.priority, Recommendation.created_at)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
