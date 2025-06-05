from typing import Self
from datetime import datetime
from sqlalchemy import select, text as sa_text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import Base
from src.auth.password.utils import verify_password


class UserModel(Base):
    __tablename__ = 'user'
    
    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    is_verified: Mapped[bool] = mapped_column(server_default=sa_text('FALSE'))
    updated_at: Mapped[datetime] = mapped_column(
        server_default=sa_text('TIMEZONE(\'UTC\', NOW())'),
        onupdate=sa_text('TIMEZONE(\'UTC\', NOW())')
    )
    
    posts = relationship('PostModel', back_populates='author', lazy='selectin', passive_deletes=True)
    
    @classmethod
    async def find_by_email(cls, session: AsyncSession, email: str):
        query = select(cls).where(cls.email == email)
        result = await session.execute(query)
        return result.scalars().first()
    
    @classmethod
    async def find_by_username(cls, session: AsyncSession, username: str):
        query = select(cls).where(cls.username == username)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def authenticate(cls, session: AsyncSession, email: str, password: str) -> Self:
        user = await cls.find_by_email(session=session, email=email)
        if not user or not verify_password(password, user.hashed_password):
            return False
        return user
