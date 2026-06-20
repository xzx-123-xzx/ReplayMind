"""
知识库 API 接口
提供知识库和案例库的上传、搜索接口
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel

from infrastructure.rag.knowledge_base_service import get_knowledge_base_service
from infrastructure.rag.case_base_service import get_case_base_service


router = APIRouter()


# ==================== 请求模型 ====================

class DocumentUpload(BaseModel):
    """文档上传请求"""
    title: str
    content: str
    category: str = "通用攻略"
    game_type: str = "general"
    source: str = "用户上传"


class VideoTranscriptUpload(BaseModel):
    """视频解说上传请求"""
    video_title: str
    transcript: str
    game_type: str = "general"
    video_url: Optional[str] = None
    timestamps: Optional[List[dict]] = None


class CaseUpload(BaseModel):
    """案例上传请求"""
    description: str
    analysis: str
    event_type: str = "通用场景"
    game_type: str = "general"
    player_level: str = "普通"
    tags: Optional[List[str]] = None


class SearchQuery(BaseModel):
    """搜索请求"""
    query: str
    game_type: Optional[str] = None
    top_k: int = 5


# ==================== 知识库接口 ====================

@router.post("/knowledge/upload")
async def upload_document(doc: DocumentUpload):
    """
    上传文档到知识库
    
    - **title**: 文档标题
    - **content**: 文档内容
    - **category**: 分类（如：英雄攻略、地图攻略）
    - **game_type**: 游戏类型（如：MOBA、FPS）
    - **source**: 来源
    """
    service = get_knowledge_base_service()
    
    doc_id = service.add_document(
        title=doc.title,
        content=doc.content,
        category=doc.category,
        game_type=doc.game_type,
        source=doc.source,
    )
    
    return {
        "success": True,
        "doc_id": doc_id,
        "message": "文档上传成功",
    }


@router.post("/knowledge/upload-video")
async def upload_video_transcript(data: VideoTranscriptUpload):
    """
    上传视频解说
    
    - **video_title**: 视频标题
    - **transcript**: 解说文本
    - **game_type**: 游戏类型
    - **video_url**: 视频链接（可选）
    - **timestamps**: 时间戳列表（可选）
    """
    service = get_knowledge_base_service()
    
    doc_id = service.add_video_transcript(
        video_title=data.video_title,
        transcript=data.transcript,
        game_type=data.game_type,
        video_url=data.video_url,
        timestamps=data.timestamps,
    )
    
    return {
        "success": True,
        "doc_id": doc_id,
        "message": "视频解说上传成功",
    }


@router.post("/knowledge/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    category: str = Form("文档说明"),
    game_type: str = Form("general"),
):
    """
    上传文本文件到知识库
    
    - **file**: 文本文件（.txt 或 .md）
    - **title**: 标题（默认使用文件名）
    - **category**: 分类
    - **game_type**: 游戏类型
    """
    # 检查文件类型
    if not file.filename.endswith(('.txt', '.md')):
        raise HTTPException(status_code=400, detail="只支持 .txt 或 .md 文件")
    
    # 读取文件内容
    content = await file.read()
    text = content.decode('utf-8')
    
    # 设置标题
    if title is None:
        title = file.filename.rsplit('.', 1)[0]
    
    service = get_knowledge_base_service()
    
    doc_id = service.add_document(
        title=title,
        content=text,
        category=category,
        game_type=game_type,
        source=file.filename,
    )
    
    return {
        "success": True,
        "doc_id": doc_id,
        "message": "文件上传成功",
        "filename": file.filename,
    }


@router.post("/knowledge/search")
async def search_knowledge(query: SearchQuery):
    """
    搜索知识库
    
    - **query**: 查询文本
    - **game_type**: 游戏类型过滤（可选）
    - **top_k**: 返回数量
    """
    service = get_knowledge_base_service()
    
    results = service.search(
        query=query.query,
        game_type=query.game_type,
        top_k=query.top_k,
    )
    
    return {
        "success": True,
        "query": query.query,
        "count": len(results),
        "results": results,
    }


@router.delete("/knowledge/{doc_id}")
async def delete_document(doc_id: str):
    """删除知识库文档"""
    service = get_knowledge_base_service()
    
    success = service.delete_document(doc_id)
    
    if success:
        return {"success": True, "message": "文档删除成功"}
    else:
        raise HTTPException(status_code=404, detail="文档不存在或删除失败")


# ==================== 案例库接口 ====================

@router.post("/cases/upload")
async def upload_case(case: CaseUpload):
    """
    上传案例到案例库
    
    - **description**: 场景描述
    - **analysis**: 分析说明
    - **event_type**: 事件类型（如：团战、Gank）
    - **game_type**: 游戏类型
    - **player_level**: 玩家水平（如：王者、大师）
    - **tags**: 标签列表
    """
    service = get_case_base_service()
    
    case_id = service.add_case(
        description=case.description,
        analysis=case.analysis,
        event_type=case.event_type,
        game_type=case.game_type,
        player_level=case.player_level,
        tags=case.tags,
    )
    
    return {
        "success": True,
        "case_id": case_id,
        "message": "案例上传成功",
    }


@router.post("/cases/search")
async def search_cases(query: SearchQuery):
    """
    搜索案例库
    
    - **query**: 查询文本
    - **game_type**: 游戏类型过滤（可选）
    - **top_k**: 返回数量
    """
    service = get_case_base_service()
    
    results = service.search_similar_cases(
        query=query.query,
        game_type=query.game_type,
        top_k=query.top_k,
    )
    
    return {
        "success": True,
        "query": query.query,
        "count": len(results),
        "results": results,
    }


# ==================== 批量上传接口 ====================

@router.post("/knowledge/batch-upload")
async def batch_upload_documents(documents: List[DocumentUpload]):
    """
    批量上传文档
    
    一次最多上传 100 个文档
    """
    if len(documents) > 100:
        raise HTTPException(status_code=400, detail="一次最多上传 100 个文档")
    
    service = get_knowledge_base_service()
    
    docs_data = [
        {
            "title": doc.title,
            "content": doc.content,
            "category": doc.category,
            "game_type": doc.game_type,
            "source": doc.source,
        }
        for doc in documents
    ]
    
    doc_ids = service.add_documents_batch(docs_data)
    
    return {
        "success": True,
        "count": len(doc_ids),
        "doc_ids": doc_ids,
        "message": f"成功上传 {len(doc_ids)} 个文档",
    }


@router.post("/cases/batch-upload")
async def batch_upload_cases(cases: List[CaseUpload]):
    """
    批量上传案例
    
    一次最多上传 100 个案例
    """
    if len(cases) > 100:
        raise HTTPException(status_code=400, detail="一次最多上传 100 个案例")
    
    service = get_case_base_service()
    
    cases_data = [
        {
            "description": case.description,
            "analysis": case.analysis,
            "event_type": case.event_type,
            "game_type": case.game_type,
            "player_level": case.player_level,
            "tags": case.tags or [],
        }
        for case in cases
    ]
    
    case_ids = service.add_cases_batch(cases_data)
    
    return {
        "success": True,
        "count": len(case_ids),
        "case_ids": case_ids,
        "message": f"成功上传 {len(case_ids)} 个案例",
    }
