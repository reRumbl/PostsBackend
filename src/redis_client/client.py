from typing import Any
from redis import asyncio as aioredis


class RedisClient:
    def __init__(self, host, endcoding='utf-8'):
        self.connection = aioredis.from_url(f'redis://{host}', encoding=endcoding)
    
    async def get(self, key) -> Any | None:
        return await self.connection.get(key)
    
    async def setex(self, key, ttl, val) -> Any | None:
        return await self.connection.setex(key, ttl, val)
    
    async def is_connected(self) -> bool:
        try:
            await self.connection.ping()
            return True
        except aioredis.TimeoutError:
            return False
    