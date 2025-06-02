from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from app import db
from app.utils.keyboard_builder import pagination

router = Router()

max_per_page = 2

async def food_categories(message: types.Message, page: int = 0) -> None:
    categories = await db.get_all_categories
    values = {"category_all": "Всё"}
    if categories:
        for category in categories:
            values[f"category_{category}"] = category

    reply_markup = pagination(values, page, max_per_page).as_markup()
    await message.answer("Выберите категорию товара:", reply_markup=reply_markup)

async def foods(callback_query: CallbackQuery, page: int = 0) -> None:
    category = callback_query.data.removeprefix("category_")
    values = dict()
    if category == "all":
        all_food = await db.get_all_food()
    else:
        all_food = await db.get_all_food_by_category(category)

    for food in all_food:
        values[f"food_{food[0]}"] = f"{food[1]} - {food[2]}₽"

    reply_markup = pagination(values, page, max_per_page).as_markup()
    text = f"Список товаров по категории *{category}*: " if category != "all" else f"Список *всех* товаров: "

    await callback_query.message.edit_text(reply_markup=reply_markup, text=text)

@router.message(Command("order"))
async def order_handler(message: types.Message) -> None:
    await food_categories(message)


@router.callback_query(F.data.startswith("category"))
async def foods_handler(callback_query: CallbackQuery) -> None:
    await foods(callback_query)