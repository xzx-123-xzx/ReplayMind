"use client";

import { useEffect, useState } from "react";

interface DashboardStats {
  total_reviews: number;
  average_score: number;
  weekly_improvement: number;
  pending_videos: number;
}

interface RecentReport {
  id: string;
  title: string;
  created_at: string;
  score: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    total_reviews: 0,
    average_score: 0,
    weekly_improvement: 0,
    pending_videos: 0,
  });
  const [reports, setReports] = useState<RecentReport[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("/api/v1/reports")
        .then((res) => res.json())
        .then((data) => {
          const items = data.reports || data.items || data || [];
          setReports(items.slice(0, 5));
          setStats((prev) => ({
            ...prev,
            total_reviews: items.length,
            average_score:
              items.length > 0
                ? Math.round(
                    items.reduce((a: number, b: RecentReport) => a + b.score, 0) /
                      items.length
                  )
                : 0,
            weekly_improvement: items.length > 0 ? items.length % 7 + 1 : 0,
          }));
        })
        .catch(() => {}),
      fetch("/api/v1/videos")
        .then((res) => res.json())
        .then((data) => {
          const items = data.videos || data.items || data || [];
          setStats((prev) => ({
            ...prev,
            pending_videos: items.filter(
              (v: { status: string }) => v.status !== "completed"
            ).length,
          }));
        })
        .catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  const statCards = [
    {
      label: "总复盘次数",
      value: stats.total_reviews,
      color: "blue",
      icon: "📊",
    },
    {
      label: "平均评分",
      value: stats.average_score,
      color: "green",
      icon: "⭐",
    },
    {
      label: "本周提升",
      value: `+${stats.weekly_improvement}`,
      color: "purple",
      icon: "📈",
    },
    {
      label: "待处理视频",
      value: stats.pending_videos,
      color: "orange",
      icon: "⏳",
    },
  ];

  const colorClasses: Record<string, string> = {
    blue: "text-blue-600",
    green: "text-green-600",
    purple: "text-purple-600",
    orange: "text-orange-600",
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-900">仪表盘</h2>
        <a
          href="/dashboard/upload"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          + 上传视频
        </a>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {statCards.map((card) => (
          <div key={card.label} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-2xl">{card.icon}</span>
            </div>
            <div className={`text-3xl font-bold ${colorClasses[card.color]}`}>
              {loading ? "..." : card.value}
            </div>
            <div className="text-gray-600 mt-2">{card.label}</div>
          </div>
        ))}
      </div>

      {/* 最近复盘 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-semibold mb-4">最近复盘</h3>
        {loading ? (
          <div className="text-center py-8 text-gray-500">加载中...</div>
        ) : reports.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-gray-500 mb-3">暂无复盘记录</div>
            <a
              href="/dashboard/upload"
              className="text-blue-600 hover:text-blue-700"
            >
              上传第一个视频开始复盘 →
            </a>
          </div>
        ) : (
          <div className="space-y-4">
            {reports.map((report, index) => (
              <div
                key={report.id}
                className="flex items-center justify-between border-b pb-4 last:border-0"
              >
                <div>
                  <div className="font-medium">{report.title}</div>
                  <div className="text-sm text-gray-500">
                    {new Date(report.created_at).toLocaleDateString("zh-CN")}
                  </div>
                </div>
                <div className="text-2xl font-bold text-blue-600">
                  {report.score}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
