from aiogram.fsm.state import State, StatesGroup

UserForm: State = State("UserForm")
"""
Состояние для добавления группы куда идти будут напоминания.

Attributes:
    AddEntry: Состояние добавления напоминания.
"""


class WorkWithRemind(StatesGroup):
    """
    Группа состояний для работы с напоминаниями.

    Attributes:
        Get: Состояние получения списка напоминаний.
        View: Состояние просмотра конкретного напоминания.
    """
    Get: State = State()
    View: State = State()



