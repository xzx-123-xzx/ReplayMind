"""
Performance Scorer Node
性能评分节点
"""

from typing import Dict, Any
from langchain_core.language_models import BaseLLM

from common import logger
from common import chat_llm as default_chat_llm
from langgraph_workflow.state import ReplayMindState, ScoreResult


class PerformanceScorerNode:
    """性能评分节点"""
    
    name = "performance_scorer"
    
    def __init__(self):
        # 从 common 获取 DeepSeek 聊天模型
        self.llm: BaseLLM = default_chat_llm
    
    async def execute(self, state: ReplayMindState) -> Dict[str, Any]:
        """
        执行性能评分
        
        Args:
            state: 当前状态
            
        Returns:
            Dict[str, Any]: 更新后的状态
        """
        logger.info("Starting performance scoring")
        
        try:
            # 构建评分上下文
            context = self._build_scoring_context(state)
            
            # 使用 LLM 进行评分
            scores = await self._llm_score(context)
            
            logger.info(f"Performance scoring completed: replay_score={scores['replay_score']}")
            
            return {
                "scores": scores,
                "current_step": "performance_scorer",
                "errors": [],
                "completed_steps": state.get("completed_steps", []) + ["performance_scorer"],
            }
        except Exception as e:
            logger.error(f"Performance scoring failed: {e}")
            return {
                "scores": self._default_scores(),
                "errors": state.get("errors", []) + [str(e)],
                "current_step": "performance_scorer",
            }
    
    def _build_scoring_context(self, state: ReplayMindState) -> str:
        """构建评分上下文"""
        events = state.get("events", [])
        transcripts = state.get("transcripts", [])
        visual_analysis = state.get("visual_analysis")
        knowledge_retrieval = state.get("knowledge_retrieval")
        
        context = f"""
        请根据以下信息对游戏表现进行评分：
        
        游戏类型：{state.get('game_type', 'unknown')}
        事件数量：{len(events)}
        
        关键事件：
        {self._format_events(events)}
        
        语音分析：
        {len(transcripts)} 个语音片段
        
        视觉分析：
        {visual_analysis.get('total_frames_analyzed', 0) if visual_analysis else 0} 帧被分析
        
        请从以下四个维度评分（1-100分）：
        1. 操作评分 - 技能使用、走位、连招等
        2. 意识评分 - 地图意识、局势判断、预判等
        3. 决策评分 - 开团选择、目标优先级、资源交换等
        4. 团队协作评分 - 配合、沟通、保护队友等
        
        最终综合评分（Replay Score）由以上四项加权平均得出。
        
        请以JSON格式返回评分结果。
        """
        
        return context
    
    def _format_events(self, events: list) -> str:
        """格式化事件列表"""
        if not events:
            return "无"
        
        return "\n".join([
            f"- [{e['timestamp']}] {e['event_type']}: {e['description']}"
            for e in events[:10]
        ])
    
    async def _llm_score(self, context: str) -> ScoreResult:
        """使用 LLM 进行评分"""
        prompt = f"""
        {context}
        
        请严格按照以下JSON格式返回评分，不要包含其他内容：
        {{
            "operation_score": 数字,
            "awareness_score": 数字,
            "decision_score": 数字,
            "teamwork_score": 数字,
            "replay_score": 数字,
            "score_details": {{
                "operation": "操作分析",
                "awareness": "意识分析",
                "decision": "决策分析",
                "teamwork": "团队协作分析"
            }}
        }}
        """
        
        response = await self.llm.ainvoke(prompt)
        
        # 解析响应（简化实现）
        try:
            import json
            import re
            
            # 提取 JSON
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                scores = json.loads(match.group())
                return ScoreResult(**scores)
        except Exception as e:
            logger.warning(f"Failed to parse LLM response: {e}")
        
        return self._default_scores()
    
    def _default_scores(self) -> ScoreResult:
        """默认评分"""
        return ScoreResult(
            operation_score=70,
            awareness_score=70,
            decision_score=70,
            teamwork_score=70,
            replay_score=70,
            score_details={
                "operation": "评分系统未完成",
                "awareness": "评分系统未完成",
                "decision": "评分系统未完成",
                "teamwork": "评分系统未完成",
            },
        )
