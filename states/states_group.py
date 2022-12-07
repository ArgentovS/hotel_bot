from telebot.handler_backends import State, StatesGroup


class UserParameterState(StatesGroup):
    city = State()
    date_start = State()
    length_stay = State()
    price_range_low = State()
    price_range_high = State()
    distance = State()
    number_hotels = State()
    photo = State()
    number_photos = State()
