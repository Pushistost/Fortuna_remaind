from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_default_commands(bot: Bot):
    return await bot.set_my_commands(
        commands=[
            BotCommand(command="change_group", description="Смена группы для отправки напоминаний"),
            BotCommand(command="get_group", description="Показать id группы для моих напоминаний"),
        ],
        scope=BotCommandScopeDefault()
    )
