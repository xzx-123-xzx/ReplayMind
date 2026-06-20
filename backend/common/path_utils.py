import os
from pathlib import Path
from typing import Union


class PathUtils:
    """路径工具类"""
    
    _project_root: Path = None
    
    @classmethod
    def get_project_root(cls) -> Path:
        """
        获取项目根目录路径
        
        Returns:
            Path: 项目根目录 Path 对象
        """
        if cls._project_root is not None:
            return cls._project_root
        
        # 向上查找项目根目录（依据常见标识文件）
        current_path = Path(__file__).resolve()
        
        for parent in [current_path] + list(current_path.parents):
            # 检查常见的项目标识
            if (
                (parent / "README.md").exists()
                or (parent / ".git").exists()
                or (parent / "pyproject.toml").exists()
                or (parent / ".env").exists()
                or ((parent / "backend").exists() and (parent / "frontend").exists())
            ):
                cls._project_root = parent
                return parent
        
        # 如果找不到，默认返回当前文件的祖父目录
        cls._project_root = current_path.parent.parent
        return cls._project_root
    
    @classmethod
    def join(cls, *paths: Union[str, Path]) -> Path:
        """
        从项目根目录开始拼接路径
        
        Args:
            *paths: 要拼接的路径部分
            
        Returns:
            Path: 拼接后的完整路径
        """
        root = cls.get_project_root()
        return root.joinpath(*paths)
    
    @classmethod
    def ensure_dir(cls, path: Union[str, Path]) -> Path:
        """
        确保目录存在，如果不存在则创建
        
        Args:
            path: 目录路径
            
        Returns:
            Path: 目录路径
        """
        dir_path = Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    
    @classmethod
    def get_data_dir(cls) -> Path:
        """获取数据目录路径"""
        return cls.ensure_dir(cls.join("data"))
    
    @classmethod
    def get_logs_dir(cls) -> Path:
        """获取日志目录路径"""
        return cls.ensure_dir(cls.join("logs"))
    
    @classmethod
    def get_uploads_dir(cls) -> Path:
        """获取上传文件目录路径"""
        return cls.ensure_dir(cls.join("data", "uploads"))
    
    @classmethod
    def get_temp_dir(cls) -> Path:
        """获取临时文件目录路径"""
        return cls.ensure_dir(cls.join("data", "temp"))
