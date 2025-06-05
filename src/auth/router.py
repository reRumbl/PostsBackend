from uuid import UUID
from fastapi import APIRouter, BackgroundTasks
from fastapi_cache.decorator import cache
from src.auth.users import User, UserRegister, UserLogin
from src.auth.dependencies import AuthServiceDep
from src.auth.jwt import TokenPairResponse, TokenRequest
from src.auth.password import ForgotPasswordSchema, PasswordResetSchema, PasswordUpdateSchema
from src.auth.email.tasks import user_mail_event
from src.schemas import SuccessResponse
from src.decorators import default_router_exceptions

router = APIRouter(prefix='/api/auth', tags=['auth'])


@router.post('/register', response_model=User)
@default_router_exceptions
async def register(data: UserRegister, bg_task: BackgroundTasks, auth_service: AuthServiceDep):
    user, mail_task_data = await auth_service.register(data) 
    bg_task.add_task(user_mail_event, mail_task_data)
    return user


@router.post('/login', response_model=TokenPairResponse)
@default_router_exceptions
async def login(data: UserLogin, auth_service: AuthServiceDep):
    tokens = await auth_service.login(data)
    return tokens


@router.post('/logout', response_model=SuccessResponse)
@default_router_exceptions
async def logout(data: TokenRequest, auth_service: AuthServiceDep):
    await auth_service.logout(data.token)
    return SuccessResponse(message='Succesfully logout')


@router.get('/users/{user_id}', response_model=User)
@cache(expire=60)
@default_router_exceptions
async def get_user(user_id: UUID, auth_service: AuthServiceDep):
    user = await auth_service.get(user_id) 
    return user


@router.post('/refresh', response_model=TokenPairResponse)
@default_router_exceptions
async def refresh(data: TokenRequest, auth_service: AuthServiceDep):
    tokens = await auth_service.refresh(data.token)
    return tokens


@router.patch('/verify/{token}', response_model=SuccessResponse)
@default_router_exceptions
async def verify(token: str, auth_service: AuthServiceDep):
    await auth_service.verify(token)
    return SuccessResponse(message='Successfully verified')


@router.post('/forgot_password', response_model=SuccessResponse)
@default_router_exceptions
async def forgot_password(data: ForgotPasswordSchema, bg_task: BackgroundTasks, auth_service: AuthServiceDep):
    mail_task_data = await auth_service.forgot_password(data)
    bg_task.add_task(user_mail_event, mail_task_data)
    return SuccessResponse(message='Email with reset token successfully sended')


@router.patch('/password_reset', response_model=SuccessResponse)
@default_router_exceptions
async def password_reset(token: str, data: PasswordResetSchema, auth_service: AuthServiceDep):
    await auth_service.reset_password(token, data)
    return SuccessResponse(message='Password successfully reseted')


@router.patch('/password_update', response_model=SuccessResponse)
@default_router_exceptions
async def password_update(token: str, data: PasswordUpdateSchema, auth_service: AuthServiceDep):
    await auth_service.password_update(token, data)
    return SuccessResponse(message='Password successfully updated')
