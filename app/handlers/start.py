from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router(name="start")

@router.message(CommandStart)
async def start(message: types.Message) -> None:
    await message.answer(f"Hello, *{message.from_user.full_name}*!")
