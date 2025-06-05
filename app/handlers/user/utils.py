import logging

from aiogram import types

from app import db
from app.utils.keyboard_builder import make_keyboard, pagination

MAX_PER_PAGE = 2


async def food_categories(message: types.Message, page: int = 0) -> None:
    categories = await db.get_all_categories()
    values = {"page_food_all_0": "Всё"}
    if categories:
        for category in categories:
            if category:
                values[f"page_food_{category}_0"] = category

    reply_markup = make_keyboard(
        pagination(values, page, MAX_PER_PAGE, "category")
    ).as_markup()
    await message.answer("Выберите категорию товара:", reply_markup=reply_markup)


async def foods(callback_query: types.CallbackQuery) -> None:
    category, page = callback_query.data.removeprefix("page_food_").split("_")
    values = dict()
    if category == "all":
        all_food = await db.get_all_food()
    else:
        all_food = await db.get_all_food_by_category(category)

    for food in all_food:
        values[f"food_{food[0]}"] = f"{food[1]} - {food[2]}₽"

    reply_markup = make_keyboard(
        pagination(values, int(page), MAX_PER_PAGE, f"food_{category}")
    ).as_markup()

    text = (
        f"Список товаров по категории *{category}*: "
        if category != "all"
        else f"Список *всех* товаров: "
    )

    await callback_query.message.edit_text(reply_markup=reply_markup, text=text)


async def food_profile(callback_query: types.CallbackQuery) -> None:
    food_id = callback_query.data.removeprefix("food_")
    food = await db.get_food(food_id)
    if not food:
        await callback_query.message.answer("Такого товара нет!")
        return None

    food_naming = food[0]
    food_description = food[1]
    food_price = food[2]
    food_image = food[3]
    food_category = food[4]

    if food_description:
        food_description = f"_{food_description}_"
    else:
        food_description = ""

    if not food_category:
        food_category = "all"

    text = f"""
*{food_naming}* - {food_price}₽
{food_description}
"""
    reply_markup = make_keyboard({f"page_food_{food_category}_0": "🔙"}).as_markup()


    if food_image:
        food_image = types.URLInputFile(food_image)
        await callback_query.message.answer_document(food_image, caption=text, reply_markup=reply_markup)
        return None

    await callback_query.message.answer(text, reply_markup=reply_markup)
    return None
