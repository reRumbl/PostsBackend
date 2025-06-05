from pydantic import BaseModel, EmailStr, SecretStr, field_validator, ValidationInfo


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class PasswordResetSchema(BaseModel):
    password: SecretStr
    confirm_password: SecretStr
    
    @field_validator('confirm_password')
    def verify_password_match(cls, v: SecretStr, info: ValidationInfo):
        password: SecretStr = info.data.get('password')

        if v.get_secret_value() != password.get_secret_value():
            raise ValueError('Passwords did not match')

        return v


class PasswordUpdateSchema(PasswordResetSchema):
    old_password: SecretStr
