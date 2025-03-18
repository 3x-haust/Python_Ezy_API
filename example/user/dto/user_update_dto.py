from typing import Optional
from pydantic import BaseModel


class UserUpdateDTO(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None