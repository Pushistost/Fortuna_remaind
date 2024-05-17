from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
user_router = Router()


@user_router.message(CommandStart())
async def user_start(message: Message):
    await message.reply("Привет, постоянный пользователь!")

