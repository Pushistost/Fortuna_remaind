from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_pool) -> None:
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        """
          Открывает сессию для всех обработчиков.

          Args:
              handler (Callable[[Message, Dict[str, Any]], Awaitable[Any]]): Следующий обработчик в цепочке middleware.
              event (Message): Входящее сообщение от пользователя.
              data (Dict[str, Any]): Дополнительные данные, переданные middleware.

          Returns:
              Any: Результат выполнения следующего обработчика в цепочке.
        """
        async with self.session_pool() as session:

            data["session"] = session

            result = await handler(event, data)
        return result
