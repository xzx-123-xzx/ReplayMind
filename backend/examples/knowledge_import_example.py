"""
知识库数据导入示例
演示如何上传文档、视频解说等作为知识库
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.rag.knowledge_base_service import get_knowledge_base_service
from infrastructure.rag.case_base_service import get_case_base_service


def example_add_single_document():
    """示例1: 添加单个文档"""
    print("\n" + "=" * 60)
    print("示例1: 添加单个文档到知识库")
    print("=" * 60)
    
    service = get_knowledge_base_service()
    
    doc_id = service.add_document(
        title="后羿对线技巧详解",
        content="""
后羿是王者荣耀中的远程射手英雄，前期较弱，后期伤害爆炸。

【对线技巧】
1. 前期（1-4级）：猥琐发育，利用二技能清兵，不要轻易上前换血
2. 中期（5-8级）：有了一定装备后，可以尝试消耗，但要注意走位
3. 后期（9级+）：伤害成型，团战找好输出位置，优先攻击前排

【出装推荐】
急速战靴 -> 末世 -> 无尽战刃 -> 破晓 -> 泣血之刃 -> 破军

【注意事项】
- 没有位移技能，非常依赖走位和辅助保护
- 大招可以远程支援，注意观察小地图
- 一技能可以探测草丛，防止被蹲
        """,
        category="英雄攻略",
        game_type="MOBA",
        source="官方攻略",
    )
    
    print(f"✅ 文档已添加，ID: {doc_id}")


def example_add_video_transcript():
    """示例2: 添加视频解说"""
    print("\n" + "=" * 60)
    print("示例2: 添加视频解说到知识库")
    print("=" * 60)
    
    service = get_knowledge_base_service()
    
    doc_id = service.add_video_transcript(
        video_title="王者荣耀：如何提高意识水平",
        transcript="""
大家好，今天来聊聊如何提高游戏意识。

首先，什么是意识？意识就是对局势的判断能力，包括：
1. 敌我位置判断
2. 资源争夺时机
3. 开团时机选择
4. 撤退时机判断

提高意识的方法：
第一，多看小地图。每5秒看一次小地图，了解敌人动向。
第二，学会预判。根据敌人最后出现位置，预判他们可能去哪里。
第三，理解兵线。兵线决定节奏，优势要推塔，劣势要清线。
第四，注意资源。暴君、主宰刷新时间要记住，提前布局。

最后，多复盘。每次死亡后思考：为什么会死？下次如何避免？
        """,
        game_type="MOBA",
        video_url="https://example.com/video/123",
        timestamps=[
            {"time": "00:00:10", "text": "什么是意识"},
            {"time": "00:01:30", "text": "提高意识的方法"},
            {"time": "00:05:00", "text": "复盘的重要性"},
        ],
    )
    
    print(f"✅ 视频解说已添加，ID: {doc_id}")


def example_batch_add_documents():
    """示例3: 批量添加文档"""
    print("\n" + "=" * 60)
    print("示例3: 批量添加文档")
    print("=" * 60)
    
    service = get_knowledge_base_service()
    
    documents = [
        {
            "title": "鲁班七号攻略",
            "content": "鲁班七号是高爆发射手，被动扫射伤害极高。前期猥琐，后期站撸。",
            "category": "英雄攻略",
            "game_type": "MOBA",
            "source": "玩家投稿",
        },
        {
            "title": "孙尚香攻略",
            "content": "孙尚香是灵活型射手，一技能翻滚后强化普攻。擅长消耗和追击。",
            "category": "英雄攻略",
            "game_type": "MOBA",
            "source": "玩家投稿",
        },
        {
            "title": "马可波罗攻略",
            "content": "马可波罗是真实伤害射手，技能附带真伤。适合打坦克阵容。",
            "category": "英雄攻略",
            "game_type": "MOBA",
            "source": "玩家投稿",
        },
    ]
    
    doc_ids = service.add_documents_batch(documents)
    print(f"✅ 批量添加完成，共 {len(doc_ids)} 个文档")
    print(f"文档ID: {doc_ids}")


def example_add_cases():
    """示例4: 添加案例库"""
    print("\n" + "=" * 60)
    print("示例4: 添加案例到案例库")
    print("=" * 60)
    
    service = get_case_base_service()
    
    cases = [
        {
            "description": "下路2v2对拼，我方辅助先手开团，但站位过于靠前被对方射手集火秒杀",
            "analysis": """
