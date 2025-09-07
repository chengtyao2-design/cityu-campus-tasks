# GitHub 仓库设置指南

现在本地环境已安装 Git，请按照以下步骤创建并连接 GitHub 仓库：

## 1. 创建 GitHub 仓库

1. 访问 [GitHub](https://github.com)
2. 点击右上角的 "+" 按钮，选择 "New repository"
3. 仓库名称: `cityu-campus-tasks`
4. 描述: `CityU Campus Tasks - 开放世界地图 × NPC 智能体校园任务系统`
5. 选择 "Public" 或 "Private"
6. **不要**勾选 "Add a README file"（我们已经创建了）
7. 点击 "Create repository"

## 2. 本地 Git 初始化和推送

在项目根目录执行以下命令：

```bash
# 初始化 Git 仓库
git init

# 添加所有文件到暂存区
git add .

# 创建初始提交
git commit -m "Initial commit: CityU Campus Tasks project setup"

# 添加远程仓库
git remote add origin https://github.com/chengtyao2-design/cityu-campus-tasks.git

# 推送到 GitHub
git push -u origin main
```

## 3. 后续开发流程

```bash
# 查看文件状态
git status

# 添加修改的文件
git add .

# 提交更改
git commit -m "描述你的更改"

# 推送到远程仓库
git push
```

## 2. 本地 Git 设置

如果需要安装 Git，请：

### Windows 用户
1. 下载 [Git for Windows](https://git-scm.com/download/win)
2. 安装后重启 PowerShell
3. 运行以下命令：

```bash
# 配置 Git
git config --global user.name "chengtyao2-design"
git config --global user.email "chengtyao2@gapps.cityu.edu.hk"

# 初始化仓库
git init
git add .
git commit -m "Initial commit: CityU Campus Tasks project setup"

# 连接到 GitHub
git remote add origin https://github.com/chengtyao2-design/cityu-campus-tasks.git
git branch -M main
git push -u origin main
```

## 3. 验证 CI/CD

推送代码后，访问 GitHub 仓库的 "Actions" 标签页，确认：

✅ Frontend CI 通过（ESLint, TypeScript, Build）
✅ Backend CI 通过（Black, Flake8, MyPy, Startup Test）
✅ Integration Tests 通过（健康检查）

## 4. 项目结构验证

确认以下文件已正确上传：

```
├── .github/workflows/check.yml  # CI/CD 配置
├── .gitignore                   # Git 忽略文件
├── README.md                    # 项目说明
├── GITHUB_SETUP.md             # 本指南
├── frontend/
│   ├── package.json            # 包含 lint, type-check 脚本
│   └── src/                    # React 源码
├── backend/
│   ├── requirements.txt        # 生产依赖
│   ├── requirements-dev.txt    # 开发依赖
│   └── main.py                 # FastAPI 应用
└── docs/                       # 文档目录
```

## 5. 本地开发验证

```bash
# 测试前端
cd frontend
npm install
npm run lint      # ESLint 检查
npm run type-check # TypeScript 检查
npm run build     # 构建测试

# 测试后端
cd backend
pip install -r requirements-dev.txt
black --check .   # 代码格式检查
flake8 .         # 代码质量检查
mypy .           # 类型检查
```

## 故障排除

如果 CI 失败，检查：

1. **Frontend 问题**:
   - `npm ci` 是否成功
   - ESLint 配置是否正确
   - TypeScript 编译是否通过

2. **Backend 问题**:
   - Python 依赖是否正确安装
   - 代码格式是否符合 Black 标准
   - 类型注解是否完整

3. **Integration 问题**:
   - 后端是否能正常启动
   - 健康检查端点是否响应正确

## 下一步

仓库创建成功后，团队成员可以：

1. Clone 仓库进行开发
2. 创建功能分支
3. 提交 Pull Request
4. 自动触发 CI/CD 检查