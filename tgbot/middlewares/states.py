from aiogram.fsm.state import State, StatesGroup

AddEntry = State("AddEntry")


class WorkWithRemind(StatesGroup):
    Get = State()
    View = State()


DelEntry = State("DelEntry")
