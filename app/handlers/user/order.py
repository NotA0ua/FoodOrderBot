import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app import db


MAX_ORDERS_AMOUNT = 2

class Order(StatesGroup):
    amount = State()


router = Router()


@router.callback_query(F.data.startswith("order"))
async def order_handler(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    food_id = int(callback_query.data.removeprefix("order_"))
    await state.update_data({"food_id": food_id})
    await state.set_state(Order.amount)
    await callback_query.message.answer(text="Введите количество товара (1-999)")
    await callback_query.message.delete()


@router.message(Order.amount)
async def order_amount_handler(message: types.Message, state: FSMContext) -> None:
    if message.text.isdigit() and (amount := int(message.text)) in range(1, 1000):
        food_id = await state.get_value("food_id")
        order_id = await db.get_order(message.from_user.id, food_id)
        food_naming = (await db.get_food(food_id))[0]
        logging.info(len(await db.get_all_orders(message.from_user.id)))
        if len(await db.get_all_orders(message.from_user.id)) < MAX_ORDERS_AMOUNT:
            if order_id:
                result = await db.update_order(order_id, amount)
            else:
                result = await db.add_order(
                    message.from_user.id, food_id, int(message.text)
                )
        else:
            await message.answer(f"Вы не можете сделать больше {MAX_ORDERS_AMOUNT} заказов!")
            await state.clear()
            return None

        if result:
            await message.answer(
                f"Отлично!\n*{food_naming}* добавлено в количестве `{amount}` шт."
            )
        else:
            await message.answer(f"Что-то пошло не так. Попробуйте еще раз!")
        await state.clear()
    else:
        await message.answer(
            "Вы ввели неправильный формат количества!\nПопробуйте еще раз или напишите /start"
        )

    return None
