from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
import time
import asyncio
from datetime import datetime
from typing import Optional, List
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import math

# 导入中间件和配置
from middleware import setup_middleware, get_middleware_stats
from config import app_config, get_middleware_config

# 导入数据加载器和模式
from data_loader import data_loader, initialize_data_loader
from search_engine import initialize_search_engine, search_tasks
from rag import initialize_rag_service, process_npc_chat
from schemas import (
    HealthStatus, TaskSchema, TaskDetailSchema, TaskListResponse, 
    TaskDetailResponse, ErrorResponse, TaskFilters, PaginationParams,
    PaginationMeta, TaskCategory, TaskDifficulty, TaskStatus,
    LocationSchema, KnowledgeSchema, SearchRequest, SearchResult, SearchResponse,
    ChatRequest, ChatResponse, Citation, MapAnchor, Suggestion
)

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 应用启动时间
app_start_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据加载器
    logger.info("正在初始化数据加载器...")
    success = initialize_data_loader()
    if not success:
        logger.error("数据加载器初始化失败")
    else:
        logger.info("数据加载器初始化成功")
        
        # 初始化搜索引擎
        logger.info("正在初始化搜索引擎...")
        search_success = initialize_search_engine(list(data_loader.tasks.values()))
        if not search_success:
            logger.error("搜索引擎初始化失败")
        else:
            logger.info("搜索引擎初始化成功")
        
        # 初始化 RAG 服务
        logger.info("正在初始化 RAG 服务...")
        rag_success = initialize_rag_service(data_loader.task_knowledge)
        if not rag_success:
            logger.error("RAG 服务初始化失败")
        else:
            logger.info("RAG 服务初始化成功")
    
    yield
    
    # 关闭时的清理工作
    logger.info("应用关闭")

