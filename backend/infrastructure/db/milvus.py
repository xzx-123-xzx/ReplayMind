"""
Milvus 向量数据库客户端
"""

from typing import List, Optional, Dict, Any
from pymilvus import (
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    connections,
    utility,
)

from common import settings, logger


class MilvusClient:
    """Milvus 向量数据库客户端"""
    
    def __init__(self):
        self.host = settings.MILVUS_HOST
        self.port = settings.MILVUS_PORT
        self.collection_prefix = settings.MILVUS_COLLECTION_PREFIX
        self._connected = False
    
    def connect(self):
        """连接到 Milvus"""
        if not self._connected:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port,
            )
            self._connected = True
            logger.info(f"Connected to Milvus at {self.host}:{self.port}")
    
    def disconnect(self):
        """断开连接"""
        if self._connected:
            connections.disconnect("default")
            self._connected = False
            logger.info("Disconnected from Milvus")
    
    def create_knowledge_base_collection(self):
        """创建知识库 Collection"""
        collection_name = f"{self.collection_prefix}knowledge_base"
        
        if utility.has_collection(collection_name):
            logger.info(f"Collection {collection_name} already exists")
            return
        
        # 定义字段
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="game_type", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="content_dense", dtype=DataType.FLOAT_VECTOR, dim=1024),
            FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=256),
        ]
        
        # 创建 Schema
        schema = CollectionSchema(
            fields=fields,
            description="ReplayMind Knowledge Base"
        )
        
        # 创建 Collection
        collection = Collection(
            name=collection_name,
            schema=schema,
        )
        
        # 创建索引
        index_params = {
            "index_type": "HNSW",
            "metric_type": "IP",
            "params": {"M": 16, "efConstruction": 200},
        }
        collection.create_index(
            field_name="content_dense",
            index_params=index_params,
        )
        
        collection.load()
        logger.info(f"Created collection {collection_name}")
    
    def create_case_base_collection(self):
        """创建案例库 Collection"""
        collection_name = f"{self.collection_prefix}case_base"
        
        if utility.has_collection(collection_name):
            logger.info(f"Collection {collection_name} already exists")
            return
        
        # 定义字段
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="case_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="game_type", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="player_level", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="event_type", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="analysis", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="description_dense", dtype=DataType.FLOAT_VECTOR, dim=1024),
            FieldSchema(name="tags", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=32),
        ]
        
        # 创建 Schema
        schema = CollectionSchema(
            fields=fields,
            description="ReplayMind Case Base"
        )
        
        # 创建 Collection
        collection = Collection(
            name=collection_name,
            schema=schema,
        )
        
        # 创建索引
        index_params = {
            "index_type": "HNSW",
            "metric_type": "IP",
            "params": {"M": 16, "efConstruction": 200},
        }
        collection.create_index(
            field_name="description_dense",
            index_params=index_params,
        )
        
        collection.load()
        logger.info(f"Created collection {collection_name}")
    
    def get_collection(self, name: str) -> Collection:
        """
        获取 Collection
        
        Args:
            name: Collection 名称
            
        Returns:
            Collection: Collection 实例
        """
        collection_name = f"{self.collection_prefix}{name}"
        return Collection(collection_name)
    
    def insert(
        self,
        collection_name: str,
        data: List[Dict[str, Any]],
    ) -> List[int]:
        """
        插入数据
        
        Args:
            collection_name: Collection 名称
            data: 要插入的数据列表
            
        Returns:
            List[int]: 插入的 ID 列表
        """
        collection = self.get_collection(collection_name)
        result = collection.insert(data)
        collection.flush()
        return result.primary_keys
    
    def search(
        self,
        collection_name: str,
        vectors: List[List[float]],
        top_k: int = 5,
        output_fields: Optional[List[str]] = None,
    ) -> List[List[Dict[str, Any]]]:
        """
        向量搜索
        
        Args:
            collection_name: Collection 名称
            vectors: 查询向量
            top_k: 返回数量
            output_fields: 输出字段
            
        Returns:
            List[List[Dict[str, Any]]]: 搜索结果
        """
        collection = self.get_collection(collection_name)
        
        search_params = {
            "metric_type": "IP",
            "params": {"ef": 128},
        }
        
        results = collection.search(
            data=vectors,
            anns_field="content_dense",
            param=search_params,
            limit=top_k,
            output_fields=output_fields or ["*"],
        )
        
        return [
            [
                {
                    "id": hit.id,
                    "distance": hit.distance,
                    **hit.entity
                }
                for hit in result
            ]
            for result in results
        ]


# 全局 Milvus 客户端
milvus_client = MilvusClient()


def get_milvus() -> MilvusClient:
    """获取 Milvus 客户端"""
    if not milvus_client._connected:
        milvus_client.connect()
    return milvus_client
