from ezyapi import EzyAPI
from ezyapi.database import DatabaseConfig
from app_service import AppService

if __name__ == "__main__":
    app = EzyAPI()
    app.add_service(AppService)
    app.run(port=8000)
