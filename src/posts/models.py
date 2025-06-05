from datetime import datetime
from uuid import UUID
from sqlalchemy import select, ForeignKey, func, text as sa_text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.dependencies import SessionDep


class PostModel(Base):
    __tablename__ = 'post'
    
    title: Mapped[str]
    description: Mapped[str]
    image_url: Mapped[str]
    author_id: Mapped[UUID] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    updated_at: Mapped[datetime] = mapped_column(
        server_default=sa_text('TIMEZONE(\'UTC\', NOW())'),
        onupdate=sa_text('TIMEZONE(\'UTC\', NOW())')
    )
    
    author = relationship('UserModel', back_populates='posts', lazy='selectin', passive_deletes=True)
    
    @classmethod
    async def count(cls, session: SessionDep):
        query = select(func.count()).select_from(cls)
        result = await session.execute(query)
        return result.scalars().first()
