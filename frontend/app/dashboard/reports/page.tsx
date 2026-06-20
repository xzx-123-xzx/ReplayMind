"use client";

import { useEffect, useState } from "react";

interface Report {
  id: string;
  video_id: string;
  title: string;
  score: number;
  summary: string;
  created_at: string;
}

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/reports")
      .then((res) => res.json())
      .then((data) => {
        setReports(data.reports || data.items || data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const scoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-900">复盘报告</h2>
        <div className="flex gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">平均评分</div>
            <div className="text-2xl font-bold text-blue-600">
              {reports.length > 0
                ? Math.round(
                    reports.reduce((a, b) => a + b.score, 0) / reports.length
                  )
                : 0}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">总报告数</div>
            <div className="text-2xl font-bold text-green-600">
              {reports.length}
            </div>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">加载中...</div>
      ) : reports.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="text-gray-500 text-lg mb-4">暂无报告</div>
          <a
            href="/dashboard/upload"
            className="text-blue-600 hover:text-blue-700"
          >
            上传视频生成复盘报告
          </a>
        </div>
      ) : (
        <div className="grid gap-4">
          {reports.map((report) => (
            <div
              key={report.id}
              className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-1">
                    {report.title}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {new Date(report.created_at).toLocaleDateString("zh-CN")}
                  </p>
                </div>
                <div
                  className={`text-3xl font-bold ${scoreColor(report.score)}`}
                >
                  {report.score}
                </div>
              </div>
              <p className="text-gray-600 mb-4">
                {report.summary?.substring(0, 200)}...
              </p>
              <a
                href="#"
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                查看完整报告 →
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
