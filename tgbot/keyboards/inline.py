from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from requests import get_categories, get_category_item


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
async def categories():
    all_categories = await get_categories()

    keyboard = InlineKeyboardBuilder()

    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))

    keyboard.add(InlineKeyboardButton(text="На обратно", callback_data="back_to_menu"))

    return keyboard.adjust(3).as_markup()


async def items(category_item):
    all_items = await get_category_item(category_item)

    keyboard = InlineKeyboardBuilder()

    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f"item_{item.id}"))

    keyboard.add(InlineKeyboardButton(text="На главную", callback_data="back_to_menu"))

    return keyboard.adjust(3).as_markup()