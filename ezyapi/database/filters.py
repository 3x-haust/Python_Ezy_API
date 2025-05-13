"""
필터 클래스 모듈

이 모듈은 데이터베이스 쿼리에 사용되는 다양한 필터 클래스들을 제공합니다.
이 필터 클래스들은 데이터베이스 쿼리를 더 쉽게 작성할 수 있도록 도와줍니다.
"""

from typing import Any, List

class Not:
    """
    '같지 않음' 필터를 생성합니다.
    
    Attributes:
        value (Any): 비교할 값
    """
    def __init__(self, value: Any):
        self.value = value

class LessThan:
    """
    '미만' 필터를 생성합니다.
    
    Attributes:
        value (Any): 비교할 값
    """
    def __init__(self, value: Any):
        self.value = value

class LessThanOrEqual:
    """
    '이하' 필터를 생성합니다.
    
    Attributes:
        value (Any): 비교할 값
    """
    def __init__(self, value: Any):
        self.value = value

class MoreThan:
    """
    '초과' 필터를 생성합니다.
    
    Attributes:
        value (Any): 비교할 값
    """
    def __init__(self, value: Any):
        self.value = value

class MoreThanOrEqual:
    """
    '이상' 필터를 생성합니다.
    
    Attributes:
        value (Any): 비교할 값
    """
    def __init__(self, value: Any):
        self.value = value

class Equal:
    """
    '같음' 필터를 생성합니다.
    
    Attributes:
        value (Any): 비교할 값
    """
    def __init__(self, value: Any):
        self.value = value

class Like:
    """
    'LIKE' 패턴 검색 필터를 생성합니다.
    
    Attributes:
        value (str): 검색할 패턴 문자열
    """
    def __init__(self, value: str):
        self.value = value

class ILike:
    """
    'ILIKE' 대소문자 구분 없이 패턴 검색 필터를 생성합니다.
    
    Attributes:
        value (str): 검색할 패턴 문자열
    """
    def __init__(self, value: str):
        self.value = value

class Between:
    """
    두 값 사이 범위 필터를 생성합니다.
    
    Attributes:
        min (Any): 최소값
        max (Any): 최대값
    """
    def __init__(self, min: Any, max: Any):
        self.min = min
        self.max = max

class In:
    """
    값의 리스트 중 하나와 일치하는 필터를 생성합니다.
    
    Attributes:
        values (List[Any]): 일치 여부를 확인할 값의 리스트
    """
    def __init__(self, values: List[Any]):
        self.values = values

class IsNull:
    """
    NULL 값 검사 필터를 생성합니다.
    """
    def __init__(self):
        pass