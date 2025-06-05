from uuid import uuid4
from datetime import datetime, timedelta, UTC
import jwt
from jwt.exceptions import PyJWTError
from src.auth.users import User
from src.auth.jwt import JwtTokenSchema, TokenPair
from src.dependencies import SessionDep
from src.auth.exceptions import AuthFailedException
from src.auth.jwt import BlackListTokenModel, SUB, EXP, IAT, JTI
from src.config import settings


def create_access_token(payload: dict, minutes: int | None = None) -> JwtTokenSchema:
    expire = datetime.now(UTC) + timedelta(minutes=minutes or settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload[EXP] = expire
    
    token = JwtTokenSchema(
        token=jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGHORITM),
        expire=expire,
        payload=payload                    
    )
    
    return token


def create_refresh_token(payload: dict) -> JwtTokenSchema:
    expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)  
    
    payload[EXP] = expire
    
    token =  JwtTokenSchema(
        token=jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGHORITM),
        expire=expire,
        payload=payload
    )
    
    return token


def create_token_pair(user: User) -> TokenPair:
    payload = {SUB: str(user.id), JTI: str(uuid4()), IAT: datetime.now(UTC)}
    
    return TokenPair(
        access=create_access_token(payload={**payload}),
        refresh=create_refresh_token(payload={**payload})
    )


async def decode_access_token(session: SessionDep, token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGHORITM])
        
        black_list_token = await session.get(BlackListTokenModel, payload[JTI])
        if black_list_token:
            raise PyJWTError('Token is blacklisted')
        
        return payload
    except PyJWTError:
        raise AuthFailedException()
    
    
async def refresh_token_state(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGHORITM])
        return create_access_token(payload=payload).token
    except PyJWTError:
        raise AuthFailedException()


def mail_token(user: User):
    '''Return 2 hour lifetime access_token for email verification'''
    payload = {SUB: str(user.id), JTI: str(uuid4()), IAT: datetime.now(UTC)}
    return create_access_token(payload=payload, minutes=2 * 60).token
