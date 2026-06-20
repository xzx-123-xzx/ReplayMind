"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";

export default function UploadPage() {
  const [uploading, setUploading] = useState(false);
  const [videoInfo, setVideoInfo] = useState<any>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append("title", file.name.replace(/\.[^/.]+$/, ""));
      formData.append("game_type", "general");
      formData.append("file", file);

      const response = await fetch("/api/v1/videos", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setVideoInfo(data);
        alert("视频上传成功！开始分析...");
      } else {
        alert("上传失败，请重试");
      }
    } catch (error) {
      console.error("Upload error:", error);
      alert("上传失败，请重试");
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "video/*": [".mp4", ".avi", ".mov", ".mkv"],
    },
    maxFiles: 1,
  });

  return (
    <div>
      <h2 className="text-3xl font-bold text-gray-900 mb-6">上传视频</h2>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition ${
          isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300"
        }`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div>
            <div className="text-6xl mb-4">⏳</div>
            <div className="text-xl font-medium text-gray-900">上传中...</div>
          </div>
        ) : (
          <div>
            <div className="text-6xl mb-4">📹</div>
            <div className="text-xl font-medium text-gray-900 mb-2">
              {isDragActive ? "拖放视频文件到此处" : "拖放视频文件或点击选择"}
            </div>
            <div className="text-gray-500">
              支持 MP4, AVI, MOV, MKV 格式
            </div>
          </div>
        )}
      </div>

      {videoInfo && (
        <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="font-medium text-green-900">上传成功！</div>
          <div className="text-sm text-green-700 mt-1">
            视频ID: {videoInfo.id}
          </div>
        </div>
      )}
    </div>
  );
}
