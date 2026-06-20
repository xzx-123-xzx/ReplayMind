"""
BGE Reranker 客户端
"""

from typing import List, Tuple, Union
import numpy as np
from sentence_transformers import CrossEncoder

from common import settings, logger


class BGERerankerClient:
    """BGE-Reranker 客户端"""
    
    def __init__(self):
        self.model = None
        self.model_name = settings.RERANKER_MODEL_NAME
        self.device = settings.RERANKER_DEVICE
        self.top_k = settings.RERANKER_TOP_K
    
    def load_model(self):
        """加载 Reranker 模型"""
        if self.model is None:
            logger.info(f"Loading BGE-Reranker model: {self.model_name}")
            self.model = CrossEncoder(
                self.model_name,
                device=self.device,
            )
            logger.info("BGE-Reranker model loaded successfully")
    
    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None,
    ) -> List[Tuple[int, float]]:
        """
        对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 文档列表
            top_k: 返回前 k 个
            
        Returns:
            List[Tuple[int, float]]: (文档索引, 相关性分数) 列表
        """
        if self.model is None:
            self.load_model()
        
        # 构建查询-文档对
        pairs = [[query, doc] for doc in documents]
        
        # 计算相关性分数
        scores = self.model.predict(pairs)
        
        # 按分数排序
        ranked_indices = np.argsort(scores)[::-1]
        k = top_k or self.top_k
        
        results = [
            (int(idx), float(scores[idx]))
            for idx in ranked_indices[:k]
        ]
        
        return results
    
    def rerank_with_scores(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None,
    ) -> List[Tuple[str, float]]:
        """
        对文档进行重排序，返回文档和分数
        
        Args:
            query: 查询文本
            documents: 文档列表
            top_k: 返回前 k 个
            
        Returns:
            List[Tuple[str, float]]: (文档, 相关性分数) 列表
        """
        ranked_results = self.rerank(query, documents, top_k)
        
        return [
            (documents[idx], score)
            for idx, score in ranked_results
        ]


# 全局 BGE Reranker 客户端
bge_reranker_client = BGERerankerClient()


def get_bge_reranker() -> BGERerankerClient:
    """获取 BGE Reranker 客户端"""
    return bge_reranker_client
