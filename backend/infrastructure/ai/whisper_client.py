"""
Whisper 语音识别客户端
"""

from typing import Optional, List, Dict, Any
import whisper
import numpy as np
from pathlib import Path

from common import settings, logger, PathUtils


class WhisperClient:
    """Whisper 语音识别客户端"""
    
    def __init__(self):
        self.model = None
        self.model_size = settings.WHISPER_MODEL_SIZE
        self.device = settings.WHISPER_DEVICE
        self.language = settings.WHISPER_LANGUAGE
    
    def load_model(self):
        """加载 Whisper 模型"""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(
                self.model_size,
                device=self.device,
            )
            logger.info("Whisper model loaded successfully")
    
    def transcribe(
        self,
        audio_path: str,
        task: str = "transcribe",
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """
        转录音频
        
        Args:
            audio_path: 音频文件路径
            task: 任务类型 (transcribe/translate)
            verbose: 是否详细输出
            
        Returns:
            Dict[str, Any]: 转录结果
        """
        if self.model is None:
            self.load_model()
        
        logger.info(f"Transcribing audio: {audio_path}")
        
        result = self.model.transcribe(
            audio=audio_path,
            task=task,
            language=self.language,
            verbose=verbose,
        )
        
        logger.info("Transcription completed")
        return result
    
    def transcribe_segments(
        self,
        audio_path: str,
        segment_length: float = 30.0,
    ) -> List[Dict[str, Any]]:
        """
        分段转录音频
        
        Args:
            audio_path: 音频文件路径
            segment_length: 分段长度（秒）
            
        Returns:
            List[Dict[str, Any]]: 分段转录结果
        """
        if self.model is None:
            self.load_model()
        
        # 加载音频
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        
        # 分段处理
        segments = []
        segment_samples = int(segment_length * whisper.audio.SAMPLE_RATE)
        
        for i in range(0, len(audio), segment_samples):
            segment_audio = audio[i:i + segment_samples]
            result = self.model.transcribe(
                segment_audio,
                language=self.language,
                task="transcribe",
            )
            
            for segment in result.get("segments", []):
                segments.append({
                    "start": segment["start"] + i / whisper.audio.SAMPLE_RATE,
                    "end": segment["end"] + i / whisper.audio.SAMPLE_RATE,
                    "text": segment["text"],
                    "language": result.get("language", "unknown"),
                })
        
        return segments
    
    def extract_audio_from_video(
        self,
        video_path: str,
        output_path: Optional[str] = None,
    ) -> str:
        """
        从视频提取音频
        
        Args:
            video_path: 视频路径
            output_path: 输出音频路径
            
        Returns:
            str: 音频文件路径
        """
        import subprocess
        
        if output_path is None:
            temp_dir = PathUtils.get_temp_dir()
            output_path = str(temp_dir / f"{Path(video_path).stem}.wav")
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-y",
            output_path,
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"Extracted audio to: {output_path}")
        
        return output_path


# 全局 Whisper 客户端
whisper_client = WhisperClient()


def get_whisper() -> WhisperClient:
    """获取 Whisper 客户端"""
    return whisper_client
