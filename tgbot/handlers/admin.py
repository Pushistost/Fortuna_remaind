import re
from datetime import datetime, timedelta

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommandScopeChat, BotCommandScopeAllPrivateChats, \
    BotCommandScopeAllChatAdministrators, BotCommandScopeAllGroupChats, BotCommandScopeDefault, CallbackQuery
from aiogram import F

from infrastructure.sqlite.models import Reminders
from tgbot.filters.admin import AdminFilter
from tgbot.filters.callback_datas import BackFromText
from tgbot.keyboards.reply import start_menu
from tgbot.middlewares.states import AddEntry, WorkWithRemind
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
    await rq.set_remind(remind_time, text)
    await state.clear()


# Part of View DATA
@admin_router.message(F.text == "Показать записи")
async def view_remind(message: Message, state: FSMContext):
    await message.answer("Список всех напоминаний:", reply_markup=await kb.reminders())
    await state.set_state(WorkWithRemind.Get)


@admin_router.callback_query(WorkWithRemind.Get, F.data.startswith("remind_"))
async def show_one_remind(query: CallbackQuery, state: FSMContext):
    remind_id = query.data.split("_")[1]
    await query.message.edit_text("Просмотр записи",
                                  reply_markup=await kb.remind_menu(remind_id=remind_id))
    # await state.update_data(remind_id=remind_id)
    await state.set_state(WorkWithRemind.View)
    await state.update_data(rem_id=remind_id)


@admin_router.callback_query(WorkWithRemind.View, F.data.startswith("remind_"))
async def show_text_remind(query: CallbackQuery):
    remind: Reminders = await rq.get_one_remind(query.data.split('_')[1])
    await query.message.edit_text(f"Текст напоминания: \n\n{remind.text}",
                                  reply_markup=kb.beck_from_text_bottom(r_id=remind.id))


@admin_router.callback_query(WorkWithRemind.View, BackFromText.filter())
async def back_from_text(query: CallbackQuery, callback_data: BackFromText, state: FSMContext):
    id = callback_data.remind_id
    await query.message.edit_text("Просмотр записи",
                                  reply_markup=await kb.remind_menu(remind_id=id))
    await state.set_state(WorkWithRemind.View)


@admin_router.callback_query(F.data == "delete", WorkWithRemind.View)
async def delete_remind_handler(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    rem_id = data.get("rem_id")
    await rq.delete_remind(rem_id)
    await query.message.edit_text("Напоминание удалено\nОбновленный список напоминаний:",
                                  reply_markup=await kb.reminders())
    await state.set_state(WorkWithRemind.Get)


@admin_router.callback_query(F.data == "back_to_reminders")
async def beck_to_list_of_remind(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text("Список всех напоминаний:", reply_markup=await kb.reminders())
    await state.set_state(WorkWithRemind.Get)


@admin_router.callback_query(F.data == "back_to_menu")
async def back_to_start(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text("Продолжаем работу", reply_markup=None)
    await state.clear()


# @admin_router.callback_query(F.data.startswith("category_"))
# async def category(callback: CallbackQuery):
#     await callback.answer("Вы выбрали категорию")
#
# await callback.message.edit_text("Выберите товар по категории",
#                                  reply_markup=await kb.items(callback.data.split("_")[1]))
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
