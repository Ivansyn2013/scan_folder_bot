from aiogram.utils.keyboard import InlineKeyboardBuilder
from pathlib import Path
from typing import List


async def found_files_kb(
    message, files: List[Path], page: int = 0, items_per_page: int = 5
):
    if not files:
        await message.answer("❌ Файлы не найдены")
        return

        # Расчет пагинации
    total_pages = (len(files) + items_per_page - 1) // items_per_page
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(files))
    current_files = files[start_idx:end_idx]

    builder = InlineKeyboardBuilder()

    # Добавляем кнопки с файлами
    for file_path in current_files:
        builder.button(
            text=f"📄 {file_path.name[:50]}",
            callback_data=f"file_{file_path.as_posix()[:3]}",
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
