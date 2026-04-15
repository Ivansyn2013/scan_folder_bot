import asyncio
import logging
import os
from aiogram.types import FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from colorama import Fore, Style
from create_obj import bot
from aiogram.methods import DeleteWebhook


DEBUG = os.getenv('DEBUG')
POLLING = os.getenv('POLLING')

WEB_SERVER_HOST = os.getenv('WEB_SERVER_HOST')
WEB_SERVER_PORT = os.getenv('WEB_SERVER_PORT')

WEBHOOK_PATH = os.getenv('WEBHOOK_PATH')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PORT = os.getenv("WEBHOOK_PORT")
WEBHOOK_SSL_CERT = os.getenv('WEBHOOK_SSL_CERT')
WEBHOOK_SSL_PRIV = os.getenv('WEBHOOK_SSL_PRIV')

logger = logging.getLogger(__name__)


async def on_startup():
    global kb_list

    logger.info('Бот загрузился')
    logger.info(
        'Соединение с базой' + f"{Fore.GREEN}{Style.DIM}{str(db_test_connect)}" if
        db_test_connect else  f"{Fore.RED}{Style.DIM}{str(db_test_connect)}" + Fore.RESET
    )
    logger.debug('Переменная DEBUG =' + str(DEBUG))

    # dp.outer_middleware.setup(CheckUserMiddleware())
    if DEBUG == "False":
        logger.info('Webhook mode start set.webhook')
        logger.info(f'Set webhook: {WEBHOOK_URL}:{WEBHOOK_PORT}{WEBHOOK_PATH}')
        await bot.set_webhook(f"{WEBHOOK_URL}:{WEBHOOK_PORT}{WEBHOOK_PATH}",
                              secret_token=WEBHOOK_SECRET,
                              drop_pending_updates=True,
                              )



async def on_shutdown():
    logging.info('Shutting down..')
    # insert code here to run it before shutdown
    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()
    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.info('Bye!')


from handlers import cliet_part, admin, other, inline_mode, tmp

cliet_part.register_handlers_client(dp)

admin.register_handlers_admin(dp)

inline_mode.register_handlers_inline(dp)

# для записи сообщений которые не ловятся хенжлерами
# пустой хендлер должен быть последним
other.register_handlers_other(dp)

#tmp.register_tmp_handlers(dp)


async def main():

    if POLLING:
        logging.basicConfig(level=logging.DEBUG)
        logging.warning('Режим pollong')
        await bot(DeleteWebhook(drop_pending_updates=True))
        await dp.start_polling(
            bot,
            skip_updates=True,
            on_startup=on_startup,
            on_shutdown=on_shutdown
        )
    else:
        logging.basicConfig(level=logging.INFO)
        logging.warning('Режим webhook')

        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)

        app = web.Application()

        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=WEBHOOK_SECRET
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

if __name__ == '__main__':
    asyncio.run(main())
