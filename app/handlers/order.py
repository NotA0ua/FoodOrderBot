from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app import db
from app.utils.keyboard_builder import pagination, make_keyboard, make_keyboard_with_plus

router = Router()

max_per_page = 2

async def food_categories(message: types.Message, page: int = 0) -> None:
    categories = await db.get_all_categories()
    values = {"category_all": "Всё"}
    if categories:
        for category in categories:
            if category:
                values[f"category_{category}"] = category

    reply_markup = make_keyboard(pagination(values, page, max_per_page, "category")).as_markup()
    await message.answer("Выберите категорию товара:", reply_markup=reply_markup)


async def foods(callback_query: types.CallbackQuery, page: int = 0) -> None:
    category = callback_query.data.removeprefix("category_")
    values = dict()
    if category == "all":
        all_food = await db.get_all_food()
    else:
        all_food = await db.get_all_food_by_category(category)

    for food in all_food:
        values[f"food_{food[0]}"] = f"{food[1]} - {food[2]}₽"

    if db.is_there_admin(callback_query.from_user.id):
        reply_markup = make_keyboard_with_plus(pagination(values, page, max_per_page, "food"), "add_food").as_markup()
    else:
        reply_markup = make_keyboard(pagination(values, page, max_per_page, "food")).as_markup()

    text = (
        f"Список товаров по категории *{category}*: "
        if category != "all"
        else f"Список *всех* товаров: "
    )

    await callback_query.message.edit_text(reply_markup=reply_markup, text=text)


@router.message(Command("order"))
async def categories_handler(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await food_categories(message)


@router.callback_query(F.data.startswith("page_category"))
async def page_categories_handler(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    page = int(callback_query.data.removeprefix("page_category_"))
    await food_categories(callback_query.message, page)


@router.callback_query(F.data.startswith("category"))
async def foods_handler(callback_query: types.CallbackQuery) -> None:
    await foods(callback_query)


@router.callback_query(F.data.startswith("page_category"))
async def foods_page_handler(callback_query: types.CallbackQuery) -> None:
    page = int(callback_query.data.removeprefix("page_category_"))
    await foods(callback_query, page)
