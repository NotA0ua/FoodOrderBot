from aiogram import Bot
from aiogram.types import BotCommand

user_commands = [BotCommand(command="start", description="Перезапустить бота"),]
admin_commands = user_commands + []

async def add_menu(bot: Bot):
    await bot.set_my_commands(user_commands, defa)