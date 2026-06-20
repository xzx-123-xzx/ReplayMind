import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from .config import settings
from .path_utils import PathUtils


def setup_logger(
    name: str = "replaymind",
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    设置并获取日志记录器
    
    Args:
        name: 日志记录器名称
        log_level: 日志级别，默认为 settings.LOG_LEVEL
        log_file: 日志文件路径，默认为 None（仅输出到控制台）
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 如果已经配置过，直接返回
    if logger.handlers:
        return logger
    
    # 设置日志级别
    level = getattr(logging, (log_level or settings.LOG_LEVEL).upper(), logging.INFO)
    logger.setLevel(level)
    
    # 避免重复添加 handler
    logger.propagate = False
    
    # 日志格式
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # 控制台输出 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件输出 handler
    if settings.LOG_TO_FILE or log_file:
        if log_file is None:
            log_dir = PathUtils.get_logs_dir()
            log_file = log_dir / f"{name}.log"
        
        file_handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=settings.LOG_FILE_MAX_BYTES,
            backupCount=settings.LOG_FILE_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# 默认日志记录器
logger = setup_logger()


def get_logger(name: str = "replaymind") -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
    
    Returns:
        logging.Logger: 日志记录器
    """
    return logging.getLogger(name)
