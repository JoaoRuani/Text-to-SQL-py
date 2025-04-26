from pydantic import BaseModel, EmailStr
from typing import List, Optional

class ConnectionStringBase(BaseModel):
    name: str
    connection_string: str
    database_type: str


class ConnectionStringCreate(ConnectionStringBase):
    pass

class ConnectionString(ConnectionStringBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    connection_strings: List[ConnectionString] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 


class TokenRequest(BaseModel):
    username: str
    password: str