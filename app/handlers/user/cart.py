from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app import db, MAX_PER_PAGE
from app.utils.keyboard_builder import pagination, make_keyboard_row

router = Router()

class CartOrder(StatesGroup):
    comment = State()



@router.message(Command("cart"))
async def cart_handler(message_callback: types.Message | types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if isinstance(message_callback, types.Message):
        message = message_callback
        user_id = int(message.from_user.id)
    else:
        message = message_callback.message
        user_id = int(message_callback.from_user.id)

    orders = await db.get_all_orders(user_id)
    values = dict()
    total_price = 0
    if orders:
        for order in orders:
            food = await db.get_food(order[1])
            if food:
                total_price += food[2] * order[2]
                food_name = food[0]
                values[f"cart_delete_{order[0]}"] = f"{order[2]} - {food_name}"
            else:
                await db.delete_order(order[0])

    values["cart_order"] = "💸"
    values["cart_all_delete"] = "🗑️"

    reply_markup = make_keyboard_row(
        pagination(values, 0, MAX_PER_PAGE, "cart")
    ).as_markup()

    await message.answer(f"Ваша корзина (общая стоимость - {total_price}₽):", reply_markup=reply_markup)


@router.callback_query(F.data.startswith("cart_delete"))
async def cart_delete_handler(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    order_id = callback_query.data.removeprefix("cart_delete_")
    if await db.get_order_by_id(order_id):
        result = await db.delete_order(order_id)
        if result:
            await callback_query.message.answer("*Заказ успешно удален!*")
            await cart_handler(callback_query, state)
            await callback_query.message.delete()
        else:
            await callback_query.message.answer(
                "*Что-то пошло не так!*\nПопробуйте еще раз"
            )
    else:
        await callback_query.message.answer("Такого заказа больше *нет*!")
        await cart_handler(callback_query, state)
        await callback_query.message.delete()

@router.callback_query(F.data == "cart_order")
async def cart_order_handler(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    if await db.get_all_orders(callback_query.from_user.id):
        await state.set_state(CartOrder.comment)
        await callback_query.message.answer("Введите комментарий админу (данные для заказа)")
    else:
        await callback_query.message.answer("У вас нет заказов!")
        await callback_query.message.delete()


@router.message(CartOrder.comment)
async def cart_order_comment_handler(message: types.Message) -> None:
    order_text = str()
    counter = 0
    for order in await db.get_all_orders(message.from_user.id):
        food = await db.get_food(order[1])
        food_naming = food[0]
        order_text += f"{order[2]} - {food_naming} ({food[2]}₽)\n"
        counter += order[2] * food[2]

    user_info = f"Пользователь{' @' + message.from_user.username + ' ' if message.from_user.username else ' '}*{message.from_user.full_name}*(`{message.from_user.id}`).\nЗаказ на сумму - `{counter}`₽.\n\n"
    user_message = f"Сообщение пользователя: _{message.text}_\n\n"

    text = user_info + user_message + order_text

    for admin in await db.get_all_admins():
        await message.bot.send_message(admin, text)

    await db.delete_all_orders(message.from_user.id)


@router.callback_query(F.data == "cart_all_delete")
async def cart_all_delete(callback_query: types.CallbackQuery) -> None:
    result = await db.delete_all_orders(callback_query.from_user.id)
    if result:
        await callback_query.message.answer("Все заказы удалены!")
        await callback_query.message.delete()

    else:
        await callback_query.message.answer("Что-то пошло не так или у вас нет заказов!")
        await callback_query.message.delete()
