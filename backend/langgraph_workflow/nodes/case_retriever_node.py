"""
Case Retriever Node
案例库检索节点
"""

from typing import Dict, Any

from common import logger
from infrastructure.db.milvus import get_milvus
from infrastructure.ai.bge_embedding import get_bge_embedding
from langgraph_workflow.state import ReplayMindState, RetrievalResult


class CaseRetrieverNode:
    """案例库检索节点"""
    
    name = "case_retriever"
    
    def __init__(self):
        self.milvus_client = get_milvus()
        self.embedding_client = get_bge_embedding()
    
    async def execute(self, state: ReplayMindState) -> Dict[str, Any]:
        """
        执行案例库检索
        
        Args:
            state: 当前状态
            
        Returns:
            Dict[str, Any]: 更新后的状态
        """
        events = state.get("events", [])
        game_type = state.get("game_type", "general")
        
        logger.info(f"Starting case retrieval for game type: {game_type}")
        
        try:
            # 构建查询
            query = self._build_case_query(events)
            
            # 案例检索
            cases = self._search_similar_cases(query, game_type)
            
            retrieval_result = RetrievalResult(
                query=query,
                documents=[],
                cases=cases,
            )
            
            logger.info(f"Case retrieval completed: {len(cases)} cases found")
            
            return {
                "case_retrieval": retrieval_result,
                "current_step": "case_retriever",
                "errors": [],
                "completed_steps": state.get("completed_steps", []) + ["case_retriever"],
            }
        except Exception as e:
            logger.error(f"Case retrieval failed: {e}")
            return {
                "case_retrieval": None,
                "errors": state.get("errors", []) + [str(e)],
                "current_step": "case_retriever",
            }
    
    def _build_case_query(self, events: list) -> str:
        """构建案例查询"""
        # 从事件中提取关键场景
        combat_events = [e for e in events if e["event_type"] == "combat"]
        descriptions = [e["description"] for e in combat_events[:3]]
        
        query = f"Similar game situations: {' '.join(descriptions)}"
        return query
    
    def _search_similar_cases(
        self,
        query: str,
        game_type: str,
        top_k: int = 5,
    ) -> list:
        """
        搜索相似案例
        
        Args:
            query: 查询文本
            game_type: 游戏类型
            top_k: 返回数量
            
        Returns:
            list: 案例列表
        """
        # 生成查询向量
        query_vector = self.embedding_client.encode_query(query)
        
        # 向量搜索
        collection = self.milvus_client.get_collection("case_base")
        
        search_params = {
            "metric_type": "IP",
            "params": {"ef": 128},
        }
        
        results = collection.search(
            data=[query_vector.tolist()],
            anns_field="description_dense",
            param=search_params,
            limit=top_k,
            output_fields=["case_id", "description", "analysis", "tags"],
        )
        
        # 提取结果
        cases = [
            {
                "case_id": hit.entity.get("case_id"),
                "description": hit.entity.get("description"),
                "analysis": hit.entity.get("analysis"),
                "tags": hit.entity.get("tags"),
                "similarity": hit.distance,
            }
            for hit in results[0]
        ]
        
        return cases
