import re
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommandScopeChat, BotCommandScopeAllPrivateChats, \
    BotCommandScopeAllChatAdministrators, BotCommandScopeAllGroupChats, BotCommandScopeDefault, CallbackQuery
from aiogram import F

from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline import yes_or_no_keyboard
from tgbot.keyboards.reply import start_menu
from tgbot.middlewares.states import AddEntry

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(CommandStart())
async def admin_start(message: Message):
    await message.answer("Ну здравствуй, Отец", reply_markup=start_menu)


# Part of Add DATA
@admin_router.message(F.text == "Добавить напоминание")
async def start_add_remind(message: Message, state: FSMContext):
    await message.answer("Введите число (часы), а с новой строки (Shift+Enter) информацию которую хотите добавить")
    await state.set_state(AddEntry)


@admin_router.message(AddEntry, F.text.as_("remind"))
async def check_remind(message: Message, state: FSMContext, remind: str):
    preparing_to_add = re.split(r"[ |\n]", remind, maxsplit=1)
    if len(preparing_to_add) == 2 and preparing_to_add[0].isdigit():
        await state.update_data(time=preparing_to_add[0])
        await state.update_data(remind=preparing_to_add[1])
        await message.answer(f"part 1: {preparing_to_add[0]}, \npart 2: {preparing_to_add[1]} добавляем",
                             reply_markup=yes_or_no_keyboard())
    else:
        await message.answer("Неверный ввод данных, попробуйте еще")
        await start_add_remind(message, state)


@admin_router.callback_query(AddEntry, F.data == "add_note")
async def add_remind(query: CallbackQuery, state: FSMContext):
    pass


# Part of View DATA
@admin_router.message(F.text == "Показать записи")
async def view_remind(message: Message, state: FSMContext):
    await message.answer("Достаем из БД записи с пагинацией по 5 шт")
    pass


# Part of Delete DATA
@admin_router.message(F.text == "Удалить запись")
async def del_remind(message: Message, state: FSMContext):
    pass


@admin_router.message(Command("reset_commands"))
async def message_reset_commands(message: Message):
    await message.bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=258829722))
    await message.bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await message.bot.delete_my_commands(scope=BotCommandScopeAllChatAdministrators())
    await message.bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await message.bot.delete_my_commands(scope=BotCommandScopeAllGroupChats())
    await message.bot.delete_my_commands(scope=BotCommandScopeDefault())
    await message.reply("Команды были удалены")
