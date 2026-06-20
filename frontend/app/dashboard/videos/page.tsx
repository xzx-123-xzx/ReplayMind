"use client";

import { useEffect, useState } from "react";

interface Video {
  id: string;
  title: string;
  uploaded_at: string;
  status: string;
  duration: number;
  size: string;
}

export default function VideosPage() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/videos")
      .then((res) => res.json())
      .then((data) => {
        setVideos(data.videos || data.items || data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const formatDuration = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  const statusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-800";
      case "processing":
        return "bg-yellow-100 text-yellow-800";
      case "failed":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const statusText = (status: string) => {
    switch (status) {
      case "completed":
        return "已完成";
      case "processing":
        return "处理中";
      case "failed":
        return "失败";
      default:
        return status;
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-900">视频管理</h2>
        <a
          href="/dashboard/upload"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          + 上传新视频
        </a>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">加载中...</div>
      ) : videos.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="text-gray-500 text-lg mb-4">暂无视频</div>
          <a
            href="/dashboard/upload"
            className="text-blue-600 hover:text-blue-700"
          >
            立即上传一个视频
          </a>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">
                  标题
                </th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">
                  时长
                </th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">
                  大小
                </th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">
                  状态
                </th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">
                  上传时间
                </th>
                <th className="px-6 py-3 text-right text-sm font-medium text-gray-600">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {videos.map((video) => (
                <tr key={video.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-900">
                    {video.title}
                  </td>
                  <td className="px-6 py-4 text-gray-600">
                    {formatDuration(video.duration)}
                  </td>
                  <td className="px-6 py-4 text-gray-600">{video.size}</td>
                  <td className="px-6 py-4">
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${statusColor(
                        video.status
                      )}`}
                    >
                      {statusText(video.status)}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-600 text-sm">
                    {new Date(video.uploaded_at).toLocaleDateString("zh-CN")}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <a
                      href="#"
                      className="text-blue-600 hover:text-blue-700 text-sm"
                    >
                      查看报告
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
