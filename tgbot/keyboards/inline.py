from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def yes_or_no_keyboard():
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
def my_orders_keyboard(orders: list):
    # Here we use a list of orders as a parameter (from simple_menu.py)

    keyboard = InlineKeyboardBuilder()
    for order in orders:
        keyboard.button(
            text=f"📝 {order['title']}",
            # Here we use an instance of OrderCallbackData class as callback_data parameter
            # order id is the field in OrderCallbackData class, that we defined above
            callback_data=OrderCallbackData(order_id=order["id"])
        )

    return keyboard.as_markup()
