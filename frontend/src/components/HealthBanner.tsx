import React, { useState, useEffect } from 'react';
import { Alert, Spin } from 'antd';
import { CheckCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';

interface HealthStatus {
  status: string;
  isLoading: boolean;
}

const HealthBanner: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus>({
    status: 'checking',
    isLoading: true,
  });

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/healthz', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setHealth({
          status: data.status || 'unknown',
          isLoading: false,
        });
      } catch (error) {
        // 静默处理错误，不在控制台显示
        setHealth({
          status: 'disconnected',
          isLoading: false,
        });
      }
    };

    // 延迟检查，避免页面加载时立即报错
    const timer = setTimeout(checkHealth, 1000);
    const interval = setInterval(checkHealth, 30000);

    return () => {
      clearTimeout(timer);
      clearInterval(interval);
    };
  }, []);

  if (health.isLoading) {
    return (
      <Alert
        message={
          <div className="flex items-center gap-2">
            <Spin size="small" />
            <span>检查后端连接状态...</span>
          </div>
        }
        type="info"
        showIcon={false}
        className="mb-4 rounded-lg"
      />
    );
  }

  const isHealthy = health.status === 'healthy';
  const isDisconnected = health.status === 'disconnected';
  
  return (
    <Alert
      message={
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {isHealthy ? (
              <CheckCircleOutlined className="text-green-500" />
            ) : (
              <ExclamationCircleOutlined className={isDisconnected ? "text-orange-500" : "text-red-500"} />
            )}
            <span className="font-medium">
              后端服务状态: {
                isHealthy ? '正常运行' : 
                isDisconnected ? '未连接' : '连接失败'
              }
            </span>
          </div>
          <span className="text-sm text-gray-500 hidden sm:block">
            {isHealthy ? 'FastAPI 服务已就绪' : 
             isDisconnected ? '前端独立运行模式' : '请检查后端服务是否启动'}
          </span>
        </div>
      }
      type={isHealthy ? 'success' : isDisconnected ? 'warning' : 'error'}
      showIcon={false}
      className="mb-4 rounded-lg"
    />
  );
};

export default HealthBanner;