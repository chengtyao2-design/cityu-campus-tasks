# Cloud Studio 导入和运行指南

本文档提供在腾讯 Cloud Studio 环境中导入和运行 CityU Campus Tasks 项目的完整指南。

## 🚀 快速开始

### 1. 导入项目

#### 方法一：通过 GitHub 仓库导入
1. 访问 [Cloud Studio](https://cloudstudio.net/)
2. 登录后点击 "新建工作空间"
3. 选择 "从 Git 仓库导入"
4. 输入仓库地址：`https://github.com/chengtyao2-design/cityu-campus-tasks.git`
5. 选择模板：**Node.js** (推荐) 或 **Python**
6. 点击 "创建工作空间"

#### 方法二：通过 URL 直接导入
直接访问：`https://cloudstudio.net/dashboard?template=https://github.com/chengtyao2-design/cityu-campus-tasks.git`

### 2. 环境准备

项目导入后，Cloud Studio 会自动检测并安装依赖。如果需要手动操作：

```bash
# 确认 Node.js 和 Python 版本
node --version  # 应该 >= 18
python --version  # 应该 >= 3.8

# 如果需要安装 Python 包管理器
curl -sSL https://install.python-poetry.org | python3 -
```

## 🔧 一键启动命令

### 方法一：使用 Cloud Studio 专用脚本（推荐）

```bash
# 给脚本执行权限
chmod +x cloudstudio-start.sh

# 一键启动前后端（后台运行）
./cloudstudio-start.sh
```

### 方法二：使用通用开发脚本

```bash
# 给脚本执行权限
chmod +x scripts/dev.sh

# 启动开发环境
./scripts/dev.sh
```

### 方法二：分步启动

#### 启动后端服务器
```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动后端服务器
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 启动前端服务器（新终端）
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动前端开发服务器
npm run dev -- --host 0.0.0.0
```

## 🌐 端口配置

### 默认端口
- **后端 API**: `8000`
- **前端应用**: `5173`

### Cloud Studio 端口访问

1. **自动端口转发**
   - Cloud Studio 会自动检测运行的服务
   - 在右侧面板查看 "端口" 标签页
   - 点击端口号旁的 "预览" 按钮

2. **手动配置端口**
   ```bash
   # 如果需要指定其他端口
   # 后端
   python -m uvicorn main:app --host 0.0.0.0 --port 3001 --reload
   
   # 前端
   npm run dev -- --host 0.0.0.0 --port 3000
   ```

3. **访问应用**
   - 前端应用：`https://your-workspace-id-5173.preview.myqcloud.com`
   - 后端 API：`https://your-workspace-id-8000.preview.myqcloud.com`
   - API 文档：`https://your-workspace-id-8000.preview.myqcloud.com/docs`

## 📋 验证清单

启动成功后，请按以下步骤验证：

### ✅ 1. 服务状态检查
```bash
# 检查进程是否运行
ps aux | grep uvicorn  # 后端进程
ps aux | grep vite     # 前端进程

# 检查端口占用
lsof -i :8000  # 后端端口
lsof -i :5173  # 前端端口
```

### ✅ 2. 后端 API 验证
```bash
# 健康检查
curl http://localhost:8000/health
# 预期响应：{"status":"healthy","message":"API is running"}

# 测试任务 API
curl http://localhost:8000/api/tasks
# 预期响应：包含任务列表的 JSON

# 测试 NPC API  
curl http://localhost:8000/api/npcs
# 预期响应：包含 NPC 列表的 JSON

# 查看 API 文档
curl http://localhost:8000/docs
# 预期响应：HTML 页面（Swagger UI）
```

### ✅ 3. 前端应用验证
1. **访问应用**：点击 Cloud Studio 端口面板中的 5173 端口预览
2. **界面检查**：应该看到 "CityU Campus Tasks" 标题
3. **控制台检查**：打开浏览器开发者工具，确认无严重错误
4. **响应式检查**：调整浏览器窗口大小，确认界面自适应

### ✅ 4. 前后端集成验证
```bash
# 检查 CORS 配置
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:8000/api/tasks

# 预期响应：包含 CORS 头的 200 响应
```

### ✅ 5. 日志检查
```bash
# 查看后端日志
tail -f logs/backend.log

# 查看前端日志
tail -f logs/frontend.log

# 检查是否有错误信息
grep -i error logs/*.log
```

### ✅ 6. Cloud Studio 特定验证
1. **端口转发**：确认右侧端口面板显示 8000 和 5173 端口
2. **预览功能**：点击端口旁的"预览"按钮能正常打开应用
3. **外部访问**：使用 Cloud Studio 提供的外部 URL 能正常访问
4. **热重载**：修改代码后确认自动重新加载

## 🎯 完整验证脚本

创建并运行以下验证脚本：

```bash
# 创建验证脚本
cat > verify.sh << 'EOF'
#!/bin/bash
echo "🔍 CityU Campus Tasks - 完整性验证"
echo "=================================="

# 1. 检查服务状态
echo "1. 检查服务状态..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 后端服务正常"
else
    echo "❌ 后端服务异常"
    exit 1
fi

if curl -s http://localhost:5173 > /dev/null; then
    echo "✅ 前端服务正常"
else
    echo "❌ 前端服务异常"
    exit 1
fi

# 2. 检查 API 端点
echo "2. 检查 API 端点..."
if curl -s http://localhost:8000/api/tasks | grep -q "tasks"; then
    echo "✅ 任务 API 正常"
else
    echo "❌ 任务 API 异常"
fi

if curl -s http://localhost:8000/api/npcs | grep -q "npcs"; then
    echo "✅ NPC API 正常"
else
    echo "❌ NPC API 异常"
fi

# 3. 检查日志
echo "3. 检查日志..."
if [ -f logs/backend.log ] && [ -f logs/frontend.log ]; then
    echo "✅ 日志文件存在"
    ERROR_COUNT=$(grep -i error logs/*.log | wc -l)
    if [ $ERROR_COUNT -eq 0 ]; then
        echo "✅ 无错误日志"
    else
        echo "⚠️  发现 $ERROR_COUNT 个错误日志"
    fi
else
    echo "❌ 日志文件缺失"
fi

echo ""
echo "🎉 验证完成！"
EOF

chmod +x verify.sh
./verify.sh
```

## 🛠️ 开发工具

### 推荐的 Cloud Studio 插件
- **ES7+ React/Redux/React-Native snippets**: React 开发
- **Python**: Python 语法支持
- **Prettier**: 代码格式化
- **GitLens**: Git 增强功能

### 开发命令
```bash
# 前端开发
cd frontend
npm run dev          # 启动开发服务器
npm run build        # 构建生产版本
npm run type-check   # TypeScript 类型检查
npm run lint         # 代码检查

# 后端开发
cd backend
pip install -r requirements-dev.txt  # 安装开发依赖
python -m pytest                     # 运行测试
black .                              # 代码格式化
flake8 .                            # 代码质量检查
```

## 🔧 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 查看端口占用
lsof -i :8000
lsof -i :5173

# 杀死进程
kill -9 <PID>
```

#### 2. 依赖安装失败
```bash
# 清理 npm 缓存
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# 清理 Python 缓存
pip cache purge
pip install -r requirements.txt --force-reinstall
```

#### 3. 前端无法访问后端 API
检查 `frontend/src` 中的 API 基础 URL 配置：
```typescript
// 确保 API_BASE_URL 指向正确的后端地址
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-backend-url' 
  : 'http://localhost:8000';
```

#### 4. CORS 错误
确保后端 `main.py` 中的 CORS 配置包含前端域名：
```python
origins = [
    "http://localhost:5173",
    "https://*.preview.myqcloud.com",  # Cloud Studio 预览域名
]
```

## 📚 更多资源

- [项目 README](../README.md)
- [开发文档](./development.md)
- [GitHub 仓库](https://github.com/chengtyao2-design/cityu-campus-tasks)
- [Cloud Studio 官方文档](https://cloudstudio.net/docs)

## 🆘 获取帮助

如果遇到问题：

1. 检查 Cloud Studio 控制台输出
2. 查看浏览器开发者工具的错误信息
3. 参考本文档的故障排除部分
4. 在项目 GitHub 仓库提交 Issue

---

**🎯 目标**：任何人都能通过这个文档在 Cloud Studio 中一键运行项目！