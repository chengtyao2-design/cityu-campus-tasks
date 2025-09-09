"""
全局中间件模块
包含错误处理、速率限制、超时控制等功能
"""
import time
import asyncio
import logging
from typing import Dict, Optional, Callable, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class GlobalErrorHandler(BaseHTTPMiddleware):
    """全局错误处理中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.error_counts = defaultdict(int)
        self.last_reset = time.time()
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # 记录请求时间
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except HTTPException as e:
            # HTTP异常直接返回
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": {
                        "code": e.status_code,
                        "message": e.detail,
                        "type": "http_exception",
                        "timestamp": datetime.now().isoformat()
                    }
                }
            )
            
        except asyncio.TimeoutError:
            # 超时错误
            self._increment_error_count("timeout")
            logger.error(f"Request timeout: {request.url}")
            return JSONResponse(
                status_code=408,
                content={
                    "error": {
                        "code": 408,
                        "message": "Request timeout",
                        "type": "timeout_error",
                        "timestamp": datetime.now().isoformat()
                    }
                }
            )
            
        except Exception as e:
            # 其他未捕获的异常
            self._increment_error_count("internal")
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": 500,
                        "message": "Internal server error",
                        "type": "internal_error",
                        "timestamp": datetime.now().isoformat(),
                        "request_id": getattr(request.state, 'request_id', None)
                    }
                }
            )
    
    def _increment_error_count(self, error_type: str):
        """增加错误计数"""
        current_time = time.time()
        
        # 每小时重置计数器
        if current_time - self.last_reset > 3600:
            self.error_counts.clear()
            self.last_reset = current_time
            
        self.error_counts[error_type] += 1
    
    def get_error_stats(self) -> Dict[str, int]:
        """获取错误统计"""
        return dict(self.error_counts)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """简单的速率限制中间件"""
    
    def __init__(
        self, 
        app: ASGIApp, 
        calls: int = 100, 
        period: int = 60,
        per_ip: bool = True
    ):
        super().__init__(app)
        self.calls = calls  # 允许的调用次数
        self.period = period  # 时间窗口（秒）
        self.per_ip = per_ip  # 是否按IP限制
        self.requests = defaultdict(deque)  # 存储请求时间戳
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 获取客户端标识
        if self.per_ip:
            client_id = self._get_client_ip(request)
        else:
            client_id = "global"
        
        current_time = time.time()
        
        # 清理过期的请求记录
        self._cleanup_old_requests(client_id, current_time)
        
        # 检查是否超过限制
        if len(self.requests[client_id]) >= self.calls:
            logger.warning(f"Rate limit exceeded for {client_id}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": 429,
                        "message": "Too many requests",
                        "type": "rate_limit_exceeded",
                        "retry_after": self.period,
                        "timestamp": datetime.now().isoformat()
                    }
                },
                headers={"Retry-After": str(self.period)}
            )
        
        # 记录当前请求
        self.requests[client_id].append(current_time)
        
        # 继续处理请求
        response = await call_next(request)
        
        # 添加速率限制头部
        remaining = max(0, self.calls - len(self.requests[client_id]))
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.period))
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 检查代理头部
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 使用客户端IP
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_requests(self, client_id: str, current_time: float):
        """清理过期的请求记录"""
        cutoff_time = current_time - self.period
        
        while (self.requests[client_id] and 
               self.requests[client_id][0] < cutoff_time):
            self.requests[client_id].popleft()
    
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """获取速率限制统计"""
        current_time = time.time()
        stats = {}
        
        for client_id, timestamps in self.requests.items():
            # 清理过期记录
            self._cleanup_old_requests(client_id, current_time)
            
            stats[client_id] = {
                "current_requests": len(timestamps),
                "limit": self.calls,
                "remaining": max(0, self.calls - len(timestamps)),
                "reset_time": current_time + self.period
            }
        
        return stats


class TimeoutMiddleware(BaseHTTPMiddleware):
    """请求超时中间件"""
    
    def __init__(self, app: ASGIApp, timeout: float = 30.0):
        super().__init__(app)
        self.timeout = timeout
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            # 设置请求超时
            response = await asyncio.wait_for(
                call_next(request), 
                timeout=self.timeout
            )
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"Request timeout after {self.timeout}s: {request.url}")
            raise asyncio.TimeoutError("Request timeout")


class LLMRetryHandler:
    """LLM服务重试处理器"""
    
    def __init__(
        self, 
        max_retries: int = 3, 
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        timeout: float = 30.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.timeout = timeout
        self.retry_counts = defaultdict(int)
        
    async def execute_with_retry(
        self, 
        func: Callable, 
        *args, 
        **kwargs
    ) -> Any:
        """执行函数并在失败时重试"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # 设置超时
                result = await asyncio.wait_for(
                    func(*args, **kwargs) if asyncio.iscoroutinefunction(func) 
                    else asyncio.create_task(asyncio.to_thread(func, *args, **kwargs)),
                    timeout=self.timeout
                )
                
                # 成功则重置重试计数
                func_name = getattr(func, '__name__', str(func))
                if func_name in self.retry_counts:
                    del self.retry_counts[func_name]
                
                return result
                
            except asyncio.TimeoutError as e:
                last_exception = e
                logger.warning(f"LLM timeout on attempt {attempt + 1}/{self.max_retries + 1}")
                
            except Exception as e:
                last_exception = e
                logger.warning(f"LLM error on attempt {attempt + 1}/{self.max_retries + 1}: {str(e)}")
            
            # 如果不是最后一次尝试，则等待后重试
            if attempt < self.max_retries:
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                logger.info(f"Retrying in {delay}s...")
                await asyncio.sleep(delay)
        
        # 记录重试失败
        func_name = getattr(func, '__name__', str(func))
        self.retry_counts[func_name] += 1
        
        # 所有重试都失败了
        logger.error(f"LLM operation failed after {self.max_retries + 1} attempts")
        raise last_exception
    
    def get_retry_stats(self) -> Dict[str, int]:
        """获取重试统计"""
        return dict(self.retry_counts)


# 全局实例
global_error_handler = None
rate_limit_middleware = None
timeout_middleware = None
llm_retry_handler = LLMRetryHandler()


def setup_middleware(app, config: Optional[Dict] = None):
    """设置中间件"""
    global global_error_handler, rate_limit_middleware, timeout_middleware
    
    if config is None:
        config = {}
    
    # 超时中间件
    timeout_config = config.get('timeout', {})
    timeout_middleware = TimeoutMiddleware(
        app, 
        timeout=timeout_config.get('request_timeout', 30.0)
    )
    
    # 速率限制中间件
    rate_limit_config = config.get('rate_limit', {})
    rate_limit_middleware = RateLimitMiddleware(
        app,
        calls=rate_limit_config.get('calls', 100),
        period=rate_limit_config.get('period', 60),
        per_ip=rate_limit_config.get('per_ip', True)
    )
    
    # 全局错误处理中间件
    global_error_handler = GlobalErrorHandler(app)
    
    return {
        'error_handler': global_error_handler,
        'rate_limiter': rate_limit_middleware,
        'timeout': timeout_middleware,
        'llm_retry': llm_retry_handler
    }


def get_middleware_stats() -> Dict[str, Any]:
    """获取所有中间件统计信息"""
    stats = {}
    
    if global_error_handler:
        stats['errors'] = global_error_handler.get_error_stats()
    
    if rate_limit_middleware:
        stats['rate_limits'] = rate_limit_middleware.get_rate_limit_stats()
    
    if llm_retry_handler:
        stats['llm_retries'] = llm_retry_handler.get_retry_stats()
    
    return stats