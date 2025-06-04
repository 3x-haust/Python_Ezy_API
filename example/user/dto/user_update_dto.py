from typing import Optional
from ezyapi import EzyBaseDTO


class UserUpdateDTO(EzyBaseDTO):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None