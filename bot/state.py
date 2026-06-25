from aiogram.fsm.state import State, StatesGroup


class AddTaskFSM(StatesGroup):
    waiting_title = State()
    waiting_priority = State()