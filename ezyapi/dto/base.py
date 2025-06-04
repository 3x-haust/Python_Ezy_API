"""
Ezy DTO 기본 클래스 모듈

이 모듈은 API DTO의 기본이 되는 클래스를 제공합니다.
"""

from pydantic import BaseModel, ConfigDict

class EzyBaseDTO(BaseModel):
    """
    모든 Ezy API DTO의 기본 클래스입니다.
    
    이 클래스는 pydantic BaseModel을 상속받아 추가 필드를 자동으로 금지합니다.
    """
    
    model_config = ConfigDict(
        extra='forbid',
        alias_generator=None,
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True
    )
