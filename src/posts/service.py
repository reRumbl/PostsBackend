from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from src.posts import Post, PostCreate, PostUpdate, PostModel
from src.schemas import PaginationParams
from src.auth.users import User, UserModel
from src.aws.client import S3Client
from src.posts.exceptions import InvalidFileTypeException, UserNotPostAuthorException


class PostsService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, post_id: UUID) -> Post:
        post = await self.session.get(PostModel, post_id)
        post_schema = Post.model_validate(post)
        return post_schema
    
    async def get_feed(self, user: User, pagination: PaginationParams) -> tuple[list[Post], int]:
        '''
        Gets post feed with pagination
        Args:
            user: Current authenticated user
            pagintaion: Pagintaion params
        Returns:
            tuple[list[Post], int] (Posts list and total count of posts in db)
        '''
        # TODO: Select posts with user preferences
        # Now just selecting all posts in order with pagination
        total_count = await PostModel.count(self.session)
        
        query = select(PostModel).limit(pagination.limit).offset(pagination.offset)
        data = await self.session.execute(query)
        posts = [Post.model_validate(p) for p in data.scalars().all()]
        return posts, total_count
    
    async def get_by_user(self, user_id: UUID) -> list[Post]:
        '''
        Gets first 10 posts with user_id authorship
        Args:
            user_id: Posts author id
        Returns:
            list[Post] (List with posts)
        '''
        user = await self.session.get(UserModel, user_id)
        posts = [Post.model_validate(post) for post in user.posts[:10]]
        return posts
        
    
    async def upload(self, user: User, data: PostCreate, file: UploadFile, client: S3Client) -> Post:
        if not file.content_type.startswith('image/'):
            raise InvalidFileTypeException()
        image_url = await client.upload_file(file)
        
        post = PostModel(title=data.title, description=data.description, image_url=image_url, author_id=user.id)
        await post.save(self.session)
        post_schema = Post.model_validate(post)
        return post_schema
    
    async def edit(self, user: User, post_id: UUID, data: PostUpdate) -> None:
        post = await self.session.get(PostModel, post_id)
        if user.id != post.author_id:
            raise UserNotPostAuthorException()
        query = update(PostModel).where(PostModel.id == post_id).values(**data.model_dump(exclude_unset=True))
        await self.session.execute(query)
        await self.session.commit()
    
    async def delete(self, user: User, post_id: UUID) -> None:
        post = await self.session.get(PostModel, post_id)
        if user.id != post.author_id:
            raise UserNotPostAuthorException()
        await self.session.delete(post)
        await self.session.commit()
    