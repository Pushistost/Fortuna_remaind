from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, BotCommandScopeChat, BotCommandScopeAllPrivateChats, \
    BotCommandScopeAllChatAdministrators, BotCommandScopeAllGroupChats, BotCommandScopeDefault

from tgbot.filters.admin import AdminFilter

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(Command("reset_commands"))
async def message_reset_commands(message: Message):
    await message.bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=258829722))
    await message.bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await message.bot.delete_my_commands(scope=BotCommandScopeAllChatAdministrators())
    await message.bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await message.bot.delete_my_commands(scope=BotCommandScopeAllGroupChats())
    await message.bot.delete_my_commands(scope=BotCommandScopeDefault())
    await message.reply("Команды были удалены")
