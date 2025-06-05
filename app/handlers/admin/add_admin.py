from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app import db

from .utils import admins


class AddAdmin(StatesGroup):
    add_admin = State()


router = Router()


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
