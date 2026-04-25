from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from loguru import logger
from sqlalchemy.orm import Session

from actions.scan_folder import scan_folder
from keyboards.files_kb import found_files_kb
from models.repositories import UserRepository, UserRequestRepository

# Создаем роутер для этого модуля
start_router = Router(name="start_router")


async def check_user(user, check_list):
    if not check_list:
        logger.error("No users in user list")
        return False
    return True if user in check_list else False


@start_router.message(CommandStart())
async def cmd_start(message: Message, user_repo: UserRepository):
    """Обработчик команды /start"""
    admin_welcome = ""
    admin = user_repo.get_by_telegram_id(message.from_user.id)
    if admin:
        admin_welcome = "Внимание, пользователь распознан как администратор"
    logger.debug(
        f"Message from user {message.from_user.first_name}\n"
        f"User ID {message.from_user.id}\n"
        f"Message {message.text}"
    )
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\nЯ бот. Я работаю\n"
        + admin_welcome
    )


@start_router.message(Command("files"))
async def cmd_start(
    message: Message,
    db_session: Session,
    user_repo: UserRepository,
    request_repo: UserRequestRepository,
    file_cache,
    user_cache,
):
    """Обработчик команды /start"""
    authorization = await check_user(message.from_user.id, user_cache.cache)

    files = await scan_folder(target="для")
    keyboard = await found_files_kb(message=message, files=files)
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\nФайлы\т", reply_markup=keyboard
    )


@start_router.message()
async def cmd_start(
    message: Message,
    db_session: Session,
    user_repo: UserRepository,
    request_repo: UserRequestRepository,
    file_cache,
    user_cache,
):
    """Любых сообщений"""
    await message.answer("Соббщение не прошло фильтрацию")
