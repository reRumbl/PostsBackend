from datetime import datetime, UTC
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.users import User, UserRegister, UserLogin, UserModel
from src.auth.jwt.utils import mail_token, create_token_pair, decode_access_token, refresh_token_state
from src.auth.jwt import TokenPairResponse, BlackListTokenModel, SUB, JTI, EXP
from src.auth.password.utils import get_password_hash, verify_password
from src.auth.password import ForgotPasswordSchema, PasswordResetSchema, PasswordUpdateSchema
from src.auth.email import MailTaskSchema, MailBodySchema
from src.auth.exceptions import (
    EmailAlreadyRegisteredException, IncorrectEmailOrPasswordException, EmailNotVerifiedException,
    UserNotFoundException, OldPasswordIsNotCorrect
)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def register(self, data: UserRegister) -> tuple[User, MailTaskSchema]:
        user = await UserModel.find_by_email(self.session, data.email)
        if user:
            raise EmailAlreadyRegisteredException()
        
        user_data = data.model_dump(exclude={'confirm_password'})
        user_data['hashed_password'] = get_password_hash(user_data['password'].get_secret_value())
        user_data.pop('password', None)
        
        user = UserModel(**user_data)
        await user.save(self.session)
        
        user_schema = User.model_validate(user)
        verify_token = mail_token(user_schema)
        
        mail_task_data = MailTaskSchema(
            user=user_schema,
            body=MailBodySchema(type='verify', token=verify_token),
            token=verify_token
        )
        
        return user_schema, mail_task_data
    
    async def login(self, data: UserLogin) -> TokenPairResponse:
        user = await UserModel.authenticate(self.session, data.email, data.password.get_secret_value())
        if not user:
            raise IncorrectEmailOrPasswordException()
        if not user.is_verified:
            raise EmailNotVerifiedException()
        
        user = User.model_validate(user)
        token_pair = create_token_pair(user)
        
        return TokenPairResponse(
            access_token=token_pair.access.token,
            refresh_token=token_pair.refresh.token
        )
    
    async def logout(self, token: str) -> None:
        payload = await decode_access_token(self.session, token)
        black_listed = BlackListTokenModel(id=payload[JTI], expire=datetime.fromtimestamp(payload[EXP]))
        await black_listed.save(self.session)
    
    async def get(self, user_id: UUID)  -> User:
        user = await self.session.get(UserModel, user_id)
        if not user:
            raise UserNotFoundException()
        user_schema = User.model_validate(user)
        return user_schema
    
    async def refresh(self, token: str) -> TokenPairResponse:
        new_access_token = await refresh_token_state(token)
        return TokenPairResponse(
            access_token=new_access_token,
            refresh_token=token
        )
    
    async def verify(self, token: str) -> None:
        payload = await decode_access_token(self.session, token)
        user = await self.session.get(UserModel, payload[SUB])
        if not user:
            raise UserNotFoundException()
        
        user.is_verified = True
        await user.save(self.session)
    
    async def forgot_password(self, data: ForgotPasswordSchema) -> MailTaskSchema:
        user = await UserModel.find_by_email(self.session, data.email)
        if not user:
            raise UserNotFoundException()
        
        user_schema = User.model_validate(user)
        reset_token = mail_token(user)
        
        mail_task_data = MailTaskSchema(
            user=user_schema,
            body=MailBodySchema(type='password-reset', token=reset_token)
        )
        return mail_task_data
    
    async def reset_password(self, token: str, data: PasswordResetSchema) -> None:
        payload = await decode_access_token(self.session, token)
        user = await self.session.get(UserModel, payload[SUB])
        if not user:
            raise UserNotFoundException()
        
        user.hashed_password = get_password_hash(data.password.get_secret_value())
        await user.save(self.session)
    
    async def password_update(self, token: str, data: PasswordUpdateSchema) -> None:
        payload = await decode_access_token(self.session, token)
        user = await self.session.get(UserModel, payload[SUB])
        if not user:
            raise UserNotFoundException()
        
        if not verify_password(data.old_password.get_secret_value(), user.hashed_password):
            raise OldPasswordIsNotCorrect()
        
        user.hashed_password = get_password_hash(data.password)
        await user.save(self.session)
        