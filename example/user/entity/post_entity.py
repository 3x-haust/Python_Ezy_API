from example.user.entity.user_entity import UserEntity
from ezyapi.database import EzyEntityBase
from typing import TYPE_CHECKING, List

from ezyapi.database.entity import ManyToOne

class PostEntity(EzyEntityBase):
    def __init__(self, id: int = None, title: str = "", content: str = "", user_id: int = None):
        self.id = id
        self.title = title
        self.content = content
        self.user_id = user_id
        
    user: UserEntity = ManyToOne('UserEntity', 'user_id')