app = FastAPI(
    title="CityU Campus Tasks API",
    description="校园任务系统后端 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置中间件
middleware_config = get_middleware_config()
middleware_instances = setup_middleware(app, middleware_config)

# 添加中间件到应用
if middleware_instances.get('timeout'):
    app.add_middleware(type(middleware_instances['timeout']))

if middleware_instances.get('rate_limiter'):
    app.add_middleware(type(middleware_instances['rate_limiter']))

if middleware_instances.get('error_handler'):
    app.add_middleware(type(middleware_instances['error_handler']))

# 映射字典
CATEGORY_MAPPING = {
    "学术研究": "academic",
    "校园活动": "activity", 
    "迎新活动": "orientation",
    "课程任务": "course",
    "社交活动": "social",
    "安全培训": "academic",
    "社团活动": "activity",
    "志愿服务": "activity",
    "学术讲座": "academic",
    "实验课程": "course",
    "数据结构": "course"
}

DIFFICULTY_MAPPING = {
    "初级": "easy",
    "中级": "medium", 
    "高级": "hard",
    "简单": "easy",
    "困难": "hard"
}

STATUS_MAPPING = {
    "active": "available",
    "可用": "available",
    "进行中": "in_progress",
    "已完成": "completed",
    "锁定": "locked"
}

# 辅助函数
def convert_task_to_schema(task) -> TaskSchema:
    """将数据模型转换为 Pydantic 模式"""
    # 映射枚举值
    category = CATEGORY_MAPPING.get(task.category, task.category)
    difficulty = DIFFICULTY_MAPPING.get(task.difficulty, task.difficulty)
    status = STATUS_MAPPING.get(task.status, task.status)
    
    # 处理 prerequisites
    prerequisites = None
    if task.prerequisites and task.prerequisites != "无":
        if isinstance(task.prerequisites, str):
            prerequisites = [task.prerequisites] if task.prerequisites.strip() else None
        else:
            prerequisites = task.prerequisites
    
    return TaskSchema(
        task_id=task.task_id,
        title=task.title,
        description=task.description,
        category=category,
        location=LocationSchema(
            name=task.location_name,
            lat=task.location_lat,
            lng=task.location_lng
        ),
        estimated_duration=task.estimated_duration,
        difficulty=difficulty,
        points=task.points,
        course_code=task.course_code,
        npc_id=task.npc_id,
        status=status,
        prerequisites=prerequisites,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

def convert_knowledge_to_schema(knowledge) -> Optional[KnowledgeSchema]:
    """将知识库模型转换为 Pydantic 模式"""
    if not knowledge:
        return None
    return KnowledgeSchema(
        knowledge_type=knowledge.knowledge_type,
        title=knowledge.title,
        content=knowledge.content,
        tags=knowledge.tags,
        difficulty_level=knowledge.difficulty_level,
        estimated_read_time=knowledge.estimated_read_time,
        prerequisites=knowledge.prerequisites,
        related_tasks=knowledge.related_tasks
    )

def apply_task_filters(tasks: List, filters: TaskFilters) -> List:
    """应用任务过滤条件"""
    filtered_tasks = tasks
    
    if filters.category:
        filtered_tasks = [t for t in filtered_tasks if t.category == filters.category]
    
    if filters.course:
        filtered_tasks = [t for t in filtered_tasks if t.course_code == filters.course]
    
    if filters.difficulty:
        filtered_tasks = [t for t in filtered_tasks if t.difficulty == filters.difficulty]
    
    if filters.status:
        filtered_tasks = [t for t in filtered_tasks if t.status == filters.status]
    
    if filters.date_from:
        filtered_tasks = [t for t in filtered_tasks if t.created_at and t.created_at >= filters.date_from]
    
    if filters.date_to:
        filtered_tasks = [t for t in filtered_tasks if t.created_at and t.created_at <= filters.date_to]
    
    if filters.search:
        search_term = filters.search.lower()
        filtered_tasks = [
            t for t in filtered_tasks 
            if search_term in t.title.lower() or search_term in t.description.lower()
        ]
    
    return filtered_tasks

def paginate_results(items: List, page: int, size: int) -> tuple:
    """分页处理"""
    total = len(items)
    pages = math.ceil(total / size) if total > 0 else 0
    start = (page - 1) * size
    end = start + size
    
    paginated_items = items[start:end]
    
    meta = PaginationMeta(
        page=page,
        size=size,
        total=total,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )
    
    return paginated_items, meta

@app.get("/")
async def root():
    """根路径"""
    return {"message": "CityU Campus Tasks API", "version": "1.0.0"}

@app.get("/healthz", response_model=HealthStatus)
async def health_check():
    """健康检查端点"""
    return HealthStatus(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        uptime=time.time() - app_start_time
    )

@app.get("/tasks", response_model=TaskListResponse)
async def get_tasks(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    category: Optional[TaskCategory] = Query(None, description="任务类别"),
    course: Optional[str] = Query(None, description="课程代码"),
    difficulty: Optional[TaskDifficulty] = Query(None, description="任务难度"),
    status: Optional[TaskStatus] = Query(None, description="任务状态"),
    date_from: Optional[datetime] = Query(None, description="开始日期"),
    date_to: Optional[datetime] = Query(None, description="结束日期"),
    search: Optional[str] = Query(None, description="搜索关键词")
):
    """获取任务列表（支持过滤和分页）"""
    try:
        # 获取所有任务
        all_tasks = data_loader.get_all_tasks()
        
        # 应用过滤条件
        filters = TaskFilters(
            category=category,
            course=course,
            difficulty=difficulty,
            status=status,
            date_from=date_from,
            date_to=date_to,
            search=search
        )
        filtered_tasks = apply_task_filters(all_tasks, filters)
        
        # 分页处理
        paginated_tasks, meta = paginate_results(filtered_tasks, page, size)
        
        # 转换为 Pydantic 模式
        task_schemas = [convert_task_to_schema(task) for task in paginated_tasks]
        
        return TaskListResponse(data=task_schemas, meta=meta)
        
    except Exception as e:
        logger.error(f"获取任务列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取任务列表失败")

@app.get("/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_task(task_id: str):
    """获取指定任务详情"""
    try:
        task = data_loader.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        knowledge = data_loader.get_task_knowledge(task_id)
        
        # 转换为详情模式
        task_schema = convert_task_to_schema(task)
        knowledge_schema = convert_knowledge_to_schema(knowledge)
        
        task_detail = TaskDetailSchema(
            **task_schema.model_dump(),
            knowledge=knowledge_schema
        )
        
        return TaskDetailResponse(data=task_detail)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取任务详情失败")

@app.get("/api/knowledge")
async def get_knowledge():
    """获取知识库列表"""
    try:
        knowledge_list = data_loader.get_all_knowledge()
        return {
            "knowledge": [
                {
                    "task_id": kb.task_id,
                    "knowledge_type": kb.knowledge_type,
                    "title": kb.title,
                    "tags": kb.tags,
                    "difficulty_level": kb.difficulty_level,
                    "estimated_read_time": kb.estimated_read_time
                }
                for kb in knowledge_list
            ],
            "total": len(knowledge_list)
        }
    except Exception as e:
        logger.error(f"获取知识库列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取知识库列表失败")

@app.get("/api/npcs")
async def get_npcs():
    """获取NPC列表"""
    try:
        # 从任务数据中提取唯一的NPC信息
        tasks = data_loader.get_all_tasks()
        npcs = {}
        
        for task in tasks:
            if task.npc_id and task.npc_id not in npcs:
                npcs[task.npc_id] = {
                    "npc_id": task.npc_id,
                    "name": f"NPC-{task.npc_id}",  # 临时名称，可以后续扩展
                    "location": {
                        "name": task.location_name,
                        "lat": task.location_lat,
                        "lng": task.location_lng
                    },
                    "associated_tasks": []
                }
            
            if task.npc_id:
                npcs[task.npc_id]["associated_tasks"].append({
                    "task_id": task.task_id,
                    "title": task.title,
                    "category": task.category
                })
        
        return {
            "npcs": list(npcs.values()),
            "total": len(npcs)
        }
    except Exception as e:
        logger.error(f"获取NPC列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取NPC列表失败")

@app.get("/api/npcs/{npc_id}")
async def get_npc(npc_id: str):
    """获取指定NPC详情"""
    try:
        # 查找与该NPC相关的所有任务
        tasks = data_loader.get_all_tasks()
        npc_tasks = [task for task in tasks if task.npc_id == npc_id]
        
        if not npc_tasks:
            raise HTTPException(status_code=404, detail="NPC不存在")
        
        # 使用第一个任务的位置信息作为NPC位置
        first_task = npc_tasks[0]
        
        return {
            "npc": {
                "npc_id": npc_id,
                "name": f"NPC-{npc_id}",
                "location": {
                    "name": first_task.location_name,
                    "lat": first_task.location_lat,
                    "lng": first_task.location_lng
                },
                "description": f"负责{len(npc_tasks)}个任务的校园向导",
                "associated_tasks": [
                    {
                        "task_id": task.task_id,
                        "title": task.title,
                        "category": task.category,
                        "difficulty": task.difficulty,
                        "points": task.points
                    }
                    for task in npc_tasks
                ]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取NPC详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取NPC详情失败")

@app.get("/api/stats")
async def get_stats():
    """获取数据统计信息"""
    try:
        stats = data_loader.get_load_stats()
        validation_results = data_loader.get_validation_results()
        
        return {
            "load_stats": stats,
            "validation_summary": {
                "total_issues": len(validation_results),
                "errors": len([r for r in validation_results if r.level.value == "error"]),
                "warnings": len([r for r in validation_results if r.level.value == "warning"]),
                "info": len([r for r in validation_results if r.level.value == "info"])
            },
            "data_counts": {
                "tasks": len(data_loader.get_all_tasks()),
                "knowledge": len(data_loader.get_all_knowledge())
            }
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取统计信息失败")

# 调试接口
@app.get("/debug/dump")
async def debug_dump():
    """导出内存数据快照 (调试接口)"""
    try:
        snapshot = data_loader.get_memory_snapshot()
        return snapshot
    except Exception as e:
        logger.error(f"导出内存快照失败: {str(e)}")
        raise HTTPException(status_code=500, detail="导出内存快照失败")

@app.get("/debug/validation")
async def debug_validation():
    """获取详细校验结果 (调试接口)"""
    try:
        validation_results = data_loader.get_validation_results()
        return {
            "validation_results": [
                {
                    "level": result.level.value,
                    "field": result.field,
                    "message": result.message,
                    "value": result.value,
                    "record_id": result.record_id
                }
                for result in validation_results
            ],
            "summary": {
                "total": len(validation_results),
                "errors": len([r for r in validation_results if r.level.value == "error"]),
                "warnings": len([r for r in validation_results if r.level.value == "warning"]),
                "info": len([r for r in validation_results if r.level.value == "info"])
            }
        }
    except Exception as e:
        logger.error(f"获取校验结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取校验结果失败")

@app.post("/debug/reload")
async def debug_reload():
    """重新加载数据 (调试接口)"""
    try:
        logger.info("手动重新加载数据")
        success = data_loader.load_all_data()
        if success:
            return {"message": "数据重新加载成功", "success": True}
        else:
            return {"message": "数据重新加载失败", "success": False}
    except Exception as e:
        logger.error(f"重新加载数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail="重新加载数据失败")


@app.get("/api/middleware/stats")
async def get_middleware_stats():
    """获取中间件统计信息"""
    try:
        stats = get_middleware_stats()
        return {
            "middleware_stats": stats,
            "config": {
                "timeout": {
                    "request_timeout": app_config.timeout.request_timeout,
                    "llm_timeout": app_config.timeout.llm_timeout
                },
                "retry": {
                    "max_retries": app_config.retry.max_retries,
                    "base_delay": app_config.retry.base_delay,
                    "max_delay": app_config.retry.max_delay
                },
                "rate_limit": {
                    "enabled": app_config.rate_limit.enabled,
                    "calls": app_config.rate_limit.calls,
                    "period": app_config.rate_limit.period
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取中间件统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取中间件统计失败")


@app.get("/api/performance/metrics")
async def get_performance_metrics():
    """获取性能指标"""
    try:
        # 这里可以集成更详细的性能监控
        return {
            "performance": {
                "p95_target": app_config.performance.p95_target,
                "slow_request_threshold": app_config.performance.slow_request_threshold,
                "enable_metrics": app_config.performance.enable_metrics
            },
            "uptime": time.time() - app_start_time,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取性能指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取性能指标失败")


@app.post("/api/test/timeout")
async def test_timeout():
    """测试超时处理 (测试接口)"""
    try:
        # 模拟长时间处理
        await asyncio.sleep(35)  # 超过默认超时时间
        return {"message": "不应该看到这个响应"}
    except Exception as e:
        logger.error(f"超时测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail="超时测试失败")


@app.post("/api/test/retry")
async def test_retry():
    """测试重试机制 (测试接口)"""
    try:
        # 使用包含"timeout"的查询来触发模拟超时
        task_info = {
            'task_id': 'TEST_TIMEOUT',
            'title': '超时测试任务',
            'description': '用于测试超时和重试机制',
            'category': 'test',
            'location_name': '测试地点',
            'location_lat': 22.0,
            'location_lng': 114.0
        }
        
        result = await process_npc_chat('TEST_TIMEOUT', 'timeout test question', task_info)
        
        return {
            "message": "重试测试完成",
            "result": {
                "answer": result.answer,
                "uncertain_reason": result.uncertain_reason
            }
        }
    except Exception as e:
        logger.error(f"重试测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail="重试测试失败")


@app.post("/tasks/search", response_model=SearchResponse, summary="Search Tasks", description="使用 BM25 算法搜索任务")
async def search_tasks_endpoint(request: SearchRequest):
    """搜索任务"""
    try:
        # 执行搜索
        top_n = request.top_n if request.top_n is not None else 10
        results = search_tasks(request.query, top_n)
        
        # 转换为响应格式
        search_results = [
            SearchResult(
                task_id=result['task_id'],
                title=result['title'],
                score=result['score'],
                lat=result['lat'],
                lng=result['lng']
            )
            for result in results
        ]
        
        # 构建元数据
        meta = {
            "query": request.query,
            "total_results": len(search_results),
            "top_n": request.top_n,
            "algorithm": "BM25",
            "search_time": "< 100ms"
        }
        
        return SearchResponse(data=search_results, meta=meta)
        
    except Exception as e:
        logger.error(f"搜索任务失败: {e}")
        raise HTTPException(status_code=500, detail="搜索任务失败")


@app.post("/npc/{task_id}/chat", response_model=ChatResponse, summary="NPC Chat", description="与任务 NPC 进行对话")
async def npc_chat(task_id: str, request: ChatRequest):
    """NPC 聊天端点"""
    try:
        # 检查任务是否存在
        task = data_loader.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 构建任务信息
        task_info = {
            'task_id': task.task_id,
            'title': task.title,
            'description': task.description,
            'category': task.category,
            'location_name': task.location_name,
            'location_lat': task.location_lat,
            'location_lng': task.location_lng
        }
        
        # 异步处理聊天请求
        rag_result = await process_npc_chat(task_id, request.question, task_info)
        
        # 构建响应
        citations = [
            Citation(
                source=citation['source'],
                content=citation['content'],
                score=citation['score']
            )
            for citation in rag_result.citations
        ]
        
        map_anchor = MapAnchor(
            lat=rag_result.map_anchor['lat'],
            lng=rag_result.map_anchor['lng']
        )
        
        suggestions = None
        if rag_result.suggestions:
            suggestions = [
                Suggestion(
                    type=suggestion['type'],
                    title=suggestion['title'],
                    description=suggestion['description']
                )
                for suggestion in rag_result.suggestions
            ]
        
        return ChatResponse(
            answer=rag_result.answer,
            citations=citations,
            map_anchor=map_anchor,
            suggestions=suggestions,
            uncertain_reason=rag_result.uncertain_reason
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"NPC 聊天失败: {e}")
        raise HTTPException(status_code=500, detail="NPC 聊天失败")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)