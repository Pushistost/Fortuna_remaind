import re
from datetime import datetime, timedelta

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommandScopeChat, BotCommandScopeAllPrivateChats, \
    BotCommandScopeAllChatAdministrators, BotCommandScopeAllGroupChats, BotCommandScopeDefault, CallbackQuery
from aiogram import F

from infrastructure.sqlite.requests import set_remind, check_remind_sql
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.reply import start_menu
from tgbot.middlewares.states import AddEntry
import tgbot.keyboards.inline as kb

from infrastructure.sqlite import requests as rq
from tgbot.misc.work_with_group import send_reminders

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
        await state.update_data(time=int(preparing_to_add[0]))
        await state.update_data(text=preparing_to_add[1])
        await message.answer(f"part 1: {preparing_to_add[0]}, \npart 2: {preparing_to_add[1]}",
                             reply_markup=await kb.yes_or_no_keyboard())
    else:
        await message.answer("Неверный ввод данных, попробуйте еще")
        await start_add_remind(message, state)


@admin_router.callback_query(AddEntry, F.data == "add_note")
async def add_remind(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    hours_to_add = data.get("time")
    text = data.get("text")
    remind_time = datetime.now() + timedelta(hours=hours_to_add)
    await query.message.edit_text(f"Ваша дата: {remind_time.strftime('%Y-%b-%d %H:%M')} \nСообщение {text}", )
    await set_remind(remind_time, text)
    await state.clear()


# Part of View DATA
@admin_router.message(F.text == "Показать записи")
async def view_remind(message: Message, state: FSMContext):
    await message.answer("Список всех напоминаний:", reply_markup=await kb.reminders())




@admin_router.message(F.text == "Удалить запись")
async def view_remind(message: Message, state: FSMContext):
    pass


# @admin_router.message(F.text)
# async def get_id(message: Message):
#     await message.answer(f"{message.chat.id}")


@admin_router.callback_query(F.data == "back_to_menu")
async def back_to_start(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text("Продолжаем работу", reply_markup=None)
    await state.clear()


# @admin_router.callback_query(F.data.startswith("category_"))
# async def category(callback: CallbackQuery):
#     await callback.answer("Вы выбрали категорию")
#
#     await callback.message.edit_text("Выберите товар по категории",
#                                      reply_markup=await kb.items(callback.data.split("_")[1]))
#
#
# @admin_router.callback_query(F.data.startswith("item_"))
# async def category(callback: CallbackQuery):
#     item_data = await rq.get_item(callback.data.split("_")[1])
#
#     await callback.answer("Вы выбрали товар")
#     await callback.message.edit_text(f"Название: {item_data.name}"
#                                      f"\nОписание: {item_data.description}"
#                                      f"\nЦена: {item_data.price}$",
#                                      reply_markup=None)


# reply_markup=await kb.items(callback.data.split("_")[1])

# Part of Delete DATA
# @admin_router.message(F.text == "Удалить запись")
# async def del_remind(message: Message, state: FSMContext):
#     pass


@admin_router.message(Command("reset_commands"))
async def message_reset_commands(message: Message):
    await message.bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=258829722))
    await message.bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await message.bot.delete_my_commands(scope=BotCommandScopeAllChatAdministrators())
    await message.bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await message.bot.delete_my_commands(scope=BotCommandScopeAllGroupChats())
    await message.bot.delete_my_commands(scope=BotCommandScopeDefault())
    await message.reply("Команды были удалены")
