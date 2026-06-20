"""
Base Repository
基础仓储类
"""

from typing import Generic, TypeVar, Type, Optional, List, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import DeclarativeMeta

from common import logger

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


class BaseRepository(Generic[ModelType]):
    """基础仓储类"""
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def get(self, id: UUID) -> Optional[ModelType]:
        """
        根据 ID 获取单个记录
        
        Args:
            id: 记录 ID
            
        Returns:
            Optional[ModelType]: 记录或 None
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters,
    ) -> List[ModelType]:
        """
        获取多条记录
        
        Args:
            skip: 跳过的记录数
            limit: 返回的记录数
            **filters: 过滤条件
            
        Returns:
            List[ModelType]: 记录列表
        """
        query = select(self.model)
        
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def create(self, **kwargs) -> ModelType:
        """
        创建记录
        
        Args:
            **kwargs: 记录属性
            
        Returns:
            ModelType: 创建的记录
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        
        logger.info(f"Created {self.model.__name__}: {instance.id}")
        return instance
    
    async def update(
        self,
        id: UUID,
        **kwargs,
    ) -> Optional[ModelType]:
        """
        更新记录
        
        Args:
            id: 记录 ID
            **kwargs: 要更新的属性
            
        Returns:
            Optional[ModelType]: 更新后的记录
        """
        await self.session.execute(
            update(self.model).where(self.model.id == id).values(**kwargs)
        )
        await self.session.flush()
        
        return await self.get(id)
    
    async def delete(self, id: UUID) -> bool:
        """
        删除记录
        
        Args:
            id: 记录 ID
            
        Returns:
            bool: 是否删除成功
        """
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.flush()
        
        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"Deleted {self.model.__name__}: {id}")
        
        return deleted
    
    async def count(self, **filters) -> int:
        """
        统计记录数量
        
        Args:
            **filters: 过滤条件
            
        Returns:
            int: 记录数量
        """
        query = select(func.count()).select_from(self.model)
        
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        result = await self.session.execute(query)
        return result.scalar()
