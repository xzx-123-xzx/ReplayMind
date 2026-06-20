"""
Video Parser Node
视频解析节点
"""

from typing import Dict, Any

from common import logger, PathUtils
from infrastructure.storage.minio_client import get_minio
from infrastructure.ai.whisper_client import get_whisper
from langgraph_workflow.state import ReplayMindState


class VideoParserNode:
    """视频解析节点"""
    
    name = "video_parser"
    
    def __init__(self):
        self.minio_client = get_minio()
        self.whisper_client = get_whisper()
    
    async def execute(self, state: ReplayMindState) -> Dict[str, Any]:
        """
        执行视频解析
        
        Args:
            state: 当前状态
            
        Returns:
            Dict[str, Any]: 更新后的状态
        """
        video_id = state["video_id"]
        logger.info(f"Starting video parsing for: {video_id}")
        
        try:
            # 从 MinIO 下载视频
            video_path = self._download_video(video_id)
            
            # 提取音频
            audio_path = self.whisper_client.extract_audio_from_video(video_path)
            
            # FFmpeg 抽帧
            frames = self._extract_frames(video_path)
            
            logger.info(f"Video parsing completed: {len(frames)} frames extracted")
            
            return {
                "video_path": video_path,
                "audio_path": audio_path,
                "frames": frames,
                "current_step": "video_parser",
                "errors": [],
                "completed_steps": state.get("completed_steps", []) + ["video_parser"],
            }
        except Exception as e:
            logger.error(f"Video parsing failed: {e}")
            return {
                "errors": state.get("errors", []) + [str(e)],
                "current_step": "video_parser",
            }
    
    def _download_video(self, video_id: str) -> str:
        """下载视频"""
        temp_dir = PathUtils.get_temp_dir()
        video_path = str(temp_dir / f"{video_id}.mp4")
        
        # 从 MinIO 下载
        object_name = f"videos/{video_id}.mp4"
        self.minio_client.download_file(object_name, video_path)
        
        return video_path
    
    def _extract_frames(self, video_path: str) -> list:
        """提取视频帧"""
        import subprocess
        from pathlib import Path
        
        frames_dir = PathUtils.get_temp_dir() / f"{Path(video_path).stem}_frames"
        frames_dir.mkdir(exist_ok=True)
        
        # 使用 FFmpeg 提取帧
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", "fps=1",  # 每秒1帧
            "-q:v", "2",
            str(frames_dir / "frame_%04d.jpg"),
            "-y",
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        # 获取帧列表
        frames = []
        for i, frame_file in enumerate(sorted(frames_dir.glob("frame_*.jpg"))):
            frames.append({
                "frame_number": i + 1,
                "path": str(frame_file),
                "timestamp": f"00:{i // 60:02d}:{i % 60:02d}",
            })
        
        return frames
