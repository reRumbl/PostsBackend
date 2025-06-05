import logging
from uuid import UUID
from datetime import datetime
from sqlalchemy import event, Engine, text as sa_text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncAttrs
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from src.config import settings

# --- Engine

engine = create_async_engine(
    url=settings.asyncpg_url,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DB_ECHO
)

SessionFactory = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[UUID] = mapped_column(server_default=sa_text('GEN_RANDOM_UUID()'), primary_key=True, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=sa_text('TIMEZONE(\'UTC\', NOW())'))
    
    async def save(self, session: AsyncSession):
        '''Add and commit object'''
        try:
            session.add(self)
            return await session.commit()
        except SQLAlchemyError as ex:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)
            ) from ex


# --- Logging ---

@event.listens_for(Engine, 'before_cursor_execute')
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    logging.getLogger('database_logger').info(f'SQL Query: {statement}')
    if parameters:
        logging.getLogger('database_logger').debug(f'Parameters: {parameters}')
