from aiogram.dispatcher.filters.state import State, StatesGroup


class AddAdmin(StatesGroup):
    Name = State()
    ID = State()
    Username = State()
    Confirm = State()
