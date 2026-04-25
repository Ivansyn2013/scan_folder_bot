# database/schemas.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    telegram_id: int
    name: Optional[str] = None
    admin: bool = False
    role_group: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserRequestBase(BaseModel):
    user_id: int
    text: str


class UserRequestCreate(UserRequestBase):
    pass


class UserRequestResponse(UserRequestBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
