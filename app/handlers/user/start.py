from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

router = Router(name="start")


@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        f"👋 Здравствуйте, {message.from_user.full_name}, я бот для заказа еды!\nНапишите /order, чтобы что-то заказать.",
        reply_markup=types.ReplyKeyboardRemove(),
    )
