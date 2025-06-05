from datetime import datetime
from pydantic import BaseModel, ConfigDict, UUID4


class JwtTokenSchema(BaseModel):
    token: str
    payload: dict
    expire: datetime


class TokenPair(BaseModel):
    access: JwtTokenSchema
    refresh: JwtTokenSchema
    
    
class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str


class TokenRequest(BaseModel):
    token: str


class BlackListToken(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Same as "orm_mode = True"
    
    id: UUID4
    expire: datetime
    created_at: datetime
