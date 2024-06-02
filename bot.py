import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

from sqlite.models import async_session, make_base
from sqlite.requests import check_remind_sql
from tgbot.config import load_config, Config
from tgbot.handlers import routers_list
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.middlewares.database import DatabaseMiddleware
from tgbot.middlewares.users import StartCommandMiddleware
from tgbot.services import broadcaster
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.services.commands_menu import set_default_commands


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "Бот был запущен")


async def remind_worker(bot: Bot, session_pool):
    """
       Проверяет и отправляет напоминания.
       Эта функция выполняет проверку напоминаний, которые должны быть отправлены на текущий момент времени.
       Args:
           bot (Bot): Экземпляр бота.
           session_pool: Пул сессий для базы данных, используемый для выполнения операций.
       Returns:
           None
    """
    async with session_pool() as session:
        await check_remind_sql(bot, session)


def register_global_middlewares(dp: Dispatcher, config: Config, session_pool):
    """
    Регистрация глобальных middleware для заданного диспетчера.
    Глобальные middleware здесь - это те, которые применяются ко всем хендлерам (вы указываете тип обновления).

    :param dp: Экземпляр диспетчера.
    :type dp: Dispatcher
    :param config: Конфигурационный объект, загруженный из файла конфигурации.
    :param session_pool: Необязательный пул сессий для базы данных с использованием SQLAlchemy.
    :return: None
    """
    middleware_types = [
        ConfigMiddleware(config),
        DatabaseMiddleware(session_pool),

    ]
    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)

    dp.message.outer_middleware(StartCommandMiddleware())


def setup_logging():
    """
    Настройка конфигурации логирования для приложения.

    Этот метод инициализирует конфигурацию логирования для приложения.
    Он устанавливает уровень логирования на INFO и настраивает базовое цветное логирование
    для вывода. Формат лога включает имя файла, номер строки, уровень логирования,
    временную метку, имя логгера и сообщение лога.

    Возвращает:
    None

    Пример использования:
    setup_logging()
    """

    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def get_storage(config):
    """
    Возвращает хранилище на основе предоставленной конфигурации.

    Args:
        config (Config): Конфигурационный объект.

    Returns:
        Storage: Объект хранилища на основе конфигурации.

    """
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


async def set_all_default_commands(bot: Bot):
    """
    Устанавливает команды бокового меню
    Args:
        bot (Bot): Объект бота
    """
    await set_default_commands(bot)


async def main():
    """
        Основная функция для запуска бота и планировщика задач.

        Эта функция выполняет следующие действия:
        1. Настраивает логирование.
        2. Создает базу данных и все необходимые таблицы.
        3. Загружает конфигурацию из файла окружения.
        4. Инициализирует хранилище для состояний FSM.
        5. Создает экземпляр бота и диспетчера.
        6. Регистрирует глобальные middlewares.
        7. Настраивает планировщик для периодической проверки времени отправки напоминаний.
        8. Устанавливает стандартные команды для бота.
        9. Выполняет действия при запуске бота.
        10. Начинает polling для обработки обновлений.

        Returns:
            None
        """
    setup_logging()
    await make_base()
    config = load_config(".env")
    storage = get_storage(config)

    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=storage)
    dp.include_routers(*routers_list)

    scheduler = AsyncIOScheduler()

    register_global_middlewares(dp, config, async_session)

    scheduler.add_job(remind_worker,
                      "interval", seconds=60, timezone='Europe/Moscow', args=(bot, async_session))
    scheduler.start()
    await set_default_commands(bot)
    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot)
    await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот был выключен!")
