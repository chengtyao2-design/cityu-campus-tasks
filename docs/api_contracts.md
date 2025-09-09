# API 契约文档

## 基础路由 API 规范

### 1. 健康检查端点

#### GET /healthz

**描述**: 检查 API 服务健康状态

**响应模式**:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-08T12:00:00Z",
  "version": "1.0.0",
  "uptime": 3600.5
}
```

**状态码**:
- `200`: 服务正常
- `503`: 服务不可用

**curl 示例**:
```bash
curl -X GET "http://localhost:8000/healthz" \
  -H "Accept: application/json"
```

### 2. 任务列表端点

#### GET /tasks

**描述**: 获取任务列表，支持过滤和分页

**查询参数**:
- `page` (int, 可选): 页码，默认 1，最小 1
- `size` (int, 可选): 每页大小，默认 20，范围 1-100
- `category` (string, 可选): 任务类别 (`course`, `activity`, `orientation`, `academic`, `social`)
- `course` (string, 可选): 课程代码
- `difficulty` (string, 可选): 任务难度 (`easy`, `medium`, `hard`)
- `status` (string, 可选): 任务状态 (`available`, `in_progress`, `completed`, `locked`)
- `date_from` (datetime, 可选): 开始日期 (ISO 8601 格式)
- `date_to` (datetime, 可选): 结束日期 (ISO 8601 格式)
- `search` (string, 可选): 搜索关键词（在标题和描述中搜索）

**响应模式**:
```json
{
  "data": [
    {
      "task_id": "TASK001",
      "title": "校园导览",
      "description": "参加新生校园导览活动",
      "category": "orientation",
      "location": {
        "name": "教学楼入口",
        "lat": 22.3364,
        "lng": 114.2654
      },
      "estimated_duration": 60,
      "difficulty": "easy",
      "points": 10,
      "course_code": null,
      "npc_id": "NPC001",
      "status": "available",
      "prerequisites": null,
      "created_at": "2025-09-01T10:00:00Z",
      "updated_at": "2025-09-01T10:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "size": 20,
    "total": 12,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

**状态码**:
- `200`: 成功
- `400`: 请求参数错误
- `500`: 服务器内部错误

**curl 示例**:

基本查询:
```bash
curl -X GET "http://localhost:8000/tasks" \
  -H "Accept: application/json"
```

带过滤条件:
```bash
curl -X GET "http://localhost:8000/tasks?category=course&difficulty=medium&page=1&size=10" \
  -H "Accept: application/json"
```

按课程过滤:
```bash
curl -X GET "http://localhost:8000/tasks?course=CS101&status=available" \
  -H "Accept: application/json"
```

日期范围过滤:
```bash
curl -X GET "http://localhost:8000/tasks?date_from=2025-09-01T00:00:00Z&date_to=2025-09-30T23:59:59Z" \
  -H "Accept: application/json"
```

搜索查询:
```bash
curl -X GET "http://localhost:8000/tasks?search=图书馆" \
  -H "Accept: application/json"
```

### 3. 任务详情端点

#### GET /tasks/{task_id}

**描述**: 获取指定任务的详细信息，包括相关知识库

**路径参数**:
- `task_id` (string, 必需): 任务ID

**响应模式**:
```json
{
  "data": {
    "task_id": "TASK001",
    "title": "校园导览",
    "description": "参加新生校园导览活动",
    "category": "orientation",
    "location": {
      "name": "教学楼入口",
      "lat": 22.3364,
      "lng": 114.2654
    },
    "estimated_duration": 60,
    "difficulty": "easy",
    "points": 10,
    "course_code": null,
    "npc_id": "NPC001",
    "status": "available",
    "prerequisites": null,
    "created_at": "2025-09-01T10:00:00Z",
    "updated_at": "2025-09-01T10:00:00Z",
    "knowledge": {
      "knowledge_type": "guide",
      "title": "校园导览要点",
      "content": "1. 香港城市大学成立于1984年...",
      "tags": ["orientation", "campus", "guide"],
      "difficulty_level": "beginner",
      "estimated_read_time": 5,
      "prerequisites": null,
      "related_tasks": ["TASK002", "TASK003"]
    }
  }
}
```

**状态码**:
- `200`: 成功
- `404`: 任务不存在
- `500`: 服务器内部错误

**curl 示例**:
```bash
curl -X GET "http://localhost:8000/tasks/TASK001" \
  -H "Accept: application/json"
```

## 错误响应格式

所有错误响应都遵循统一格式:

```json
{
  "error": "ValidationError",
  "message": "请求参数验证失败",
  "details": {
    "field": "page",
    "value": 0,
    "constraint": "must be >= 1"
  }
}
```

## 数据类型定义

### TaskCategory 枚举
- `course`: 课程任务
- `activity`: 活动任务
- `orientation`: 迎新任务
- `academic`: 学术任务
- `social`: 社交任务

### TaskDifficulty 枚举
- `easy`: 简单
- `medium`: 中等
- `hard`: 困难

### TaskStatus 枚举
- `available`: 可用
- `in_progress`: 进行中
- `completed`: 已完成
- `locked`: 锁定

## 分页规则

- 默认页码: 1
- 默认页大小: 20
- 最大页大小: 100
- 页码从 1 开始计数
- 空结果返回空数组，meta 信息正常

## 过滤规则

- 多个过滤条件使用 AND 逻辑
- 字符串匹配区分大小写
- 日期过滤使用 ISO 8601 格式
- 搜索功能不区分大小写，支持部分匹配

## 性能要求

- 响应时间: < 200ms (正常负载)
- 并发支持: 100+ 请求/秒
- 数据一致性: 强一致性读取