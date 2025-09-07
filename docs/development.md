# 开发指南

## 环境要求

- Node.js 18+
- Python 3.9+
- Git

## 本地开发

### 1. 克隆项目

```bash
git clone <repository-url>
cd cityu-campus-tasks
```

### 2. 环境配置

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑环境变量
vim .env
```

### 3. 安装依赖

```bash
# 前端
cd frontend
npm install

# 后端
cd ../backend
pip install -r requirements.txt
```

### 4. 启动开发服务器

```bash
# 前端 (端口 5173)
cd frontend
npm run dev

# 后端 (端口 8000)
cd backend
uvicorn main:app --reload
```

## 代码规范

### 前端
- 使用 TypeScript
- 遵循 ESLint 规则
- 使用 Tailwind CSS 进行样式开发

### 后端
- 使用 Python 类型注解
- 遵循 PEP 8 规范
- 使用 FastAPI 最佳实践

## 测试

```bash
# 前端测试
cd frontend
npm run test

# 后端测试
cd backend
pytest