from datetime import datetime

from aiogram import Bot
from sqlalchemy import select, ScalarResult, delete
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.sqlite.models import async_session, Reminders
from tgbot.misc.work_with_group import send_reminders


async def get_reminders() -> ScalarResult[Reminders]:
    """
    Получает все напоминания из базы данных.
    :return: Список объектов напоминаний.
    """
    async with async_session() as session:  # type: AsyncSession
        result = await session.scalars(select(Reminders))
        return result


async def set_remind(data: datetime, text: str) -> None:
    """
    Устанавливает новое напоминание в базе данных.
    :param data: Дата и время напоминания.
    :param text: Текст напоминания.
    """
    async with async_session() as session:  # type: AsyncSession
        session.add(Reminders(time=data, text=text))
        await session.commit()


# -> ScalarResult[Reminders]
async def check_remind_sql(bot: Bot):
    """
    Проверяет напоминания, которые должны быть отправлены.
    :return: Список объектов напоминаний, которые должны быть отправлены.
    """
    async with async_session() as session:  # type: AsyncSession
        ready_remind = await session.scalars(select(Reminders).where(Reminders.time <= datetime.now()))
        if ready_remind:
            await send_reminders(bot, ready_remind)


async def get_one_remind(id_remind: int) -> Reminders:
    """
    Получает одно напоминание из базы данных по его идентификатору.
    Args:
        id_remind (int): Идентификатор напоминания.
    Returns:
        Reminders: Объект напоминания, соответствующий указанному идентификатору.
    """
    async with async_session() as session:  # type: AsyncSession
        result = await session.scalar(select(Reminders).where(Reminders.id == id_remind))
        return result


async def delete_remind(id_remind: int) -> None:
    """
    Удаляет напоминание из базы данных по его идентификатору.
    Args:
        id_remind (int): Идентификатор напоминания.
    Returns:
        None
    """
    async with async_session() as session:  # type: AsyncSession
        await session.execute(delete(Reminders).where(Reminders.id == id_remind))
        await session.commit()
