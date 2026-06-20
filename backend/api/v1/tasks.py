"""
Tasks API Routes
任务管理 API
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from common import logger
from infrastructure.db.postgres import get_db
from infrastructure.db.redis import get_redis, cache_get, cache_set
from pydantic import BaseModel


router = APIRouter()


class TaskStatus(BaseModel):
    """任务状态"""
    task_id: str
    status: str
    current_step: Optional[str]
    completed_steps: list
    errors: list
    progress: float


@router.get("/{task_id}", response_model=TaskStatus)
async def get_task_status(
    task_id: str,
):
    """
    获取任务状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        TaskStatus: 任务状态
    """
    # 从 Redis 获取任务状态
    cache_key = f"task:{task_id}"
    task_data = await cache_get(cache_key)
    
    if not task_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # 计算进度
    completed_steps = task_data.get("completed_steps", [])
    total_steps = 9  # 工作流总步骤数
    progress = len(completed_steps) / total_steps * 100
    
    return TaskStatus(
        task_id=task_id,
        status=task_data.get("status", "running"),
        current_step=task_data.get("current_step"),
        completed_steps=completed_steps,
        errors=task_data.get("errors", []),
        progress=progress,
    )


@router.get("/{task_id}/logs")
async def get_task_logs(
    task_id: str,
    limit: int = 100,
):
    """
    获取任务日志
    
    Args:
        task_id: 任务ID
        limit: 返回的日志条数
        
    Returns:
        dict: 任务日志
    """
    cache_key = f"task:{task_id}:logs"
    logs = await cache_get(cache_key)
    
    if not logs:
        return {"task_id": task_id, "logs": []}
    
    return {
        "task_id": task_id,
        "logs": logs[-limit:] if len(logs) > limit else logs,
    }


@router.post("/{task_id}/cancel")
async def cancel_task(
    task_id: str,
):
    """
    取消任务
    
    Args:
        task_id: 任务ID
        
    Returns:
        dict: 取消结果
    """
    cache_key = f"task:{task_id}"
    task_data = await cache_get(cache_key)
    
    if not task_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task_data.get("status") in ["completed", "failed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task cannot be cancelled"
        )
    
    # 更新任务状态
    task_data["status"] = "cancelled"
    await cache_set(cache_key, task_data, expire=3600)
    
    logger.info(f"Task cancelled: {task_id}")
    
    return {"task_id": task_id, "status": "cancelled"}
