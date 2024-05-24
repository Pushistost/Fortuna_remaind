from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить напоминание"),
        ],
        [
            KeyboardButton(text="Показать записи"),
        ]
    ],
    resize_keyboard=True
)
