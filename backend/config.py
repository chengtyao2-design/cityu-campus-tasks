"""
应用配置模块
管理中间件、超时、重试等配置
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class TimeoutConfig:
    """超时配置"""
    request_timeout: float = 30.0  # 请求超时时间（秒）
    llm_timeout: float = 25.0      # LLM调用超时时间（秒）
    
    @classmethod
    def from_env(cls) -> 'TimeoutConfig':
        return cls(
            request_timeout=float(os.getenv('REQUEST_TIMEOUT', 30.0)),
            llm_timeout=float(os.getenv('LLM_TIMEOUT', 25.0))
        )


@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3           # 最大重试次数
    base_delay: float = 1.0        # 基础延迟时间（秒）
    max_delay: float = 10.0        # 最大延迟时间（秒）
    exponential_backoff: bool = True  # 是否使用指数退避
    
    @classmethod
    def from_env(cls) -> 'RetryConfig':
        return cls(
            max_retries=int(os.getenv('MAX_RETRIES', 3)),
            base_delay=float(os.getenv('BASE_DELAY', 1.0)),
            max_delay=float(os.getenv('MAX_DELAY', 10.0)),
            exponential_backoff=os.getenv('EXPONENTIAL_BACKOFF', 'true').lower() == 'true'
        )


@dataclass
class RateLimitConfig:
    """速率限制配置"""
    enabled: bool = True           # 是否启用速率限制
    calls: int = 100              # 允许的调用次数
    period: int = 60              # 时间窗口（秒）
    per_ip: bool = True           # 是否按IP限制
    
    # 特殊端点的速率限制
    chat_calls: int = 20          # 聊天端点调用次数
    chat_period: int = 60         # 聊天端点时间窗口
    search_calls: int = 50        # 搜索端点调用次数
    search_period: int = 60       # 搜索端点时间窗口
    
    @classmethod
    def from_env(cls) -> 'RateLimitConfig':
        return cls(
            enabled=os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true',
            calls=int(os.getenv('RATE_LIMIT_CALLS', 100)),
            period=int(os.getenv('RATE_LIMIT_PERIOD', 60)),
            per_ip=os.getenv('RATE_LIMIT_PER_IP', 'true').lower() == 'true',
            chat_calls=int(os.getenv('CHAT_RATE_LIMIT_CALLS', 20)),
            chat_period=int(os.getenv('CHAT_RATE_LIMIT_PERIOD', 60)),
            search_calls=int(os.getenv('SEARCH_RATE_LIMIT_CALLS', 50)),
            search_period=int(os.getenv('SEARCH_RATE_LIMIT_PERIOD', 60))
        )


@dataclass
class ErrorHandlingConfig:
    """错误处理配置"""
    log_errors: bool = True        # 是否记录错误日志
    include_traceback: bool = False # 是否在响应中包含堆栈跟踪（仅开发环境）
    error_rate_threshold: int = 100 # 错误率阈值（每小时）
    
    @classmethod
    def from_env(cls) -> 'ErrorHandlingConfig':
        return cls(
            log_errors=os.getenv('LOG_ERRORS', 'true').lower() == 'true',
            include_traceback=os.getenv('INCLUDE_TRACEBACK', 'false').lower() == 'true',
            error_rate_threshold=int(os.getenv('ERROR_RATE_THRESHOLD', 100))
        )


@dataclass
class PerformanceConfig:
    """性能配置"""
    enable_metrics: bool = True    # 是否启用性能指标
    slow_request_threshold: float = 2.0  # 慢请求阈值（秒）
    p95_target: float = 2.5       # P95响应时间目标（秒）
    
    @classmethod
    def from_env(cls) -> 'PerformanceConfig':
        return cls(
            enable_metrics=os.getenv('ENABLE_METRICS', 'true').lower() == 'true',
            slow_request_threshold=float(os.getenv('SLOW_REQUEST_THRESHOLD', 2.0)),
            p95_target=float(os.getenv('P95_TARGET', 2.5))
        )


@dataclass
class AppConfig:
    """应用总配置"""
    timeout: TimeoutConfig
    retry: RetryConfig
    rate_limit: RateLimitConfig
    error_handling: ErrorHandlingConfig
    performance: PerformanceConfig
    
    # 环境配置
    environment: str = "development"
    debug: bool = False
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        return cls(
            timeout=TimeoutConfig.from_env(),
            retry=RetryConfig.from_env(),
            rate_limit=RateLimitConfig.from_env(),
            error_handling=ErrorHandlingConfig.from_env(),
            performance=PerformanceConfig.from_env(),
            environment=os.getenv('ENVIRONMENT', 'development'),
            debug=os.getenv('DEBUG', 'false').lower() == 'true'
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'timeout': {
                'request_timeout': self.timeout.request_timeout,
                'llm_timeout': self.timeout.llm_timeout
            },
            'retry': {
                'max_retries': self.retry.max_retries,
                'base_delay': self.retry.base_delay,
                'max_delay': self.retry.max_delay,
                'exponential_backoff': self.retry.exponential_backoff
            },
            'rate_limit': {
                'enabled': self.rate_limit.enabled,
                'calls': self.rate_limit.calls,
                'period': self.rate_limit.period,
                'per_ip': self.rate_limit.per_ip,
                'chat_calls': self.rate_limit.chat_calls,
                'chat_period': self.rate_limit.chat_period,
                'search_calls': self.rate_limit.search_calls,
                'search_period': self.rate_limit.search_period
            },
            'error_handling': {
                'log_errors': self.error_handling.log_errors,
                'include_traceback': self.error_handling.include_traceback,
                'error_rate_threshold': self.error_handling.error_rate_threshold
            },
            'performance': {
                'enable_metrics': self.performance.enable_metrics,
                'slow_request_threshold': self.performance.slow_request_threshold,
                'p95_target': self.performance.p95_target
            },
            'environment': self.environment,
            'debug': self.debug
        }


# 全局配置实例
app_config = AppConfig.from_env()


def get_middleware_config() -> Dict[str, Any]:
    """获取中间件配置"""
    return {
        'timeout': {
            'request_timeout': app_config.timeout.request_timeout
        },
        'rate_limit': {
            'calls': app_config.rate_limit.calls,
            'period': app_config.rate_limit.period,
            'per_ip': app_config.rate_limit.per_ip
        },
        'retry': {
            'max_retries': app_config.retry.max_retries,
            'base_delay': app_config.retry.base_delay,
            'max_delay': app_config.retry.max_delay,
            'timeout': app_config.timeout.llm_timeout
        }
    }


def get_endpoint_rate_limits() -> Dict[str, Dict[str, int]]:
    """获取端点特定的速率限制配置"""
    return {
        '/npc/*/chat': {
            'calls': app_config.rate_limit.chat_calls,
            'period': app_config.rate_limit.chat_period
        },
        '/tasks/search': {
            'calls': app_config.rate_limit.search_calls,
            'period': app_config.rate_limit.search_period
        }
    }


def is_production() -> bool:
    """检查是否为生产环境"""
    return app_config.environment.lower() == 'production'


def is_development() -> bool:
    """检查是否为开发环境"""
    return app_config.environment.lower() == 'development'