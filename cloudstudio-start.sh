#!/bin/bash

# Cloud Studio 一键启动脚本
# 专为腾讯 Cloud Studio 环境优化

echo "🌐 Cloud Studio - CityU Campus Tasks 一键启动"
echo "================================================"

# 设置错误时退出
set -e

# 检查环境
echo "🔍 检查运行环境..."
if [ -d "/home/cloudstudio" ] || [ -n "$CLOUDSTUDIO_ENV" ]; then
    echo "✅ Cloud Studio 环境检测成功"
else
    echo "⚠️  未检测到 Cloud Studio 环境，但继续执行..."
fi

# 确定 Python 命令
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "🐍 使用 Python: $($PYTHON_CMD --version)"
echo "📦 使用 Node.js: $(node --version)"

# 快速安装依赖
echo ""
echo "📦 安装项目依赖..."

# 后端依赖
echo "  - 安装后端依赖..."
cd backend
$PYTHON_CMD -m pip install -r requirements.txt --quiet --disable-pip-version-check
cd ..

# 前端依赖
echo "  - 安装前端依赖..."
cd frontend
npm install --silent --no-audit --no-fund
cd ..

# 创建环境文件
if [ ! -f .env ]; then
    echo "📝 创建环境配置文件..."
    cp .env.example .env
fi

echo "✅ 依赖安装完成"

# 启动服务
echo ""
echo "🚀 启动应用服务..."

# 启动后端
echo "🔧 启动后端服务器..."
cd backend
nohup $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端 PID: $BACKEND_PID"
cd ..

# 等待后端启动
echo "⏳ 等待后端服务启动..."
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 后端服务启动成功"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ 后端服务启动超时"
        exit 1
    fi
    sleep 1
done

# 启动前端
echo "🎨 启动前端服务器..."
cd frontend
nohup npm run dev -- --host 0.0.0.0 --port 5173 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端 PID: $FRONTEND_PID"
cd ..

# 等待前端启动
echo "⏳ 等待前端服务启动..."
sleep 5

echo ""
echo "🎉 启动完成！"
echo "================================================"
echo ""
echo "📱 访问地址："
echo "  🌐 前端应用: http://localhost:5173"
echo "  🔧 后端 API: http://localhost:8000"
echo "  📚 API 文档: http://localhost:8000/docs"
echo ""
echo "📊 服务状态："
echo "  后端进程: $BACKEND_PID"
echo "  前端进程: $FRONTEND_PID"
echo ""
echo "📋 常用命令："
echo "  查看后端日志: tail -f logs/backend.log"
echo "  查看前端日志: tail -f logs/frontend.log"
echo "  停止所有服务: kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "🔗 在 Cloud Studio 中："
echo "  1. 查看右侧 '端口' 面板"
echo "  2. 点击端口号旁的 '预览' 按钮"
echo "  3. 或使用 Cloud Studio 提供的预览 URL"
echo ""

# 保存 PID 到文件
mkdir -p logs
echo $BACKEND_PID > logs/backend.pid
echo $FRONTEND_PID > logs/frontend.pid

echo "✨ 服务已在后台运行，可以开始开发了！"