"use client";

import { useEffect, useState } from "react";

interface GrowthRecord {
  id: string;
  created_at: string;
  score: number;
  category: string;
  insight: string;
}

export default function GrowthPage() {
  const [records, setRecords] = useState<GrowthRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/growth")
      .then((res) => res.json())
      .then((data) => {
        setRecords(data.records || data.items || data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const categoryColor = (category: string) => {
    const colors: Record<string, string> = {
      strategy: "bg-purple-100 text-purple-800",
      teamwork: "bg-blue-100 text-blue-800",
      communication: "bg-green-100 text-green-800",
      technical: "bg-orange-100 text-orange-800",
      decision: "bg-pink-100 text-pink-800",
    };
    return colors[category] || "bg-gray-100 text-gray-800";
  };

  const categoryText = (category: string) => {
    const texts: Record<string, string> = {
      strategy: "战略思维",
      teamwork: "团队协作",
      communication: "沟通交流",
      technical: "技术能力",
      decision: "决策能力",
    };
    return texts[category] || category;
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-900">成长中心</h2>
        <div className="flex gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">已记录成长</div>
            <div className="text-2xl font-bold text-purple-600">
              {records.length}
            </div>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">加载中...</div>
      ) : records.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="text-gray-500 text-lg mb-4">暂无成长记录</div>
          <p className="text-gray-400 text-sm mb-4">
            完成视频复盘后，系统会自动分析你的成长记录
          </p>
          <a
            href="/dashboard/upload"
            className="text-blue-600 hover:text-blue-700"
          >
            上传视频开始复盘
          </a>
        </div>
      ) : (
        <div className="relative">
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200" />
          <div className="space-y-4">
            {records.map((record) => (
              <div key={record.id} className="relative pl-20">
                <div className="absolute left-6 w-5 h-5 rounded-full bg-blue-500 border-4 border-white shadow" />
                <div className="bg-white rounded-lg shadow p-6">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <span
                        className={`inline-block px-2 py-1 text-xs rounded-full mb-2 ${categoryColor(
                          record.category
                        )}`}
                      >
                        {categoryText(record.category)}
                      </span>
                      <div className="text-sm text-gray-500">
                        {new Date(record.created_at).toLocaleDateString(
                          "zh-CN"
                        )}
                      </div>
                    </div>
                    <div className="text-2xl font-bold text-blue-600">
                      {record.score}
                    </div>
                  </div>
                  <p className="text-gray-700">{record.insight}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
