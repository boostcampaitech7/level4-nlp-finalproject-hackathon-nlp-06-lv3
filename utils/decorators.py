import time
from functools import wraps
from typing import Callable

import openai


def retry_with_exponential_backoff(max_retry: int = 9, base_wait: int = 1):
    """
    지수 백오프 방식으로 재시도하는 데코레이터
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            wait_time = base_wait
            for attempt in range(max_retry):
                try:
                    return func(*args, **kwargs)
                except openai.RateLimitError as e:
                    print(f"[RateLimitError] 재시도 {attempt+1}/{max_retry}회: {e}")
                    if attempt < max_retry - 1:
                        time.sleep(wait_time)
                        wait_time *= 2
                    else:
                        raise e  # 최대 재시도 횟수 초과 시 에러 발생

        return wrapper

    return decorator
