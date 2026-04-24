 # ---- Базовый образ для финального контейнера ----
# Используем slim-версию для минимального размера
FROM python:3.12-slim AS final

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем переменные окружения для Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Устанавливаем необходимые системные зависимости (если нужны)
# RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Копируем зависимости проекта из стадии сборки
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Копируем код приложения
COPY --chown=app:app . /app

# Создаем непривилегированного пользователя для безопасности
RUN addgroup --system app && adduser --system --group app
USER app

# Активируем виртуальное окружение
ENV PATH="/app/.venv/bin:$PATH"

# Команда для запуска бота
CMD ["python", "-m", "bot"]  # замените "bot" на имя вашего главного модуля


# ---- Стадия сборки с uv ----
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Копируем файлы зависимостей
COPY --chown=app:app pyproject.toml uv.lock* /app/

# Устанавливаем зависимости с оптимизациями для продакшена
# --no-dev: не устанавливать dev-зависимости
# --frozen: использовать существующий uv.lock без его обновления
# --no-install-project: не устанавливать сам проект (только зависимости)
RUN uv sync --frozen --no-dev --no-install-project

# Копируем весь проект
COPY --chown=app:app . /app

# Устанавливаем сам проект в виртуальное окружение
RUN uv sync --frozen --no-dev