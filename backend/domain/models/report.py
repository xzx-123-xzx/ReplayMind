"""
Report 模型
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from infrastructure.db.postgres import Base


class Report(Base):
    """复盘报告模型"""
    
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    markdown_content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    video = relationship("Video", back_populates="report")
    user = relationship("User", back_populates="reports")
    scores = relationship("Score", back_populates="report", uselist=False)
    recommendations = relationship("Recommendation", back_populates="report")
    
    def __repr__(self):
        return f"<Report(id={self.id}, video_id={self.video_id})>"


class Score(Base):
    """评分模型"""
    
    __tablename__ = "scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False, unique=True, index=True)
    operation_score = Column(Integer, nullable=False)
    awareness_score = Column(Integer, nullable=False)
    decision_score = Column(Integer, nullable=False)
    teamwork_score = Column(Integer, nullable=False)
    replay_score = Column(Integer, nullable=False)
    score_details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    report = relationship("Report", back_populates="scores")
    
    def __repr__(self):
        return f"<Score(report_id={self.report_id}, replay_score={self.replay_score})>"


class Recommendation(Base):
    """建议模型"""
    
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False, index=True)
    category = Column(String(128), nullable=False)
    content = Column(Text, nullable=False)
    priority = Column(Integer, default=1)
    is_actionable = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    report = relationship("Report", back_populates="recommendations")
    
    def __repr__(self):
        return f"<Recommendation(id={self.id}, category={self.category})>"
