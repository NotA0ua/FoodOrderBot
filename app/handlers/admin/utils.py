from aiogram import types

from app import db, MAX_PER_PAGE
from app.utils.keyboard_builder import pagination, make_keyboard_with_plus


async def admins(message: types.Message, page: int = 0) -> None:
    admins_list = await db.get_all_admins()
    if admins_list:
        values = dict()
        for admin_id in admins_list:
            admin_username = (
                await message.bot.get_chat_member(chat_id=admin_id, user_id=admin_id)
            ).user.username
            values[f"admin_{admin_id}"] = (
                admin_username if admin_username else str(admin_id)
            )

        keyboard = pagination(values, page, MAX_PER_PAGE, "admin")

        await message.answer(
            f"*Список всех админов*:",
            reply_markup=make_keyboard_with_plus(keyboard, "add_admin").as_markup(),
        )
