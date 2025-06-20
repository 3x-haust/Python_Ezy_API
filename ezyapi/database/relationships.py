from typing import TypeVar, Type, List, Any, get_type_hints, get_origin, get_args, Annotated

T = TypeVar('T')

class RelationshipMeta:
    """
    관계 메타데이터 클래스
    
    데이터베이스 엔티티 간의 관계 정보를 저장합니다.
    """
    def __init__(self, relation_type: str, target_entity: Type, foreign_key: str = None, mapped_by: str = None):
        self.relation_type = relation_type
        self.target_entity = target_entity
        self.foreign_key = foreign_key
        self.mapped_by = mapped_by
    
    def __repr__(self):
        return f"RelationshipMeta(type={self.relation_type}, target={self.target_entity.__name__})"

def OneToMany(target_entity: Type[T], mapped_by: str):
    """
    일대다 관계 메타데이터 생성자
    
    Args:
        target_entity: 대상 엔티티 클래스
        mapped_by: 대상 엔티티에서 이 엔티티를 참조하는 필드명
    
    Usage:
        class User(EzyEntityBase):
            orders: Annotated[List['Order'], OneToMany(OrderEntity, mapped_by='user_id')] = None
    """
    return RelationshipMeta('one_to_many', target_entity, mapped_by=mapped_by)

def ManyToOne(target_entity: Type[T], foreign_key: str = None):
    """
    다대일 관계 메타데이터 생성자
    
    Args:
        target_entity: 대상 엔티티 클래스
        foreign_key: 외래키 필드명 (생략시 자동 생성)
    
    Usage:
        class Order(EzyEntityBase):
            user: Annotated['User', ManyToOne(UserEntity, foreign_key='user_id')] = None
            user_id: int = None
    """
    return RelationshipMeta('many_to_one', target_entity, foreign_key=foreign_key)

def get_relationship_metadata(entity_class: Type) -> dict:
    """
    엔티티 클래스에서 관계 메타데이터를 추출합니다.
    
    Args:
        entity_class: 엔티티 클래스
        
    Returns:
        dict: 필드명을 키로 하는 RelationshipMeta 딕셔너리
    """
    metadata = {}
    
    if hasattr(entity_class, '_relationship_metadata'):
        return entity_class._relationship_metadata
    
    try:
        type_hints = get_type_hints(entity_class, include_extras=True)
        
        for field_name, field_type in type_hints.items():
            if field_name.startswith('_'):
                continue
                
            if get_origin(field_type) is Annotated:
                args = get_args(field_type)
                for arg in args[1:]:
                    if isinstance(arg, RelationshipMeta):
                        metadata[field_name] = arg
                        break
    except Exception:
        pass
    
    entity_class._relationship_metadata = metadata
    return metadata
