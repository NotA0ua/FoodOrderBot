from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import KeyboardBuilder, ReplyKeyboardBuilder


def make_keyboard() -> KeyboardBuilder:
    builder = ReplyKeyboardBuilder()

    for index in range(1, 11):
        builder.button(text=f"Set {index}", callback_data=f"set:{index}")

    return builder
