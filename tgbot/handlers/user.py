import re

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import F
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite.requests import add_user
from tgbot.filters.callback_datas import BackFromText
from tgbot.keyboards.reply import start_menu
from tgbot.misc.states import WorkWithRemind, UserForm
import tgbot.keyboards.inline as kb
from sqlite import Remind, requests as rq
from tgbot.misc.utils import add_remind

user_router = Router()


# Приветствие и настройка группы для напоминаний
@user_router.message(CommandStart())
async def user_start(message: Message, new_user: bool) -> None:
    """
    Обрабатывает команду /start для администраторов.

    Args:
        message: Объект входящего сообщения.
        new_user: Параметр указывающий новый это юзер или нет
    """
    await message.answer("Правила простые:\n\n"
                         "Вначале пишешь цифру - это будут часы, потом пробел или Shift+Enter "
                         "Далее пишешь текст напоминания", reply_markup=start_menu)
    if new_user:
        await message.answer("Вы явно новый пользователь, а значит вам нужно непременно "
                             "вписать id группы для напоминания, иначе бот не сможет работать. "
                             "\n\nКак найти id группы или свой: добавляем этого бота к себе "
                             "в группу @username_to_id_bot и выберем в меню группу или человека, "
                             "кликаем - получаем id \n\nИ последнее: для того, что бы бот отправлял "
                             "вам в группу напоминание - вам нужно его туда добавить.")
        await message.answer("Отправьте сюда id группы для напоминаний")


@user_router.message(F.text.as_("group_id"), UserForm.Start)
async def add_group_id(message: Message, group_id: str, state: FSMContext, session: AsyncSession):
    """
    Обрабатывает ввод ID группы пользователем и сохраняет его в базе данных.

    Этот обработчик вызывается, когда пользователь находится в состоянии `UserForm.Start`
    и отправляет сообщение, содержащее ID группы. Обработчик пытается преобразовать введенное
    значение в целое число. Если преобразование удачно, ID группы сохраняется в базе данных,
    состояние FSM очищается и пользователю отправляется подтверждение. Если преобразование
    не удается, пользователю отправляется сообщение об ошибке.

    Args:
        message (Message): Входящее сообщение от пользователя.
        group_id (str): Введенный пользователем ID группы.
        state (FSMContext): Контекст состояния FSM для пользователя.
        session (AsyncSession): Сессия SQLAlchemy для взаимодействия с базой данных.

    Raises:
        ValueError: Если введенное значение не может быть преобразовано в целое число.
    """
    try:
        group_id = int(group_id.strip())
        await add_user(user_id=message.from_user.id, group_id=int(group_id), session=session)
        await state.clear()
        await message.answer(f"Ваш ID группы {group_id} сохранен!")
    except ValueError:
        await message.answer(f"Неверный ввод, это должно быть положительное или отрицательное число, попробуйте снова")


@user_router.message(F.text.as_("group_id"), UserForm.Change)
async def add_group_id(message: Message, group_id: str, state: FSMContext, session: AsyncSession):
    """
    Обрабатывает ввод ID группы пользователем и сохраняет его в базе данных.

    Этот обработчик вызывается, когда пользователь находится в состоянии `UserForm.Change`
    и отправляет сообщение, содержащее ID группы. Действует так же как и установка группы при старте, разница в том,
    что тут есть кнопка отмены, что бы человек не застревал в этом состоянии и мог просто отменить смену группы более
    интуитивным способом.

    Args:
        message (Message): Входящее сообщение от пользователя.
        group_id (str): Введенный пользователем ID группы.
        state (FSMContext): Контекст состояния FSM для пользователя.
        session (AsyncSession): Сессия SQLAlchemy для взаимодействия с базой данных.

    Raises:
        ValueError: Если введенное значение не может быть преобразовано в целое число.
    """
    try:
        group_id = int(group_id.strip())
        await add_user(user_id=message.from_user.id, group_id=int(group_id), session=session)
        await state.clear()
        await message.answer(f"Ваш ID группы {group_id} сохранен!")
    except ValueError:
        await message.answer(f"Неверный ввод, это должно быть положительное или отрицательное число, "
                             f"попробуйте снова", reply_markup=kb.jast_go_to_start())


@user_router.message(Command("change_group"))
async def change_group(message: Message, state: FSMContext):
    """
    Запускает смену процесс замены группы для напоминаний.

    Args:
        message (Message): Объект сообщения.
        state (FSMContext): Контекст состояния FSM для пользователя.

    Returns:
        None
    """
    await message.answer("Отправьте сюда id группы для напоминаний")
    await state.set_state(UserForm.Change)


@user_router.message(Command("get_group"))
async def get_group(message: Message, session: AsyncSession):
    """
    Показывает какая группа привязана к пользователю.

    Args:
        message (Message): Объект сообщения.
        session (AsyncSession): Сессия базы данных, используемая для выполнения операций.
                        Должна быть экземпляром `AsyncSession` из SQLAlchemy.

    Returns:
        None
    """
    group_id = await rq.get_group_id(message.from_user.id, session)
    await message.answer(f"ID вашей группы для напоминаний:\n\n{group_id}")


