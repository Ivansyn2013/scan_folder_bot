import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from loguru import logger
from pydantic import BaseModel, Field, ValidationError, validator


class DatabaseSettings(BaseModel):
    """Настройки базы данных"""

    host: str = Field(default="localhost", description="Хост базы данных")
    port: int = Field(default=5432, ge=1, le=65535, description="Порт")
    database: str = Field(..., min_length=1, description="Имя базы данных")
    username: str = Field(..., min_length=1, description="Имя пользователя")
    password: str = Field(..., min_length=1, description="Пароль")
    pool_size: int = Field(
        default=10, ge=1, le=100, description="Размер пула соединений"
    )


class AppSettings(BaseModel):
    """Главные настройки приложения"""

    app_name: str = Field(default="Scaner folder bot", max_length=100)
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    api_version: str = Field(default="v1")
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    environment: str = Field(default="development")
    bot_token: Optional[str] = Field(default=None)
    admin_pass: Optional[str] = Field(default=None)
    admin_id: Optional[str] = Field(default=None)
    target_folder: Optional[Path] = Field(default=None)
    user_roles: Optional[List[str]] = Field(default=None)
    proxy_url: Optional[str] = Field(default=None)
    use_proxy: bool = Field(default=False)
    is_polling: bool = Field(default=False)
    database_url: Optional[str] = Field(default=None)
    base_dir: Path = Field(default_factory=lambda: Path.cwd().parent)

    # Дополнительные параметры
    extra_config: Dict[str, Union[str, int, float, bool]] = Field(default_factory=dict)

    def __init__(self, **data):
        data.setdefault("debug", os.getenv("DEBUG", "").lower() in ("1", "true", "yes"))
        data.setdefault("bot_token", os.getenv("TOKEN"))
        data.setdefault("admin_pass", os.getenv("ADMIN_PASS"))
        data.setdefault("admin_id", os.getenv("ADMIN_ID"))
        raw_folder = os.getenv("TARGET_FOLDER")
        data.setdefault("target_folder", Path(raw_folder) if raw_folder else None)
        raw_roles = os.getenv("ROLES")
        data.setdefault("user_roles", raw_roles.split(",") if raw_roles else None)
        data.setdefault("proxy_url", os.getenv("PROXY_URL"))
        data.setdefault(
            "use_proxy", os.getenv("USE_PROXY", "").lower() in ("1", "true", "yes")
        )
        data.setdefault(
            "is_polling", os.getenv("POLLING", "").lower() in ("1", "true", "yes")
        )
        data.setdefault("database_url", os.getenv("DATABASE_URL"))
        debug = data.get("debug", False)
        data.setdefault("log_level", "DEBUG" if debug else "INFO")
        super().__init__(**data)

    @validator("debug")
    def validate_debug_environment(cls, v, values):
        """Нельзя включать debug в production"""
        if v and values.get("environment") == "production":
            raise ValueError("Debug mode cannot be enabled in production environment")
        return v

    @validator("allowed_hosts")
    def ensure_localhost(cls, v, values):
        """Добавляем localhost если нет в production"""
        if values.get("environment") == "production" and "localhost" in v:
            raise ValueError("Production cannot have localhost in allowed_hosts")
        return v

    class Config:
        title = "Application Configuration"
        use_enum_values = True
        validate_assignment = True
        extra = "forbid"


app_settings = AppSettings()
logger.debug(f"App settings {app_settings}")

# Пример использования
if __name__ == "__main__":
    # Создание настроек из словаря
    config_data = {
        "app_name": "MyAwesomeApp",
        "debug": True,
        "log_level": "DEBUG",
        "api_version": "v2",
        "environment": "development",
        "database": {
            "host": "localhost",
            "port": 5432,
            "database": "myapp_db",
            "username": "postgres",
            "password": "postgres123",
        },
        "redis": {"host": "localhost", "port": 6379, "db": 1},
        "extra_config": {"max_workers": 10, "timeout": 30.5, "retry": True},
    }

    try:
        # Инициализация настроек
        settings = AppSettings(**config_data)

        # Доступ к настройкам через атрибуты
        print(f"App: {settings.app_name}")
        print(f"Debug: {settings.debug}")
        print(f"Log level: {settings.log_level}")
        print(f"DB host: {settings.database.host}")
        print(f"DB port: {settings.database.port}")

        if settings.redis:
            print(f"Redis host: {settings.redis.host}")

        # Сериализация в JSON
        json_config = settings.json(indent=2)
        print("\nJSON конфигурация:")
        print(json_config)

        # Сериализация в словарь
        dict_config = settings.dict()
        print(f"\nСловарь: {dict_config.keys()}")

        # Обновление настроек
        settings.debug = False
        print(f"\nDebug после обновления: {settings.debug}")

    except ValidationError as e:
        print(f"Ошибка валидации: {e}")
