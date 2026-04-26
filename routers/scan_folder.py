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
start_router = Router(name="start_router")


@start_router.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery):
    """Обработчик кнопки отмены"""
    await callback.message.edit_text("❌ Действие отменено")
    await callback.answer()


@start_router.callback_query(F.data.startswith("page:"))
async def pagination_handler(
    callback: CallbackQuery,
    file_cache: FilesCache,
):
    """Обработчик пагинации"""
    _, target, page = callback.data.split(":")
    page = int(page)

    keyboard = await found_files_kb(
        message=callback.message, file_cache=file_cache, target=target, page=page
    )

    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@start_router.callback_query(F.data.startswith("file:"))
async def file_download_handler(
    callback: CallbackQuery,
    file_cache: FilesCache,
):
    """Обработчик выбора файла"""
    file_id = callback.data.split(":")[1]

    # Ищем файл в кэше по ID
    found_file = next((f for f in file_cache.cache if f.id == file_id), None)

    if not found_file:
        await callback.answer("❌ Файл не найден в кэше", show_alert=True)
        return

    file_path = found_file.path
    if not file_path.exists():
        await callback.answer("❌ Файл не найден на диске", show_alert=True)
        return

    await callback.answer("Отправляю файл...")
    await callback.message.answer_document(
        document=FSInputFile(path=file_path, filename=found_file.name)
    )


async def check_user(user, check_list):
    if not check_list:
        logger.error("No users in user list")
        return False
    return True if user in check_list else False


@start_router.message(CommandStart())
async def cmd_start(
    message: Message,
    db_session: Session,
    user_repo: UserRepository,
    request_repo: UserRequestRepository,
    file_cache: FilesCache,
    user_cache: UserCache,
):
    """Обработчик команды /start"""
    # Admin
    admin_welcome = ""

    user = message.from_user.id
    admin_ids = [user.telegram_id for user in user_cache.admin.get_ids()]
    if user in admin_ids:
        admin_welcome = "Внимание, пользователь распознан как администратор"
    logger.debug(
        f"Message from user {message.from_user.first_name} "
        f"User ID {message.from_user.id}"
        f"Message {message.text}"
    )
    # User
    user = message.from_user
    users_ids = [user.telegram_id for user in user_cache.cache]
    check = user.id in users_ids
    if not check:
        await user_cache.update()
        users_ids = [user.telegram_id for user in user_cache.cache]
        new_check = user.id in users_ids
        if not new_check:
            logger.warning(
                f"User {user.id, user.first_name} no register. Send "
                f"message {message.text[:30]}"
            )
            new_user = CustomUser(
                telegram_id=user.id,
                name=user.first_name,
                role_group=UserRole.NOT_REGISTER,
            )
            user_repo.add(new_user)
            await user_cache.update()

    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\nЯ бот. Для  работы "
        f"обатитесь к администратору!\n" + admin_welcome
    )


@start_router.message(Command("files"))
async def files(
    message: Message,
    bot: Bot,
    db_session: Session,
    user_repo: UserRepository,
    request_repo: UserRequestRepository,
    file_cache,
    user_cache,
):
    """Обработчик команды /files"""

    users_ids = [user.telegram_id for user in user_cache.cache]
    authorization = message.from_user.id in users_ids

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
        f"Привет, {message.from_user.first_name}! 👋\nФайлы\n", reply_markup=keyboard
    )
