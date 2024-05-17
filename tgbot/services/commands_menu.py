from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat


async def set_all_chat_admins_commands(bot: Bot):
    return await bot.set_my_commands(
        commands=[
            BotCommand(command="set_remind", description="Создать напоминание"),
            BotCommand(command="view_remind", description="Показать напоминания"),
            BotCommand(command="del_remind", description="Удалить напоминание"),
        ],
        scope=BotCommandScopeChat(chat_id=258829722)
    )