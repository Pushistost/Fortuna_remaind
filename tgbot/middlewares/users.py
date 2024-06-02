from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from sqlite.requests import check_user
from tgbot.misc.states import UserForm


class StartCommandMiddleware(BaseMiddleware):
    """
      Middleware для обработки команды /start.

      Это middleware проверяет, существует ли пользователь в базе данных, когда он отправляет команду /start.
      Если пользователь новый, его состояние FSM переводится в состояние `UserForm.Start`.
      В противном случае, состояние остается неизменным. Информация о том, является ли пользователь новым,
      сохраняется в `data["new_user"]`.

    """
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        """
          Обрабатывает входящие сообщения и проверяет команду /start.

          Args:
              handler (Callable[[Message, Dict[str, Any]], Awaitable[Any]]): Следующий обработчик в цепочке middleware.
              event (Message): Входящее сообщение от пользователя.
              data (Dict[str, Any]): Дополнительные данные, переданные middleware.

          Returns:
              Any: Результат выполнения следующего обработчика в цепочке.
        """
        if event.text == "/start":
            session = data.get("session")
            state: FSMContext = data.get("state")
            exist_user = await check_user(event.from_user.id, session)

            if not exist_user:
                data["new_user"] = True
                await state.set_state(UserForm.Start)
            else:
                data["new_user"] = False

        return await handler(event, data)
