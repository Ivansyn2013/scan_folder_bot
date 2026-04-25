# database/models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    BigInteger,
    ForeignKey,
    Enum as SqlEnum,
)
from sqlalchemy.orm import declarative_base
from datetime import datetime
import pytz
from enum import Enum

Base = declarative_base()


class UserRole(str, Enum):
    """Роли пользователей"""

    NOT_REGISTER = "NOT_REGISTER"
    GENERAL = "general"
    STAFF = "staff"
    ADMIN = "admin"
    # MODERATOR = "moderator"
    # VIP = "vip"

    @classmethod
    def list_roles(cls):
        """Получить список всех ролей"""
        return [role.value for role in cls]

    @classmethod
    def is_valid(cls, role: str) -> bool:
        """Проверить, существует ли роль"""
        return role in cls.list_roles()


class CustomUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(
        BigInteger, unique=True, nullable=False, index=True
    )  # BigInteger для TG ID
    name = Column(String(255), nullable=True)  # Увеличил длину
    admin = Column(Boolean, default=False, nullable=False)
    role_group = Column(
        SqlEnum(
            UserRole,
            values_callable=lambda obj: [
                e.value for e in obj
            ],  # Явно указываем значения
            name="user_role_enum",  # Имя enum в БД (опционально)
            native_enum=False,
            # create_type=True
        ),  # Создавать тип в БД (для PostgreSQL)
        nullable=True,
        default=UserRole.NOT_REGISTER,
    )

    created_at = Column(
        DateTime, default=datetime.now(pytz.timezone("Europe/Moscow")), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.now(pytz.timezone("Europe/Moscow")),
        onupdate=datetime.now(pytz.timezone("Europe/Moscow")),
    )

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, name={self.name})>"


class UserRequest(Base):
    __tablename__ = "user_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger, ForeignKey("users.telegram_id"), index=True, nullable=False
    )  # Связь с пользователем
    text = Column(String(100), nullable=False)  # Увеличил длину
    created_at = Column(
        DateTime, default=datetime.now(pytz.timezone("Europe/Moscow")), nullable=False
    )

    def __repr__(self):
        return f"<UserRequest(user_id={self.user_id}, created_at={self.created_at})>"
