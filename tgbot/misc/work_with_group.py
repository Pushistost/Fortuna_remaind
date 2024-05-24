from aiogram import Bot
from aiogram.enums import ParseMode


async def send_reminders(bot: Bot, ready_remind_list):
    """
    Отправляет напоминания в указанный чат.

    Args:
        bot (Bot): Экземпляр бота для отправки сообщений.
        ready_remind_list (list): Список напоминаний для отправки.

    Returns:
        None
    """
    if ready_remind_list:
        for remind in ready_remind_list:
            await bot.send_message(
                chat_id=-1002032136082,
                text=f"*Свежее напоминание*:\n\n{remind.text}",
                parse_mode=ParseMode.MARKDOWN_V2
            )
