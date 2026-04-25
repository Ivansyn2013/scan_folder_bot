from pydantic import BaseModel, Field, validator, ValidationError
from typing import List, Dict, Union
import os
from pathlib import Path
from loguru import logger


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
    debug: bool = os.getenv("DEBUG")
    log_level: str = "DEBUG" if debug else "INFO"
    api_version: str = Field(default="v1")
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    environment: str = Field(default="development")
    bot_token: str = os.getenv("TOKEN")
    admin_pass: str = os.getenv("ADMIN_PASS")
    admin_id: str = os.getenv("ADMIN_ID")
    target_folder: Path = Path(os.getenv("TARGET_FOLDER"))
    user_roles: List[str] = os.getenv("ROLES")
    proxy_url: str = os.getenv("PROXY_URL")
    use_proxy: bool = os.getenv("USE_PROXY")
    is_polling: bool = os.getenv("POLLING")
    database_url: str = os.getenv("DATABASE_URL")
    base_dir: Path = Path.cwd().parent

    # Вложенные настройки
    # database: DatabaseSettings

    # Дополнительные параметры
    extra_config: Dict[str, Union[str, int, float, bool]] = Field(default_factory=dict)

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
        # Дополнительные настройки Pydantic
        use_enum_values = True  # Использовать значения enum вместо объектов
        validate_assignment = True  # Валидировать при присваивании
        extra = "forbid"  # Запретить дополнительные поля


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

    # Пример загрузки из JSON файла
    # import json
    # with open('config.json', 'r') as f:
    #     config_json = json.load(f)
    #     settings = AppSettings(**config_json)

    # Пример загрузки из переменных окружения
    # from pydantic import BaseSettings
    #
    # class EnvSettings(BaseSettings):
    #     database_url: str
    #     secret_key: str
    #
    #     class Config:
    #         env_file = ".env"
    #         env_file_encoding = "utf-8"
