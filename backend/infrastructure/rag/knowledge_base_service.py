"""
知识库管理服务
支持上传文档、视频解说文本等作为知识库数据
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from common import logger, settings
from infrastructure.db.milvus import get_milvus
from infrastructure.ai.bge_embedding import get_bge_embedding


class KnowledgeBaseService:
    """知识库管理服务"""
    
    def __init__(self):
        self.milvus = get_milvus()
        self.embedding = get_bge_embedding()
        self.collection_name = "knowledge_base"
    
    def add_document(
        self,
        title: str,
        content: str,
        category: str = "通用攻略",
        game_type: str = "general",
        source: str = "用户上传",
        doc_id: Optional[str] = None,
    ) -> str:
        """
        添加单个文档到知识库
        
        Args:
            title: 文档标题
            content: 文档内容
            category: 分类（如：英雄攻略、地图攻略、技巧说明）
            game_type: 游戏类型（如：MOBA、FPS、RTS）
            source: 来源
            doc_id: 文档ID（可选，自动生成）
        
        Returns:
            str: 文档ID
        """
        # 生成文档ID
        if doc_id is None:
            doc_id = f"doc-{uuid.uuid4().hex[:12]}"
        
        # 生成内容向量
        logger.info(f"Generating embedding for document: {title}")
        content_vector = self.embedding.encode_query(content)
        
        # 构建数据
        data = [{
            "doc_id": doc_id,
            "category": category,
            "game_type": game_type,
            "title": title,
            "content": content,
            "content_dense": content_vector.tolist(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": source,
        }]
        
        # 插入 Milvus
        self.milvus.insert(self.collection_name, data)
        logger.info(f"Document added to knowledge base: {doc_id}")
        
        return doc_id
    
    def add_documents_batch(
        self,
        documents: List[Dict[str, str]],
    ) -> List[str]:
        """
        批量添加文档
        
        Args:
            documents: 文档列表，每个文档包含 title, content, category, game_type, source
        
        Returns:
            List[str]: 文档ID列表
        """
        doc_ids = []
        data_list = []
        
        # 批量生成向量
        contents = [doc["content"] for doc in documents]
        logger.info(f"Generating embeddings for {len(contents)} documents...")
        vectors = self.embedding.encode(contents)
        
        for i, doc in enumerate(documents):
            doc_id = f"doc-{uuid.uuid4().hex[:12]}"
            doc_ids.append(doc_id)
            
            data_list.append({
                "doc_id": doc_id,
                "category": doc.get("category", "通用攻略"),
                "game_type": doc.get("game_type", "general"),
                "title": doc["title"],
                "content": doc["content"],
                "content_dense": vectors[i].tolist(),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": doc.get("source", "用户上传"),
            })
        
        # 批量插入
        self.milvus.insert(self.collection_name, data_list)
        logger.info(f"Batch insert completed: {len(doc_ids)} documents")
        
        return doc_ids
    
    def add_from_text_file(
        self,
        file_path: str,
        title: Optional[str] = None,
        category: str = "文档说明",
        game_type: str = "general",
        source: Optional[str] = None,
    ) -> str:
        """
        从文本文件导入
        
        Args:
            file_path: 文件路径
            title: 标题（默认使用文件名）
            category: 分类
            game_type: 游戏类型
            source: 来源（默认使用文件名）
        
        Returns:
            str: 文档ID
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # 读取文件内容
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 设置默认值
        if title is None:
            title = path.stem
        if source is None:
            source = path.name
        
        return self.add_document(
            title=title,
            content=content,
            category=category,
            game_type=game_type,
            source=source,
        )
    
    def add_from_markdown(
        self,
        file_path: str,
        game_type: str = "general",
    ) -> List[str]:
        """
        从 Markdown 文件导入（支持多段分割）
        
        Args:
            file_path: Markdown 文件路径
            game_type: 游戏类型
        
        Returns:
            List[str]: 文档ID列表
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 按 ## 分割
        sections = content.split("\n## ")
        documents = []
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
            
            lines = section.strip().split("\n")
            title = lines[0].replace("#", "").strip()
            body = "\n".join(lines[1:]).strip()
            
            if len(body) < 50:  # 忽略太短的段落
                continue
            
            documents.append({
                "title": title,
                "content": body,
                "category": "攻略文档",
                "game_type": game_type,
                "source": path.name,
            })
        
        return self.add_documents_batch(documents)
    
    def add_video_transcript(
        self,
        video_title: str,
        transcript: str,
        game_type: str = "general",
        video_url: Optional[str] = None,
        timestamps: Optional[List[Dict]] = None,
    ) -> str:
        """
        添加视频解说文本
        
        Args:
            video_title: 视频标题
            transcript: 解说文本
            game_type: 游戏类型
            video_url: 视频链接
            timestamps: 时间戳列表 [{"time": "00:01:23", "text": "..."}]
        
        Returns:
            str: 文档ID
        """
        # 构建完整内容
        content = f"视频标题：{video_title}\n\n"
        
        if video_url:
            content += f"视频链接：{video_url}\n\n"
        
        if timestamps:
            content += "时间轴解说：\n"
            for ts in timestamps:
                content += f"[{ts['time']}] {ts['text']}\n"
            content += "\n"
        
        content += f"完整解说：\n{transcript}"
        
        return self.add_document(
            title=f"[视频解说] {video_title}",
            content=content,
            category="视频解说",
            game_type=game_type,
            source=video_url or "视频上传",
        )
    
    def search(
        self,
        query: str,
        game_type: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        搜索知识库
        
        Args:
            query: 查询文本
            game_type: 游戏类型过滤
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
            output_fields=["doc_id", "title", "content", "category", "game_type", "source"],
        )
        
        # 过滤游戏类型
        filtered_results = []
        for result in results[0]:
            if game_type and result.get("game_type") != game_type:
                continue
            filtered_results.append(result)
        
        return filtered_results
    
    def delete_document(self, doc_id: str) -> bool:
        """
        删除文档
        
        Args:
            doc_id: 文档ID
        
        Returns:
            bool: 是否成功
        """
        try:
            collection = self.milvus.get_collection(self.collection_name)
            collection.delete(f'doc_id == "{doc_id}"')
            logger.info(f"Document deleted: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False


# 全局服务实例
knowledge_base_service = KnowledgeBaseService()


def get_knowledge_base_service() -> KnowledgeBaseService:
    """获取知识库服务实例"""
    return knowledge_base_service
