from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

from caches.caches import FilesCache, UserCache
from keyboards.admin_kb import user_mod_kb, users_kb, admin_kb
from models.repositories import UserRepository, UserRequestRepository
from models.users import UserRole

# Создаем роутер для этого модуля

admin_router = Router(name="admin_router")


@admin_router.message(Command("admin"))
async def admin(
    message: Message,
    db_session: Session,
    bot: Bot,
    user_repo: UserRepository,
    request_repo: UserRequestRepository,
    file_cache: FilesCache,
    user_cache: UserCache,
):
    """Обработчик команды /admin"""
    user_id = message.from_user.id
    user = user_repo.get_by_telegram_id(user_id)

    if user is None or user.admin is False:
        await message.answer(
            f"Привет, {message.from_user.first_name}! 👋\n"
            f"Вы не зарегистрированы в системе \n"
            f"О Ваших действия будет доложено администратору"
        )
        admins = user_repo.get_admins()
        await bot.send_message(
            chat_id=admins[0].telegram_id,
            text=f"Пользователь {message.from_user.first_name} {message.from_user.last_name} ({message.from_user.username}) не зарегистрирован в системе",
        )
        return

    await message.answer(
        text=f"Привет! {message.from_user.first_name}! "
        f"Сегодня пользователей: {len(user_repo.get_all())}"
        f"👋",
        reply_markup=await admin_kb(),
    )


@admin_router.callback_query(F.data.startswith("show_"))
async def admin_user_show_callback(
    callback: CallbackQuery,
    db_session: Session,
    bot: Bot,
    user_repo: UserRepository,
    request_repo: UserRequestRepository,
    file_cache: FilesCache,
    user_cache: UserCache,
):
    user_id = callback.from_user.id
    user = user_repo.get_by_telegram_id(user_id)

    if user is None or user.admin is False:
        await callback.message.answer(
            f"Привет, {callback.from_user.first_name}! 👋\n"
            f"Вы не зарегистрированы в системе \n"
            f"О Ваших действия будет доложено администратору"
        )
        admins = user_repo.get_admins()
        await bot.send_message(
            chat_id=admins[0].telegram_id,
            text=f"Пользователь {callback.from_user.first_name} {callback.from_user.last_name} ({callback.from_user.username}) не зарегистрирован в системе",
        )
        return

    data = callback.data.split("show_")[1]

    await callback.message.answer(
        text=f"Действия с пользвателями {data}", reply_markup=await users_kb(data)
    )


@admin_router.callback_query(F.data.startswith("user_mod_do_staff"))
async def admin_user_mod_staff_callback(
    callback: CallbackQuery,
    db_session: Session,
    bot: Bot,
    user_repo: UserRepository,
    request_repo: UserRequestRepository,
    file_cache: FilesCache,
    user_cache: UserCache,
):
    user_id = callback.from_user.id
    user = user_repo.get_by_telegram_id(user_id)

    if user is None or user.admin is False:
        await callback.message.answer(
            f"Привет, {callback.from_user.first_name}! 👋\n"
            f"Вы не зарегистрированы в системе \n"
            f"О Ваших действия будет доложено администратору"
        )
        admins = user_repo.get_admins()
        await bot.send_message(
            chat_id=admins[0].telegram_id,
            text=f"Пользователь {callback.from_user.first_name} {callback.from_user.last_name} ({callback.from_user.username}) не зарегистрирован в системе",
        )
        return

    user_id = int(callback.data.split("user_mod_do_staff_")[1])
    user = user_repo.get(user_id)
    user_repo.update(user_id, {"role_group": UserRole.STAFF})
    db_session.commit()
    await callback.answer("Пользователь добавлен в staff")


@admin_router.callback_query(F.data.startswith("user_"))
async def admin_user_callback(
    callback: CallbackQuery,
    db_session: Session,
    bot: Bot,
    user_repo: UserRepository,
    request_repo: UserRequestRepository,
    file_cache: FilesCache,
    user_cache: UserCache,
):
    user_id = callback.from_user.id
    user = user_repo.get_by_telegram_id(user_id)

    if user is None or user.admin is False:
        await callback.message.answer(
            f"Привет, {callback.from_user.first_name}! 👋\n"
            f"Вы не зарегистрированы в системе \n"
            f"О Ваших действия будет доложено администратору"
        )
        admins = user_repo.get_admins()
        await bot.send_message(
            chat_id=admins[0].telegram_id,
            text=f"Пользователь {callback.from_user.first_name} {callback.from_user.last_name} ({callback.from_user.username}) не зарегистрирован в системе",
        )
        return

    user_id = int(callback.data.split("user_")[1])
    user = user_repo.get(user_id)
    await callback.message.answer(
        text="Действия с пользвоателем", reply_markup=await user_mod_kb(user)
    )
