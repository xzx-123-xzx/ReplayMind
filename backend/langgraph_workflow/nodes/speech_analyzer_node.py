"""
Speech Analyzer Node
语音分析节点
"""

from typing import Dict, Any

from common import logger
from infrastructure.ai.whisper_client import get_whisper
from langgraph_workflow.state import ReplayMindState


class SpeechAnalyzerNode:
    """语音分析节点"""
    
    name = "speech_analyzer"
    
    def __init__(self):
        self.whisper_client = get_whisper()
    
    async def execute(self, state: ReplayMindState) -> Dict[str, Any]:
        """
        执行语音分析
        
        Args:
            state: 当前状态
            
        Returns:
            Dict[str, Any]: 更新后的状态
        """
        audio_path = state.get("audio_path")
        
        if not audio_path:
            logger.warning("No audio path provided for speech analysis")
            return {
                "transcripts": [],
                "speech_analysis": None,
                "errors": state.get("errors", []) + ["No audio path provided"],
            }
        
        logger.info(f"Starting speech analysis for audio: {audio_path}")
        
        try:
            # Whisper 转录
            transcript_result = self.whisper_client.transcribe(audio_path)
            
            # 提取转录段落
            transcripts = [
                {
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"],
                    "language": transcript_result.get("language", "unknown"),
                }
                for segment in transcript_result.get("segments", [])
            ]
            
            # 语音分析（简化版，实际需要更复杂的分析）
            speech_analysis = self._analyze_speech(transcripts)
            
            logger.info(f"Speech analysis completed: {len(transcripts)} segments")
            
            return {
                "transcripts": transcripts,
                "speech_analysis": speech_analysis,
                "current_step": "speech_analyzer",
                "errors": [],
                "completed_steps": state.get("completed_steps", []) + ["speech_analyzer"],
            }
        except Exception as e:
            logger.error(f"Speech analysis failed: {e}")
            return {
                "transcripts": [],
                "speech_analysis": None,
                "errors": state.get("errors", []) + [str(e)],
                "current_step": "speech_analyzer",
            }
    
    def _analyze_speech(self, transcripts: list) -> Dict[str, Any]:
        """
        分析语音内容
        
        Args:
            transcripts: 转录列表
            
        Returns:
            Dict[str, Any]: 语音分析结果
        """
        total_words = sum(len(t["text"].split()) for t in transcripts)
        total_duration = (
            transcripts[-1]["end"] - transcripts[0]["start"]
            if transcripts else 0
        )
        
        return {
            "total_segments": len(transcripts),
            "total_words": total_words,
            "total_duration": total_duration,
            "speech_rate": total_words / total_duration if total_duration > 0 else 0,
            "language": transcripts[0].get("language", "unknown") if transcripts else "unknown",
        }
