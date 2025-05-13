"""
라우트 데코레이터 모듈

이 모듈은 API 엔드포인트를 정의하는 데 사용되는 데코레이터를 제공합니다.
"""

from functools import wraps
from typing import Callable

def route(method: str, path: str, **kwargs):
    """
    API 엔드포인트 경로와 HTTP 메소드를 수동으로 설정하기 위한 데코레이터
    
    이 데코레이터는 서비스 메소드의 자동 라우팅 규칙을 오버라이드하여
    사용자 정의 URL 경로와 HTTP 메소드를 설정할 수 있게 해줍니다.
    
    Args:
        method (str): HTTP 메소드 ('get', 'post', 'put', 'delete', 'patch' 등)
        path (str): API 엔드포인트 URL 경로
        **kwargs: FastAPI 라우트 설정을 위한 추가 키워드 인자 (설명, 태그 등)
        
    Returns:
        Callable: 데코레이터 함수
        
    Example:
        ```python
        @route('get', '/custom-path/{id}', description='사용자 정의 경로')
        async def get_item_by_id(self, id: int):
            return {"id": id}
        ```
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        wrapper.__route_info__ = {
            'method': method.lower(),
            'path': path,
            'extra_kwargs': kwargs
        }
        return wrapper
    return decorator