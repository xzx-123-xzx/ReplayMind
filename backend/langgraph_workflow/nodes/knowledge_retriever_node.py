"""
Knowledge Retriever Node
知识库检索节点
"""

from typing import Dict, Any
import numpy as np

from common import logger
from infrastructure.db.milvus import get_milvus
from infrastructure.ai.bge_embedding import get_bge_embedding
from infrastructure.ai.bge_reranker import get_bge_reranker
from langgraph_workflow.state import ReplayMindState, RetrievalResult


class KnowledgeRetrieverNode:
    """知识库检索节点"""
    
    name = "knowledge_retriever"
    
    def __init__(self):
        self.milvus_client = get_milvus()
        self.embedding_client = get_bge_embedding()
        self.reranker_client = get_bge_reranker()
    
    async def execute(self, state: ReplayMindState) -> Dict[str, Any]:
        """
        执行知识库检索
        
        Args:
            state: 当前状态
            
        Returns:
            Dict[str, Any]: 更新后的状态
        """
        events = state.get("events", [])
        game_type = state.get("game_type", "general")
        
        logger.info(f"Starting knowledge retrieval for game type: {game_type}")
        
        try:
            # 构建查询
            query = self._build_query(events)
            
            # 向量检索
            documents = self._hybrid_search(query, game_type)
            
            retrieval_result = RetrievalResult(
                query=query,
                documents=documents,
                cases=[],
            )
            
            logger.info(f"Knowledge retrieval completed: {len(documents)} documents found")
            
            return {
                "knowledge_retrieval": retrieval_result,
                "current_step": "knowledge_retriever",
                "errors": [],
                "completed_steps": state.get("completed_steps", []) + ["knowledge_retriever"],
            }
        except Exception as e:
            logger.error(f"Knowledge retrieval failed: {e}")
            return {
                "knowledge_retrieval": None,
                "errors": state.get("errors", []) + [str(e)],
                "current_step": "knowledge_retriever",
            }
    
    def _build_query(self, events: list) -> str:
        """构建检索查询"""
        # 从事件中提取关键信息构建查询
        event_types = [e["event_type"] for e in events[:5]]
        descriptions = [e["description"] for e in events[:3]]
        
        query = f"Game analysis for events: {', '.join(event_types)}. "
        query += f"Key moments: {' '.join(descriptions)}"
        
        return query
    
    def _hybrid_search(
        self,
        query: str,
        game_type: str,
        top_k: int = 10,
    ) -> list:
        """
        混合搜索
        
        Args:
            query: 查询文本
            game_type: 游戏类型
            top_k: 返回数量
            
        Returns:
            list: 检索结果列表
        """
        # 生成查询向量
        query_vector = self.embedding_client.encode_query(query)
        
        # 向量搜索
        collection = self.milvus_client.get_collection("knowledge_base")
        
        search_params = {
            "metric_type": "IP",
            "params": {"ef": 128},
        }
        
        results = collection.search(
            data=[query_vector.tolist()],
            anns_field="content_dense",
            param=search_params,
            limit=top_k,
            output_fields=["title", "content", "category", "source"],
        )
        
        # 提取结果
        documents = [
            {
                "title": hit.entity.get("title"),
                "content": hit.entity.get("content"),
                "category": hit.entity.get("category"),
                "source": hit.entity.get("source"),
                "score": hit.distance,
            }
            for hit in results[0]
        ]
        
        return documents
