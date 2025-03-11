from fastapi import HTTPException
from typing import List

from example.user.dto.user_response_dto import UserResponseDTO
from example.user.dto.user_create_dto import UserCreateDTO
from example.user.entity import UserEntity

from ezyapi import EzyService

class UserService(EzyService):
    async def get_user_by_id(self, id: int) -> UserResponseDTO:
        user = await self.repository.find_one(where={"id": id})

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponseDTO(id=user.id, name=user.name, email=user.email, age=user.age)
    
    async def list_users(self) -> List[UserResponseDTO]:
        users = await self.repository.find()
        return [
            UserResponseDTO(id=user.id, name=user.name, email=user.email, age=user.age)
            for user in users
        ]
    
    async def create_user(self, data: UserCreateDTO) -> UserResponseDTO:
        new_user = UserEntity(name=data.name, email=data.email, age=data.age)
        saved_user = await self.repository.save(new_user)
        
        return UserResponseDTO(id=saved_user.id, name=saved_user.name, 
                             email=saved_user.email, age=saved_user.age)
    
    async def update_user_by_id(self, id: int, data: UserCreateDTO) -> UserResponseDTO:
        user = await self.repository.find_one(where={"id": id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
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