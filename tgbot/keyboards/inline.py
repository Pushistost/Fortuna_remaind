from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from infrastructure.sqlite.requests import get_reminders, check_remind_sql


# from infrastructure.sqlite.requests import get_categories, get_category_item


async def yes_or_no_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="📝 добавить запись",
        callback_data="add_note"
    )
    keyboard.button(
        text="📋 отмена",
        callback_data="abolition"
    )

    keyboard.adjust(2)

    return keyboard.as_markup()


# Как один из вариантов показа записей:
async def reminders():
    all_reminders = await get_reminders()

    keyboard = InlineKeyboardBuilder()

    for remind in all_reminders:
        keyboard.add(InlineKeyboardButton(text=f"ID: {remind.id} | DATA: {remind.time.strftime('%b-%d %H:%M')}"
                                               f" | TEXT: {remind.text}", callback_data=f"remind_{remind.id}"))

    keyboard.add(InlineKeyboardButton(text="На обратно", callback_data="back_to_menu"))

    return keyboard.adjust(1).as_markup()


async def ready_reminders():
    all_reminders = await check_remind_sql()

    if all_reminders:

        keyboard = InlineKeyboardBuilder()

        for remind in all_reminders:
            keyboard.add(InlineKeyboardButton(text=f"ID: {remind.id} | DATA: {remind.time.strftime('%b-%d %H:%M')}"
                                                   f" | TEXT: {remind.text}", callback_data=f"remind_{remind.id}"))

        keyboard.add(InlineKeyboardButton(text="На обратно", callback_data="back_to_menu"))

        return keyboard.adjust(1).as_markup()

    return None
#
#
# async def items(category_item):
#     all_items = await get_category_item(category_item)
#
#     keyboard = InlineKeyboardBuilder()
#
#     for item in all_items:
#         keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f"item_{item.id}"))
#
#     keyboard.add(InlineKeyboardButton(text="На главную", callback_data="back_to_menu"))
#
#     return keyboard.adjust(3).as_markup()