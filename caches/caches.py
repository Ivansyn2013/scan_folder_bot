from datetime import datetime
from typing import Any, List, NamedTuple, Optional

import pytz
from loguru import logger

from actions.scan_folder import scan_folder_cache
from models.repositories import UserRepository
from models.sessions import db_manager as db


class BaseCache:
    _instance: Optional["BaseCache"] = None
    _initialized = False
    last_update = None

    def __new__(cls):
        """Контролируем создание единственного экземпляра"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.cache: Optional[List[Any]] = []
            self.last_update: Optional[datetime] = None
            self._initialized = True
            logger.info(f"Cache {self} singleton created")

    async def initialize(self):
        """Асинхронная инициализация (вызовите при старте бота)"""
        if self.cache == []:
            await self.update()
            logger.info("Cache initialized")
        return self

    async def update(self):
        logger.warning("Call update method from BaseCahe class. No cahnges in cache")
        return self.cache


class UserCache(BaseCache):
    """
    Class for use user cache
    self.cache =
    """

    class UserManager:
        """
        Manages user-related operations and data, specifically handling a user cache and
        providing methods to extract user information. The class relies on input data
        being structured in a way that it includes a `telegram_id` for each user.

        :ivar cache: Stores user-related data, which is a list of user objects with a
                     `telegram_id` attribute.
        :type cache: list
        """

        def __init__(self, cache):
            self.cache = cache

        def get_ids(self):
            if not self.cache or self.cache == []:
                logger.warning("User cache is empty")
                return []
            return [user.telegram_id for user in self.cache]

        def get_user_by_telegram_id(self, telegram_id):
            return next(
                (user.id for user in self.cache if user.telegram_id == telegram_id),
                None,
            )

    def __init__(self):
        super().__init__()
        self.staff: UserCache.UserManager = None
        self.admin: UserCache.UserManager = None
        self.not_register: UserCache.UserManager = None
        self.allowed: UserCache.UserManager = None

    async def update(self):
        session = db.get_session()
        user_repo = UserRepository(session)

        self.staff = self.UserManager(user_repo.get_staff())
        self.admin = self.UserManager(user_repo.get_admins())
        self.not_register = self.UserManager(user_repo.get_not_register())
        self.allowed = self.staff.cache + self.admin.cache
        self.cache = self.staff.cache + self.admin.cache + self.not_register.cache
        self.last_update = datetime.now(pytz.timezone("Europe/Moscow"))
        return True

    def get_user_by_telegram_id(self, telegram_id):
        """

        :param telegram_id:
        :return:User.id from CustomUser
        """
        if not self.cache or self.cache == []:
            logger.warning("User cache is empty")
            return None
        result =  (
            self.staff.get_user_by_telegram_id(telegram_id)
            or self.admin.get_user_by_telegram_id(telegram_id)
            or self.not_register.get_user_by_telegram_id(telegram_id)
        )
        return result

    def __repr__(self) -> str:
        return f"UserCache(files={len(self.cache) if self.cache else 0}, last_update={self.last_update})"


class FilesCache(BaseCache):
    """
    Class for use Files cahce
    """

    async def update(self):
        self.cache: List[NamedTuple] = await scan_folder_cache()
        logger.info(f"Files cache was updated. {self}")
        self.last_update = datetime.now(pytz.timezone("Europe/Moscow"))
        return self.cache

    def __repr__(self) -> str:
        return f"FilesCache(files={len(self.cache) if self.cache else 0}, last_update={self.last_update})"


user_cache = UserCache()
file_cache = FilesCache()
