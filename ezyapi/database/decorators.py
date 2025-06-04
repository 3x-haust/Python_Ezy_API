"""
데이터베이스 컬럼 데코레이터 모듈

이 모듈은 엔티티 필드의 데이터베이스 컬럼 설정을 위한 타입 힌트 기반 데코레이터를 제공합니다.
"""

from typing import Any, Type, Annotated, get_type_hints, get_origin, get_args

class ColumnMeta:
    """컬럼 메타데이터 클래스"""
    def __init__(self, 
                 primary: bool = False, 
                 auto_increment: bool = None,
                 nullable: bool = True,
                 unique: bool = False,
                 default: Any = None,
                 column_type: str = None):
        self.primary = primary
        self.auto_increment = auto_increment if auto_increment is not None else primary
        self.nullable = nullable
        self.unique = unique
        self.default = default
        self.column_type = column_type
    
    def __repr__(self):
        return f"ColumnMeta(primary={self.primary}, auto_increment={self.auto_increment}, nullable={self.nullable})"

def Column(primary: bool = False,
           auto_increment: bool = None,
           nullable: bool = True,
           unique: bool = False,
           default: Any = None,
           column_type: str = None):
    """
    컬럼 설정 메타데이터 생성자
    
    Usage:
        class User(EzyEntityBase):
            name: Annotated[str, Column()] = ""
    """
    return ColumnMeta(
        primary=primary,
        auto_increment=auto_increment,
        nullable=nullable,
        unique=unique,
        default=default,
        column_type=column_type
    )

def PrimaryColumn(auto_increment: bool = False, 
                  column_type: str = None):
    """
    Primary Key 컬럼 메타데이터
    
    Usage:
        class User(EzyEntityBase):
            user_code: Annotated[str, PrimaryColumn(column_type="VARCHAR(50)")] = None
    """
    return Column(
        primary=True,
        auto_increment=auto_increment,
        nullable=False,
        column_type=column_type
    )

def PrimaryGeneratedColumn(column_type: str = "INTEGER"):
    """
    자동 생성되는 Primary Key 컬럼 메타데이터
    
    Usage:
        class User(EzyEntityBase):
            user_id: Annotated[int, PrimaryGeneratedColumn(column_type="BIGINT")] = None
    """
    return Column(
        primary=True,
        auto_increment=True,
        nullable=False,
        column_type=column_type
    )

def get_column_metadata(entity_class: Type) -> dict:
    """
    엔티티 클래스에서 컬럼 메타데이터를 추출합니다.
    
    Args:
        entity_class: 엔티티 클래스
        
    Returns:
        dict: 컬럼명을 키로 하는 ColumnMeta 딕셔너리
    """
    metadata = {}
    
    if hasattr(entity_class, '_column_metadata'):
        return entity_class._column_metadata
    
    try:
        type_hints = get_type_hints(entity_class, include_extras=True)
        
        for field_name, field_type in type_hints.items():
            if field_name.startswith('_'):
                continue
                
            if get_origin(field_type) is Annotated:
                args = get_args(field_type)
                for arg in args[1:]:
                    if isinstance(arg, ColumnMeta):
                        metadata[field_name] = arg
                        break
    except Exception:
        pass
    
    entity_class._column_metadata = metadata
    return metadata
