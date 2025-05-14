"""
서비스 기본 클래스 모듈

이 모듈은 API 서비스의 기본 클래스를 제공합니다.
"""

from typing import Optional

class EzyService:
    """
    Ezy API 서비스의 기본 클래스입니다.
    
    모든 API 서비스는 이 클래스를 상속받아 구현합니다.
    서비스는 비즈니스 로직을 포함하고 API 엔드포인트에 매핑됩니다.
    
    Attributes:
        repository (Optional[EzyRepository]): 이 서비스에서 사용할 레포지토리. 기본값은 None입니다.
    """
    def __init__(self, repository=None):
        """
        EzyService 클래스의 생성자
        
        Args:
            repository (Optional[EzyRepository]): 이 서비스에 연결할 레포지토리 인스턴스.
        """
        self.repository = repository