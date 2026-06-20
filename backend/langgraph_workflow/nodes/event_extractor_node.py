"""
Event Extractor Node
事件抽取节点
"""

from typing import Dict, Any, List
import uuid

from common import logger
from langgraph_workflow.state import ReplayMindState, GameEvent, EventType


class EventExtractorNode:
    """事件抽取节点"""
    
    name = "event_extractor"
    
    async def execute(self, state: ReplayMindState) -> Dict[str, Any]:
        """
        执行事件抽取
        
        Args:
            state: 当前状态
            
        Returns:
            Dict[str, Any]: 更新后的状态
        """
        logger.info("Starting event extraction")
        
        try:
            # 获取语音分析和视觉分析结果
            speech_analysis = state.get("speech_analysis")
            visual_analysis = state.get("visual_analysis")
            transcripts = state.get("transcripts", [])
            frames = state.get("frames", [])
            
            # 抽取事件
            events = self._extract_events(
                transcripts=transcripts,
                frames=frames,
                speech_analysis=speech_analysis,
                visual_analysis=visual_analysis,
            )
            
            logger.info(f"Event extraction completed: {len(events)} events found")
            
            return {
                "events": events,
                "current_step": "event_extractor",
                "errors": [],
                "completed_steps": state.get("completed_steps", []) + ["event_extractor"],
            }
        except Exception as e:
            logger.error(f"Event extraction failed: {e}")
            return {
                "events": [],
                "errors": state.get("errors", []) + [str(e)],
                "current_step": "event_extractor",
            }
    
    def _extract_events(
        self,
        transcripts: List[Dict[str, Any]],
        frames: List[Dict[str, Any]],
        speech_analysis: Dict[str, Any],
        visual_analysis: Dict[str, Any],
    ) -> List[GameEvent]:
        """
        从分析结果中抽取事件
        
        Args:
            transcripts: 转录列表
            frames: 帧列表
            speech_analysis: 语音分析结果
            visual_analysis: 视觉分析结果
            
        Returns:
            List[GameEvent]: 事件列表
        """
        events = []
        
        # 基于语音转录抽取事件
        for transcript in transcripts:
            event = self._extract_event_from_transcript(transcript)
            if event:
                events.append(event)
        
        # 基于视觉分析抽取战斗事件
        if visual_analysis and visual_analysis.get("frame_analyses"):
            for analysis in visual_analysis["frame_analyses"]:
                event = self._extract_combat_event(analysis)
                if event:
                    events.append(event)
        
        # 按时间排序
        events.sort(key=lambda x: x["timestamp"])
        
        return events
    
    def _extract_event_from_transcript(self, transcript: Dict[str, Any]) -> GameEvent:
        """从转录中抽取事件"""
        text = transcript.get("text", "").lower()
        
        # 简化的事件检测
        event_type = EventType.OTHER
        description = transcript.get("text", "")
        
        # 基于关键词识别事件类型
        if any(kw in text for kw in ["团战", "打团", "fight"]):
            event_type = EventType.TEAMFIGHT
        elif any(kw in text for kw in ["击杀", "kill", "死", "dead"]):
            event_type = EventType.DEATH
        elif any(kw in text for kw in ["目标", "object", "龙", "buff"]):
            event_type = EventType.OBJECTIVE
        
        return GameEvent(
            event_id=str(uuid.uuid4()),
            timestamp=str(transcript.get("start", 0)),
            event_type=event_type,
            description=description,
            confidence=0.8,
            metadata={"source": "transcript"},
        )
    
    def _extract_combat_event(self, analysis: Dict[str, Any]) -> GameEvent:
        """从视觉分析中抽取战斗事件"""
        # 简化实现
        return None
