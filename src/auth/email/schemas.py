from pydantic import BaseModel, EmailStr
from src.auth.users import User


class MailBodySchema(BaseModel):
    token: str
    type: str
    

class EmailSchema(BaseModel):
    recipients: list[EmailStr]
    subject: str
    body: MailBodySchema


class MailTaskSchema(BaseModel):
    user: User
    body: MailBodySchema
