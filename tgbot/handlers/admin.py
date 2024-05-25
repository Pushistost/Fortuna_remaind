import re
from datetime import datetime, timedelta
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.utils.markdown import markdown_decoration
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommandScopeChat, BotCommandScopeAllPrivateChats, \
    BotCommandScopeAllChatAdministrators, BotCommandScopeAllGroupChats, BotCommandScopeDefault, CallbackQuery
from aiogram import F
from infrastructure.sqlite.models import Reminders
from tgbot.filters.admin import AdminFilter
from tgbot.filters.callback_datas import BackFromText
from tgbot.keyboards.reply import start_menu
from tgbot.middlewares.states import WorkWithRemind
import tgbot.keyboards.inline as kb
from infrastructure.sqlite import requests as rq
from tgbot.misc.utils import add_remind

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(CommandStart())
async def admin_start(message: Message) -> None:
    """
    Обрабатывает команду /start для администраторов.

    Args:
        message: Объект входящего сообщения.
    """
    await message.answer("Короче правила простые, но на всякий случай повторю:\n"
                         "Тупо пишешь цифру - это будут часы, потом пробел или Shift+Enter"
                         "Далее пишешь текст напоминания", reply_markup=start_menu)


@admin_router.message(F.text != "Показать записи", F.text.as_("remind"))
async def check_remind(message: Message, remind: str) -> None:
    """
    Проверяет и обрабатывает напоминание, переданное в сообщении.

    Args:
        message (Message): Объект сообщения.
        remind (str): Текст напоминания.

    Returns:
        None
    """
    preparing_to_add = re.split(r"[ |\n]", remind, maxsplit=1)

    if len(preparing_to_add) == 2 and preparing_to_add[0].isdigit():
        time = int(preparing_to_add[0])
        text = preparing_to_add[1]
        await add_remind(time=time, remind=text, message=message)
    else:
        await message.answer("Не верный формат записи", parse_mode=ParseMode.MARKDOWN_V2)


@admin_router.message(F.text == "Показать записи")
async def view_remind(message: Message, state: FSMContext) -> None:
    """
    Показывает список всех напоминаний.

    Args:
        message: Объект входящего сообщения.
        state: Контекст конечного автомата.
    """
    await message.answer("Список всех напоминаний:", reply_markup=await kb.reminders(),
                         parse_mode=ParseMode.MARKDOWN_V2)
    await state.set_state(WorkWithRemind.Get)


@admin_router.callback_query(WorkWithRemind.Get, F.data.startswith("remind_"))
async def show_one_remind(query: CallbackQuery, state: FSMContext) -> None:
    """
    Показывает детали одного напоминания.

    Args:
        query: Объект входящего callback-запроса.
        state: Контекст конечного автомата.
    """
    remind_id = int(query.data.split("_")[1])
    await query.message.edit_text("Просмотр записи",
                                  reply_markup=await kb.remind_menu(remind_id=remind_id),
                                  parse_mode=ParseMode.MARKDOWN_V2)
    await state.set_state(WorkWithRemind.View)
    await state.update_data(rem_id=remind_id)


@admin_router.callback_query(WorkWithRemind.View, F.data.startswith("remind_"))
async def show_text_remind(query: CallbackQuery) -> None:
    """
    Показывает текст конкретного напоминания.

    Args:
        query: Объект входящего callback-запроса.
    """
    remind: Reminders = await rq.get_one_remind(int(query.data.split('_')[1]))
    await query.message.edit_text(f"*Текст напоминания*: \n\n{remind.text}",
                                  reply_markup=kb.beck_from_text_bottom(r_id=remind.id),
                                  parse_mode=ParseMode.MARKDOWN_V2)


@admin_router.callback_query(WorkWithRemind.View, BackFromText.filter())
async def back_from_text(query: CallbackQuery, callback_data: BackFromText, state: FSMContext) -> None:
    """
    Возвращает к меню напоминаний из просмотра текста напоминания.

    Args:
        query: Объект входящего callback-запроса.
        callback_data: Объект данных callback.
        state: Контекст конечного автомата.
    """
    rem_id = callback_data.remind_id
    await query.message.edit_text("Просмотр записи",
                                  reply_markup=await kb.remind_menu(remind_id=rem_id), parse_mode=ParseMode.MARKDOWN_V2)
    await state.set_state(WorkWithRemind.View)


@admin_router.callback_query(F.data == "delete", WorkWithRemind.View)
async def delete_remind_handler(query: CallbackQuery, state: FSMContext) -> None:
    """
    Удаляет напоминание.

    Args:
        query: Объект входящего callback-запроса.
        state: Контекст конечного автомата.
    """
    data = await state.get_data()
    rem_id = data.get("rem_id")
    await rq.delete_remind(rem_id)
    await query.message.edit_text("*Напоминание удалено*\nОбновленный список напоминаний:",
                                  reply_markup=await kb.reminders(), parse_mode=ParseMode.MARKDOWN_V2)
    await state.set_state(WorkWithRemind.Get)


@admin_router.callback_query(F.data == "back_to_reminders")
async def beck_to_list_of_remind(query: CallbackQuery, state: FSMContext) -> None:
    """
    Возвращает к списку напоминаний.

    Args:
        query: Объект входящего callback-запроса.
        state: Контекст конечного автомата.
    """
    await query.message.edit_text("Список всех напоминаний:", reply_markup=await kb.reminders(),
                                  parse_mode=ParseMode.MARKDOWN_V2)
    await state.set_state(WorkWithRemind.Get)


@admin_router.callback_query(F.data == "back_to_menu")
async def back_to_start(query: CallbackQuery, state: FSMContext) -> None:
    """
    Возвращает к стартовому меню.

    Args:
        query: Объект входящего callback-запроса.
        state: Контекст конечного автомата.
    """
    await query.message.edit_text("Продолжаем работу", reply_markup=None, parse_mode=ParseMode.MARKDOWN_V2)
    await state.clear()


@admin_router.message(Command("reset_commands"))
async def message_reset_commands(message: Message):
    await message.bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=258829722))
    await message.bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await message.bot.delete_my_commands(scope=BotCommandScopeAllChatAdministrators())
    await message.bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await message.bot.delete_my_commands(scope=BotCommandScopeAllGroupChats())
    await message.bot.delete_my_commands(scope=BotCommandScopeDefault())
    await message.reply("Команды были удалены")
