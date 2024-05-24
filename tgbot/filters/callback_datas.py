from aiogram.filters.callback_data import CallbackData


class BackFromText(CallbackData, prefix="from_text"):
    """
    Класс для обработки callback данных, возвращающийся от текстового напоминания.

    Attributes:
        remind_id (int): Идентификатор напоминания.
    """

    remind_id: int
    """
    Идентификатор напоминания.

    Тип: int
    """
