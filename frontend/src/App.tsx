import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [backendStatus, setBackendStatus] = useState<string>('检查中...')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 确保DOM已加载完成
    const timer = setTimeout(() => {
      // 检查后端健康状态
      fetch('http://localhost:8000/health')
        .then(res => {
          if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
          }
          return res.json();
        })
        .then(data => {
          console.log('Backend response:', data);
          setBackendStatus(data.status || 'unknown');
        })
        .catch(error => {
          console.error('Backend connection error:', error);
          setBackendStatus('后端未连接');
        })
        .finally(() => {
          setIsLoading(false);
        });
    }, 100);

    return () => clearTimeout(timer);
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-xl text-gray-600">加载中...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            CityU Campus Tasks
          </h1>
          <p className="text-xl text-gray-600">
            开放世界地图 × NPC 智能体校园任务系统
          </p>
        </header>

        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                前端状态
              </h2>
              <div className="space-y-2">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                  <span>React + Vite 运行中</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                  <span>Tailwind CSS 已加载</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                  <span>TypeScript 支持</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                后端状态
              </h2>
              <div className="space-y-2">
                <div className="flex items-center">
                  <div className={`w-3 h-3 rounded-full mr-3 ${
                    backendStatus === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                  <span>FastAPI: {backendStatus}</span>
                </div>
                <div className="text-sm text-gray-600 mt-2">
                  端口: http://localhost:8000
                </div>
              </div>
            </div>
          </div>

          <div className="mt-12 bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              快速开始
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-gray-700 mb-2">前端开发</h3>
                <code className="block bg-gray-100 p-3 rounded text-sm">
                  cd frontend<br/>
                  npm install<br/>
                  npm run dev
                </code>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700 mb-2">后端开发</h3>
                <code className="block bg-gray-100 p-3 rounded text-sm">
                  cd backend<br/>
                  pip install -r requirements.txt<br/>
                  uvicorn main:app --reload
                </code>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App