【问题分析】
1. 辅助开团时机正确，但站位失误
2. 没有注意对方打野位置，盲目开团
3. 射手没有跟上输出，导致辅助被秒

【正确做法】
1. 先确认对方打野位置（看小地图）
2. 辅助开团后立即后撤，让射手输出
3. 保持阵型，不要脱节
            """,
            "event_type": "团战",
            "game_type": "MOBA",
            "player_level": "王者",
            "tags": ["团战", "下路", "站位失误"],
        },
        {
            "description": "中路法师被对方打野Gank，闪现过墙逃生成功",
            "analysis": """
【正确操作】
1. 提前在河道草丛插眼，发现敌方打野
2. 及时后撤，拉开距离
3. 闪现过墙时机准确，成功逃生

【关键点】
- 意识到位，提前插眼
- 反应迅速，果断交闪
- 熟悉地形，知道可以过墙的位置
            """,
            "event_type": "Gank",
            "game_type": "MOBA",
            "player_level": "大师",
            "tags": ["Gank", "逃生", "意识"],
        },
    ]
    
    case_ids = service.add_cases_batch(cases)
    print(f"✅ 案例添加完成，共 {len(case_ids)} 个案例")
    print(f"案例ID: {case_ids}")


def example_search_knowledge():
    """示例5: 搜索知识库"""
    print("\n" + "=" * 60)
    print("示例5: 搜索知识库")
    print("=" * 60)
    
    service = get_knowledge_base_service()
    
    query = "后羿前期怎么打"
    results = service.search(query, game_type="MOBA", top_k=3)
    
    print(f"查询: {query}")
    print(f"找到 {len(results)} 条结果:\n")
    
    for i, result in enumerate(results, 1):
        print(f"【结果 {i}】")
        print(f"标题: {result.get('title')}")
        print(f"分类: {result.get('category')}")
        print(f"相似度: {result.get('distance', 0):.4f}")
        print(f"内容摘要: {result.get('content', '')[:100]}...")
        print()


def example_search_cases():
    """示例6: 搜索案例库"""
    print("\n" + "=" * 60)
    print("示例6: 搜索案例库")
    print("=" * 60)
    
    service = get_case_base_service()
    
    query = "下路团战站位"
    results = service.search_similar_cases(query, game_type="MOBA", top_k=3)
    
    print(f"查询: {query}")
    print(f"找到 {len(results)} 条相似案例:\n")
    
    for i, result in enumerate(results, 1):
        print(f"【案例 {i}】")
        print(f"事件类型: {result.get('event_type')}")
        print(f"玩家水平: {result.get('player_level')}")
        print(f"场景描述: {result.get('description')[:100]}...")
        print(f"分析: {result.get('analysis', '')[:150]}...")
        print()


def example_import_from_file():
    """示例7: 从文件导入"""
    print("\n" + "=" * 60)
    print("示例7: 从文件导入知识库")
    print("=" * 60)
    
    # 创建示例文件
    sample_file = Path(__file__).parent / "sample_knowledge.txt"
    sample_content = """
王者荣耀地图攻略

【上路】
上路通常是战士或坦克的路线，单人对线为主。
关键点：
1. 控制兵线，不要压太深
2. 注意河道草丛，防止被Gank
3. 适时支援中路或入侵敌方野区

【中路】
中路是法师的路线，距离最短，支援最快。
关键点：
1. 快速清线，然后游走支援
2. 在河道插眼，保护自己
3. 配合打野抓上路或下路

【下路】
下路是射手+辅助的组合，团队核心输出。
关键点：
1. 射手猥琐发育，辅助保护视野
2. 控制小龙，争夺资源
3. 团战时射手找好输出位置
    """
    
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write(sample_content)
    
    print(f"示例文件已创建: {sample_file}")
    
    service = get_knowledge_base_service()
    doc_id = service.add_from_text_file(
        str(sample_file),
        title="王者荣耀地图攻略",
        category="地图攻略",
        game_type="MOBA",
    )
    
    print(f"✅ 文件导入成功，文档ID: {doc_id}")
    
    # 清理示例文件
    sample_file.unlink()


def main():
    """运行所有示例"""
    print("\n")
    print("#" * 60)
    print("#  ReplayMind 知识库数据导入示例")
    print("#" * 60)
    
    try:
        # 运行示例
        example_add_single_document()
        example_add_video_transcript()
        example_batch_add_documents()
        example_add_cases()
        example_search_knowledge()
        example_search_cases()
        example_import_from_file()
        
        print("\n" + "#" * 60)
        print("#  所有示例运行完成！")
        print("#" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
