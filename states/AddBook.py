from aiogram.dispatcher.filters.state import State, StatesGroup


class AddBook(StatesGroup):
    Title = State()
    Author = State()
    Pages = State()
    Description = State()
    Year = State()
    price = State()
    Image = State()
    Confirm = State()
