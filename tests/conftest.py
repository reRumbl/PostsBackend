from typing import AsyncGenerator
import pytest
from pytest_asyncio import fixture
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend
# from redis import asyncio as aioredis
from httpx import AsyncClient, ASGITransport
from src.database import Base
from src.auth.jwt import models
from src.auth.users import models
from src.posts import models
from src.dependencies import get_db
from src.main import app
from src.config import settings

engine_test = create_async_engine(settings.test_asyncpg_url, poolclass=NullPool)
session_factory_test = async_sessionmaker(engine_test, expire_on_commit=False)


async def get_db_test() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory_test() as session:
        yield session


app.dependency_overrides[get_db] = get_db_test


@fixture(scope='session', autouse=True)
async def prepare_database():
    async with engine_test.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


# @fixture(scope='session', autouse=True)
# async def prepare_redis():
#     redis = aioredis.from_url(f'redis://{settings.REDIS_HOST}', encoding='utf8', decode_responses=True)  # Redis init
#     await redis.ping()
#     FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')
#     yield
#     await redis.close()


@fixture(scope='session')
async def test_async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://testserver') as client:
        yield client
