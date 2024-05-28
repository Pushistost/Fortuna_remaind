from aiogram.fsm.state import State, StatesGroup

AddEntry: State = State("AddEntry")
"""
Состояние для добавления напоминания.

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


# DelEntry: State = State("DelEntry")
# """
# Состояние для удаления напоминания.
#
# Attributes:
#     DelEntry: Состояние удаления напоминания.
# """
