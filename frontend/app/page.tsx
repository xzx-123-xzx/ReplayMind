export default function HomePage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-900 mb-4">
          ReplayMind
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          基于多模态AI与RAG的游戏录像智能复盘系统
        </p>
        <div className="flex gap-4 justify-center">
          <a
            href="/dashboard"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            开始使用
          </a>
          <a
            href="/docs"
            className="px-6 py-3 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
          >
            查看文档
          </a>
        </div>
      </div>
    </main>
  );
}
