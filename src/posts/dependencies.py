from typing import Annotated
from fastapi import Depends
from src.dependencies import SessionDep
from src.posts.service import PostsService


def get_posts_service(session: SessionDep):
    return PostsService(session)


PostsServiceDep = Annotated[PostsService, Depends(get_posts_service)]
