import asyncio
from loguru import logger
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram.client.session.aiohttp import AiohttpSession
from settings.settings import app_settings
from routers.scan_folder import start_router
import sys

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

    dp.include_router(start_router)

    async def on_startup():

        logger.info("Бот загрузился")
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
        await bot(DeleteWebhook(drop_pending_updates=True))
        await dp.start_polling(
            bot, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown
        )
    else:
        logger.warning("Режим webhook")
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        try:
            web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
        except Exception as e:
            print(e)
            print(f" host={WEB_SERVER_HOST}")
            print(f" port{WEB_SERVER_PORT}")
            print(f" path={WEBHOOK_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
