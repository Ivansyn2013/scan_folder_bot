import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String, Boolean, Enum
from datetime import datetime

Base = declarative_base()


class CustomUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    telegram_id = Column(String(50))
    admin = Boolean(default=False)
    role_group = Enum()


class UserRequest(Base):
    __tablename__ = "user_requests"
    id = Column(Integer, primary_key=True)
    creation_at = DateTime(timezone="Europe/Moscow", default=datetime.now())
    text = Column(String(20))
