"""
案例库管理服务
支持上传高分玩家案例、游戏场景分析等
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from common import logger
from infrastructure.db.milvus import get_milvus
from infrastructure.ai.bge_embedding import get_bge_embedding


class CaseBaseService:
    """案例库管理服务"""
    
    def __init__(self):
        self.milvus = get_milvus()
        self.embedding = get_bge_embedding()
        self.collection_name = "case_base"
    
    def add_case(
        self,
        description: str,
        analysis: str,
        event_type: str = "通用场景",
        game_type: str = "general",
        player_level: str = "普通",
        tags: Optional[List[str]] = None,
        case_id: Optional[str] = None,
    ) -> str:
        """
        添加单个案例
        
        Args:
            description: 场景描述
            analysis: 分析说明
            event_type: 事件类型（如：团战、对线、Gank）
            game_type: 游戏类型
            player_level: 玩家水平（如：王者、大师、钻石）
            tags: 标签列表
            case_id: 案例ID（可选）
        
        Returns:
            str: 案例ID
        """
        if case_id is None:
            case_id = f"case-{uuid.uuid4().hex[:12]}"
        
        if tags is None:
            tags = []
        
        # 生成向量
        logger.info(f"Generating embedding for case: {case_id}")
        description_vector = self.embedding.encode_query(description)
        
        # 构建数据
        data = [{
            "case_id": case_id,
            "game_type": game_type,
            "player_level": player_level,
            "event_type": event_type,
            "description": description,
            "analysis": analysis,
            "description_dense": description_vector.tolist(),
            "tags": ",".join(tags),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }]
        
        # 插入 Milvus
        self.milvus.insert(self.collection_name, data)
        logger.info(f"Case added to case base: {case_id}")
        
        return case_id
    
    def add_cases_batch(
        self,
        cases: List[Dict[str, Any]],
    ) -> List[str]:
        """
        批量添加案例
        
        Args:
            cases: 案例列表
        
        Returns:
            List[str]: 案例ID列表
        """
        case_ids = []
        data_list = []
        
        # 批量生成向量
        descriptions = [case["description"] for case in cases]
        logger.info(f"Generating embeddings for {len(descriptions)} cases...")
        vectors = self.embedding.encode(descriptions)
        
        for i, case in enumerate(cases):
            case_id = f"case-{uuid.uuid4().hex[:12]}"
            case_ids.append(case_id)
            
            tags = case.get("tags", [])
            
            data_list.append({
                "case_id": case_id,
                "game_type": case.get("game_type", "general"),
                "player_level": case.get("player_level", "普通"),
                "event_type": case.get("event_type", "通用场景"),
                "description": case["description"],
                "analysis": case["analysis"],
                "description_dense": vectors[i].tolist(),
                "tags": ",".join(tags) if isinstance(tags, list) else tags,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        
        # 批量插入
        self.milvus.insert(self.collection_name, data_list)
        logger.info(f"Batch insert completed: {len(case_ids)} cases")
        
        return case_ids
    
    def search_similar_cases(
        self,
        query: str,
        game_type: Optional[str] = None,
        event_type: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        搜索相似案例
        
        Args:
            query: 查询文本
            game_type: 游戏类型过滤
            event_type: 事件类型过滤
            top_k: 返回数量
        
        Returns:
            List[Dict]: 搜索结果
        """
        # 生成查询向量
        query_vector = self.embedding.encode_query(query)
        
        # 向量搜索
        results = self.milvus.search(
            self.collection_name,
            vectors=[query_vector.tolist()],
            top_k=top_k,
            output_fields=["case_id", "description", "analysis", "event_type", "player_level", "tags"],
        )
        
        # 过滤
        filtered_results = []
        for result in results[0]:
            if game_type and result.get("game_type") != game_type:
                continue
            if event_type and result.get("event_type") != event_type:
                continue
            filtered_results.append(result)
        
        return filtered_results


# 全局服务实例
case_base_service = CaseBaseService()


def get_case_base_service() -> CaseBaseService:
    """获取案例库服务实例"""
    return case_base_service
