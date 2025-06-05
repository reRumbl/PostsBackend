from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Form, UploadFile
from fastapi_cache.decorator import cache
from src.posts import Post, PostCreate, PostUpdate
from src.posts.dependencies import PostsServiceDep
from src.auth.dependencies import CurrentUserDep
from src.aws.dependencies import S3ClientDep
from src.dependencies import PaginationDep
from src.schemas import SuccessResponse, DataListResponse, PaginationInfo
from src.decorators import default_router_exceptions

router = APIRouter(prefix='/api/posts', tags=['posts'])


@router.get('/feed', response_model=DataListResponse[Post])
@default_router_exceptions
async def get_posts_feed(user: CurrentUserDep, pagination: PaginationDep, posts_service: PostsServiceDep):
    posts, count = await posts_service.get_feed(user, pagination)
    return DataListResponse(
        data=posts, 
        pagination=PaginationInfo(
            offset=pagination.offset, 
            limit = pagination.limit, 
            count=count
        )
    )


@router.get('/{post_id}', response_model=Post)
@default_router_exceptions
@cache(expire=60)
async def get_post(post_id: UUID, posts_service: PostsServiceDep):
    post = await posts_service.get(post_id)
    return post


@router.get('/user/{user_id}', response_model=list[Post])
@default_router_exceptions
@cache(expire=60)
async def get_posts_by_user(user_id: UUID, posts_service: PostsServiceDep):
    posts = await posts_service.get_by_user(user_id)
    return posts


@router.post('/upload', response_model=Post)
@default_router_exceptions
async def upload_post(
    title: Annotated[str, Form()], 
    description: Annotated[str | None, Form()],
    file: UploadFile,
    user: CurrentUserDep, 
    posts_service: PostsServiceDep,
    client: S3ClientDep
):
    data = PostCreate(title=title, description=description)
    post = await posts_service.upload(user, data, file, client)
    return post


@router.put('/{post_id}', response_model=SuccessResponse)
@default_router_exceptions
async def edit_post(post_id: UUID, data: PostUpdate, user: CurrentUserDep, posts_service: PostsServiceDep):
    await posts_service.edit(user, post_id, data)
    return SuccessResponse(message='Post successfully updated')


@router.delete('/{post_id}', response_model=SuccessResponse)
@default_router_exceptions
async def delete_post(post_id: UUID, user: CurrentUserDep, posts_service: PostsServiceDep):
    await posts_service.delete(user, post_id)
    return SuccessResponse(message='Post successfully deleted')
