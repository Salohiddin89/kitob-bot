from aiogram.dispatcher.filters.state import State, StatesGroup


class EditBook(StatesGroup):
    ChooseBook = State()
    ChooseField = State()
    NewValue = State()
    Confirm = State()
