from ezyapi import EzyAPI
from ezyapi.database import DatabaseConfig
from example.user.user_service import UserService
from example.app_service import AppService

if __name__ == "__main__":
    app = EzyAPI(
        title="User Management API",
        description="API for managing users"
    )
    db_config = DatabaseConfig(
        db_type="sqlite",
        connection_params={
            "dbname": "user.db",
        }
    )
    app.configure_database(db_config)
    app.add_service(UserService)
    app.add_service(AppService)
    app.run(port=8000)