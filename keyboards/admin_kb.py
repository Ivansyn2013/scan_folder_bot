from aiogram.utils.keyboard import InlineKeyboardBuilder

from models.repositories import UserRepository
from models.sessions import db_manager


async def admin_kb():

    builder = InlineKeyboardBuilder()

    # Добавляем кнопки с файлами

    # Добавляем кнопку отмены
    builder.button(text="Пользователи staff", callback_data="show_staff")
    builder.button(text="Пользователи admin", callback_data="show_admin")
    builder.button(text="Пользователи not_reg", callback_data="show_NOT_REGISTER")
    builder.button(text="❌ Отмена", callback_data="cancel")

    # Настраиваем расположение: все кнопки по одной в ряд
    builder.adjust(1)

    return builder.as_markup()


async def users_kb(role_grop, page: int = 0, items_per_page: int = 5):
    """
    Generates an inline keyboard with user data and navigation buttons based on the
    provided pagination parameters.

    This asynchronous function creates a paginated inline keyboard for users.
    It retrieves user data from the repository, calculates the specific set of users
    to display based on the current page and items per page, and adds appropriate
    navigation buttons to navigate between pages or cancel the operation.

    :param page: The current page number for pagination. Default is 0.
    :type page: int
    :param items_per_page: The number of users to display per page. Default is 5.
    :type items_per_page: int
    :return: An inline keyboard markup containing user data and navigation buttons.
    :rtype: Any
    """
    session = db_manager.get_session()
    user_repo = UserRepository(session)
    users = user_repo.get_by_role_group(role_grop)

    # Расчет пагинации
    total_pages = (len(users) + items_per_page - 1) // items_per_page
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(users))
    current_users = users[start_idx:end_idx]

    builder = InlineKeyboardBuilder()

    # Добавляем кнопки с файлами
    for user in current_users:
        builder.button(
            text=f"📄 {user.name[:50]}",
            callback_data=f"user_{user.id}",
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


async def user_mod_kb(user):
    builder = InlineKeyboardBuilder()

    # builder.button(text="◀️ Назад", callback_data=f"user_mod_")
    builder.button(
        text="Добавить в пользователя️", callback_data=f"user_mod_do_staff_{user.id}"
    )

    # Добавляем кнопку отмены
    builder.button(text="❌ Отмена", callback_data="cancel")

    # Настраиваем расположение: все кнопки по одной в ряд
    builder.adjust(1)

    return builder.as_markup()
