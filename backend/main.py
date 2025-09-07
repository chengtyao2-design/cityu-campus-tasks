from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = FastAPI(
    title="CityU Campus Tasks API",
    description="校园任务系统后端 API",
    version="1.0.0"
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
    """获取任务列表 (示例端点)"""
    return {
        "tasks": [
            {
                "id": 1,
                "title": "图书馆打卡",
                "description": "在图书馆完成学习任务",
                "location": {"lat": 22.3364, "lng": 114.2654},
                "status": "active"
            },
            {
                "id": 2,
                "title": "食堂用餐",
                "description": "体验校园美食",
                "location": {"lat": 22.3370, "lng": 114.2660},
                "status": "pending"
            }
        ]
    }

@app.get("/api/npcs")
async def get_npcs():
    """获取 NPC 列表 (示例端点)"""
    return {
        "npcs": [
            {
                "id": 1,
                "name": "图书管理员小李",
                "type": "librarian",
                "location": {"lat": 22.3364, "lng": 114.2654},
                "available": True
            },
            {
                "id": 2,
                "name": "食堂阿姨",
                "type": "cafeteria_staff",
                "location": {"lat": 22.3370, "lng": 114.2660},
                "available": True
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)