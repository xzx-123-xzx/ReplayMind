import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache
from .path_utils import PathUtils


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = "ReplayMind"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://replaymind:replaymind123@localhost:5432/replaymind"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 10
    
    # Milvus 配置
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION_PREFIX: str = "replaymind_"
    
    # MinIO 配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "replaymind"
    MINIO_SECRET_KEY: str = "replaymind123"
    MINIO_BUCKET_NAME: str = "replaymind"
    MINIO_SECURE: bool = False
    
    # DeepSeek 配置（替代 Ollama 聊天模型）
    MODEL_API_KEY: str = ""
    MODEL_BASE_URL: str = "https://api.deepseek.com"
    MODEL_NAME: str = "deepseek-v4-flash"
    
    # Ollama 配置（仅用于视觉模型）
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_VISION_MODEL: str = "qwen2.5-vl:7b"
    
    # Embedding 配置
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-m3"
    EMBEDDING_DEVICE: str = "cuda"
    EMBEDDING_BATCH_SIZE: int = 32
    
    # Reranker 配置
    RERANKER_MODEL_NAME: str = "BAAI/bge-reranker-v2-m3"
    RERANKER_DEVICE: str = "cuda"
    RERANKER_TOP_K: int = 5
    
    # Whisper 配置
    WHISPER_MODEL_SIZE: str = "base"
    WHISPER_DEVICE: str = "cuda"
    WHISPER_LANGUAGE: Optional[str] = "zh"
    
    # 视频处理配置
    VIDEO_MAX_SIZE_MB: int = 500
    VIDEO_ALLOWED_FORMATS: list = ["mp4", "avi", "mov", "mkv"]
    VIDEO_KEYFRAME_INTERVAL: float = 2.0
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_TO_FILE: bool = True
    LOG_FILE_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5
    
    # JWT 配置
    JWT_SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # CORS 配置
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    model_config = {
        "env_file": PathUtils.get_project_root() / ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例
    
    Returns:
        Settings: 配置对象
    """
    return Settings()


settings = get_settings()
