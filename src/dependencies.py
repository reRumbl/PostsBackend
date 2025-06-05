from typing import Annotated
from collections.abc import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import SessionFactory
from src.schemas import PaginationParams


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]

PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]
