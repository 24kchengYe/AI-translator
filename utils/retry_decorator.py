"""
重试装饰器
提供自动重试功能，用于处理网络请求失败
"""
import time
import functools
from typing import Callable, Any
from config import config


def retry_with_backoff(max_retries: int = None, delay: int = None):
    """
    重试装饰器，支持指数退避

    Args:
        max_retries: 最大重试次数，默认从config读取
        delay: 初始延迟秒数，默认从config读取
    """
    if max_retries is None:
        max_retries = config.MAX_RETRIES
    if delay is None:
        delay = config.RETRY_DELAY

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (1.5 ** attempt)
                        print(f"重试 {attempt + 1}/{max_retries}，等待 {wait_time:.1f}秒...")
                        time.sleep(wait_time)
                    else:
                        print(f"达到最大重试次数 {max_retries}")

            # 如果所有重试都失败，抛出最后一个异常
            raise last_exception

        return wrapper
    return decorator
