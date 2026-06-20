"""
Video Repository
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from domain.models.video import Video, VideoStatus, VideoFrame, AudioTranscript, GameEvent
from domain.repositories.base import BaseRepository


class VideoRepository(BaseRepository[Video]):
    """视频仓储"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Video, session)
    
    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status: Optional[VideoStatus] = None,
    ) -> List[Video]:
        """获取用户的视频列表"""
        query = select(Video).where(Video.user_id == user_id)
        
        if status:
            query = query.where(Video.status == status)
        
        query = query.order_by(Video.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_by_status(self, status: VideoStatus) -> List[Video]:
        """根据状态获取视频"""
        result = await self.session.execute(
            select(Video).where(Video.status == status)
        )
        return list(result.scalars().all())


class VideoFrameRepository(BaseRepository[VideoFrame]):
    """视频帧仓储"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(VideoFrame, session)
    
    async def get_by_video(
        self,
        video_id: UUID,
        keyframes_only: bool = False,
    ) -> List[VideoFrame]:
        """获取视频的所有帧"""
        query = select(VideoFrame).where(VideoFrame.video_id == video_id)
        
        if keyframes_only:
            query = query.where(VideoFrame.is_keyframe == 1)
        
        query = query.order_by(VideoFrame.frame_number)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())


class AudioTranscriptRepository(BaseRepository[AudioTranscript]):
    """音频转录仓储"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(AudioTranscript, session)
    
    async def get_by_video(self, video_id: UUID) -> List[AudioTranscript]:
        """获取视频的所有转录"""
        result = await self.session.execute(
            select(AudioTranscript)
            .where(AudioTranscript.video_id == video_id)
            .order_by(AudioTranscript.start_time)
        )
        return list(result.scalars().all())


class GameEventRepository(BaseRepository[GameEvent]):
    """游戏事件仓储"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(GameEvent, session)
    
    async def get_by_video(self, video_id: UUID) -> List[GameEvent]:
        """获取视频的所有事件"""
        result = await self.session.execute(
            select(GameEvent)
            .where(GameEvent.video_id == video_id)
            .order_by(GameEvent.timestamp)
        )
        return list(result.scalars().all())
    
    async def get_by_type(
        self,
        video_id: UUID,
        event_type: str,
    ) -> List[GameEvent]:
        """根据类型获取事件"""
        result = await self.session.execute(
            select(GameEvent)
            .where(
                and_(
                    GameEvent.video_id == video_id,
                    GameEvent.event_type == event_type,
                )
            )
            .order_by(GameEvent.timestamp)
        )
        return list(result.scalars().all())
