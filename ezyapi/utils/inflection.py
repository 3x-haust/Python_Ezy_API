"""
문자열 변환 유틸리티 모듈

이 모듈은 엔티티 이름, 테이블 이름 등의 변환을 위한 유틸리티 함수들을 제공합니다.
"""

import inflect

p = inflect.engine()

def to_plural(name: str) -> str:
    """
    단수형 명사를 복수형으로 변환합니다.
    
    Args:
        name (str): 변환할 단수형 단어
        
    Returns:
        str: 복수형으로 변환된 단어
    """
    return p.plural(name.lower())

def to_singular(name: str) -> str:
    """
    복수형 명사를 단수형으로 변환합니다.
    
    Args:
        name (str): 변환할 복수형 단어
        
    Returns:
        str: 단수형으로 변환된 단어 또는 이미 단수형인 경우 원래 단어
    """
    return p.singular_noun(name.lower()) or name.lower()

def get_table_name_from_entity(entity_class) -> str:
    """
    엔티티 클래스로부터 데이터베이스 테이블 이름을 생성합니다.
    
    Args:
        entity_class: 엔티티 클래스
        
    Returns:
        str: 테이블 이름
    """
    name = entity_class.__name__
    if name.endswith("Entity"):
        name = name[:-6]
    return to_plural(name.lower())

def get_service_name(service_class) -> str:
    """
    서비스 클래스로부터 서비스 이름을 추출합니다.
    
    Args:
        service_class: 서비스 클래스
        
    Returns:
        str: 서비스 이름 (소문자)
    """
    name = service_class.__name__
    if name.endswith("Service"):
        name = name[:-7]
    return to_singular(name.lower())