# migrations/env.py
import sys

from settings.settings import app_settings

# Добавляем путь к вашему проекту (если нужно)
sys.path.append(str(app_settings.base_dir))

from alembic import context
from sqlalchemy import engine_from_config, pool

# Импортируем вашу базу и модели
from models.users import (  # Ваши модели
    Base,  # Или откуда у вас импортируется Base
)

# Это самое важное! Указываем Alembic метаданные ваших моделей
target_metadata = Base.metadata

# Получаем конфиг и запускаем нужную функцию
config = context.config

# Переопределяем URL из настроек приложения
if app_settings.database_url:
    config.set_main_option("sqlalchemy.url", app_settings.database_url)


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


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
