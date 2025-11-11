from aiogram.dispatcher.filters.state import State, StatesGroup


class PlaceOrder(StatesGroup):
    Name = State()
    Username = State()
    Phone = State()
    Confirm = State()
