"""
Videos API Routes
视频管理 API
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from common import logger, PathUtils
from infrastructure.db.postgres import get_db
from domain.repositories.video_repo import VideoRepository
from infrastructure.storage.minio_client import get_minio
from pydantic import BaseModel


router = APIRouter()


class VideoResponse(BaseModel):
    """视频响应模型"""
    id: UUID
    title: str
    game_type: Optional[str]
    status: str
    file_size: Optional[int]
    duration_seconds: Optional[int]
    created_at: str
    
    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    """视频列表响应"""
    total: int
    videos: List[VideoResponse]


@router.post("", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(
    title: str,
    game_type: Optional[str] = None,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    上传视频
    
    Args:
        title: 视频标题
        game_type: 游戏类型
        file: 视频文件
        db: 数据库会话
        
    Returns:
        VideoResponse: 视频信息
    """
    logger.info(f"Uploading video: {title}")
    
    # 验证文件类型
    allowed_types = ["video/mp4", "video/avi", "video/quicktime", "video/x-matroska"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type"
        )
    
    try:
        # 保存文件到临时目录
        temp_dir = PathUtils.get_temp_dir()
        temp_file = temp_dir / file.filename
        
        with open(temp_file, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 上传到 MinIO
        minio_client = get_minio()
        minio_client.ensure_bucket()
        
        video_id = str(UUID())
        object_name = f"videos/{video_id}.mp4"
        minio_client.upload_file(object_name, str(temp_file), file.content_type)
        
        # 保存到数据库
        repo = VideoRepository(db)
        video = await repo.create(
            title=title,
            game_type=game_type,
            file_path=object_name,
            file_size=len(content),
        )
        
        logger.info(f"Video uploaded successfully: {video.id}")
        
        return VideoResponse(
            id=video.id,
            title=video.title,
            game_type=video.game_type,
            status=video.status.value,
            file_size=video.file_size,
            duration_seconds=video.duration_seconds,
            created_at=video.created_at.isoformat(),
        )
    except Exception as e:
        logger.error(f"Video upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=VideoListResponse)
async def list_videos(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    获取视频列表
    
    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        status: 状态过滤
        db: 数据库会话
        
    Returns:
        VideoListResponse: 视频列表
    """
    repo = VideoRepository(db)
    videos = await repo.get_multi(skip=skip, limit=limit)
    total = await repo.count()
    
    return VideoListResponse(
        total=total,
        videos=[
            VideoResponse(
                id=v.id,
                title=v.title,
                game_type=v.game_type,
                status=v.status.value,
                file_size=v.file_size,
                duration_seconds=v.duration_seconds,
                created_at=v.created_at.isoformat(),
            )
            for v in videos
        ]
    )


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    获取视频详情
    
    Args:
        video_id: 视频ID
        db: 数据库会话
        
    Returns:
        VideoResponse: 视频信息
    """
    repo = VideoRepository(db)
    video = await repo.get(video_id)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    return VideoResponse(
        id=video.id,
        title=video.title,
        game_type=video.game_type,
        status=video.status.value,
        file_size=video.file_size,
        duration_seconds=video.duration_seconds,
        created_at=video.created_at.isoformat(),
    )


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    删除视频
    
    Args:
        video_id: 视频ID
        db: 数据库会话
    """
    repo = VideoRepository(db)
    video = await repo.get(video_id)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # 从 MinIO 删除
    if video.file_path:
        minio_client = get_minio()
        try:
            minio_client.delete_object(video.file_path)
        except Exception as e:
            logger.warning(f"Failed to delete file from MinIO: {e}")
    
    # 从数据库删除
    await repo.delete(video_id)
    
    logger.info(f"Video deleted: {video_id}")
