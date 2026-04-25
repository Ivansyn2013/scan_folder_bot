# Scan Folder Bot

Telegram bot for scanning folders and sending files (Excel files) to users with search and pagination features.

## Features
- Scan directory for `.xlsx` files.
- Search files by name.
- Pagination for file list.
- User authorization system.
- Docker support with PostgreSQL.
- Database migrations with Alembic.

## Prerequisites
- Python 3.12+
- Docker and Docker Compose (optional, for containerized deployment)
- [uv](https://github.com/astral-sh/uv) (recommended for local development)

## Setup and Installation

### 1. Configuration
Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
```
Edit `.env` and set:
- `TOKEN`: Your Telegram Bot Token.
- `ADMIN_ID`: Your Telegram ID.
- `TARGET_FOLDER`: Path to the folder you want to scan.

### 2. Using Docker (Recommended)
The easiest way to start the project is using Docker Compose:
```bash
docker-compose up -d --build
```
This will:
- Start a PostgreSQL database.
- Run database migrations automatically.
- Start the bot.

### 3. Local Installation
If you prefer to run it locally:

1. Install dependencies:
   ```bash
   uv sync
   ```
2. Run database migrations:
   ```bash
   alembic upgrade head
   ```
3. Start the bot:
   ```bash
   python main.py
   ```

## Database Migrations (Alembic)

To manage database schema changes, use the following commands:

- **Create a new migration:**
  ```bash
  alembic revision --autogenerate -m "description of changes"
  ```
- **Apply migrations to the latest version:**
  ```bash
  alembic upgrade head
  ```
- **Rollback one migration:**
  ```bash
  alembic downgrade -1
  ```

## Bot Commands
- `/start` - Register or wake up the bot.
- `/files` - Show available files (requires authorization).
- Any text - Search for files by name.

## Project Structure
- `actions/` - Core logic for scanning folders.
- `models/` - SQLAlchemy models and repositories.
- `routers/` - Telegram handlers (aiogram).
- `keyboards/` - Inline keyboards and pagination.
- `caches/` - In-memory caches for users and files.
- `migrations/` - Alembic migration scripts.