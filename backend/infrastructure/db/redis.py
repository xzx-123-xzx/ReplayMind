"""
Redis 连接和缓存管理
"""

import json
from typing import Optional, Any
from redis.asyncio import Redis, ConnectionPool

from common import settings, logger


# Redis 连接池
redis_pool: Optional[ConnectionPool] = None
redis_client: Optional[Redis] = None


async def init_redis():
    """初始化 Redis 连接"""
    global redis_pool, redis_client
    
    logger.info(f"Initializing Redis with URL: {settings.REDIS_URL}")
    
    try:
        redis_pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_POOL_SIZE,
            decode_responses=True,
        )
        redis_client = Redis(connection_pool=redis_pool)
        
        # 测试连接
        await redis_client.ping()
        logger.info("Redis initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        raise


async def close_redis():
    """关闭 Redis 连接"""
    global redis_client, redis_pool
    
    if redis_client:
        await redis_client.close()
    if redis_pool:
        await redis_pool.disconnect()
    
    logger.info("Redis connections closed")


def get_redis() -> Redis:
    """
    获取 Redis 客户端
    
    Returns:
        Redis: Redis 客户端实例
    """
    if redis_client is None:
        raise RuntimeError("Redis not initialized")
    return redis_client


# 缓存操作辅助函数
async def cache_set(key: str, value: Any, expire: int = 3600):
    """
    设置缓存
    
    Args:
        key: 缓存键
        value: 缓存值
        expire: 过期时间（秒）
    """
    redis = get_redis()
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False)
    await redis.set(key, value, ex=expire)


async def cache_get(key: str) -> Optional[Any]:
    """
    获取缓存
    
    Args:
        key: 缓存键
        
    Returns:
        Optional[Any]: 缓存值
    """
    redis = get_redis()
    value = await redis.get(key)
    
    if value:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return None


async def cache_delete(key: str):
    """删除缓存"""
    redis = get_redis()
    await redis.delete(key)


async def cache_exists(key: str) -> bool:
    """检查缓存是否存在"""
    redis = get_redis()
    return await redis.exists(key) > 0
