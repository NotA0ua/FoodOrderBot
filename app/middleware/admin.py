import logging
from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app import db


class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        admins = await db.get_all_admins()

        if event.from_user.id in admins:
            return await handler(event, data)
        else:
            return None
