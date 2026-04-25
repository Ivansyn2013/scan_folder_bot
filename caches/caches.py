from datetime import datetime
from actions.scan_folder import scan_folder_cache
import pytz
from loguru import logger
from typing import Optional, List, Any, NamedTuple
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
    """

    async def update(self):
        session = db.get_session()
        user_repo = UserRepository(session)

        self.cache = user_repo.get_staff()
        self.cache.append(user_repo.get_admins())
        self.last_update = datetime.now(pytz.timezone("Europe/Moscow"))
        return self.cache

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
