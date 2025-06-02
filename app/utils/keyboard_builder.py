from aiogram.utils.keyboard import (
    KeyboardBuilder,
    InlineKeyboardBuilder,
    InlineKeyboardButton,
)


def make_keyboard(values: dict[str, str]) -> KeyboardBuilder:
    builder = InlineKeyboardBuilder()

    keys = list(values.keys())

    for i in range(0, len(keys), 2):
        if i == len(keys) - 1:
            builder.row(
                InlineKeyboardButton(text=values[keys[i]], callback_data=keys[i]),
                width=2,
            )
        else:
            builder.row(
                InlineKeyboardButton(text=values[keys[i]], callback_data=keys[i]),
                InlineKeyboardButton(
                    text=values[keys[i + 1]], callback_data=keys[i + 1]
                ),
                width=2,
            )

    return builder


def make_keyboard_for_admin(values: dict[str, str]) -> KeyboardBuilder:
    builder = make_keyboard(values)

    builder.row(InlineKeyboardButton(text="➕", callback_data="add_admin"), width=1)

    return builder


def pagination(
    values: dict[str, str], page: int, max_per_page: int
) -> KeyboardBuilder:
    new_values = dict()

    values = new_values

    keys = list(values.keys())

    max_page_div = len(keys) // max_per_page
    max_page_mod = len(keys) % max_per_page
    if len(keys) <= max_per_page:
        return make_keyboard_for_admin(values)
    else:
        new_values = dict()
        if page == 0:
            for key in keys[0:max_per_page]:
                new_values[key] = values[key]
            new_values[f"page_{page+1}"] = "⏩"

        elif page == max_page_div and max_page_mod != 0:
            for key in keys[page * max_per_page :]:
                new_values[key] = values[key]
            new_values[f"page_{page-1}"] = "⏪"

        else:
            for key in keys[page * max_per_page : (page + 1) * max_per_page]:
                new_values[key] = values[key]

                new_values[f"page_{page-1}"] = "⏪"
                new_values[f"page_{page+1}"] = "⏩"

        return make_keyboard_for_admin(new_values)
