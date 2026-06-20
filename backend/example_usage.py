#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
示例代码：展示如何使用 common 模块中的工具
"""

from backend.common import (
    PathUtils,
    settings,
    get_settings,
    logger,
    get_logger,
    chat_llm,
    vision_llm,
    get_chat_llm,
)


def example_path_utils():
    """路径工具类示例"""
    print("=" * 60)
    print("PathUtils 使用示例")
    print("=" * 60)
    
    # 获取项目根目录
    project_root = PathUtils.get_project_root()
    print(f"项目根目录: {project_root}")
    
    # 拼接路径
    data_dir = PathUtils.join("data")
    print(f"数据目录: {data_dir}")
    
    # 获取常用目录
    logs_dir = PathUtils.get_logs_dir()
    uploads_dir = PathUtils.get_uploads_dir()
    temp_dir = PathUtils.get_temp_dir()
    
    print(f"日志目录: {logs_dir}")
    print(f"上传目录: {uploads_dir}")
    print(f"临时目录: {temp_dir}")
    print()


def example_config():
    """配置示例"""
    print("=" * 60)
    print("Config 使用示例")
    print("=" * 60)
    
    # 获取配置
    print(f"应用名称: {settings.APP_NAME}")
    print(f"版本: {settings.APP_VERSION}")
    print(f"调试模式: {settings.DEBUG}")
    print(f"数据库URL: {settings.DATABASE_URL}")
    print(f"API前缀: {settings.API_PREFIX}")
    print()


def example_logger():
    """日志示例"""
    print("=" * 60)
    print("Logger 使用示例")
    print("=" * 60)
    
    # 使用默认 logger
    logger.info("这是一条 info 日志")
    logger.warning("这是一条 warning 日志")
    logger.error("这是一条 error 日志")
    
    # 获取自定义 logger
    custom_logger = get_logger("custom_module")
    custom_logger.info("这是自定义模块的日志")
    print()


def example_llm():
    """LLM 示例"""
    print("=" * 60)
    print("LLM 使用示例")
    print("=" * 60)
    
    print(f"聊天模型: {settings.MODEL_NAME}")
    print(f"视觉模型: {settings.OLLAMA_VISION_MODEL}")
    print(f"Ollama 地址: {settings.OLLAMA_HOST}")
    print()


def main():
    """主函数"""
    print("\nReplayMind Common 模块示例\n")
    
    example_path_utils()
    example_config()
    example_logger()
    example_llm()
    
    print("=" * 60)
    print("示例执行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
