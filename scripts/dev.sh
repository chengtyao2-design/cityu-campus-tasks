#!/bin/bash

# CityU Campus Tasks 一键启动脚本
# 适用于 Cloud Studio 和本地开发环境

echo "🚀 启动 CityU Campus Tasks 开发环境..."

# 检查依赖
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js 18+"
    exit 1
fi

if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Python 未安装，请先安装 Python 3.8+"
    exit 1
fi

# 确定 Python 命令
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

echo "📦 安装依赖..."

# 安装前端依赖
echo "  - 安装前端依赖..."
cd frontend
npm install --silent
if [ $? -ne 0 ]; then
    echo "❌ 前端依赖安装失败"
    exit 1
fi
cd ..

# 安装后端依赖
echo "  - 安装后端依赖..."
cd backend
$PYTHON_CMD -m pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "❌ 后端依赖安装失败"
    exit 1
fi
cd ..

# 复制环境变量文件
if [ ! -f .env ]; then
    echo "📝 创建环境变量文件..."
    cp .env.example .env
fi

echo "✅ 依赖安装完成！"
echo ""

# 检查是否在 Cloud Studio 环境
if [ -n "$CLOUDSTUDIO_ENV" ] || [ -n "$CODESPACE_NAME" ] || [ -d "/home/cloudstudio" ]; then
    echo "🌐 检测到云端开发环境，启动服务..."
    
    # 后台启动后端
    echo "🔧 启动后端服务器 (端口 8000)..."
    cd backend
    nohup $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    # 等待后端启动
    sleep 3
    
    # 检查后端是否启动成功
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ 后端服务器启动成功"
    else
        echo "❌ 后端服务器启动失败，请检查 backend.log"
        exit 1
    fi
    
    # 启动前端
    echo "🎨 启动前端服务器 (端口 5173)..."
    cd frontend
    npm run dev -- --host 0.0.0.0 &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "🎉 服务启动完成！"
    echo ""
    echo "📱 访问地址："
    echo "  前端应用: http://localhost:5173"
    echo "  后端 API: http://localhost:8000"
    echo "  API 文档: http://localhost:8000/docs"
    echo ""
    echo "📋 进程 ID："
    echo "  后端 PID: $BACKEND_PID"
    echo "  前端 PID: $FRONTEND_PID"
    echo ""
    echo "🛑 停止服务："
    echo "  kill $BACKEND_PID $FRONTEND_PID"
    echo ""
    echo "📊 查看日志："
    echo "  后端日志: tail -f backend.log"
    echo "  前端日志: 查看当前终端输出"
    echo ""
    echo "⏳ 前端服务器启动中，请稍候..."
    
    # 等待用户中断
    wait $FRONTEND_PID
    
else
    echo "💻 本地开发环境检测到"
    echo ""
    echo "🔧 手动启动命令："
    echo ""
    echo "1. 启动后端 (新终端):"
    echo "   cd backend && $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    echo ""
    echo "2. 启动前端 (新终端):"
    echo "   cd frontend && npm run dev"
    echo ""
    echo "3. 访问应用:"
    echo "   前端: http://localhost:5173"
    echo "   后端: http://localhost:8000"
fi