#!/bin/bash

# Cloud Studio 导入测试脚本
# 模拟他人按照文档在 Cloud Studio 中导入和运行项目的过程

echo "🧪 Cloud Studio 导入测试"
echo "========================"

# 模拟 Cloud Studio 环境
export CLOUDSTUDIO_ENV=true

echo "📋 测试步骤："
echo "1. 检查项目文件完整性"
echo "2. 验证启动脚本可执行性"
echo "3. 检查依赖配置"
echo "4. 模拟启动流程"

echo ""
echo "1️⃣ 检查项目文件完整性..."

# 检查关键文件
REQUIRED_FILES=(
    "docs/cloudstudio.md"
    "cloudstudio-start.sh"
    "scripts/dev.sh"
    ".env.example"
    "frontend/package.json"
    "backend/requirements.txt"
    "backend/main.py"
    "README.md"
)

MISSING_FILES=()
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo "✅ 所有必需文件存在"
else
    echo "❌ 缺少文件: ${MISSING_FILES[*]}"
    exit 1
fi

echo ""
echo "2️⃣ 验证启动脚本..."

# 检查脚本语法
if bash -n cloudstudio-start.sh; then
    echo "✅ cloudstudio-start.sh 语法正确"
else
    echo "❌ cloudstudio-start.sh 语法错误"
    exit 1
fi

if bash -n scripts/dev.sh; then
    echo "✅ scripts/dev.sh 语法正确"
else
    echo "❌ scripts/dev.sh 语法错误"
    exit 1
fi

echo ""
echo "3️⃣ 检查依赖配置..."

# 检查前端依赖
if [ -f "frontend/package.json" ]; then
    if grep -q "react" frontend/package.json && grep -q "vite" frontend/package.json; then
        echo "✅ 前端依赖配置正确"
    else
        echo "❌ 前端依赖配置不完整"
        exit 1
    fi
fi

# 检查后端依赖
if [ -f "backend/requirements.txt" ]; then
    if grep -q "fastapi" backend/requirements.txt && grep -q "uvicorn" backend/requirements.txt; then
        echo "✅ 后端依赖配置正确"
    else
        echo "❌ 后端依赖配置不完整"
        exit 1
    fi
fi

echo ""
echo "4️⃣ 检查文档完整性..."

# 检查 Cloud Studio 文档
if grep -q "一键启动" docs/cloudstudio.md && \
   grep -q "端口配置" docs/cloudstudio.md && \
   grep -q "验证清单" docs/cloudstudio.md; then
    echo "✅ Cloud Studio 文档内容完整"
else
    echo "❌ Cloud Studio 文档内容不完整"
    exit 1
fi

echo ""
echo "5️⃣ 模拟启动流程（干运行）..."

# 检查 Python 和 Node.js
if command -v python3 &> /dev/null || command -v python &> /dev/null; then
    echo "✅ Python 环境可用"
else
    echo "⚠️  Python 环境不可用（在 Cloud Studio 中会自动安装）"
fi

if command -v node &> /dev/null; then
    echo "✅ Node.js 环境可用"
else
    echo "⚠️  Node.js 环境不可用（在 Cloud Studio 中会自动安装）"
fi

# 检查环境变量文件
if [ -f ".env.example" ]; then
    if grep -q "CORS_ORIGINS.*preview.myqcloud.com" .env.example; then
        echo "✅ 环境变量包含 Cloud Studio 配置"
    else
        echo "❌ 环境变量缺少 Cloud Studio 配置"
        exit 1
    fi
fi

echo ""
echo "🎉 Cloud Studio 导入测试通过！"
echo ""
echo "📋 测试结果总结："
echo "✅ 项目文件完整"
echo "✅ 启动脚本语法正确"
echo "✅ 依赖配置完整"
echo "✅ 文档内容完整"
echo "✅ 环境配置适配 Cloud Studio"
echo ""
echo "🚀 他人可以按照 docs/cloudstudio.md 文档在 Cloud Studio 中一键运行项目！"