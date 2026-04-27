# middlewares/db_middleware.py
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from sqlalchemy.orm import Session
from loguru import logger
from caches import file_cache, user_cache
from models.repositories import UserRepository, UserRequestRepository
from models.sessions import db_manager
from models.users import CustomUser, UserRequest


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
            data["file_cache"] = file_cache
            data["user_cache"] = user_cache

            #
            if isinstance(event, Message):
                user_t_id = event.from_user.id
                admin_ids = user_cache.admin.get_ids()
                staff_ids = user_cache.staff.get_ids()
                not_register_ids = user_cache.not_register.get_ids()
                user_ids = admin_ids + staff_ids + not_register_ids

                if user_t_id not in user_ids:
                    user_session: Session = db_manager.get_session()
                    new_user_repo = UserRepository(user_session)
                    new_user = CustomUser(
                        name=event.from_user.first_name,
                        telegram_id=event.from_user.id,
                    )
                    new_user_repo.add(new_user)
                    user_session.commit()
                    logger.info(
                        f"User <{new_user.name}> успешно добавлен в базу с ролью <{new_user.role_group}>"
                    )

                    data["user_cache"].update()

                if event.text:
                    new_req_session: Session = db_manager.get_session()
                    new_req_repo = UserRequestRepository(new_req_session)
                    new_req = new_req_repo.add(
                        UserRequest(
                            user_id=user_cache.get_user_by_telegram_id(user_t_id),
                            text=event.text,
                        )
                    )
                    new_req_session.commit()

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
