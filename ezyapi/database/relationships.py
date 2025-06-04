from typing import TypeVar, Type, List, Any
from functools import wraps

T = TypeVar('T')

class RelationshipMeta:
    def __init__(self, relation_type: str, target_entity: Type, foreign_key: str = None, mapped_by: str = None):
        self.relation_type = relation_type
        self.target_entity = target_entity
        self.foreign_key = foreign_key
        self.mapped_by = mapped_by

def OneToMany(target_entity: Type[T], mapped_by: str):
    def decorator(cls):
        if not hasattr(cls, '_relationships'):
            cls._relationships = {}
        
        for name, value in cls.__dict__.items():
            if hasattr(value, '__annotations__') and 'List[' in str(value.__annotations__):
                cls._relationships[name] = RelationshipMeta('one_to_many', target_entity, mapped_by=mapped_by)
        
        return cls
    return decorator

def ManyToOne(target_entity: Type[T], foreign_key: str):
    def decorator(cls):
        if not hasattr(cls, '_relationships'):
            cls._relationships = {}
            
        for name, value in cls.__dict__.items():
            if hasattr(value, '__annotations__') and target_entity.__name__ in str(value.__annotations__):
                cls._relationships[name] = RelationshipMeta('many_to_one', target_entity, foreign_key=foreign_key)
        
        return cls
    return decorator
