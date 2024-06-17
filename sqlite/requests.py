from datetime import datetime

from aiogram import Bot
from sqlalchemy import select, ScalarResult, delete
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite import User
from sqlite.models import Remind
from tgbot.misc.work_with_group import send_reminders


async def get_reminders(session: AsyncSession, user_id: int) -> ScalarResult[Remind]:
    """
    Получает все напоминания из базы данных.
    :return: Список объектов напоминаний.
    :param session: Сессия базы данных, используемая для выполнения операций.
                Должна быть экземпляром `AsyncSession` из SQLAlchemy.
    :param user_id: (int) id пользователя
    """
    result = await session.scalars(select(Remind).where(Remind.user_id == user_id))
    return result


async def set_remind(tg_id: int, data: datetime, text: str, hours: int, session: AsyncSession) -> None:
    """
    Устанавливает новое напоминание в базе данных.
    :param tg_id: Дата и время напоминания.
    :param data: Дата и время напоминания.
    :param text: Текст напоминания.
    :param hours: Сколько часов в таймере
    :param session: Сессия базы данных, используемая для выполнения операций.
                    Должна быть экземпляром `AsyncSession` из SQLAlchemy.

    """
    session.add(Remind(user_id=tg_id, time=data, text=text, hours=hours))
    await session.commit()


# -> ScalarResult[Remind]
async def check_remind_sql(bot: Bot, session: AsyncSession):
    """
    Проверяет напоминания, которые должны быть отправлены.
    :return: Список объектов напоминаний, которые должны быть отправлены.
    :param session: Сессия базы данных, используемая для выполнения операций.
                Должна быть экземпляром `AsyncSession` из SQLAlchemy.
    :param bot: Экземпляр класса бот
    """
    query = select(Remind, User).join(User, Remind.user_id == User.tg_id).where(Remind.time <= datetime.now())
    result = await session.execute(query)
    ready_remind = result.fetchall()

    if ready_remind:
        await send_reminders(bot, ready_remind, session)


async def get_one_remind(id_remind: int, session: AsyncSession) -> Remind:
    """
    Получает одно напоминание из базы данных по его идентификатору.
    Args:
        id_remind (int): Идентификатор напоминания.
        session (AsyncSession): Сессия базы данных, используемая для выполнения операций.
                        Должна быть экземпляром `AsyncSession` из SQLAlchemy.

    Returns:
        Remind: Объект напоминания, соответствующий указанному идентификатору.
    """
    result = await session.scalar(select(Remind).where(Remind.id == id_remind))
    return result


async def delete_remind(id_remind: int, session: AsyncSession) -> None:
    """
    Удаляет напоминание из базы данных по его идентификатору.
    Args:
        id_remind (int): Идентификатор напоминания.
        session (AsyncSession): Сессия базы данных, используемая для выполнения операций.
                        Должна быть экземпляром `AsyncSession` из SQLAlchemy.
    Returns:
        None
    """
    await session.execute(delete(Remind).where(Remind.id == id_remind))
    await session.commit()


async def check_user(user_id: int, session: AsyncSession):
    """
      Проверяет наличие пользователя в базе данных.
      Args:
          user_id (int): id пользователя.
          session (AsyncSession): Сессия базы данных, используемая для выполнения операций.
                          Должна быть экземпляром `AsyncSession` из SQLAlchemy.
      Returns:
          None
      """
    result = await session.scalar(select(User).where(User.tg_id == user_id))
    return result is not None


async def add_user(user_id: int, group_id: int, session: AsyncSession):
    """
      Добавляет пользователя в БД вместе с группой для напоминаний
      Args:
          user_id (int): id пользователя.
          group_id (int): id группы
          session (AsyncSession): Сессия базы данных, используемая для выполнения операций.
                          Должна быть экземпляром `AsyncSession` из SQLAlchemy.
      Returns:
          None
      """
    session.add(User(tg_id=user_id, group_id=group_id))
    await session.commit()


async def get_group_id(user_id: int, session: AsyncSession):
    """
      Достает по запросу группу которая привязана к пользователю
      Args:
          user_id (int): id пользователя.
          session (AsyncSession): Сессия базы данных, используемая для выполнения операций.
                          Должна быть экземпляром `AsyncSession` из SQLAlchemy.
      Returns:
          ID группы для напоминания
      """
    result = await session.scalar(select(User.group_id).where(User.tg_id == user_id))
    return result
