from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from src.auth.service import AuthService
from src.auth.users import User, UserModel
from src.auth.jwt.utils import decode_access_token
from src.auth.jwt import SUB
from src.dependencies import SessionDep
from src.auth.exceptions import UnauthorizedUserException


def get_auth_service(session: SessionDep):
    return AuthService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')
TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(token: TokenDep, session: SessionDep) -> User:
    payload = await decode_access_token(session, token)
    user = await session.get(UserModel, payload[SUB])
    if not user:
        raise UnauthorizedUserException()
    
    user_schema = User.model_validate(user)
    return user_schema


CurrentUserDep = Annotated[User, Depends(get_current_user)]        
