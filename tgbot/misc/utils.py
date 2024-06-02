from datetime import timedelta, datetime

from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.utils.text_decorations import markdown_decoration
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite.requests import set_remind


async def add_remind(tg_id: int, time: int, remind: str, message: Message, session: AsyncSession) -> None:
    """
        Добавляет напоминание и отправляет сообщение с подтверждением.

        Args:
            tg_id (int): ID пользователя телеграм
            time (int): Время (в часах), через которое нужно напомнить.
            remind (str): Текст напоминания.
            message (Message): Объект сообщения.
            session (AsyncSession): Сессия базы данных, используемая для выполнения операций.
                        Должна быть экземпляром `AsyncSession` из SQLAlchemy.
        Returns:
            None
        """
    hours_to_add = time
    text = remind
    remind_time = datetime.now() + timedelta(hours=hours_to_add)
    await message.answer(f"*Запись добавлена*\n\n*Время напоминания*: {remind_time.strftime('%Y %b %d %H:%M')}"
                         f"\n*Сообщение*: {markdown_decoration.quote(text)}", parse_mode=ParseMode.MARKDOWN_V2)
    await set_remind(tg_id=tg_id, data=remind_time, text=text, hours=time, session=session)
