from pydantic import BaseModel
from app.models.user import User
from typing import Any


class UserInfo(BaseModel):
    username: str
    password: str

class UserSearchingParams(BaseModel):
    id: int | None = None
    username: str | None = None


class SessionInfo(BaseModel):
    user_id: int


class SessionSearchingParams(BaseModel):
    id: str | None = None
    user: int | None = None
