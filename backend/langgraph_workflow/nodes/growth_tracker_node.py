"""
Growth Tracker Node
成长跟踪节点
"""

from typing import Dict, Any
from datetime import datetime, date

from common import logger
from langgraph_workflow.state import ReplayMindState


class GrowthTrackerNode:
    """成长跟踪节点"""
    
    name = "growth_tracker"
    
    async def execute(self, state: ReplayMindState) -> Dict[str, Any]:
        """
        执行成长跟踪
        
        Args:
            state: 当前状态
            
        Returns:
            Dict[str, Any]: 更新后的状态
        """
        user_id = state.get("user_id")
        scores = state.get("scores", {})
        
        logger.info(f"Starting growth tracking for user: {user_id}")
        
        try:
            # 更新成长记录
            growth_update = await self._update_growth_record(
                user_id=user_id,
                scores=scores,
            )
            
            logger.info("Growth tracking completed")
            
            return {
                "growth_update": growth_update,
                "current_step": "growth_tracker",
                "errors": [],
                "completed_steps": state.get("completed_steps", []) + ["growth_tracker"],
            }
        except Exception as e:
            logger.error(f"Growth tracking failed: {e}")
            return {
                "growth_update": None,
                "errors": state.get("errors", []) + [str(e)],
                "current_step": "growth_tracker",
            }
    
    async def _update_growth_record(
        self,
        user_id: str,
        scores: dict,
    ) -> Dict[str, Any]:
        """
        更新成长记录
        
        Args:
            user_id: 用户ID
            scores: 评分
            
        Returns:
            Dict[str, Any]: 成长更新结果
        """
        today = date.today()
        
        # 构建能力雷达图数据
        ability_radar = {
            "operation": scores.get("operation_score", 0),
            "awareness": scores.get("awareness_score", 0),
            "decision": scores.get("decision_score", 0),
            "teamwork": scores.get("teamwork_score", 0),
        }
        
        # 计算趋势（简化版）
        trend_data = {
            "operation_trend": 0,
            "awareness_trend": 0,
            "decision_trend": 0,
            "teamwork_trend": 0,
        }
        
        growth_update = {
            "record_date": today.isoformat(),
            "total_replays": 1,
            "avg_replay_score": scores.get("replay_score", 0),
            "ability_radar": ability_radar,
            "trend_data": trend_data,
        }
        
        return growth_update
