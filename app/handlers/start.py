from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router(name="start")


@router.message(CommandStart())
async def start(message: types.Message) -> None:
    await message.answer(f"Здравствуйте, {message.from_user.full_name}, я бот для заказа еды!\nНапишите /order, чтобы что-то заказать.")
