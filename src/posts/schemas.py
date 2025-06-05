from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PostBase(BaseModel):
    title: str
    description: str | None = None


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    title: str | None = None


class Post(PostBase):
    model_config = ConfigDict(from_attributes=True)  # Same as "orm_mode = True"
    
    id: UUID
    image_url: str
    author_id: UUID
    created_at: datetime
    updated_at: datetime
