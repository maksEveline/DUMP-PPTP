# - *- coding: utf- 8 - *-
from aiogram.types import Message, CallbackQuery
from tgbot.data.config import db, currencies
from tgbot.utils.utils_functions import get_admins, get_unix, get_exchange
from tgbot.data.loader import bot


def convert_ref(lang, ref):
    ref = int(ref)
    refs = lang.ref_s

    if ref % 10 == 1 and ref % 100 != 11:
        count = 0
    elif 2 <= ref % 10 <= 4 and (ref % 100 < 10 or ref % 100 >= 20):
        count = 1
    else:
        count = 2

    return f"{refs[count]}"


async def open_profile(texts, call: CallbackQuery = None, message: Message = None):
    if call:
        user = await db.get_user(id=call.from_user.id)
    else:
        user = await db.get_user(id=message.from_user.id)

    user_id = user['id']
    us = await bot.get_chat(user_id)
    user_name = user['user_name']
    name = f"@{user_name}"
    if user_name == "":
        name = us.get_mention(as_html=True)
    balance = user['balance_rub']
    total_refill = user['total_refill']
    reg_date = user['reg_date']
    ref_count = user['ref_count']
    settings = await db.get_settings()
    cur, tr = "", ""
    if settings['currency'] == 'rub':
        cur = 'rub'
        balance = float(user['balance_rub'])
        tr = total_refill
    elif settings['currency'] == 'usd':
        cur = 'usd'
        balance = float(user['balance_dollar'])
        tr = total_refill
    elif settings['currency'] == 'eur':
        cur = 'eur'
        balance = float(user['balance_euro'])
        tr = await get_exchange(total_refill, 'RUB', 'EUR')

    curr = currencies[cur]['sign']
    return texts.open_profile_text.format(user_name=name, user_id=user_id, balance=balance, curr=curr,
                                          total_refill=tr, reg_date=reg_date, ref_count=ref_count)


# Автоматическая очистка ежедневной статистики после 00:00
async def update_profit_day():
    await db.update_settings(profit_day=get_unix())


# Автоматическая очистка еженедельной статистики в понедельник 00:00
async def update_profit_week():
    await db.update_settings(profit_week=get_unix())


async def autobackup_db():
    db_path = "tgbot/data/database.db"
    with open(db_path, "rb") as data:
        for admin in get_admins():
            await bot.send_document(chat_id=admin, document=data, caption="<b>⚙️ АвтоБэкап базы данных ⚙️</b>")
