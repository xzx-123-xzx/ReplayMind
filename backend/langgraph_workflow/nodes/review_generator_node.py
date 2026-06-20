"""
Review Generator Node
复盘报告生成节点
"""

from typing import Dict, Any
from langchain_core.language_models import BaseLLM

from common import logger
from common import chat_llm as default_chat_llm
from langgraph_workflow.state import ReplayMindState


class ReviewGeneratorNode:
    """复盘报告生成节点"""
    
    name = "review_generator"
    
    def __init__(self):
        # 从 common 获取 DeepSeek 聊天模型
        self.llm: BaseLLM = default_chat_llm
    
    async def execute(self, state: ReplayMindState) -> Dict[str, Any]:
        """
        生成复盘报告
        
        Args:
            state: 当前状态
            
        Returns:
            Dict[str, Any]: 更新后的状态
        """
        logger.info("Starting review report generation")
        
        try:
            # 构建报告上下文
            context = self._build_report_context(state)
            
            # 使用 LLM 生成报告
            report_content = await self._generate_report(context)
            
            logger.info("Review report generation completed")
            
            return {
                "report_content": report_content,
                "current_step": "review_generator",
                "errors": [],
                "completed_steps": state.get("completed_steps", []) + ["review_generator"],
            }
        except Exception as e:
            logger.error(f"Review report generation failed: {e}")
            return {
                "report_content": self._default_report(),
                "errors": state.get("errors", []) + [str(e)],
                "current_step": "review_generator",
            }
    
    def _build_report_context(self, state: ReplayMindState) -> str:
        """构建报告上下文"""
        events = state.get("events", [])
        scores = state.get("scores", {})
        knowledge_retrieval = state.get("knowledge_retrieval")
        case_retrieval = state.get("case_retrieval")
        
        context = f"""
        请根据以下信息生成一份专业的游戏复盘报告：
        
        ## 基本信息
        - 游戏类型：{state.get('game_type', 'unknown')}
        - 录像ID：{state.get('video_id')}
        
        ## 评分结果
        - 操作评分：{scores.get('operation_score', 'N/A')}
        - 意识评分：{scores.get('awareness_score', 'N/A')}
        - 决策评分：{scores.get('decision_score', 'N/A')}
        - 团队协作：{scores.get('teamwork_score', 'N/A')}
        - 综合评分：{scores.get('replay_score', 'N/A')}
        
        ## 关键事件
        {self._format_events(events)}
        
        ## 知识库检索结果
        {self._format_documents(knowledge_retrieval)}
        
        ## 相似案例
        {self._format_cases(case_retrieval)}
        
        ## 报告要求
        请生成一份完整的 Markdown 格式复盘报告，包含以下部分：
        1. 比赛概览
        2. 关键时间线
        3. 失误分析
        4. 优势分析
        5. AI 建议
        6. 下一步训练计划
        
        报告应该专业、详细、有建设性。
        """
        
        return context
    
    def _format_events(self, events: list) -> str:
        """格式化事件"""
        if not events:
            return "无"
        
        return "\n".join([
            f"- [{e['timestamp']}] {e['event_type']}: {e['description']}"
            for e in events[:15]
        ])
    
    def _format_documents(self, retrieval) -> str:
        """格式化文档"""
        if not retrieval or not retrieval.get("documents"):
            return "无相关知识"
        
        docs = retrieval["documents"][:3]
        return "\n".join([f"- {d.get('title', 'Unknown')}" for d in docs])
    
    def _format_cases(self, retrieval) -> str:
        """格式化案例"""
        if not retrieval or not retrieval.get("cases"):
            return "无相似案例"
        
        cases = retrieval["cases"][:3]
        return "\n".join([f"- {c.get('case_id', 'Unknown')}" for c in cases])
    
    async def _generate_report(self, context: str) -> str:
        """使用 LLM 生成报告"""
        prompt = f"""
        {context}
        
        请严格按照 Markdown 格式生成报告，不要包含其他说明文字。
        """
        
        report = await self.llm.ainvoke(prompt)
        return report
    
    def _default_report(self) -> str:
        """默认报告"""
        return """# 游戏复盘报告

报告生成中，请稍后重试。
"""
