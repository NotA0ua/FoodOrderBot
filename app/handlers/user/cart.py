from aiogram import Router, F, types
from aiogram.filters import Command

from app import db, MAX_PER_PAGE
from app.utils.keyboard_builder import pagination, make_keyboard_row

router = Router()


@router.message(Command("cart"))
async def cart_handler(message_callback: types.Message | types.CallbackQuery) -> None:
    if isinstance(message_callback, types.Message):
        message = message_callback
        user_id = int(message.from_user.id)
    else:
        message = message_callback.message
        user_id = int(message_callback.from_user.id)

    orders = await db.get_all_orders(user_id)
    values = dict()
    if orders:
        for order in orders:
            food = await db.get_food(order[1])
            if food:
                food_name = food[0]
                values[f"cart_delete_{order[0]}"] = f"{order[2]} - {food_name}"
            else:
                await db.delete_order(order[0])

    reply_markup = make_keyboard_row(
        pagination(values, 0, MAX_PER_PAGE, "cart")
    ).as_markup()

    await message.answer("Ваша корзина:", reply_markup=reply_markup)


@router.callback_query(F.data.startswith("cart_delete"))
async def cart_delete_handler(callback_query: types.CallbackQuery) -> None:
    order_id = callback_query.data.removeprefix("cart_delete_")
    if await db.get_order_by_id(order_id):
        result = await db.delete_order(order_id)
        if result:
            await callback_query.message.answer("*Заказ успешно удален!*")
            await cart_handler(callback_query)
            await callback_query.message.delete()
        else:
            await callback_query.message.answer(
                "*Что-то пошло не так!*\nПопробуйте еще раз"
            )
    else:
        await callback_query.message.answer("Такого заказа больше *нет*!")
        await cart_handler(callback_query)
        await callback_query.message.delete()
