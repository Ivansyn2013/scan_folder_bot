# database/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from settings.settings import app_settings


class DatabaseManager:
    """Менеджер БД с поддержкой различных СУБД"""

    def __init__(self, db_url: str = None):
        # Поддержка разных БД через URL
        # SQLite: sqlite:///database.db
        # PostgreSQL: postgresql://user:pass@localhost/db
        # MySQL: mysql+pymysql://user:pass@localhost/db
        self.db_url = app_settings.database_url
        self.engine = None
        self.session_factory = None

    def initialize(self):
        """Инициализация подключения к БД"""
        connect_args = {}

        # Специальные настройки для SQLite
        if "sqlite" in self.db_url:
            connect_args = {"check_same_thread": False}

        self.engine = create_engine(
            self.db_url,
            echo=False,  # True для отладки SQL
            poolclass=NullPool if "sqlite" in self.db_url else None,
            connect_args=connect_args,
        )

        self.session_factory = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False, expire_on_commit=False
        )

    def get_session(self) -> Session:
        """Получить новую сессию"""
        if not self.session_factory:
            self.initialize()
        return self.session_factory()

    def create_tables(self):
        """Создать все таблицы"""
        from models.users import Base

        Base.metadata.create_all(bind=self.engine)

    def close(self):
        """Закрыть соединение"""
        if self.engine:
            self.engine.dispose()


# Глобальный экземпляр менеджера
db_manager = DatabaseManager()
