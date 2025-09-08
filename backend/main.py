from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# 导入数据加载器
from data_loader import data_loader, initialize_data_loader

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.get("/")
async def root():
    """根路径"""
    return {"message": "CityU Campus Tasks API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "message": "API is running"}

@app.get("/api/tasks")
async def get_tasks():
    """获取任务列表"""
    try:
        tasks = data_loader.get_all_tasks()
        return {
            "tasks": [
                {
                    "task_id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "category": task.category,
                    "location": {
                        "name": task.location_name,
                        "lat": task.location_lat,
                        "lng": task.location_lng
                    },
                    "estimated_duration": task.estimated_duration,
                    "difficulty": task.difficulty,
                    "points": task.points,
                    "course_code": task.course_code,
                    "npc_id": task.npc_id,
                    "status": task.status
                }
                for task in tasks
            ],
            "total": len(tasks)
        }
    except Exception as e:
        logger.error(f"获取任务列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取任务列表失败")

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """获取指定任务详情"""
    try:
        task = data_loader.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        knowledge = data_loader.get_task_knowledge(task_id)
        
        return {
            "task": {
                "task_id": task.task_id,
                "title": task.title,
                "description": task.description,
                "category": task.category,
                "location": {
                    "name": task.location_name,
                    "lat": task.location_lat,
                    "lng": task.location_lng
                },
                "estimated_duration": task.estimated_duration,
                "difficulty": task.difficulty,
                "points": task.points,
                "prerequisites": task.prerequisites,
                "course_code": task.course_code,
                "npc_id": task.npc_id,
                "status": task.status,
                "created_at": task.created_at,
                "updated_at": task.updated_at
            },
            "knowledge": {
                "knowledge_type": knowledge.knowledge_type,
                "title": knowledge.title,
                "content": knowledge.content,
                "tags": knowledge.tags,
                "difficulty_level": knowledge.difficulty_level,
                "estimated_read_time": knowledge.estimated_read_time,
                "prerequisites": knowledge.prerequisites,
                "related_tasks": knowledge.related_tasks
            } if knowledge else None
        }
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)