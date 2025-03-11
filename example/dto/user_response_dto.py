from typing import Optional
from pydantic import BaseModel

class UserResponseDTO(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None