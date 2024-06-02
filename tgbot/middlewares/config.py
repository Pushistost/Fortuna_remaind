from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message


class ConfigMiddleware(BaseMiddleware):
    """
    Middleware для добавления конфигурации в контекст данных обработчика.

    Атрибуты:
        config: Конфигурационный объект, который будет добавлен в контекст данных.
    """

    def __init__(self, config: Any) -> None:
        """
        Инициализирует ConfigMiddleware с переданным конфигурационным объектом.

        Параметры:
            config: Конфигурационный объект, который будет добавлен в контекст данных.
        """
        self.config = config

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        """
          Дает доступ к config данным обработчикам.

          Args:
              handler (Callable[[Message, Dict[str, Any]], Awaitable[Any]]): Следующий обработчик в цепочке middleware.
              event (Message): Входящее сообщение от пользователя.
              data (Dict[str, Any]): Дополнительные данные, переданные middleware.

          Returns:
              Any: Результат выполнения следующего обработчика в цепочке.
        """
        data["config"] = self.config

        return await handler(event, data)
