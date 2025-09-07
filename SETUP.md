# 环境设置指南

## 当前状态
✅ 项目结构已创建完成
✅ 后端代码已就绪
✅ 前端代码已就绪
⚠️ 需要安装 Node.js 和配置环境

## 环境要求检查

### 1. Node.js 安装检查
```powershell
# 检查 Node.js 是否安装
node --version
npm --version
```

如果提示找不到命令，请：
1. 访问 https://nodejs.org/ 下载并安装 Node.js 18+ LTS 版本
2. 重启 PowerShell 终端
3. 重新运行检查命令

### 2. Python 环境检查
```powershell
# 检查 Python 版本
python --version
pip --version
```

## 快速启动步骤

### 步骤 1: 安装前端依赖
```powershell
cd frontend
npm install
```

### 步骤 2: 安装后端依赖
```powershell
cd ../backend
pip install -r requirements.txt
```

### 步骤 3: 配置环境变量
```powershell
# 复制环境变量文件
copy .env.example .env
```

### 步骤 4: 启动服务

**启动后端** (新终端窗口):
```powershell
cd backend
python -m uvicorn main:app --reload
```

**启动前端** (新终端窗口):
```powershell
cd frontend
npm run dev
```

## 验收测试

1. **后端健康检查**: http://localhost:8000/health
   - 应返回: `{"status": "healthy", "message": "API is running"}`

2. **前端页面**: http://localhost:5173
   - 应显示: CityU Campus Tasks 欢迎页面
   - 后端状态应显示为 "healthy"

## 故障排除

### Node.js 相关问题
- 确保安装了 Node.js 18+ LTS 版本
- 重启终端后重试
- 检查系统 PATH 环境变量

### Python 相关问题
- 确保使用 Python 3.9+
- 如果 pip 安装失败，尝试: `python -m pip install --upgrade pip`

### 端口占用问题
- 前端默认端口: 5173
- 后端默认端口: 8000
- 如有冲突，可在启动命令中指定其他端口

## 项目结构说明

```
├── frontend/          # React + Vite + TypeScript + Tailwind
├── backend/           # FastAPI + Python
├── data/              # 数据文件和种子数据
├── scripts/           # 构建和部署脚本
├── docs/              # 项目文档
├── .env.example       # 环境变量模板
└── README.md          # 项目说明