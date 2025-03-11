from ezyapi.database import EzyEntityBase

class UserEntity(EzyEntityBase):
    def __init__(self, id: int = None, name: str = "", email: str = "", age: int = None):
        self.id = id
        self.name = name
        self.email = email
        self.age = age
