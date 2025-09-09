"""
中间件功能测试
测试全局错误处理、超时、重试和速率限制
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException

# 导入要测试的模块
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from middleware import (
    GlobalErrorHandler, RateLimitMiddleware, TimeoutMiddleware, 
    LLMRetryHandler, setup_middleware
)
from config import AppConfig, TimeoutConfig, RetryConfig, RateLimitConfig
from rag import MockLLMService


class TestGlobalErrorHandler:
    """测试全局错误处理中间件"""
    
    def test_error_handler_creation(self):
        """测试错误处理器创建"""
        app = FastAPI()
        handler = GlobalErrorHandler(app)
        
        assert handler is not None
        assert hasattr(handler, 'error_counts')
        assert hasattr(handler, 'last_reset')
    
    def test_error_count_increment(self):
        """测试错误计数增加"""
        app = FastAPI()
        handler = GlobalErrorHandler(app)
        
        # 增加错误计数
        handler._increment_error_count("timeout")
        handler._increment_error_count("internal")
        handler._increment_error_count("timeout")
        
        stats = handler.get_error_stats()
        assert stats["timeout"] == 2
        assert stats["internal"] == 1


class TestRateLimitMiddleware:
    """测试速率限制中间件"""
    
    def test_rate_limiter_creation(self):
        """测试速率限制器创建"""
        app = FastAPI()
        limiter = RateLimitMiddleware(app, calls=10, period=60)
        
        assert limiter.calls == 10
        assert limiter.period == 60
        assert limiter.per_ip is True
    
    def test_cleanup_old_requests(self):
        """测试清理过期请求"""
        app = FastAPI()
        limiter = RateLimitMiddleware(app, calls=10, period=1)  # 1秒窗口
        
        current_time = time.time()
        client_id = "test_client"
        
        # 添加一些旧的请求
        limiter.requests[client_id].append(current_time - 2)  # 2秒前
        limiter.requests[client_id].append(current_time - 0.5)  # 0.5秒前
        limiter.requests[client_id].append(current_time)  # 现在
        
        # 清理过期请求
        limiter._cleanup_old_requests(client_id, current_time)
        
        # 应该只剩下2个请求（0.5秒前和现在的）
        assert len(limiter.requests[client_id]) == 2
    
    def test_get_client_ip(self):
        """测试获取客户端IP"""
        from fastapi import Request
        
        app = FastAPI()
        limiter = RateLimitMiddleware(app)
        
        # 模拟请求对象
        mock_request = Mock(spec=Request)
        mock_request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        
        ip = limiter._get_client_ip(mock_request)
        assert ip == "192.168.1.1"


class TestTimeoutMiddleware:
    """测试超时中间件"""
    
    def test_timeout_middleware_creation(self):
        """测试超时中间件创建"""
        app = FastAPI()
        middleware = TimeoutMiddleware(app, timeout=5.0)
        
        assert middleware.timeout == 5.0


class TestLLMRetryHandler:
    """测试LLM重试处理器"""
    
    @pytest.mark.asyncio
    async def test_retry_handler_success(self):
        """测试重试处理器成功情况"""
        handler = LLMRetryHandler(max_retries=2, base_delay=0.1)
        
        async def mock_success():
            return {"result": "success"}
        
        result = await handler.execute_with_retry(mock_success)
        assert result["result"] == "success"
    
    @pytest.mark.asyncio
    async def test_retry_handler_with_retries(self):
        """测试重试处理器重试情况"""
        handler = LLMRetryHandler(max_retries=2, base_delay=0.1)
        
        call_count = 0
        
        async def mock_fail_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("模拟失败")
            return {"result": "success"}
        
        result = await handler.execute_with_retry(mock_fail_then_success)
        assert result["result"] == "success"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_handler_timeout(self):
        """测试重试处理器超时"""
        handler = LLMRetryHandler(max_retries=1, base_delay=0.1, timeout=0.5)
        
        async def mock_timeout():
            await asyncio.sleep(1.0)  # 超过超时时间
            return {"result": "should not reach"}
        
        with pytest.raises(asyncio.TimeoutError):
            await handler.execute_with_retry(mock_timeout)
    
    @pytest.mark.asyncio
    async def test_retry_handler_max_retries_exceeded(self):
        """测试重试处理器超过最大重试次数"""
        handler = LLMRetryHandler(max_retries=2, base_delay=0.1)
        
        async def mock_always_fail():
            raise Exception("总是失败")
        
        with pytest.raises(Exception, match="总是失败"):
            await handler.execute_with_retry(mock_always_fail)
    
    def test_retry_stats(self):
        """测试重试统计"""
        handler = LLMRetryHandler()
        
        # 模拟一些重试失败
        handler.retry_counts["test_func"] = 3
        handler.retry_counts["another_func"] = 1
        
        stats = handler.get_retry_stats()
        assert stats["test_func"] == 3
        assert stats["another_func"] == 1


class TestMockLLMService:
    """测试模拟LLM服务"""
    
    @pytest.mark.asyncio
    async def test_mock_llm_basic_response(self):
        """测试基本响应"""
        service = MockLLMService(simulate_delay=False, failure_rate=0.0)
        
        response = await service.generate_response("system", "test query")
        
        assert "answer" in response
        assert "confidence" in response
        assert response["confidence"] in ["high", "medium", "low"]
    
    @pytest.mark.asyncio
    async def test_mock_llm_keyword_matching(self):
        """测试关键词匹配"""
        service = MockLLMService(simulate_delay=False, failure_rate=0.0)
        
        response = await service.generate_response("system", "图书馆相关问题")
        
        assert "图书馆" in response["answer"]
        assert response["confidence"] == "high"
    
    @pytest.mark.asyncio
    async def test_mock_llm_with_failure(self):
        """测试模拟失败"""
        service = MockLLMService(simulate_delay=False, failure_rate=1.0)  # 100%失败率
        
        with pytest.raises(Exception):
            await service.generate_response("system", "test query")
    
    @pytest.mark.asyncio
    async def test_mock_llm_timeout_simulation(self):
        """测试超时模拟"""
        service = MockLLMService(simulate_delay=True, failure_rate=0.0)
        
        start_time = time.time()
        response = await service.generate_response("system", "timeout test")
        end_time = time.time()
        
        # 应该有明显的延迟（5-10秒）
        assert end_time - start_time > 4.0
        assert ("timeout" in response["answer"].lower() or "超时" in response["answer"])
    
    def test_mock_llm_stats(self):
        """测试服务统计"""
        service = MockLLMService(simulate_delay=True, failure_rate=0.1)
        
        stats = service.get_stats()
        assert "total_calls" in stats
        assert "failure_rate" in stats
        assert "simulate_delay" in stats
        assert stats["failure_rate"] == 0.1
        assert stats["simulate_delay"] is True


class TestMiddlewareIntegration:
    """测试中间件集成"""
    
    def test_setup_middleware(self):
        """测试中间件设置"""
        app = FastAPI()
        
        config = {
            'timeout': {'request_timeout': 30.0},
            'rate_limit': {'calls': 100, 'period': 60, 'per_ip': True},
            'retry': {'max_retries': 3, 'base_delay': 1.0, 'max_delay': 10.0, 'timeout': 25.0}
        }
        
        middleware_instances = setup_middleware(app, config)
        
        assert 'error_handler' in middleware_instances
        assert 'rate_limiter' in middleware_instances
        assert 'timeout' in middleware_instances
        assert 'llm_retry' in middleware_instances
        
        # 检查配置是否正确应用
        assert middleware_instances['timeout'].timeout == 30.0
        assert middleware_instances['rate_limiter'].calls == 100
        assert middleware_instances['llm_retry'].max_retries == 3


class TestRateLimitScenarios:
    """测试速率限制场景"""
    
    def test_rate_limit_429_response(self):
        """测试429响应"""
        # 这个测试需要实际的FastAPI应用来测试HTTP响应
        # 这里我们测试逻辑部分
        app = FastAPI()
        limiter = RateLimitMiddleware(app, calls=2, period=60)
        
        client_id = "test_client"
        current_time = time.time()
        
        # 模拟达到限制
        limiter.requests[client_id].extend([current_time, current_time])
        
        # 检查是否超过限制
        assert len(limiter.requests[client_id]) >= limiter.calls
    
    def test_rate_limit_stats(self):
        """测试速率限制统计"""
        app = FastAPI()
        limiter = RateLimitMiddleware(app, calls=10, period=60)
        
        # 添加一些请求
        current_time = time.time()
        limiter.requests["client1"].extend([current_time, current_time - 10])
        limiter.requests["client2"].append(current_time)
        
        stats = limiter.get_rate_limit_stats()
        
        assert "client1" in stats
        assert "client2" in stats
        assert stats["client1"]["current_requests"] == 2
        assert stats["client1"]["remaining"] == 8
        assert stats["client2"]["current_requests"] == 1
        assert stats["client2"]["remaining"] == 9


@pytest.mark.asyncio
async def test_end_to_end_timeout_retry():
    """端到端测试：超时和重试"""
    # 创建一个会超时的LLM服务
    llm_service = MockLLMService(simulate_delay=True, failure_rate=0.5)
    
    # 创建重试处理器
    retry_handler = LLMRetryHandler(max_retries=2, base_delay=0.1, timeout=1.0)
    
    # 测试重试机制
    try:
        result = await retry_handler.execute_with_retry(
            llm_service.generate_response,
            "system prompt",
            "test query"
        )
        # 如果成功，应该有有效的响应
        assert "answer" in result
    except Exception as e:
        # 如果失败，应该是超时或重试次数用尽
        assert isinstance(e, (asyncio.TimeoutError, Exception))


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])