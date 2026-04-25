from aiogram.utils.keyboard import InlineKeyboardBuilder
from pathlib import Path
from typing import List
from caches.caches import FilesCache
from loguru import logger

async def found_files_kb(
        message,
        file_cache: FilesCache,
        target:str,
        page: int = 0,
        items_per_page: int = 5
):
    if not file_cache.cache:
        await message.answer("❌ Файлы не найдены")
        return

    files = [f for f in file_cache.cache if target.lower() in f.name.lower()]
    logger.debug(f"Target is '{target}' Found files {files} in all files {len(file_cache.cache)}")
        # Расчет пагинации
    total_pages = (len(files) + items_per_page - 1) // items_per_page
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(files))
    current_files = files[start_idx:end_idx]

    builder = InlineKeyboardBuilder()

    # Добавляем кнопки с файлами
    for _file in current_files:
        builder.button(
            text=f"📄 {_file.name[:50]}",
            callback_data=f"{_file.id}",
        )

    # Добавляем кнопки навигации
    if page > 0:
        builder.button(text="◀️ Назад", callback_data=f"page_{page - 1}")
    if page < total_pages - 1:
        builder.button(text="Вперед ▶️", callback_data=f"page_{page + 1}")

    # Добавляем кнопку отмены
    builder.button(text="❌ Отмена", callback_data="cancel")

    # Настраиваем расположение: все кнопки по одной в ряд
    builder.adjust(1)

    return builder.as_markup()
