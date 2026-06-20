"""
PostgreSQL 连接诊断脚本
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.common import settings


async def test_connection():
    """测试数据库连接"""
    print(f"尝试连接: {settings.DATABASE_URL}")
    print(f"主机: localhost")
    print(f"端口: 5432")
    print()

    try:
        import asyncpg

        print("正在连接...")
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='123456',
            database='replaymind',
            timeout=5
        )
        print("连接成功!")

        # 执行简单查询
        result = await conn.fetchval("SELECT version();")
        print(f"数据库版本: {result[:80]}...")

        await conn.close()
        print("连接已关闭")

    except asyncpg.InvalidCatalogNameError as e:
        print(f"错误: 数据库 'replaymind' 不存在!")
        print(f"请先创建数据库: CREATE DATABASE replaymind;")
    except asyncpg.InvalidPasswordError as e:
        print(f"错误: 用户名或密码错误!")
        print(f"请检查配置或创建用户:")
        print(f"  CREATE USER replaymind WITH PASSWORD 'replaymind123';")
        print(f"  CREATE DATABASE replaymind OWNER replaymind;")
    except asyncpg.PostgreSQLError as e:
        print(f"PostgreSQL 错误: {e}")
    except ConnectionRefusedError as e:
        print(f"错误: 连接被拒绝!")
        print(f"请确保 PostgreSQL 服务正在运行，并监听在 5432 端口")
    except Exception as e:
        print(f"错误: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(test_connection())
