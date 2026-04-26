from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, FSInputFile, Message
from loguru import logger
from sqlalchemy.orm import Session

from caches.caches import FilesCache, UserCache
from keyboards.files_kb import found_files_kb
from models.repositories import UserRepository, UserRequestRepository
from models.users import CustomUser, UserRole

# Создаем роутер для этого модуля
any_mess_router = Router(name="any_mess_router")


@any_mess_router.message()
async def any_message(
    message: Message,
    bot: Bot,
    db_session: Session,
    user_repo: UserRepository,
    request_repo: UserRequestRepository,
    file_cache,
    user_cache,
):
    """Любых сообщений"""
    if len(message.text) > 15:
        await message.answer("Сообщение не прошло фильтрацию")
        return

    users_ids = [user.telegram_id for user in user_cache.cache]
    authorization = message.from_user.id in users_ids

    logger.debug(
        f"Message from user {message.from_user.id, message.from_user.first_name}"
    )
    if not authorization:
        await message.answer("У вас нет прав доступа")
        admins = user_repo.get_admins()
        await bot.send_message(
            chat_id=admins[0].telegram_id,
            text=f"User has no access {message.from_user.id, message.from_user.first_name}"
            f"{message.text[:30]}",
        )
        return

        # files = await scan_folder(target="для")
    keyboard = await found_files_kb(
        message=message, file_cache=file_cache, target=message.text[:10]
    )
    await message.answer(
        f"Привет Anymess handleer, {message.from_user.first_name}! 👋\nФайлы\n",
        reply_markup=keyboard,
    )
