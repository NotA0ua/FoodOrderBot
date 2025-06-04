import logging

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app import db
from app.middleware import AdminMiddleware
from app.handlers.order import food_categories

from validators import url


class AddFood(StatesGroup):
    naming = State()
    description = State()
    price = State()
    image = State()
    category = State()


router = Router()
router.message.middleware(AdminMiddleware())
router.callback_query.middleware(AdminMiddleware())


@router.callback_query(F.data == "add_food")
async def add_food_handler(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AddFood.naming)
    await callback_query.message.answer("Введите *имя* товара:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="❌ Отмена")]]))


@router.message(Command("add_food"))
async def add_food_handler(message: types.Message, state: FSMContext) -> None:
    await state.set_state(AddFood.naming)
    await message.answer("Введите *имя* товара:",
                         reply_markup=ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="❌ Отмена")]]))


@router.message(F.text == "❌ Отмена")
async def add_food_cancel_handler(message: types.Message, state: FSMContext) -> None:
    if "AddFood" in await state.storage.get_state(state.key):
        await state.clear()
        new_message = await message.answer("Clear", reply_markup=types.ReplyKeyboardRemove())
        await new_message.delete()
        await food_categories(message)


@router.message(AddFood.naming)
async def add_food_name_handler(message: types.Message, state: FSMContext) -> None:
    await state.update_data({"naming": message.text})
    await state.set_state(AddFood.description)
    await message.answer("Введите *описание* товара.\n(Если нет, то `-`):")


@router.message(AddFood.description)
async def add_food_description_handler(message: types.Message, state: FSMContext) -> None:
    if message.text == "-":
        await state.update_data({"description": None})
    else:
        await state.update_data({"description": message.text})
    await state.set_state(AddFood.price)
    await message.answer("Введите *цену* товара\n(Например 42, 100):")


@router.message(AddFood.price)
async def add_food_price_handler(message: types.Message, state: FSMContext) -> None:
    if message.text.isdigit():
        await state.update_data({"price": message.text})
        await state.set_state(AddFood.image)
        await message.answer("Введите *ссылку на изображение* товара.\n(Если нет, то `-`):")
    else:
        await message.answer("Вы ввели неправильный формат цены!\nПопробуйте ещё раз:")


@router.message(AddFood.image)
async def add_food_image_handler(message: types.Message, state: FSMContext) -> None:
    if message.text == "-":
        await state.update_data({"image": None})
    if url(str(message.text)) or message.text == "-":
        await state.update_data({"image": message.text})
        await state.set_state(AddFood.category)
        await message.answer("Введите *категорию* товара.\n(Если нет, то `-`):")
    else:
        await message.answer("Вы ввели неправильный формат ссылки на изображение!\nПопробуйте ещё раз:")


@router.message(AddFood.category)
async def add_food_category_handler(message: types.Message, state: FSMContext) -> None:
    if message.text == "-":
        await state.update_data({"category": None})
    else:
        await state.update_data({"category": message.text})

    storage = await state.get_data()
    naming = storage["naming"]
    description = storage["description"]
    price = storage["price"]
    image = storage["image"]
    category = storage["category"]

    result = await db.add_food(naming=naming, description=description, price=price, image=image, category=category)
    await state.clear()
    if result:
        await message.answer(f"""
        Отлично, товар создан!
        Название: `{naming}`
        Описание: `{description}`
        Цена: `{price}`
        Ссылка на изображение: `{image}`
        Категория: `{category}`
        """, reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("Ой-ой, что-то пошло не так! Попробуйте еще раз.",
                             reply_markup=types.ReplyKeyboardRemove())
