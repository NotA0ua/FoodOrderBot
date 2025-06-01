from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app import db
from app.utils.keyboard_builder import pagination

router = Router(name="admin")

max_per_page = 2

class AddAdmin(StatesGroup):
    add_admin = State()

@router.message(Command("admin"))
async def admins(message: types.Message, page: int = 0) -> None:
    admins_list = [i[0] for i in await db.get_all_admins()]
    if admins_list:
        values = dict()
        for admin_id in admins_list:
            admin_username = (await message.bot.get_chat_member(chat_id=admin_id, user_id=admin_id)).user.username
            values[str(admin_id)] = admin_username if admin_username else str(admin_id)

        keyboard = pagination(values, page, max_per_page, "admin")

        await message.answer("*Список всех админов*:", reply_markup=keyboard.as_markup())
    else:
        await message.answer("Админов нет, но такого быть не может :>")

@router.callback_query(F.data.contains("page"))
async def callback_admin(callback_query: types.CallbackQuery) -> None:
    page = int(callback_query.data[4:])
    
    await callback_query.message.delete()
    await admins(callback_query.message, page)

@router.callback_query(F.data == "add_admin")
async def add_admin(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AddAdmin.add_admin)
    await callback_query.message.edit_text(reply_markup=None, text="Введите *ID* админа")

@router.message(AddAdmin.add_admin)
async def enter_admin_id(message: types.Message, state: FSMContext) -> None:
    if message.text.isdigit():
        admin_id = int(message.text)
        await db.add_admin(admin_id)
        await state.clear()
        await message.delete()
        await admins(message)
    else:
        await message.answer("*Вы неправильно ввели пользователя!*\nВведите пользователя еще раз или нажмите /start")
