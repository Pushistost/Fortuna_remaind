from typing import Coroutine, Any, Optional

from aiogram import Bot
from sqlalchemy import ScalarResult

from infrastructure.sqlite.models import Reminders


async def send_reminders(bot: Bot, ready_remind_list):

    if ready_remind_list:
        for remind in ready_remind_list:
            await bot.send_message(chat_id=-1002032136082, text=remind.text)

