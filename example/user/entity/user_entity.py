from ezyapi.database import EzyEntityBase
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .post_entity import PostEntity

class UserEntity(EzyEntityBase):
    def __init__(self, id: int = None, name: str = "", email: str = "", age: int = None):
        self.id = id
        self.name = name
        self.email = email
        self.age = age
        
    posts: List['PostEntity'] = []
