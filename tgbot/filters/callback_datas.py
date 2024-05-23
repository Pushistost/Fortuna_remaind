from aiogram.filters.callback_data import CallbackData


class BackFromText(CallbackData, prefix="from_text"):
    remind_id: int
