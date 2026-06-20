"""
User Repository
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.models.user import User
from domain.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """用户仓储"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_multi_by_ids(self, ids: List[UUID]) -> List[User]:
        """根据 ID 列表获取用户"""
        result = await self.session.execute(
            select(User).where(User.id.in_(ids))
        )
        return list(result.scalars().all())
