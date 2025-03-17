# Transport layer: REST API
from ezyapi import EzyService
from user.dto.user_create_dto import UserCreateDTO
from user.dto.user_update_dto import UserUpdateDTO
from user.entity.user_entity import UserEntity

class UserService(EzyService):
    def create(self, data: UserCreateDTO):
        return 'This action adds a new user'

    def find_all(self):
        return 'This action returns all users'

    def find_one(self, id: int):
        return f'This action returns a #{id} user'

    def update(self, id: int, data: UserUpdateDTO):
        return f'This action updates a #{id} user'

    def remove(self, id: int):
        return f'This action removes a #{id} user'
