"""
Video 模型
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, String, Integer, BigInteger, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from infrastructure.db.postgres import Base


class VideoStatus(str, Enum):
    """视频状态枚举"""
    UPLOADING = "uploading"
    PARSING = "parsing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class Video(Base):
    """视频模型"""
    
    __tablename__ = "videos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    game_type = Column(String(64), nullable=True, index=True)
    file_path = Column(String(1024), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    status = Column(
        SQLEnum(VideoStatus),
        default=VideoStatus.UPLOADING,
        nullable=False,
        index=True
    )
    duration_seconds = Column(Integer, nullable=True)
    thumbnail_path = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="videos")
    frames = relationship("VideoFrame", back_populates="video")
    transcripts = relationship("AudioTranscript", back_populates="video")
    events = relationship("GameEvent", back_populates="video")
    report = relationship("Report", back_populates="video", uselist=False)
    
    def __repr__(self):
        return f"<Video(id={self.id}, title={self.title}, status={self.status})>"


class VideoFrame(Base):
    """视频帧模型"""
    
    __tablename__ = "video_frames"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False, index=True)
    frame_number = Column(Integer, nullable=False)
    timestamp = Column(String(32), nullable=False)
    frame_path = Column(String(1024), nullable=False)
    is_keyframe = Column(Integer, default=0)
    keyframe_score = Column(String(32), nullable=True)
    
    # 关系
    video = relationship("Video", back_populates="frames")
    
    def __repr__(self):
        return f"<VideoFrame(id={self.id}, video_id={self.video_id}, frame={self.frame_number})>"


class AudioTranscript(Base):
    """音频转录模型"""
    
    __tablename__ = "audio_transcripts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False, index=True)
    start_time = Column(String(32), nullable=False)
    end_time = Column(String(32), nullable=False)
    transcript = Column(String, nullable=False)
    speaker_info = Column(String, nullable=True)
    confidence = Column(String(16), nullable=True)
    
    # 关系
    video = relationship("Video", back_populates="transcripts")
    
    def __repr__(self):
        return f"<AudioTranscript(id={self.id}, video_id={self.video_id})>"


class GameEvent(Base):
    """游戏事件模型"""
    
    __tablename__ = "game_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False, index=True)
    event_id = Column(String(64), nullable=False)
    timestamp = Column(String(32), nullable=False)
    event_type = Column(String(64), nullable=False)
    description = Column(String, nullable=False)
    confidence = Column(String(16), nullable=True)
    event_metadata = Column(String, nullable=True)
    
    # 关系
    video = relationship("Video", back_populates="events")
    
    def __repr__(self):
        return f"<GameEvent(id={self.id}, event_type={self.event_type})>"
