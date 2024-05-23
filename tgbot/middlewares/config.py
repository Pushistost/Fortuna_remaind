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
        Асинхронный метод для вызова middleware.

        Параметры:
            handler: Обработчик, который будет вызван после выполнения middleware.
            event: Объект сообщения, который обрабатывается.
            data: Словарь данных, передаваемых в обработчик.

        Возвращает:
            Результат выполнения обработчика.
        """
        # Добавляем конфигурацию в данные контекста
        data["config"] = self.config
        # Вызываем обработчик с обновленными данными
        return await handler(event, data)
