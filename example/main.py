from fastapi import HTTPException
from typing import List

from example.dto.user_response_dto import UserResponseDTO
from example.dto.user_create_dto import UserCreateDTO
from example.entity import UserEntity

from ezyapi import EzyAPI, EzyService
from ezyapi.database import EzyEntityBase, DatabaseConfig

class UserEntity(EzyEntityBase):
    def __init__(self, id: int = None, name: str = "", email: str = "", age: int = None):
        self.id = id
        self.name = name
        self.email = email
        self.age = age

class UserService(EzyService):
    async def get_user_by_id(self, id: int) -> UserResponseDTO:
        """특정 ID로 사용자 조회"""
        user = await self.repository.find_by_id(id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponseDTO(id=user.id, name=user.name, email=user.email, age=user.age)
    
    async def list_users(self) -> List[UserResponseDTO]:
        """모든 사용자 목록 조회"""
        users = await self.repository.find_all()
        return [
            UserResponseDTO(id=user.id, name=user.name, email=user.email, age=user.age)
            for user in users
        ]
    
    async def create_user(self, data: UserCreateDTO) -> UserResponseDTO:
        """새 사용자 생성"""
        new_user = UserEntity(name=data.name, email=data.email, age=data.age)
        saved_user = await self.repository.save(new_user)
        
        return UserResponseDTO(id=saved_user.id, name=saved_user.name, 
                             email=saved_user.email, age=saved_user.age)
    
    async def update_user_by_id(self, id: int, data: UserCreateDTO) -> UserResponseDTO:
        """사용자 정보 업데이트"""
        user = await self.repository.find_by_id(id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.name = data.name
        user.email = data.email
        user.age = data.age
        
        updated_user = await self.repository.save(user)
        
        return UserResponseDTO(id=updated_user.id, name=updated_user.name, 
                             email=updated_user.email, age=updated_user.age)
    
    async def delete_user_by_id(self, id: int) -> dict:
        """사용자 삭제"""
        success = await self.repository.delete(id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "User deleted successfully"}

if __name__ == "__main__":
    app = EzyAPI(
        title="User Management API", 
        description="API for managing users"
    )
    app.configure_database("sqlite", "example.db")
    app.add_service(UserService)
    app.run(port=8000)