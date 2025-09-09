"""
Pydantic 数据模式定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TaskCategory(str, Enum):
    """任务类别枚举"""
    COURSE = "course"
    ACTIVITY = "activity"
    ORIENTATION = "orientation"
    ACADEMIC = "academic"
    SOCIAL = "social"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    LOCKED = "locked"


class TaskDifficulty(str, Enum):
    """任务难度枚举"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class HealthStatus(BaseModel):
    """健康检查响应模式"""
    status: str = Field(..., description="服务状态")
    timestamp: datetime = Field(..., description="检查时间")
    version: str = Field(..., description="API版本")
    uptime: Optional[float] = Field(None, description="运行时间(秒)")


class LocationSchema(BaseModel):
    """位置信息模式"""
    name: str = Field(..., description="位置名称")
    lat: float = Field(..., description="纬度", ge=-90, le=90)
    lng: float = Field(..., description="经度", ge=-180, le=180)


class TaskSchema(BaseModel):
    """任务信息模式"""
    task_id: str = Field(..., description="任务ID")
    title: str = Field(..., description="任务标题")
    description: str = Field(..., description="任务描述")
    category: TaskCategory = Field(..., description="任务类别")
    location: LocationSchema = Field(..., description="任务位置")
    estimated_duration: int = Field(..., description="预估时长(分钟)", gt=0)
    difficulty: TaskDifficulty = Field(..., description="任务难度")
    points: int = Field(..., description="任务积分", ge=0)
    course_code: Optional[str] = Field(None, description="课程代码")
    npc_id: Optional[str] = Field(None, description="NPC ID")
    status: TaskStatus = Field(TaskStatus.AVAILABLE, description="任务状态")
    prerequisites: Optional[List[str]] = Field(None, description="前置任务")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class KnowledgeSchema(BaseModel):
    """知识库信息模式"""
    knowledge_type: str = Field(..., description="知识类型")
    title: str = Field(..., description="知识标题")
    content: str = Field(..., description="知识内容")
    tags: Optional[List[str]] = Field(None, description="标签")
    difficulty_level: Optional[str] = Field(None, description="难度等级")
    estimated_read_time: Optional[int] = Field(None, description="预估阅读时间(分钟)")
    prerequisites: Optional[List[str]] = Field(None, description="前置知识")
    related_tasks: Optional[List[str]] = Field(None, description="相关任务")


class TaskDetailSchema(TaskSchema):
    """任务详情模式（包含知识库信息）"""
    knowledge: Optional[KnowledgeSchema] = Field(None, description="相关知识库")


class PaginationMeta(BaseModel):
    """分页元数据"""
    page: int = Field(..., description="当前页码", ge=1)
    size: int = Field(..., description="每页大小", ge=1, le=100)
    total: int = Field(..., description="总记录数", ge=0)
    pages: int = Field(..., description="总页数", ge=0)
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")


class TaskListResponse(BaseModel):
    """任务列表响应模式"""
    data: List[TaskSchema] = Field(..., description="任务列表")
    meta: PaginationMeta = Field(..., description="分页信息")


class TaskDetailResponse(BaseModel):
    """任务详情响应模式"""
    data: TaskDetailSchema = Field(..., description="任务详情")


class SearchRequest(BaseModel):
    """搜索请求模式"""
    query: str = Field(..., description="搜索关键词", min_length=1, max_length=200)
    top_n: Optional[int] = Field(10, description="返回结果数量", ge=1, le=50)


class SearchResult(BaseModel):
    """搜索结果项模式"""
    task_id: str = Field(..., description="任务ID")
    title: str = Field(..., description="任务标题")
    score: float = Field(..., description="相关性分数", ge=0)
    lat: float = Field(..., description="纬度", ge=-90, le=90)
    lng: float = Field(..., description="经度", ge=-180, le=180)


class SearchResponse(BaseModel):
    """搜索响应模式"""
    data: List[SearchResult] = Field(..., description="搜索结果列表")
    meta: Dict[str, Any] = Field(..., description="搜索元数据")


class ChatRequest(BaseModel):
    """NPC 聊天请求模式"""
    question: str = Field(..., description="用户问题", min_length=1, max_length=500)


class Citation(BaseModel):
    """引用信息模式"""
    source: str = Field(..., description="引用来源")
    content: str = Field(..., description="引用内容片段")
    score: float = Field(..., description="相关性分数", ge=0)


class MapAnchor(BaseModel):
    """地图锚点模式"""
    lat: float = Field(..., description="纬度", ge=-90, le=90)
    lng: float = Field(..., description="经度", ge=-180, le=180)


class Suggestion(BaseModel):
    """建议信息模式"""
    type: str = Field(..., description="建议类型")
    title: str = Field(..., description="建议标题")
    description: str = Field(..., description="建议描述")


class ChatResponse(BaseModel):
    """NPC 聊天响应模式"""
    answer: str = Field(..., description="回答内容")
    citations: List[Citation] = Field(..., description="引用信息列表")
    map_anchor: MapAnchor = Field(..., description="地图锚点")
    suggestions: Optional[List[Suggestion]] = Field(None, description="相关建议")
    uncertain_reason: Optional[str] = Field(None, description="不确定原因")


class ErrorResponse(BaseModel):
    """错误响应模式"""
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")


class TaskFilters(BaseModel):
    """任务过滤参数"""
    category: Optional[TaskCategory] = Field(None, description="任务类别")
    course: Optional[str] = Field(None, description="课程代码")
    difficulty: Optional[TaskDifficulty] = Field(None, description="任务难度")
    status: Optional[TaskStatus] = Field(None, description="任务状态")
    date_from: Optional[datetime] = Field(None, description="开始日期")
    date_to: Optional[datetime] = Field(None, description="结束日期")
    search: Optional[str] = Field(None, description="搜索关键词")


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(1, description="页码", ge=1)
    size: int = Field(20, description="每页大小", ge=1, le=100)