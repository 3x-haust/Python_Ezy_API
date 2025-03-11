from typing import Optional

class UserEntity:
    def __init__(self, id: int, name: str, email: str, age: Optional[int] = None):
        self.id = id
        self.name = name
        self.email = email
        self.age = age
