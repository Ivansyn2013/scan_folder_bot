# middlewares/db_middleware.py
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.orm import Session

from models.sessions import db_manager
from models.repositories import UserRepository, UserRequestRepository


class DatabaseMiddleware(BaseMiddleware):
    """Middleware для внедрения сессии БД в хендлеры"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Создаем сессию для этого запроса
        session: Session = db_manager.get_session()

        try:
            # Внедряем сессию и репозитории в data
            data["db_session"] = session
            data["user_repo"] = UserRepository(session)
            data["request_repo"] = UserRequestRepository(session)

            # Выполняем хендлер
            result = await handler(event, data)

            # Коммитим изменения
            session.commit()

            return result

        except Exception as e:
            # Откат при ошибке
            session.rollback()
            raise e
        finally:
            # Закрываем сессию
            session.close()
