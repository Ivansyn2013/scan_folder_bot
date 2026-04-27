import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.methods import DeleteWebhook
from loguru import logger

from caches import file_cache, user_cache
from middleware.db_middleware import DatabaseMiddleware
from models.repositories import UserRepository
from models.users import CustomUser, UserRole
from routers.admin_panel import admin_router
from routers.any_messages import any_mess_router
from routers.scan_folder import start_router
from settings.settings import app_settings

logger.remove()
# Добавляем свой обработчик с нужным уровнем логирования
logger.add(
    sys.stderr,  # Вывод в stderr
    level=app_settings.log_level,  # Уровень логирования
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)


async def main():

    if app_settings.use_proxy:
        session = AiohttpSession(proxy=app_settings.proxy_url)
        bot = Bot(token=app_settings.bot_token, session=session)
        logger.info(f"Using proxy: {app_settings.proxy_url} ")
    else:
        bot = Bot(token=app_settings.bot_token)
        logger.info("Not using proxy")

    # Dispatch handlers
    dp = Dispatcher()

    # ROUTERS
    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(any_mess_router)

    # MIDDLEWARE
    # dp.update.middleware(DatabaseMiddleware())
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())

    async def on_startup():
        from models.sessions import db_manager

        logger.info("Бот загрузился")
        await file_cache.initialize()
        await user_cache.initialize()
        logger.info(f"Loaded caches {file_cache}")
        logger.info(f"Loaded User cache {user_cache}")

        session = db_manager.get_session()
        try:
            user_repo = UserRepository(session)
            admin = user_repo.get_by_telegram_id(app_settings.admin_id)
            if not admin:
                logger.info("Admin user not found")
                admin = CustomUser(
                    name="admin",
                    admin=True,
                    role_group=UserRole.ADMIN,
                    telegram_id=app_settings.admin_id,
                )
                user_repo.add(admin)
                session.commit()
                logger.info(
                    f"Admin user created successfully t_id :{app_settings.admin_id}"
                )
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

        # logger.info(
        #     'Соединение с базой' + f"{Fore.GREEN}{Style.DIM}{str(db_test_connect)}" if
        #     db_test_connect else f"{Fore.RED}{Style.DIM}{str(db_test_connect)}" + Fore.RESET
        # )

    async def on_shutdown():
        logger.info("Выключение бота...")
        # insert code here to run it before shutdown
        # Remove webhook (not acceptable in some cases)
        if not app_settings.is_polling:
            await bot.delete_webhook()
        # Close DB connection (if used)
        await dp.storage.close()
        await dp.storage.wait_closed()
        logger.info("Бай!")

    if app_settings.is_polling:
        logger.info("Режим pollong")
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        await bot(DeleteWebhook(drop_pending_updates=True))
        await dp.start_polling(bot, skip_updates=True)
    # else:
    #     logger.warning("Режим webhook")
    #     dp.startup.register(on_startup)
    #     dp.shutdown.register(on_shutdown)
    #     app = web.Application()
    #     webhook_requests_handler = SimpleRequestHandler(
    #         dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET
    #     )
    #     webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    #     setup_application(app, dp, bot=bot)
    #     try:
    #         web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
    #     except Exception as e:
    #         print(e)
    #         print(f" host={WEB_SERVER_HOST}")
    #         print(f" port{WEB_SERVER_PORT}")
    #         print(f" path={WEBHOOK_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
