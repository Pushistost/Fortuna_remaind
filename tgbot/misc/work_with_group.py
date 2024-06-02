from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.utils.text_decorations import markdown_decoration
from sqlalchemy import ScalarResult
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlite import Remind


async def clean_remind_list(remind_list: list, session: AsyncSession):
    """
    Удаляет напоминание из базы данных.

    Args:
        remind_list (list): Напоминания для удаления.
        session (AsyncSession): Сессия базы данных, используемая для выполнения операций.
                Должна быть экземпляром `AsyncSession` из SQLAlchemy.

    Returns:
        None
    """
    for remind in remind_list:
        stmt = delete(Remind).where(Remind.id == remind.id)
        await session.execute(stmt)
    await session.commit()


async def send_reminders(bot: Bot, ready_remind_list: ScalarResult, session: AsyncSession):
    """
    Отправляет напоминания в указанный чат и удаляет их из базы данных.

    Args:
        bot (Bot): Экземпляр бота для отправки сообщений.
        ready_remind_list (list): Список напоминаний для отправки.
        session (AsyncSession): Сессия базы данных, используемая для выполнения операций.
                Должна быть экземпляром `AsyncSession` из SQLAlchemy.
    Returns:
        None
    """

    print(f"Reminders is {type(ready_remind_list)}")

    for remind in ready_remind_list:
        # Отправка напоминания
        await bot.send_message(
            chat_id=remind.tg_id,
            text=f"*Прошло {remind.hours}ч*:\n\n{markdown_decoration.quote(remind.text)}",
            parse_mode=ParseMode.MARKDOWN_V2
        )

    await clean_remind_list(ready_remind_list, session)
