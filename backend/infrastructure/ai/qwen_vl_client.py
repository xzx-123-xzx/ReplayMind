"""
Ollama 视觉理解客户端
"""

from typing import Optional, List, Dict, Any, Union
from PIL import Image
from langchain_ollama import OllamaLLM

from common import settings, logger


class QwenVLClient:
    """Qwen2.5-VL 视觉理解客户端"""
    
    def __init__(self):
        self.llm = OllamaLLM(
            base_url=settings.OLLAMA_HOST,
            model=settings.OLLAMA_VISION_MODEL,
            temperature=0.2,
        )
        self.model_name = settings.OLLAMA_VISION_MODEL
    
    def analyze_image(
        self,
        image_path: str,
        prompt: str,
    ) -> str:
        """
        分析图像
        
        Args:
            image_path: 图像路径
            prompt: 分析提示
            
        Returns:
            str: 分析结果
        """
        logger.info(f"Analyzing image: {image_path}")
        
        # 构建消息
        from langchain_core.messages import HumanMessage
        from langchain_core.chat_history import FileChatMessageHistory
        
        # 注意：Ollama 的视觉模型需要特殊的消息格式
        # 这里使用简化的实现
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"file://{image_path}"},
            ]
        )
        
        response = self.llm.invoke([message])
        logger.info("Image analysis completed")
        
        return response
    
    def analyze_game_frame(
        self,
        frame_path: str,
    ) -> Dict[str, Any]:
        """
        分析游戏画面帧
        
        Args:
            frame_path: 帧图像路径
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        prompt = """请分析这个游戏画面，提取以下信息：
        1. 场景类型（野区/河道/塔下/基地等）
        2. 可见的英雄或单位
        3. 血量和技能状态
        4. 可能的战斗状态
        5. 关键物品和装备
        
        请用JSON格式返回结果。"""
        
        result = self.analyze_image(frame_path, prompt)
        
        # 解析结果（实际使用时需要更健壮的解析）
        return {
            "raw_response": result,
            "frame_path": frame_path,
        }
    
    def batch_analyze_frames(
        self,
        frame_paths: List[str],
        prompt: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        批量分析帧
        
        Args:
            frame_paths: 帧路径列表
            prompt: 分析提示
            
        Returns:
            List[Dict[str, Any]]: 分析结果列表
        """
        if prompt is None:
            prompt = "请分析这个游戏画面。"
        
        results = []
        for frame_path in frame_paths:
            result = self.analyze_game_frame(frame_path)
            results.append(result)
        
        return results


# 全局 Qwen VL 客户端
qwen_vl_client = QwenVLClient()


def get_qwen_vl() -> QwenVLClient:
    """获取 Qwen VL 客户端"""
    return qwen_vl_client
