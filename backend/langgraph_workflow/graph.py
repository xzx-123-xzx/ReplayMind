"""
LangGraph 主工作流
"""

from typing import Dict, Any, Callable
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from common import logger
from langgraph_workflow.state import ReplayMindState
from langgraph_workflow.nodes.video_parser_node import VideoParserNode
from langgraph_workflow.nodes.speech_analyzer_node import SpeechAnalyzerNode
from langgraph_workflow.nodes.vision_analyzer_node import VisionAnalyzerNode
from langgraph_workflow.nodes.event_extractor_node import EventExtractorNode
from langgraph_workflow.nodes.knowledge_retriever_node import KnowledgeRetrieverNode
from langgraph_workflow.nodes.case_retriever_node import CaseRetrieverNode
from langgraph_workflow.nodes.performance_scorer_node import PerformanceScorerNode
from langgraph_workflow.nodes.review_generator_node import ReviewGeneratorNode
from langgraph_workflow.nodes.growth_tracker_node import GrowthTrackerNode


class ReplayMindWorkflow:
    """ReplayMind LangGraph 工作流"""
    
    def __init__(self):
        self.graph = None
        self._build_graph()
    
    def _build_graph(self):
        """构建工作流图"""
        # 创建节点
        video_parser = VideoParserNode()
        speech_analyzer = SpeechAnalyzerNode()
        vision_analyzer = VisionAnalyzerNode()
        event_extractor = EventExtractorNode()
        knowledge_retriever = KnowledgeRetrieverNode()
        case_retriever = CaseRetrieverNode()
        performance_scorer = PerformanceScorerNode()
        review_generator = ReviewGeneratorNode()
        growth_tracker = GrowthTrackerNode()
        
        # 创建工作流
        workflow = StateGraph(ReplayMindState)
        
        # 添加节点
        workflow.add_node("video_parser", video_parser.execute)
        workflow.add_node("speech_analyzer", speech_analyzer.execute)
        workflow.add_node("vision_analyzer", vision_analyzer.execute)
        workflow.add_node("event_extractor", event_extractor.execute)
        workflow.add_node("knowledge_retriever", knowledge_retriever.execute)
        workflow.add_node("case_retriever", case_retriever.execute)
        workflow.add_node("performance_scorer", performance_scorer.execute)
        workflow.add_node("review_generator", review_generator.execute)
        workflow.add_node("growth_tracker", growth_tracker.execute)
        
        # 设置入口点
        workflow.set_entry_point("video_parser")
        
        # 定义边
        workflow.add_edge("video_parser", "speech_analyzer")
        workflow.add_edge("video_parser", "vision_analyzer")
        
        # 并行执行语音和视觉分析后，合并到事件抽取
        workflow.add_edge("speech_analyzer", "event_extractor")
        workflow.add_edge("vision_analyzer", "event_extractor")
        
        # 事件抽取后，并行检索知识库和案例库
        workflow.add_edge("event_extractor", "knowledge_retriever")
        workflow.add_edge("event_extractor", "case_retriever")
        
        # 检索完成后，进行性能评分
        workflow.add_edge("knowledge_retriever", "performance_scorer")
        workflow.add_edge("case_retriever", "performance_scorer")
        
        # 评分完成后，生成报告
        workflow.add_edge("performance_scorer", "review_generator")
        
        # 报告生成后，更新成长记录
        workflow.add_edge("review_generator", "growth_tracker")
        
        # 完成
        workflow.add_edge("growth_tracker", END)
        
        # 创建检查点
        checkpointer = MemorySaver()
        
        # 编译工作流
        self.graph = workflow.compile(checkpointer=checkpointer)
        
        logger.info("ReplayMind workflow built successfully")
    
    async def run(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行工作流
        
        Args:
            initial_state: 初始状态
            
        Returns:
            Dict[str, Any]: 最终状态
        """
        logger.info("Starting ReplayMind workflow")
        
        # 运行工作流
        result = await self.graph.ainvoke(initial_state)
        
        logger.info("ReplayMind workflow completed")
        return result
    
    def get_graph(self):
        """获取工作流图"""
        return self.graph


# 全局工作流实例
workflow = ReplayMindWorkflow()


def get_workflow() -> ReplayMindWorkflow:
    """获取工作流实例"""
    return workflow
