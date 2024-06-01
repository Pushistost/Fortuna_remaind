from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite.requests import check_user
from tgbot.misc.states import UserForm


class StartCommandMiddleware(BaseMiddleware):
    # def __init__(self, session: AsyncSession) -> None:
    #     self.session = session
    #

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if event.text == "/start":
            session = data.get("session")
            state: FSMContext = data.get("state")
            exist_user = await check_user(event.from_user.id, session)
            if not exist_user:
                data["new_user"] = True
                await state.set_state(UserForm)
            else:
                data["new_user"] = False
        return await handler(event, data)
