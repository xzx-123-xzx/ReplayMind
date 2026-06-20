"""
LangGraph State 定义
"""

from typing import TypedDict, List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """事件类型枚举"""
    COMBAT = "combat"
    OBJECTIVE = "objective"
    DEATH = "death"
    TEAMFIGHT = "teamfight"
    ROTATION = "rotation"
    OTHER = "other"


class GameEvent(TypedDict):
    """游戏事件结构"""
    event_id: str
    timestamp: str
    event_type: EventType
    description: str
    confidence: float
    metadata: Dict[str, Any]


class ScoreResult(TypedDict):
    """评分结果"""
    operation_score: int
    awareness_score: int
    decision_score: int
    teamwork_score: int
    replay_score: int
    score_details: Dict[str, Any]


class RetrievalResult(TypedDict):
    """检索结果"""
    query: str
    documents: List[Dict[str, Any]]
    cases: List[Dict[str, Any]]


class ReplayMindState(TypedDict):
    """ReplayMind 工作流状态"""
    
    # 输入
    video_id: str
    user_id: str
    game_type: str
    
    # 视频解析
    video_path: Optional[str]
    frames: List[Dict[str, Any]]
    audio_path: Optional[str]
    
    # 语音分析
    transcripts: List[Dict[str, Any]]
    speech_analysis: Optional[Dict[str, Any]]
    
    # 视觉分析
    visual_analysis: Optional[Dict[str, Any]]
    
    # 事件抽取
    events: List[GameEvent]
    
    # RAG检索
    knowledge_retrieval: Optional[RetrievalResult]
    case_retrieval: Optional[RetrievalResult]
    
    # 评分
    scores: Optional[ScoreResult]
    
    # 报告生成
    report_content: Optional[str]
    
    # 成长跟踪
    growth_update: Optional[Dict[str, Any]]
    
    # 状态跟踪
    current_step: str
    errors: List[str]
    completed_steps: List[str]
