from aiogram import types
from aiogram.types import InlineKeyboardButton

from app import db, MAX_PER_PAGE
from app.utils.keyboard_builder import make_keyboard, pagination


async def food_categories(message: types.Message, page: int = 0) -> None:
    categories = await db.get_all_categories()
    values = {"page_food_all_0": "📦 Всё"}
    if categories:
        for category in categories:
            if category:
                values[f"page_food_{category}_0"] = category

    reply_markup = make_keyboard(
        pagination(values, page, MAX_PER_PAGE, "category")
    ).as_markup()
    await message.answer("📋 Выберите категорию товара:", reply_markup=reply_markup)


async def foods(callback_query: types.CallbackQuery) -> None:
    category, page = callback_query.data.removeprefix("page_food_").split("_")
    values = dict()
    if category == "all":
        all_food = await db.get_all_food()
    else:
        all_food = await db.get_all_food_by_category(category)

    for food in all_food:
        values[f"food_{category}_{food[0]}"] = f"{food[1]} - {food[2]}₽"

    reply_markup = (make_keyboard(
        pagination(values, int(page), MAX_PER_PAGE, f"food_{category}")
    ).row(InlineKeyboardButton(text="🔙", callback_data="page_category_0")).as_markup())

    text = (
        f"📋 Список товаров по категории *{category}*: "
        if category != "all"
        else f"📦 Список *всех* товаров: "
    )

    if callback_query.message.photo:
        await callback_query.message.answer(text=text, reply_markup=reply_markup)
        await callback_query.message.delete()
    else:
        await callback_query.message.edit_text(text=text, reply_markup=reply_markup)


async def food_profile(callback_query: types.CallbackQuery) -> None:
    category, food_id = callback_query.data.removeprefix("food_").split("_")
    food = await db.get_food(food_id)
    if not food:
        await callback_query.message.answer("⚠️ Такого товара нет!")
        return None

    naming = food[0]
    description = food[1]
    price = food[2]
    image = food[3]

    if description:
        description = f"_{description}_"
    else:
        description = ""

    text = f"🧺 *{naming}* - {price}₽\n{description}"
    reply_markup = make_keyboard(
        {f"order_{food_id}": "📝", f"page_food_{category}_0": "🔙"}
    ).as_markup()

    if image:
        await callback_query.message.answer_photo(
            image, caption=text, reply_markup=reply_markup
        )
        await callback_query.message.delete()
        return None

    await callback_query.message.edit_text(text, reply_markup=reply_markup)
    return None


async def search_naming(message: types.Message | types.CallbackQuery) -> None:
    if isinstance(message, types.CallbackQuery):
        search, page = message.data.removeprefix("page_search_").split("_")
    else:
        page = 0
        search = message.text

    food_items = await db.get_food_by_naming(search)
    values = dict()
    if food_items:
        for food in food_items:
            values[f"food_all_{food[0]}"] = food[1]

    reply_markup = make_keyboard(pagination(values, int(page), MAX_PER_PAGE, f"search_{search}")).as_markup()

    if isinstance(message, types.CallbackQuery):
        await message.message.edit_text(f"🔍 Список товаров по поиску `{search}`", reply_markup=reply_markup)
    else:
        await message.answer(f"🔍 Список товаров по поиску `{search}`", reply_markup=reply_markup)
