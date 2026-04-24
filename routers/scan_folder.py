from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from loguru import logger
from actions.scan_folder import scan_folder
from keyboards.files_kb import found_files_kb

# Создаем роутер для этого модуля
start_router = Router(name="start_router")


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    logger.debug(
        f"Message from user {message.from_user.first_name}\n"
        f"User ID {message.from_user.id}\n"
        f"Message {message.text}"
    )
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\nЯ бот на aiogram 3.x"
    )


@start_router.message(Command("files"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    files = await scan_folder(target="для")
    keyboard = await found_files_kb(message=message, files=files)
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\nФайлы\т", reply_markup=keyboard
    )
