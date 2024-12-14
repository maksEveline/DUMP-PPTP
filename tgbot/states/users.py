from aiogram.dispatcher.filters.state import State, StatesGroup


class UsersCoupons(StatesGroup):
    here_coupon = State()


class UserRefills(StatesGroup):
    here_amount = State()


class UserProducts(StatesGroup):
    here_amount_to_buy = State()


class SearchPositions(StatesGroup):
    query = State()