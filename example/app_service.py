from ezyapi import EzyService

class AppService(EzyService):
    async def get_app(self, url: str) -> str:
        return f"{url}"
