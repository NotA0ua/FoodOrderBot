from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.utils.keyboard_builder import make_keyboard
from .utils import admins
from ... import db

router = Router(name="admin")


@router.message(Command("admin", "admins"))
async def admins_handler(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await admins(message)


@router.callback_query(F.data.startswith("page_admin"))
async def page_admins_handler(callback_query: types.CallbackQuery) -> None:
    page = int(callback_query.data.removeprefix("page_admin_"))

    await callback_query.message.delete()
    await admins(callback_query.message, page)


@router.callback_query(F.data.startswith("admin"))
async def admin_handler(callback_query: types.CallbackQuery) -> None:
    admin_id = int(callback_query.data[6:])
    admin_username: str = (
        await callback_query.bot.get_chat_member(chat_id=admin_id, user_id=admin_id)
    ).user.username
    await callback_query.message.edit_text(
        text=f"👨‍💻 Админ @{admin_username} - `{admin_id}`",
        reply_markup=make_keyboard(
            {f"delete_admin_{admin_id}": "🗑", "page_admin_0": "🔙"}
        ).as_markup(),
    )


@router.callback_query(F.data.contains("delete_admin"))
async def delete_admin_handler(callback_query: types.CallbackQuery) -> None:
    admin_id = int(callback_query.data[13:])
    await db.delete_admin(admin_id)
    await callback_query.message.delete()
