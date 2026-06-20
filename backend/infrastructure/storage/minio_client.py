"""
MinIO 对象存储客户端
"""

from typing import Optional
from pathlib import Path
from minio import Minio
from minio.error import S3Error

from common import settings, logger, PathUtils


class MinioClient:
    """MinIO 对象存储客户端"""
    
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
    
    def ensure_bucket(self):
        """确保 Bucket 存在"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.info(f"Bucket already exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Failed to ensure bucket: {e}")
            raise
    
    def upload_file(
        self,
        object_name: str,
        file_path: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        上传文件
        
        Args:
            object_name: 对象名称
            file_path: 文件路径
            content_type: 内容类型
            
        Returns:
            str: 对象 URL
        """
        self.client.fput_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            file_path=file_path,
            content_type=content_type,
        )
        logger.info(f"Uploaded file: {object_name}")
        return f"{settings.MINIO_ENDPOINT}/{self.bucket_name}/{object_name}"
    
    def upload_data(
        self,
        object_name: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        上传数据
        
        Args:
            object_name: 对象名称
            data: 数据
            content_type: 内容类型
            
        Returns:
            str: 对象 URL
        """
        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            data=data,
            length=len(data),
            content_type=content_type,
        )
        logger.info(f"Uploaded data: {object_name}")
        return f"{settings.MINIO_ENDPOINT}/{self.bucket_name}/{object_name}"
    
    def download_file(self, object_name: str, file_path: str):
        """下载文件"""
        self.client.fget_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            file_path=file_path,
        )
        logger.info(f"Downloaded file: {object_name}")
    
    def get_presigned_url(
        self,
        object_name: str,
        expires: int = 3600,
    ) -> str:
        """
        获取预签名 URL
        
        Args:
            object_name: 对象名称
            expires: 过期时间（秒）
            
        Returns:
            str: 预签名 URL
        """
        url = self.client.presigned_get_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            expires=expires,
        )
        return url
    
    def delete_object(self, object_name: str):
        """删除对象"""
        self.client.remove_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
        )
        logger.info(f"Deleted object: {object_name}")
    
    def list_objects(self, prefix: str = "") -> list:
        """
        列出对象
        
        Args:
            prefix: 前缀
            
        Returns:
            list: 对象列表
        """
        objects = self.client.list_objects(
            bucket_name=self.bucket_name,
            prefix=prefix,
            recursive=True,
        )
        return [
            {
                "name": obj.object_name,
                "size": obj.size,
                "last_modified": obj.last_modified,
            }
            for obj in objects
        ]


# 全局 MinIO 客户端
minio_client = MinioClient()


def get_minio() -> MinioClient:
    """获取 MinIO 客户端"""
    return minio_client
