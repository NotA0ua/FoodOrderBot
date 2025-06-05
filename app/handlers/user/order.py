from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from .utils import foods, food_categories, food_profile

router = Router()


@router.message(Command("order"))
async def categories_handler(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await food_categories(message)


@router.callback_query(F.data.startswith("page_category"))
async def page_categories_handler(
    callback_query: types.CallbackQuery
) -> None:
    page = int(callback_query.data.removeprefix("page_category_"))
    await food_categories(callback_query.message, page)


@router.callback_query(F.data.startswith("page_food"))
async def foods_page_handler(callback_query: types.CallbackQuery) -> None:
    await foods(callback_query)

@router.callback_query(F.data.startswith("food"))
async def food_page_handler(callback_query: types.CallbackQuery) -> None:
    await food_profile(callback_query)
