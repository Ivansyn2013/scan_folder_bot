from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from loguru import logger
from sqlalchemy.orm import Session
from models.repositories import UserRepository, UserRequestRepository
from caches.caches import FilesCache, UserCache
from actions.scan_folder import scan_folder
from keyboards.files_kb import found_files_kb
from .scan_folder import check_user
from aiogram import Bot

# Создаем роутер для этого модуля
admin_router = Router(name="admin_router")



@admin_router.message(Command('admin'))
async def admin(message: Message,
    db_session: Session,
    bot: Bot,
    user_repo: UserRepository,
    request_repo: UserRequestRepository,
    file_cache: FilesCache,
    user_cache: UserCache,):

    """Обработчик команды /admin"""
    user_id = message.from_user.id
    user = await user_repo.get_user_by_id(user_id=user_id)
    if user is None or user.admin is False:
        await message.answer(
            f"Привет, {message.from_user.first_name}! 👋\n"
            f"Вы не зарегистрированы в системе \n"
            f"О Ваших действия будет доложено администратору"
        )
        admins = await user_repo.get_admins()
        await bot.send_message(user_id=admins[0].telegram_id,
                               text=f"Пользователь {message.from_user.first_name} {message.from_user.last_name} ({message.from_user.username}) не зарегистрирован в системе")
        return

    await message.answer(
        f"Привет! {message.from_user.first_name}! "
        f"Сегодня пользователей: {len(user_repo.get_all())}"
        f"👋"
    )


@admin_router.message(Command("files"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    files = await scan_folder(target="для")
    keyboard = await found_files_kb(message=message, files=files)
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\nФайлы\т", reply_markup=keyboard
    )
