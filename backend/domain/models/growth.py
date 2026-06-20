"""
Growth 模型
"""

import uuid
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Float, Date, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from infrastructure.db.postgres import Base


class GrowthRecord(Base):
    """成长记录模型"""
    
    __tablename__ = "growth_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    record_date = Column(Date, nullable=False, index=True)
    total_replays = Column(Integer, default=0)
    avg_replay_score = Column(Float, nullable=True)
    ability_radar = Column(JSON, default=dict)
    trend_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="growth_records")
    
    def __repr__(self):
        return f"<GrowthRecord(id={self.id}, user_id={self.user_id}, date={self.record_date})>"
