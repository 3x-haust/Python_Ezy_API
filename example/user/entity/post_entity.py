from ezyapi.database import EzyEntityBase
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_entity import UserEntity

class PostEntity(EzyEntityBase):
    def __init__(self, id: int = None, title: str = "", content: str = "", user_id: int = None):
        self.id = id
        self.title = title
        self.content = content
        self.user_id = user_id
        
    user: 'UserEntity' = None
