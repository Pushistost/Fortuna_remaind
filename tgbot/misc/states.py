from aiogram.fsm.state import State, StatesGroup


class UserForm(StatesGroup):
    """
    Состояние для добавления группы куда идти будут напоминания.

    Attributes:
        Start: Состояние добавления напоминания новых пользователей.
        Change: Состояние для смены группы для напоминаний.
    """
    Start: State = State()
    Change: State = State()


class WorkWithRemind(StatesGroup):
    """
    Группа состояний для работы с напоминаниями.

    Attributes:
        Get: Состояние получения списка напоминаний.
        View: Состояние просмотра конкретного напоминания.
    """
    Get: State = State()
    View: State = State()
