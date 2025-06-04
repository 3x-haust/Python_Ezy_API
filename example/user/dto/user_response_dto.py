from typing import Optional
from ezyapi import EzyBaseDTO

class UserResponseDTO(EzyBaseDTO):
    id: int
    name: str
    email: str
    age: Optional[int] = None