# Блок просмотра записей и работы с ними
@user_router.message(F.text != "Показать записи", F.text.as_("remind"))
async def check_remind(message: Message, remind: str, session: AsyncSession, new_user: bool, state: FSMContext) -> None:
    """
    Проверяет и обрабатывает напоминание, переданное в сообщении.

    Args:
        message (Message): Объект сообщения.
        remind (str): Текст напоминания.
        state (FSMContext): Контекст конечного автомата.
        new_user (bool): Данные в общем словаре новый пользователь или нет
        session (AsyncSession): Сессия базы данных, используемая для выполнения операций.
                        Должна быть экземпляром `AsyncSession` из SQLAlchemy.

    Returns:
        None
    """
    if new_user:
        await state.set_state(UserForm.Start)
        await message.answer("Отправьте сюда id группы для напоминаний")

    else:
        preparing_to_add = re.split(r"[ |\n]", remind, maxsplit=1)

        if len(preparing_to_add) == 2 and preparing_to_add[0].isdigit():
            time = int(preparing_to_add[0])
            text = preparing_to_add[1]
            await add_remind(tg_id=message.from_user.id, time=time, remind=text, message=message, session=session)
        else:
            await message.answer("Не верный формат записи", parse_mode=ParseMode.MARKDOWN_V2)


@user_router.message(F.text == "Показать записи")
async def view_remind(message: Message, state: FSMContext, session: AsyncSession) -> None:
    """
    Показывает список всех напоминаний.

    Args:
        message (Message): Объект входящего сообщения.
        state (FSMContext): Контекст конечного автомата.
        session (AsyncSession): Сессия базы данных, используемая для выполнения операций.
                Должна быть экземпляром `AsyncSession` из SQLAlchemy.

    """
    await message.answer("Список всех напоминаний:", reply_markup=await kb.reminders(session),
                         parse_mode=ParseMode.MARKDOWN_V2)
    await state.set_state(WorkWithRemind.Get)


@user_router.callback_query(WorkWithRemind.Get, F.data.startswith("remind_"))
async def show_one_remind(query: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    """
    Показывает детали одного напоминания.

    Args:
        query (CallbackQuery): Объект входящего callback-запроса.
        state (FSMContext): Контекст конечного автомата.
        session (AsyncSession): Сессия базы данных, используемая для выполнения операций.
                Должна быть экземпляром `AsyncSession` из SQLAlchemy.
    """
    remind_id = int(query.data.split("_")[1])
    await query.message.edit_text("Просмотр записи",
                                  reply_markup=await kb.remind_menu(remind_id=remind_id, session=session),
                                  parse_mode=ParseMode.MARKDOWN_V2)
    await state.set_state(WorkWithRemind.View)
    await state.update_data(rem_id=remind_id)


@user_router.callback_query(WorkWithRemind.View, F.data.startswith("remind_"))
async def show_text_remind(query: CallbackQuery, session: AsyncSession) -> None:
    """
    Показывает текст конкретного напоминания.

    Args:
        query (CallbackQuery): Объект входящего callback-запроса.
        session (AsyncSession): Сессия базы данных, используемая для выполнения операций.
                Должна быть экземпляром `AsyncSession` из SQLAlchemy.
    """
    remind: Remind = await rq.get_one_remind(int(query.data.split('_')[1]), session)
    await query.message.edit_text(f"*Текст напоминания*: \n\n{remind.text}",
                                  reply_markup=kb.beck_from_text_bottom(r_id=remind.id),
                                  parse_mode=ParseMode.MARKDOWN_V2)


@user_router.callback_query(WorkWithRemind.View, BackFromText.filter())
async def back_from_text(query: CallbackQuery, callback_data: BackFromText,
                         state: FSMContext, session: AsyncSession) -> None:
    """
    Возвращает к меню напоминаний из просмотра текста напоминания.

    Args:
        query (CallbackQuery): Объект входящего callback-запроса.
        callback_data: Объект данных callback.
        state (FSMContext): Контекст конечного автомата.
        session (AsyncSession): Сессия базы данных, используемая для выполнения операций.
                Должна быть экземпляром `AsyncSession` из SQLAlchemy.
    """
    rem_id = callback_data.remind_id
    await query.message.edit_text("Просмотр записи",
                                  reply_markup=await kb.remind_menu(remind_id=rem_id, session=session),
                                  parse_mode=ParseMode.MARKDOWN_V2)
    await state.set_state(WorkWithRemind.View)


@user_router.callback_query(F.data == "back_to_reminders")
async def beck_to_list_of_remind(query: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    """
    Возвращает к списку напоминаний.

    Args:
        query (CallbackQuery): Объект входящего callback-запроса.
        state (FSMContext): Контекст конечного автомата.
        session (AsyncSession): Сессия базы данных, используемая для выполнения операций.
                Должна быть экземпляром `AsyncSession` из SQLAlchemy.
    """
    await query.message.edit_text("Список всех напоминаний:", reply_markup=await kb.reminders(session),
                                  parse_mode=ParseMode.MARKDOWN_V2)
    await state.set_state(WorkWithRemind.Get)


@user_router.callback_query(F.data == "back_to_menu")
async def back_to_start(query: CallbackQuery, state: FSMContext) -> None:
    """
    Возвращает к стартовому меню.

    Args:
        query (CallbackQuery): Объект входящего callback-запроса.
        state (FSMContext): Контекст конечного автомата.
    """
    await query.message.edit_text("Продолжаем работу", reply_markup=None, parse_mode=ParseMode.MARKDOWN_V2)
    await state.clear()


# Блок удаления записей
@user_router.callback_query(F.data == "delete", WorkWithRemind.View)
async def delete_remind_handler(query: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    """
    Удаляет напоминание.

    Args:
        query (CallbackQuery): Объект входящего callback-запроса.
        state (FSMContext): Контекст конечного автомата.
        session (AsyncSession): Сессия базы данных, используемая для выполнения операций.
                Должна быть экземпляром `AsyncSession` из SQLAlchemy.
    """
    data = await state.get_data()
    rem_id = data.get("rem_id")
    await rq.delete_remind(rem_id, session)
    await query.message.edit_text("*Напоминание удалено*\nОбновленный список напоминаний:",
                                  reply_markup=await kb.reminders(session), parse_mode=ParseMode.MARKDOWN_V2)
    await state.set_state(WorkWithRemind.Get)
