from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.handlers.user.utils import search_naming

router = Router()

class Search(StatesGroup):
    naming = State()

@router.message(Command("search"))
async def search_handler(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Search.naming)
    await message.answer("🪧 Введите название товара:")

@router.message(Search.naming)
async def search_naming_handler(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await search_naming(message)

@router.callback_query(F.data.startswith("page_search"))
async def page_search_handler(callback_query: types.CallbackQuery) -> None:
    await search_naming(callback_query)