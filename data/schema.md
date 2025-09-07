# 数据模式文档

## 概述

本文档定义了 CityU Campus Tasks 项目的数据结构和格式规范。

## 数据文件

### 1. tasks.csv - 任务数据

**文件路径**: `data/tasks.csv`  
**格式**: CSV (逗号分隔值)  
**编码**: UTF-8  

#### 字段定义

| 字段名 | 类型 | 必需 | 描述 | 示例 |
|--------|------|------|------|------|
| task_id | string | ✅ | 任务唯一标识符，格式：T + 3位数字 | T001 |
| title | string | ✅ | 任务标题，2-50字符 | 图书馆文献检索 |
| description | string | ✅ | 任务详细描述，10-500字符 | 在图书馆完成指定主题的文献检索任务... |
| category | string | ✅ | 任务分类 | 学术研究 |
| location_name | string | ✅ | 任务地点名称 | 邵逸夫图书馆 |
| latitude | float | ✅ | 纬度坐标 | 22.3364 |
| longitude | float | ✅ | 经度坐标 | 114.2654 |
| difficulty | string | ✅ | 难度等级 | 初级 |
| estimated_duration | integer | ✅ | 预估完成时间（分钟） | 60 |
| prerequisites | string | ❌ | 前置条件 | CS1001 |
| rewards | string | ✅ | 任务奖励 | 学分+2 |
| status | string | ✅ | 任务状态 | active |
| created_at | datetime | ✅ | 创建时间（ISO 8601格式） | 2024-01-15T09:00:00Z |
| updated_at | datetime | ✅ | 更新时间（ISO 8601格式） | 2024-01-15T09:00:00Z |
| npc_id | string | ✅ | 关联NPC标识符 | NPC001 |
| course_code | string | ❌ | 关联课程代码 | CS2402 |

#### 枚举值

**category (任务分类)**:
- 学术研究
- 安全培训
- 社团活动
- 志愿服务
- 文艺活动
- 创业实践
- 体育运动
- 生活体验

**difficulty (难度等级)**:
- 初级
- 中级
- 高级

**status (任务状态)**:
- active (活跃)
- inactive (非活跃)
- completed (已完成)
- pending (待处理)

#### 约束条件

- `task_id`: 必须匹配正则表达式 `^T\d{3}$`
- `latitude`: 应在 22.0-23.0 范围内（香港地区）
- `longitude`: 应在 114.0-115.0 范围内（香港地区）
- `estimated_duration`: 1-480 分钟（最多8小时）
- `course_code`: 格式为 `^[A-Z]{2}\d{4}$`（如 CS2402）

### 2. task_kb.jsonl - 任务知识库

**文件路径**: `data/task_kb.jsonl`  
**格式**: JSONL (每行一个JSON对象)  
**编码**: UTF-8  

#### 字段定义

| 字段名 | 类型 | 必需 | 描述 | 示例 |
|--------|------|------|------|------|
| task_id | string | ✅ | 关联的任务ID | T001 |
| knowledge_type | string | ✅ | 知识类型 | procedure |
| content | string | ✅ | 知识内容，20-2000字符 | 文献检索步骤：1. 确定检索主题... |
| tags | array[string] | ✅ | 标签数组 | ["图书馆", "学术研究"] |
| difficulty | string | ✅ | 难度等级 | 初级 |
| estimated_time | integer | ✅ | 预估学习时间（分钟） | 60 |
| course_code | string | ❌ | 关联课程代码 | CS2402 |

#### 枚举值

**knowledge_type (知识类型)**:
- procedure (操作流程)
- safety_guide (安全指南)
- interview_tips (面试技巧)
- guide_script (导览脚本)
- project_requirements (项目要求)
- photography_guide (摄影指南)
- business_plan (商业计划)
- fitness_plan (健身计划)
- performance_guide (表演指南)
- lab_procedure (实验流程)
- food_review (美食评测)
- academic_notes (学术笔记)

**difficulty (难度等级)**:
- 初级
- 中级
- 高级

#### 约束条件

- `task_id`: 必须匹配正则表达式 `^T\d{3}$`
- `content`: 长度至少20个字符
- `tags`: 必须是非空数组
- `estimated_time`: 必须是正整数
- `course_code`: 格式为 `^[A-Z]{2}\d{4}$`（可选）

## 数据关系

### 任务与知识库关系

- 一个任务 (Task) 对应一条知识库记录 (TaskKB)
- 通过 `task_id` 字段建立关联
- 知识库提供任务执行的详细指导信息

### 任务与课程关系

- 任务可以关联到具体课程（通过 `course_code`）
- 课程代码格式：学院缩写(2字母) + 课程编号(4数字)
- 示例课程：
  - CS2402: 计算机科学系数据结构课程
  - EE3001: 电子工程系电路分析课程

## 样例数据

### 课程相关任务 (2门课程)

1. **CS2402 - 数据结构**
   - T001: 图书馆文献检索
   - T005: 数据结构课程项目

2. **EE3001 - 电路分析**
   - T002: 实验室安全培训
   - T010: 电路分析实验

### 活动任务 (10种活动)

1. T003: 学生会招新面试 (社团活动)
2. T004: 校园导览志愿服务 (志愿服务)
3. T006: 环保主题摄影比赛 (文艺活动)
4. T007: 创业计划书撰写 (创业实践)
5. T008: 体育馆健身打卡 (体育运动)
6. T009: 国际文化节表演 (文艺活动)
7. T011: 食堂美食探索 (生活体验)
8. T012: 学术讲座参与 (学术研究)

## 数据校验

使用 `scripts/validate_data.py` 脚本进行数据校验：

```bash
python scripts/validate_data.py
```

校验内容包括：
- 字段完整性检查
- 数据类型验证
- 格式规范验证
- 约束条件检查
- 关联关系验证

## 数据扩展

### 添加新任务

1. 在 `tasks.csv` 中添加新行
2. 在 `task_kb.jsonl` 中添加对应的知识记录
3. 运行校验脚本确保数据格式正确
4. 更新相关文档

### 添加新字段

1. 更新数据模式文档
2. 修改校验脚本
3. 更新现有数据文件
4. 测试数据兼容性

## 注意事项

- 所有时间字段使用 UTC 时区
- 坐标系统使用 WGS84
- 文本内容支持中英文混合
- JSON 字符串需要正确转义
- CSV 字段包含逗号时需要用引号包围