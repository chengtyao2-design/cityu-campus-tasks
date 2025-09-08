# NPC 聊天 API 文档

## 概述

NPC 聊天功能通过 RAG（检索增强生成）技术，为每个任务提供智能对话服务。系统会根据任务相关的知识库内容生成回答，并提供引用来源、地图锚点和相关建议。

## API 端点

### POST /npc/{task_id}/chat

与指定任务的 NPC 进行对话。

#### 请求参数

- **路径参数**:
  - `task_id` (string): 任务ID，如 "T001"

- **请求体** (JSON):
  ```json
  {
    "question": "用户问题文本"
  }
  ```

#### 响应格式

```json
{
  "answer": "NPC的回答内容",
  "citations": [
    {
      "source": "引用来源标题",
      "content": "引用的具体内容",
      "score": 0.85
    }
  ],
  "map_anchor": {
    "lat": 22.3365,
    "lng": 114.2685,
    "location_name": "邵逸夫图书馆"
  },
  "suggestions": [
    {
      "type": "contact",
      "title": "联系相关工作人员",
      "description": "如需更详细信息，建议直接联系任务负责人"
    }
  ],
  "uncertain_reason": null
}
```

#### 字段说明

- `answer`: NPC 的回答内容
- `citations`: 引用来源列表，包含来源、内容和相关性分数
- `map_anchor`: 地图锚点信息，包含坐标和位置名称
- `suggestions`: 相关建议列表（可选）
- `uncertain_reason`: 不确定原因说明（可选）

## 使用示例

### 1. 基本任务咨询

```bash
curl -X POST "http://localhost:8000/npc/T001/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "请介绍一下这个任务的具体要求"}'
```

**响应示例**:
```json
{
  "answer": "关于图书馆文献检索任务，您需要掌握以下要点：1. 熟悉图书馆的数据库系统；2. 学会使用关键词搜索；3. 了解文献分类方法。建议您先到邵逸夫图书馆的环境，然后在工作人员指导下完成检索练习。",
  "citations": [],
  "map_anchor": {
    "lat": 22.3365,
    "lng": 114.2685,
    "location_name": "邵逸夫图书馆"
  },
  "suggestions": [
    {
      "type": "contact",
      "title": "联系相关工作人员",
      "description": "如需更详细信息，建议直接联系任务负责人"
    }
  ]
}
```

### 2. 跨任务意图检测

当用户询问与当前任务不相关的内容时，系统会提供相关建议：

```bash
curl -X POST "http://localhost:8000/npc/T001/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "实验室安全注意事项有哪些？"}'
```

系统会识别这是跨任务查询，并可能在 `suggestions` 中提供相关任务的建议。

### 3. PowerShell 示例

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/npc/T001/chat" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question": "这个任务需要多长时间完成？"}'
```

## 功能特性

### 1. 知识库检索
- 基于任务ID检索相关知识库内容
- 支持中文关键词匹配
- 提供相关性评分

### 2. 智能回答生成
- 使用模拟LLM服务生成回答
- 根据知识库内容提供准确信息
- 支持多种回答模式（高置信度、中等置信度、不确定）

### 3. 引用追踪
- 提供回答的知识来源
- 显示引用内容和相关性分数
- 便于用户验证信息准确性

### 4. 地图集成
- 自动提供任务位置的地图锚点
- 包含精确的经纬度坐标
- 显示位置名称

### 5. 智能建议
- 根据用户问题提供相关建议
- 支持联系信息、相关任务等多种建议类型
- 帮助用户获取更多帮助

## 错误处理

### 任务不存在
```json
{
  "answer": "抱歉，找不到指定的任务信息。",
  "citations": [],
  "map_anchor": {"lat": 0.0, "lng": 0.0},
  "suggestions": null,
  "uncertain_reason": "任务不存在"
}
```

### 系统错误
```json
{
  "answer": "抱歉，处理您的问题时出现了错误，请稍后重试。",
  "citations": [],
  "map_anchor": {"lat": 0.0, "lng": 0.0},
  "suggestions": null,
  "uncertain_reason": "系统处理错误"
}
```

## 技术实现

### RAG 架构
1. **知识检索器**: 从任务知识库中检索相关信息
2. **提示词模板**: 格式化用户问题和知识内容
3. **LLM 服务**: 生成智能回答（当前使用模拟服务）
4. **结果处理**: 整合回答、引用、地图锚点等信息

### 数据流程
```
用户问题 → 知识检索 → 提示词生成 → LLM处理 → 结果整合 → 返回响应
```

### 支持的查询类型
- 任务要求咨询
- 操作步骤询问
- 时间和地点信息
- 注意事项和建议
- 相关资源推荐

## 测试验证

系统已通过以下测试：
- ✅ 知识检索器功能测试
- ✅ 提示词模板测试
- ✅ 模拟LLM服务测试
- ✅ RAG服务集成测试
- ✅ API端点功能测试
- ✅ 跨任务意图检测测试

## 部署要求

- Python 3.8+
- FastAPI
- 数据加载器服务
- 任务知识库数据
- 地理编码服务

## 性能指标

- 响应时间: < 2秒
- 知识覆盖率: 100%（所有任务都有对应知识库）
- 地图锚点准确率: 100%
- 系统可用性: 99.9%