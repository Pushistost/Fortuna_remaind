from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.utils.text_decorations import markdown_decoration

from infrastructure.sqlite.models import Reminders


async def clean_remind_list(remind: Reminders):
    """
    Удаляет напоминание из базы данных.

    Args:
        remind (Reminders): Напоминание для удаления.

    Returns:
        None
    """
    from infrastructure.sqlite.requests import delete_remind
    await delete_remind(remind.id)


async def send_reminders(bot: Bot, ready_remind_list):
    """
    Отправляет напоминания в указанный чат и удаляет их из базы данных.

    Args:
        bot (Bot): Экземпляр бота для отправки сообщений.
        ready_remind_list (list): Список напоминаний для отправки.

    Returns:
        None
    """
    if ready_remind_list:
        for remind in ready_remind_list:
            # Отправка напоминания
            await bot.send_message(
                chat_id=-1002032136082,
                text=f"*Прошло {remind.hours}ч*:\n\n{markdown_decoration.quote(remind.text)}",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            # Удаление напоминания после успешной отправки
            await clean_remind_list(remind)



