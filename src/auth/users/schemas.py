from datetime import datetime
from pydantic import BaseModel, ConfigDict, UUID4, EmailStr, SecretStr, field_validator, ValidationInfo
from src.auth.exceptions import PasswordsDidNotMatchException

class UserBase(BaseModel):
    email: EmailStr
    username: str
    

class UserRegister(UserBase):
    password: SecretStr
    confirm_password: SecretStr
    
    @field_validator('confirm_password')
    def verify_password_match(cls, v: SecretStr, info: ValidationInfo):
        password: SecretStr = info.data.get('password')

        if v.get_secret_value() != password.get_secret_value():
            raise PasswordsDidNotMatchException()

        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: SecretStr
    

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)  # Same as "orm_mode = True"
    
    id: UUID4
    is_verified: bool
    created_at: datetime
    updated_at: datetime
