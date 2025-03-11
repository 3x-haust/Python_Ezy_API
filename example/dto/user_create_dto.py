from typing import Optional
from pydantic import BaseModel

class UserCreateDTO(BaseModel):
    name: str
    email: str
    age: Optional[int] = None