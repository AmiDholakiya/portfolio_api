from pydantic import BaseModel, Field
import datetime
from typing import Optional


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    
    
class TokenPayload(BaseModel):
    data: str = None
    exp: int = None


class LoginPayload(BaseModel):
    email: str = Field(..., description="user email")
    password: str = Field(..., min_length=5, max_length=24, description="user password")
    

class LoginResponse(BaseModel):
    id: str
    email: str


class SystemUser(LoginResponse):
    password: str

class Authentication(BaseModel):
    access_token :str = None
    refresh_token :str = None
    username :str = None
    client_id :str = None
    created_at: Optional[datetime.datetime] = datetime.datetime.now()

# oauth2_scheme  = OAuth2PasswordBearer(
#     tokenUrl="token"
# )
