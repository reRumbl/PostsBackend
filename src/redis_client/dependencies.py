from typing import Annotated
from fastapi import Depends
from src.redis_client.client import RedisClient
from src.config import settings


def get_redis_client():
    return RedisClient(settings.REDIS_HOST)


RedisClientDep = Annotated[RedisClient, Depends(get_redis_client)]
