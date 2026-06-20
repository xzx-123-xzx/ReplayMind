"""
Vision Analyzer Node
视觉分析节点
"""

from typing import Dict, Any, List

from common import logger
from infrastructure.ai.qwen_vl_client import get_qwen_vl
from langgraph_workflow.state import ReplayMindState


class VisionAnalyzerNode:
    """视觉分析节点"""
    
    name = "vision_analyzer"
    
    def __init__(self):
        self.qwen_vl_client = get_qwen_vl()
    
    async def execute(self, state: ReplayMindState) -> Dict[str, Any]:
        """
        执行视觉分析
        
        Args:
            state: 当前状态
            
        Returns:
            Dict[str, Any]: 更新后的状态
        """
        frames = state.get("frames", [])
        
        if not frames:
            logger.warning("No frames provided for vision analysis")
            return {
                "visual_analysis": None,
                "errors": state.get("errors", []) + ["No frames provided"],
            }
        
        logger.info(f"Starting vision analysis for {len(frames)} frames")
        
        try:
            # 选择关键帧进行分析（每10帧取一帧）
            key_frames = frames[::10] if len(frames) > 10 else frames
            
            # 批量分析
            frame_analyses = self._batch_analyze_frames(key_frames)
            
            # 综合分析
            visual_analysis = self._aggregate_analysis(frame_analyses)
            
            logger.info(f"Vision analysis completed: {len(frame_analyses)} frames analyzed")
            
            return {
                "visual_analysis": visual_analysis,
                "current_step": "vision_analyzer",
                "errors": [],
                "completed_steps": state.get("completed_steps", []) + ["vision_analyzer"],
            }
        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return {
                "visual_analysis": None,
                "errors": state.get("errors", []) + [str(e)],
                "current_step": "vision_analyzer",
            }
    
    def _batch_analyze_frames(self, frames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量分析帧
        
        Args:
            frames: 帧列表
            
        Returns:
            List[Dict[str, Any]]: 分析结果列表
        """
        analyses = []
        
        for frame in frames:
            try:
                result = self.qwen_vl_client.analyze_game_frame(frame["path"])
                analyses.append({
                    "frame_number": frame["frame_number"],
                    "timestamp": frame["timestamp"],
                    "analysis": result,
                })
            except Exception as e:
                logger.warning(f"Frame analysis failed: {e}")
        
        return analyses
    
    def _aggregate_analysis(self, frame_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        综合分析结果
        
        Args:
            frame_analyses: 帧分析列表
            
        Returns:
            Dict[str, Any]: 综合分析结果
        """
        return {
            "total_frames_analyzed": len(frame_analyses),
            "frame_analyses": frame_analyses,
            "scenes": self._extract_scenes(frame_analyses),
            "key_events": self._extract_key_events(frame_analyses),
        }
    
    def _extract_scenes(self, frame_analyses: List[Dict[str, Any]]) -> List[str]:
        """提取场景"""
        # 简化实现
        return ["scene_1", "scene_2"]
    
    def _extract_key_events(self, frame_analyses: List[Dict[str, Any]]) -> List[str]:
        """提取关键事件"""
        # 简化实现
        return []
