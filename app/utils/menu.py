import logging

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from app import db

user_commands = [
    BotCommand(command="start", description="Перезапустить бота"),
    BotCommand(command="order", description="Заказать товар"),
    BotCommand(command="cart", description="Показать корзину"),
]
admin_commands = user_commands + [
    BotCommand(command="admin", description="Добавить админа"),
    BotCommand(command="admins", description="Показать всех админов"),
    BotCommand(command="foods", description="Показать все товары"),
    BotCommand(command="add_food", description="Добавить товар"),
    BotCommand(command="edit_food", description="Изменить товар"),
    BotCommand(command="delete_food", description="Удалить товар"),
]


async def add_menu(bot: Bot):
    await bot.set_my_commands(user_commands, BotCommandScopeDefault())

    admins = await db.get_all_admins()
    if admins is not None:
        for admin in admins:
            await bot.set_my_commands(
                admin_commands, BotCommandScopeChat(chat_id=admin[0])
            )
    logging.log(level=logging.INFO, msg="Yep")