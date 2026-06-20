"""
PostgreSQL 数据库连接和会话管理
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from common import settings, logger


class Base(DeclarativeBase):
    """SQLAlchemy 声明基类"""
    pass


# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
    future=True,
)

# 创建会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db():
    """初始化数据库"""
    try:
        # 创建所有表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
    logger.info("Database connections closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖项
    
    Yields:
        AsyncSession: 数据库会话
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
