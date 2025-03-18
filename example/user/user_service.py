from ezyapi.core import route
from fastapi import HTTPException
from typing import List, Optional

from user.dto.user_update_dto import UserUpdateDTO
from user.dto.user_response_dto import UserResponseDTO
from user.dto.user_create_dto import UserCreateDTO
from user.entity import UserEntity

from ezyapi import EzyService

class UserService(EzyService):
    @route('get', '/name/{name}', description="Get user by name")
    async def get_user_by_name(self, name: str) -> UserResponseDTO:
        user = await self.repository.find_one(where={"name": name})

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponseDTO(id=user.id, name=user.name, email=user.email, age=user.age)

    async def edit_user_by_id(self, id: int, data: UserUpdateDTO) -> UserResponseDTO:
        user = await self.repository.find_one(where={"id": id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if data.name is not None:
            user.name = data.name
        if data.email is not None:
            user.email = data.email
        if data.age is not None:
            user.age = data.age

        updated_user = await self.repository.save(user)

        return UserResponseDTO(
            id=updated_user.id, name=updated_user.name,
            email=updated_user.email, age=updated_user.age
        )

    
    async def get_user_by_id(self, id: int) -> UserResponseDTO:
        user = await self.repository.find_one(where={"id": id})

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
                
        return UserResponseDTO(id=user.id, name=user.name, email=user.email, age=user.age)
    
    async def list_users(self, name: Optional[str] = None, age: Optional[int] = None) -> List[UserResponseDTO]:
        filters = {}
        if age is not None:
            filters["age"] = age

        if name is not None:
            filters["name"] = name

        users = await self.repository.find(where=filters)
        return [
            UserResponseDTO(id=user.id, name=user.name, email=user.email, age=user.age)
            for user in users
        ]
    
    async def create_user(self, data: UserCreateDTO) -> UserResponseDTO:
        new_user = UserEntity(name=data.name, email=data.email, age=data.age)
        saved_user = await self.repository.save(new_user)
        
        return UserResponseDTO(id=saved_user.id, name=saved_user.name, 
                             email=saved_user.email, age=saved_user.age)
    
    async def update_user_by_id(self, id: int, data: UserUpdateDTO) -> UserResponseDTO:
        user = await self.repository.find_one(where={"id": id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if data.name is None or data.email is None or data.age is None:
            raise HTTPException(status_code=400, detail="Name, email and age are required")
        
        user.name = data.name
        user.email = data.email
        user.age = data.age

        updated_user = await self.repository.save(user)

        
        return UserResponseDTO(id=updated_user.id, name=updated_user.name, 
                             email=updated_user.email, age=updated_user.age)
    
    async def delete_user_by_id(self, id: int) -> dict:
        success = await self.repository.delete(id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "User deleted successfully"}