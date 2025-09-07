#!/bin/bash

# 开发环境启动脚本

echo "🚀 启动 CityU Campus Tasks 开发环境..."

# 检查依赖
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js 18+"
    exit 1
fi

if ! command -v python &> /dev/null; then
    echo "❌ Python 未安装，请先安装 Python 3.9+"
    exit 1
fi

# 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend
npm install
cd ..

# 安装后端依赖
echo "📦 安装后端依赖..."
cd backend
pip install -r requirements.txt
cd ..

# 复制环境变量文件
if [ ! -f .env ]; then
    echo "📝 创建环境变量文件..."
    cp .env.example .env
fi

echo "✅ 开发环境准备完成！"
echo ""
echo "启动命令："
echo "前端: cd frontend && npm run dev"
echo "后端: cd backend && uvicorn main:app --reload"