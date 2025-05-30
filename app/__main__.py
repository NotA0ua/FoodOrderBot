import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio

from app.env import BOT_TOKEN
from app.handlers import router
from app import db
from app.utils.menu import add_menu

dp = Dispatcher()
dp.include_routers(router)


async def main() -> None:
    await db.connect()

    bot = Bot(
        token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    await add_menu(bot)
    await dp.start_polling(bot)

    await db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
