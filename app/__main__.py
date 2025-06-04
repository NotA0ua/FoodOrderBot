import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.methods import DeleteWebhook

from app import db
from app.env import BOT_TOKEN
from app.handlers import router
from app.middleware import ThrottlingMiddleware
from app.utils.menu import add_menu

dp = Dispatcher()
dp.include_routers(router)

dp.message.middleware(ThrottlingMiddleware())
dp.callback_query.middleware(ThrottlingMiddleware())


async def on_stop(bot: Bot) -> None:
    logging.log(level=logging.INFO, msg="Shutdown requested")
    await db.close()


async def main() -> None:
    await db.connect()

    bot = Bot(
        token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    await bot(DeleteWebhook(drop_pending_updates=True))

    dp.shutdown.register(on_stop)

    await add_menu(bot)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
