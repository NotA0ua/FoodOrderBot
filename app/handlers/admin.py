from aiogram import Router, types
from aiogram.filters import Command

from app import db

router = Router(name="admin")


@router.message(Command("admins"))
async def admins(message: types.Message) -> None:
    admin = [i[0] for i in await db.get_all_admins()]
    if admin:
        admin_str = ""

        for i in admin:
            adm = await message.bot.get_chat_member(chat_id=i, user_id=i)
            admin_str += f"@{adm.user.username} - `{i}`\n"

        await message.answer(admin_str)
    else:
        await message.answer("Админов нет, но такого быть не может :>")

# @router.message(Command("add_admin"))
# async def add_admin(message: types.Message) -> None:
#