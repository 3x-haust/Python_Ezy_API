from typing import Optional
from ezyapi import EzyBaseDTO

class UserCreateDTO(EzyBaseDTO):
    name: str
    email: str
    age: Optional[int] = None