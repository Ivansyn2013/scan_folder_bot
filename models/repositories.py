# database/repositories.py
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
from models.users import CustomUser, UserRequest
from loguru import logger
from models.users import UserRole


class AbstractRepository(ABC):
    """Абстрактный базовый репозиторий"""

    @abstractmethod
    def add(self, entity: Any) -> Any:
        pass

    @abstractmethod
    def get(self, id: int) -> Optional[Any]:
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Any]:
        pass

    @abstractmethod
    def update(self, id: int, data: Dict[str, Any]) -> Optional[Any]:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass


class BaseRepository(AbstractRepository):
    """Базовый репозиторий с общими методами"""

    def __init__(self, session: Session, model_class):
        self.session = session
        self.model = model_class

    def add(self, entity: Any) -> Any:
        self.session.add(entity)
        self.session.flush()
        return entity

    def add_all(self, entities: List[Any]) -> List[Any]:
        self.session.add_all(entities)
        self.session.flush()
        return entities

    def get(self, id: int) -> Optional[Any]:
        return self.session.get(self.model, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Any]:
        stmt = select(self.model).offset(skip).limit(limit + 1)
        result = list(self.session.execute(stmt).scalars().all())
        if len(result) > limit:
            logger.error(f"Instanses are more that limin <{limit}>")
        return list(self.session.execute(stmt).scalars().all())

    def update(self, id: int, data: Dict[str, Any]) -> Optional[Any]:
        entity = self.get(id)
        if entity:
            for key, value in data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            self.session.flush()
        return entity

    def delete(self, id: int) -> bool:
        stmt = delete(self.model).where(self.model.id == id)
        result = self.session.execute(stmt)
        return result.rowcount > 0


# Специфичные репозитории для каждой модели
class UserRepository(BaseRepository):
    """Репозиторий для работы с пользователями"""

    def __init__(self, session: Session):
        super().__init__(session, CustomUser)
        self.model = CustomUser

    def get_by_telegram_id(self, telegram_id: int) -> Optional[CustomUser]:
        stmt = select(self.model).where(self.model.telegram_id == telegram_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_admins(self) -> List[CustomUser]:
        stmt = select(self.model).where(self.model.admin == True)
        return list(self.session.execute(stmt).scalars().all())

    def upsert_from_telegram(self, telegram_id: int, name: str = None) -> CustomUser:
        """Создать или обновить пользователя из Telegram"""
        user = self.get_by_telegram_id(telegram_id)

        if not user:
            user = self.model(telegram_id=telegram_id, name=name, admin=False)
            self.add(user)
        elif name and user.name != name:
            user.name = name
            self.session.flush()

        return user

    def get_staff(self) -> List[CustomUser]:
        stmt = select(self.model).where(self.model.role_group == UserRole.STAFF)
        return list(self.session.execute(stmt).scalars().all())

    def get_not_register(self) -> List[CustomUser]:
        stmt = select(self.model).where(self.model.role_group == UserRole.NOT_REGISTER)
        return list(self.session.execute(stmt).scalars().all())


class UserRequestRepository(BaseRepository):
    """Репозиторий для запросов пользователей"""

    def __init__(self, session: Session):
        super().__init__(session, UserRequest)

    def get_by_user(self, telegram_id: int, limit: int = 10) -> List[UserRequest]:
        stmt = (
            select(self.model)
            .where(self.model.user_id == telegram_id)
            .order_by(self.model.created_at.desc())
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())

    def create_request(self, telegram_id: int, text: str) -> UserRequest:
        request = self.model(user_id=telegram_id, text=text)
        return self.add(request)
