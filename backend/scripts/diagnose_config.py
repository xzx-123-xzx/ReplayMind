"""
配置诊断脚本
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.common.path_utils import PathUtils

print("=== 路径诊断 ===")
print(f"当前文件: {__file__}")
print(f"项目根目录: {PathUtils.get_project_root()}")
print(f".env 文件路径: {PathUtils.get_project_root() / '.env'}")
print(f".env 文件存在: {(PathUtils.get_project_root() / '.env').exists()}")
print()

# 直接读取 .env 文件
env_path = PathUtils.get_project_root() / ".env"
if env_path.exists():
    print("=== .env 文件内容 (DATABASE_URL) ===")
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if 'DATABASE_URL' in line:
                print(line.strip())
print()

# 加载配置
from backend.common import settings

print("=== 加载的配置 ===")
print(f"DATABASE_URL: {settings.DATABASE_URL}")
print()
