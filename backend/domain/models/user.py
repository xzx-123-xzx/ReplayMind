"""
User 模型
"""

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from infrastructure.db.postgres import Base


class User(Base):
    """用户模型"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    avatar_url = Column(String(512), nullable=True)
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    videos = relationship("Video", back_populates="user")
    reports = relationship("Report", back_populates="user")
    growth_records = relationship("GrowthRecord", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
