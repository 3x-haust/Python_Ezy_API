from ezyapi import EzyAPI
from ezyapi.database import DatabaseConfig
from app_service import AppService
from user.user_service import UserService

if __name__ == "__main__":
    app = EzyAPI()
    app.add_service(AppService)
    app.add_service(UserService)
    app.run(port=8000)
