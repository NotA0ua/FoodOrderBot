from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from app import db

user_commands = [
    BotCommand(command="start", description="Перезапустить бота"),
    BotCommand(command="order", description="Заказать товар"),
    BotCommand(command="cart", description="Показать корзину"),
]
admin_commands = user_commands + [
    BotCommand(command="admin", description="Список админов"),
    BotCommand(command="foods", description="Показать все товары"),
]


async def add_menu(bot: Bot):
    await bot.set_my_commands(user_commands, BotCommandScopeDefault())

    admins = await db.get_all_admins()
    if admins is not None:
        for admin in admins:
            await bot.set_my_commands(
                admin_commands, BotCommandScopeChat(chat_id=admin[0])
            )