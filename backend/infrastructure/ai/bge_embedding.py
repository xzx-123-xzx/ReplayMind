"""
BGE Embedding 客户端
"""

from typing import List, Union, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

from common import settings, logger


class BGEEmbeddingClient:
    """BGE-M3 Embedding 客户端"""
    
    def __init__(self):
        self.model = None
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.device = settings.EMBEDDING_DEVICE
        self.batch_size = settings.EMBEDDING_BATCH_SIZE
    
    def load_model(self):
        """加载 Embedding 模型"""
        if self.model is None:
            logger.info(f"Loading BGE-M3 model: {self.model_name}")
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device,
            )
            logger.info("BGE-M3 model loaded successfully")
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: Optional[int] = None,
        normalize_embeddings: bool = True,
    ) -> np.ndarray:
        """
        生成文本嵌入
        
        Args:
            texts: 文本或文本列表
            batch_size: 批次大小
            normalize_embeddings: 是否归一化
            
        Returns:
            np.ndarray: 嵌入向量
        """
        if self.model is None:
            self.load_model()
        
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            sentences=texts,
            batch_size=batch_size or self.batch_size,
            normalize_embeddings=normalize_embeddings,
            show_progress_bar=len(texts) > 10,
        )
        
        return embeddings
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        生成查询嵌入
        
        Args:
            query: 查询文本
            
        Returns:
            np.ndarray: 查询嵌入向量
        """
        return self.encode([query])[0]
    
    def encode_documents(
        self,
        documents: List[str],
    ) -> List[np.ndarray]:
        """
        生成文档嵌入
        
        Args:
            documents: 文档列表
            
        Returns:
            List[np.ndarray]: 文档嵌入向量列表
        """
        embeddings = self.encode(documents)
        return [emb for emb in embeddings]


# 全局 BGE Embedding 客户端
bge_embedding_client = BGEEmbeddingClient()


def get_bge_embedding() -> BGEEmbeddingClient:
    """获取 BGE Embedding 客户端"""
    return bge_embedding_client
