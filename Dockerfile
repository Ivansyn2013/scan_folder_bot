# ---- Стадия сборки с uv ----
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Настройка uv для оптимизации
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock* /app/

# Устанавливаем зависимости
RUN uv sync --frozen --no-dev --no-install-project


# ---- Финальный образ ----
FROM python:3.12-slim AS final

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем переменные окружения для Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Копируем виртуальное окружение из стадии сборки
COPY --from=builder /app/.venv /app/.venv

# Копируем код приложения
COPY . /app

# Создаем непривилегированного пользователя для безопасности
RUN addgroup --system app && adduser --system --group app && \
    chown -R app:app /app
USER app

# Команда для запуска бота
CMD ["alembic", "upgrade", "head"]
