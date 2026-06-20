"""
数据库初始化脚本
创建 PostgreSQL 表、Milvus Collection、MinIO Bucket
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.infrastructure.db.postgres import engine, Base
from backend.infrastructure.db.milvus import get_milvus
from backend.infrastructure.storage.minio_client import MinioClient


async def create_postgres_tables():
    """创建 PostgreSQL 表"""
    print("=" * 50)
    print("1. Creating PostgreSQL tables...")
    print("=" * 50)

    # 导入所有模型以确保它们被注册到 Base.metadata
    from backend.domain.models import user, video, report, growth

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("PostgreSQL tables created successfully!")
    print("Tables: users, videos, video_frames, audio_transcripts, game_events, reports, scores, recommendations, growth_records")


def create_milvus_collections():
    """创建 Milvus Collection"""
    print("\n" + "=" * 50)
    print("2. Creating Milvus Collections...")
    print("=" * 50)

    milvus = get_milvus()
    milvus.connect()

    # 创建知识库 Collection
    milvus.create_knowledge_base_collection()
    print("Collection: replaymind_knowledge_base (created)")

    # 创建案例库 Collection
    milvus.create_case_base_collection()
    print("Collection: replaymind_case_base (created)")


def create_minio_bucket():
    """创建 MinIO Bucket"""
    print("\n" + "=" * 50)
    print("3. Creating MinIO Bucket...")
    print("=" * 50)

    minio_client = MinioClient()
    minio_client.ensure_bucket()
    print("Bucket: replaymind (ready)")


async def main():
    """主函数"""
    print("\n")
    print("#" * 60)
    print("#  ReplayMind 数据库初始化脚本")
    print("#" * 60)

    try:
        # 1. PostgreSQL
        await create_postgres_tables()

        # 2. Milvus
        create_milvus_collections()

        # 3. MinIO
        try:
            create_minio_bucket()
        except Exception as e:
            print(f"\n警告: MinIO 初始化失败，后续可手动处理 - {e}")
            print("请确保 MinIO 服务正在运行并检查 .env 中的 MINIO_ACCESS_KEY/MINIO_SECRET_KEY")

        print("\n" + "#" * 60)
        print("#  数据库初始化完成! (PostgreSQL + Milvus 已就绪)")
        print("#" * 60)
        print("\n")

    except Exception as e:
        print(f"\n错误: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
