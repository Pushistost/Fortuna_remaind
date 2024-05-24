from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from infrastructure.sqlite.requests import get_reminders, get_one_remind
from tgbot.filters.callback_datas import BackFromText


async def yes_or_no_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для добавления записи или отмены.

    Returns:
        InlineKeyboardBuilder: Клавиатура с кнопками "добавить запись" и "отмена".
    """
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="📝 Добавить запись",
        callback_data="add_note"
    )
    keyboard.button(
        text="❌ Отмена",
        callback_data="back_to_menu"
    )

    keyboard.adjust(2)

    return keyboard.as_markup()


async def reminders() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком всех напоминаний.

    Returns:
        InlineKeyboardMarkup: Клавиатура со списком напоминаний и кнопкой возврата в меню.
    """
    all_reminders = await get_reminders()

    keyboard = InlineKeyboardBuilder()

    for remind in all_reminders:
        keyboard.add(InlineKeyboardButton(
            text=f"ID: {remind.id} | DATA: {remind.time.strftime('%b %d %H:%M')} | TEXT: {remind.text}",
            callback_data=f"remind_{remind.id}"))

    keyboard.add(InlineKeyboardButton(text="На обратно", callback_data="back_to_menu"))

    return keyboard.adjust(1).as_markup()


async def ready_reminders() -> InlineKeyboardMarkup or None:
    """
    Создает клавиатуру со списком всех готовых напоминаний, если таковые имеются.

    Returns:
        InlineKeyboardMarkup: Клавиатура со списком напоминаний и кнопкой возврата в меню,
        или None если напоминаний нет.
    """
    all_reminders = await get_reminders()

    if all_reminders:
        keyboard = InlineKeyboardBuilder()

        for remind in all_reminders:
            keyboard.add(InlineKeyboardButton(
                text=f"ID: {remind.id} | DATA: {remind.time.strftime('%b-%d %H:%M')} | TEXT: {remind.text}",
                callback_data=f"remind_{remind.id}"))

        keyboard.add(InlineKeyboardButton(text="В начало", callback_data="back_to_menu"))

        return keyboard.adjust(1).as_markup()

    return None


async def remind_menu(remind_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для меню напоминания с опциями удаления и возврата.

    Args:
        remind_id (int): Идентификатор напоминания.

    Returns:
        InlineKeyboardMarkup: Клавиатура с информацией о напоминании, кнопками удаления и возврата.
    """
    remind = await get_one_remind(remind_id)

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text=f"ID: {remind.id} | DATA: {remind.time.strftime('%b %d %H:%M')} | TEXT: {remind.text}",
        callback_data=f"remind_{remind.id}"))
    keyboard.button(
        text="❌ Удалить запись",
        callback_data="delete"
    )
    keyboard.button(
        text="⬅️ Назад",
        callback_data="back_to_reminders"
    )

    keyboard.adjust(1, 2)

    return keyboard.as_markup()


def beck_from_text_bottom(r_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой для возврата к списку напоминаний.

    Args:
        r_id (int): Идентификатор напоминания.

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой "назад".
    """
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="⬅️ Назад", callback_data=BackFromText(remind_id=r_id)
    )

    return keyboard.as_markup()


def jast_go_to_start() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой для возврата стартовому меню из создания напоминания

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой "назад".
    """
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="⬅️ Назад", callback_data="back_to_menu"
    )

    return keyboard.as_markup()
