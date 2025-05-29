from aiogram.utils.keyboard import InlineKeyboardBuilder


def make_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    for index in range(1, 11):
        builder.button(text=f"Set {index}", callback_data=f"set:{index}")

    return builder