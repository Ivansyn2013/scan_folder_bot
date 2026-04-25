# migrations/env.py
import sys
from pathlib import Path
from settings.settings import app_settings

# Добавляем путь к вашему проекту (если нужно)
sys.path.append(str(app_settings.base_dir))

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Импортируем вашу базу и модели
from models.users import Base  # Или откуда у вас импортируется Base
from models.users import CustomUser, UserRequest  # Ваши модели

# Это самое важное! Указываем Alembic метаданные ваших моделей
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в offline режиме (без подключения к БД)"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Для SQLite включаем batch режим
        render_as_batch=True if "sqlite" in url else False,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в online режиме (с подключением к БД)"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Для SQLite включаем batch режим
            render_as_batch=True if "sqlite" in str(connection.dialect) else False,
            # Сравнивать типы столбцов (полезно для изменений)
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# Получаем конфиг и запускаем нужную функцию
config = context.config
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
