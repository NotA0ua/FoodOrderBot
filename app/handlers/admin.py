from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app import db
from app.middleware import AdminMiddleware
from app.utils.keyboard_builder import (
    pagination,
    make_keyboard, make_keyboard_with_plus,
)

router = Router(name="admin")

router.message.middleware(AdminMiddleware())
router.callback_query.middleware(AdminMiddleware())

max_per_page = 5


class AddAdmin(StatesGroup):
    add_admin = State()


async def admins(message: types.Message, page: int = 0):
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

        keyboard = pagination(values, page, max_per_page, "admin")

        await message.answer(
            f"*Список всех админов*:", reply_markup=make_keyboard_with_plus(keyboard, "add_admin").as_markup()
        )


@router.message(Command("admin", "admins"))
async def admins_handler(message: types.Message) -> None:
    await admins(message)


@router.callback_query(F.data.startswith("page_admin"))
async def page_admins_handler(callback_query: types.CallbackQuery) -> None:
    page = int(callback_query.data.removeprefix("page_admin_"))

    await callback_query.message.delete()
    await admins(callback_query.message, page)


@router.callback_query(F.data == "add_admin")
async def add_admin_handler(
    callback_query: types.CallbackQuery, state: FSMContext
) -> None:
    await state.set_state(AddAdmin.add_admin)
    await callback_query.message.edit_text(
        reply_markup=None, text="Введите *ID* админа:"
    )


@router.message(AddAdmin.add_admin)
async def admin_id_handler(message: types.Message, state: FSMContext) -> None:
    if message.text.isdigit():
        admin_id = int(message.text)
        await db.add_admin(admin_id)
        await state.clear()
        await admins(message)
    else:
        await message.answer(
            "*Вы неправильно ввели пользователя!*\nВведите пользователя еще раз или нажмите /start"
        )


@router.callback_query(F.data.startswith("admin"))
async def admin_handler(callback_query: types.CallbackQuery) -> None:
    admin_id = int(callback_query.data[6:])
    admin_username: str = (
        await callback_query.bot.get_chat_member(chat_id=admin_id, user_id=admin_id)
    ).user.username
    await callback_query.message.edit_text(
        text=f"Пользователь @{admin_username} - `{admin_id}`",
        reply_markup=make_keyboard(
            {f"delete_admin_{admin_id}": "🗑", "page_admin_0": "🔙"}
        ).as_markup(),
    )


@router.callback_query(F.data.contains("delete_admin"))
async def delete_admin_handler(callback_query: types.CallbackQuery) -> None:
    admin_id = int(callback_query.data[13:])
    await db.delete_admin(admin_id)
    await callback_query.message.delete()
