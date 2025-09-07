# CityU Campus Tasks

开放世界地图 × NPC 智能体校园任务系统

## 项目结构

```
├── frontend/          # React + TypeScript + Vite 前端
├── backend/           # FastAPI Python 后端
├── .github/workflows/ # GitHub Actions CI/CD
├── docs/             # 项目文档
├── data/             # 数据文件
└── scripts/          # 构建脚本
```

## 快速开始

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

访问: http://localhost:5173

### 后端开发

```bash
cd backend
pip install -r requirements.txt
python main.py
```

访问: http://localhost:8000
API文档: http://localhost:8000/docs

## 开发工具

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: Tailwind CSS
- **代码检查**: ESLint + TypeScript

### 后端
- **框架**: FastAPI
- **运行时**: Python 3.11+
- **代码格式**: Black
- **代码检查**: Flake8 + MyPy

## CI/CD

项目使用 GitHub Actions 进行持续集成：

- ✅ 依赖安装
- ✅ 代码格式检查 (Black, ESLint)
- ✅ 类型检查 (MyPy, TypeScript)
- ✅ 构建测试
- ✅ 集成测试

## 部署

### 本地开发
```bash
# 启动后端
cd backend && python main.py

# 启动前端 (新终端)
cd frontend && npm run dev
```

### 生产构建
```bash
# 构建前端
cd frontend && npm run build

# 后端生产运行
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

MIT License