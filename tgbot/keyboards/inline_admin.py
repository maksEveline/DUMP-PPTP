# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from tgbot.data.config import db, currencies
from tgbot.data.config import lang_ru as texts
from tgbot.utils.utils_functions import convert_time, get_channels, convert_words
import time
from datetime import datetime, timedelta

def admin_menu():
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton("🖤 Общие настройки", callback_data="settings"))
    kb.append(InlineKeyboardButton("🎲 Доп. настройки", callback_data="extra_settings"))
    kb.append(InlineKeyboardButton("❗ Выключатели", callback_data="on_off"))
    kb.append(InlineKeyboardButton("📊 Статистика", callback_data="stats"))
    kb.append(InlineKeyboardButton("🔍 Искать", callback_data="find:"))
    kb.append(InlineKeyboardButton("💎 Управление товарами", callback_data="pr_edit"))
    kb.append(InlineKeyboardButton("📌 Рассылка", callback_data="mail_start"))
    kb.append(InlineKeyboardButton("💰 Платежные системы", callback_data="payments"))
    kb.append(InlineKeyboardButton("💫 Рекламные кнопки", callback_data="pr_buttons"))
    kb.append(InlineKeyboardButton("🧩 Кнопки в рассылке", callback_data="mail_buttons"))
    kb.append(InlineKeyboardButton("🎉 Розыгрыши", callback_data="contests_admin"))
    kb.append(InlineKeyboardButton(texts.back, callback_data="back_to_user_menu"))

    keyboard.add(kb[0], kb[1])
    keyboard.add(kb[2], kb[4])
    keyboard.add(kb[3])
    keyboard.add(kb[5], kb[7])
    keyboard.add(kb[6], kb[9])
    keyboard.add(kb[8])
    keyboard.add(kb[10])
    keyboard.add(kb[11])

    return keyboard


async def contests_inl():
    kb = InlineKeyboardMarkup(row_width=1)

    s = await db.get_contests_settings()
    cur = (await db.get_settings())['currency']

    btn0 = InlineKeyboardButton(f'✨ Кол-во победителей | {s["winners_num"]} {convert_words(s["winners_num"], ["человек", "человека", "людей"])}', callback_data='edit_winners_contest')
    btn1 = InlineKeyboardButton(f'💰 Приз | {s["prize"]}{currencies[cur]["sign"]}', callback_data='edit_prize_contest')
    btn2 = InlineKeyboardButton(f'❗ Условия', callback_data='contest_conditions')
    btn3 = InlineKeyboardButton(f'💥 Кол-во участников | {s["members_num"]} {convert_words(s["winners_num"], ["человек", "человека", "людей"])}', callback_data="edit_members_contest")
    btn4 = InlineKeyboardButton(f'🌐 Закончить розыгрыш через {s["end_time"]} {convert_time(s["end_time"], "seconds")}',
                                callback_data='edit_end_time_contest')
    btn5 = InlineKeyboardButton(f"❌ Закончить розыгрыш сейчас", callback_data="cancel_contest_now")
    btn6 = InlineKeyboardButton(f'⭐ Начать розыгрыш', callback_data='create_contest')
    btn7 = InlineKeyboardButton(texts.back, callback_data='settings_back')

    kb.add(btn0, btn1, btn2, btn3, btn4, btn5, btn6, btn7)

    return kb


async def choose_contest_for_mail_button(contests):
    k = InlineKeyboardMarkup()

    for contest in contests:
        prize = contest['prize']
        a = (contest['end_time'] - time.time())
        a1 = datetime.today()
        a2 = a1 + timedelta(seconds=a)
        end_time_ = a2 - a1
        end_time = str(end_time_).split(".")[0]
        if len(end_time.split(",")) == 2:
            day = end_time.split(",")[0]
            day = day.split(" ")[0]
            day_text = convert_words(int(day), ['день', 'дня', "дней"])
            end_time = f"{day} {day_text}, {end_time.split(', ')[1]}"
        else:
            end_time = f"{end_time.split(', ')[0]}"
        bot_settings = await db.get_settings()
        k.add(InlineKeyboardButton(text=f"🎁 | {prize}{currencies[bot_settings['currency']]['sign']} | {end_time}",
                                   callback_data=f"mail_button_contest_create:{contest['id']}"))
    return k


async def choose_contest_for_cancel(contests):
    k = InlineKeyboardMarkup()

    for contest in contests:
        prize = contest['prize']
        a = (contest['end_time'] - time.time())
        a1 = datetime.today()
        a2 = a1 + timedelta(seconds=a)
        end_time_ = a2 - a1
        end_time = str(end_time_).split(".")[0]
        if len(end_time.split(",")) == 2:
            day = end_time.split(",")[0]
            day = day.split(" ")[0]
            day_text = convert_words(int(day), ['день', 'дня', "дней"])
            end_time = f"{day} {day_text}, {end_time.split(', ')[1]}"
        else:
            end_time = f"{end_time.split(', ')[0]}"
        bot_settings = await db.get_settings()
        k.add(InlineKeyboardButton(text=f"🎁 | {prize}{currencies[bot_settings['currency']]['sign']} | {end_time}",
                                   callback_data=f"cancel_contest:{contest['id']}"))
    return k

def cancel_contest_now_yes_no(contest_id):
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(f"✅ Да, хочу", callback_data=f"cancel_contest_:yes:{contest_id}"))
    kb.append(InlineKeyboardButton(f"❌ Нет, не хочу", callback_data=f"cancel_contest_:no:{contest_id}"))

    keyboard.add(kb[0], kb[1])

    return keyboard

async def contests_conditions_inl():
    kb = InlineKeyboardMarkup(row_width=1)

    s = await db.get_contests_settings()

    channels_count = len(get_channels(s['channels_ids']))

    btn0 = InlineKeyboardButton(f'🛒 Кол-во покупок | {s["purchases_num"]} {convert_words(s["purchases_num"], ["покупка", "покупки", "покупок"])}', callback_data='edit_con_conds:purchases')
    btn1 = InlineKeyboardButton(f'💳 Кол-во пополнений | {s["refills_num"]} {convert_words(s["refills_num"], ["пополнение", "пополнения", "пополнений"])}', callback_data='edit_con_conds:refills')
    btn2 = InlineKeyboardButton(f'💎 ID Каналов для подписки | Кол-во: {channels_count} шт.', callback_data='edit_con_conds:channels_ids')
    btn3 = InlineKeyboardButton(texts.back, callback_data='contests')

    kb.add(btn0, btn1, btn2, btn3)

    return kb


def mail_buttons_inl():
    kb = InlineKeyboardMarkup(row_width=1)

    btn0 = InlineKeyboardButton('+ Создать кнопку', callback_data='mail_buttons:add')
    btn2 = InlineKeyboardButton('Текущие кнопки', callback_data='mail_buttons:current')
    btn3 = InlineKeyboardButton(texts.back, callback_data='settings_back')

    kb.add(btn0, btn2, btn3)

    return kb


def get_type(name, type):
    if type == 'link':
        return f'{name} (Ссылка)'
    elif type == 'category_open':
        return f'{name} (Категория)'
    elif type == 'pod_category_open':
        return f'{name} (Под-Категория)'
    elif type == 'position_open':
        return f'{name} (Позиция)'
    elif type == "contest_open":
        return f'{name} (Розыгрыш)'


async def mail_buttons_current_inl():
    kb = InlineKeyboardMarkup()
    btns = await db.get_all_mail_buttons()

    for btn in btns:
        kb.add(InlineKeyboardButton(get_type(btn['name'], str(btn['type'].split('|')[0])), callback_data=f"edit_mail_button:{btn['id']}"))

    kb.add(InlineKeyboardButton(texts.back, callback_data=f'mail_buttons'))

    return kb


def mail_buttons_edit_inl(btn_id):
    kb = InlineKeyboardMarkup()

    kb.add(InlineKeyboardButton('⭐ Изменить название', callback_data=f'edits_mail_btn:edit_name:{btn_id}'))
    kb.add(InlineKeyboardButton('❗ Удалить', callback_data=f'edits_mail_btn:del:{btn_id}'))
    kb.add(InlineKeyboardButton(texts.back, callback_data=f'mail_buttons:current'))

    return kb


def mail_buttons_type_inl():
    kb = InlineKeyboardMarkup(row_width=1)

    btn0 = InlineKeyboardButton('Кнопка открытия категории', callback_data='add_mail_buttons:category')
    btn1 = InlineKeyboardButton('Кнопка открытия под-категории', callback_data='add_mail_buttons:pod_category')
    btn2 = InlineKeyboardButton('Кнопка открытия позиции', callback_data='add_mail_buttons:position')
    btn3 = InlineKeyboardButton('Кнопка-ссылка', callback_data='add_mail_buttons:link')
    btn4 = InlineKeyboardButton('Кнопка открытия розыгрыша', callback_data='add_mail_buttons:contest')
    btn5 = InlineKeyboardButton(texts.back, callback_data='mail_buttons')

    kb.add(btn0, btn1, btn2, btn3, btn4, btn5)

    return kb


def mail_buttons_contest_yes_no(contest_id):
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton("✅ Да, хочу", callback_data=f"mail_button_create_contest:yes:{contest_id}"))
    kb.append(InlineKeyboardButton("❌ Нет, не хочу", callback_data=f"mail_button_create_contest:no:{contest_id}"))

    keyboard.add(kb[0], kb[1])

    return keyboard


def back_sett():
    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(texts.back, callback_data="settings_back"))

    return keyboard


def extra_back():
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(texts.back, callback_data="extra_settings"))

    keyboard.add(kb[0])

    return keyboard

def extra_settings_inl():
    keyboard = InlineKeyboardMarkup()
    kb = []


    kb.append(InlineKeyboardButton(f"💎 Создать промокод", callback_data="promo_create"))
    kb.append(InlineKeyboardButton(f"🎲 Удалить промокод", callback_data="promo_delete"))
    kb.append(InlineKeyboardButton(f"2️⃣ Изменить кол-во рефералов для 2 лвла", callback_data="ref_lvl_edit:2"))
    kb.append(InlineKeyboardButton(f"3️⃣ Изменить кол-во рефералов для 3 лвла", callback_data="ref_lvl_edit:3"))
    kb.append(InlineKeyboardButton(texts.back, callback_data="settings_back"))

    keyboard.add(kb[0], kb[1])
    keyboard.add(kb[2])
    keyboard.add(kb[3])
    keyboard.add(kb[4])

    return keyboard

def pr_buttons_inl():
    keyboard = InlineKeyboardMarkup()
    kb = []


    kb.append(InlineKeyboardButton(f"+ Создать кнопку", callback_data="pr_button:create"))
    kb.append(InlineKeyboardButton(f"- Удалить кнопку", callback_data="pr_button:delete"))
    kb.append(InlineKeyboardButton(texts.back, callback_data="settings_back"))

    keyboard.add(kb[0], kb[1])
    keyboard.add(kb[2])

    return keyboard

def pr_buttons_back():
    keyboard = InlineKeyboardMarkup()
    kb = []


    kb.append(InlineKeyboardButton(texts.back, callback_data="pr_buttons"))

    keyboard.add(kb[0])

    return keyboard

async def on_off_inl():
    keyboard = InlineKeyboardMarkup()
    kb = []
    s = await db.get_settings()
    work = s['is_work']
    purchases = s['is_buy']
    refills = s['is_refill']
    ref_system = s['is_ref']
    notify = s['is_notify']
    sub = s['is_sub']
    key = s['keyboard']
    contests = s['contests_is_on']
    multi_lang = s['multi_lang']

    if sub == "True":
        sub_emoji = "✅"
    else:
        sub_emoji = "❌"

    if notify == "True":
        notify_emoji = "✅"
    else:
        notify_emoji = "❌"

    if work == "True":
        work_emoji = "✅"
    else:
        work_emoji = "❌"

    if purchases == "True":
        buy_emoji = "✅"
    else:
        buy_emoji = "❌"

    if refills == "True":
        refill_emoji = "✅"
    else:
        refill_emoji = "❌"

    if ref_system == "True":
        ref_emoji = "✅"
    else:
        ref_emoji = "❌"

    if contests == "True":
        contests_emoji = "✅"
    else:
        contests_emoji = "❌"

    if multi_lang == "True":
        lang_emoji = "✅"
    else:
        lang_emoji = "❌"

    kb.append(InlineKeyboardButton(f"Тех. Работы | {work_emoji}", callback_data="work:on_off"))
    kb.append(InlineKeyboardButton(f"Покупки | {buy_emoji}", callback_data="buys:on_off"))
    kb.append(InlineKeyboardButton(f"Пополнения | {refill_emoji}", callback_data="refills:on_off"))
    kb.append(InlineKeyboardButton(f"Реф. Система | {ref_emoji}", callback_data="ref:on_off"))
    kb.append(InlineKeyboardButton(f"Розыгрыши | {contests_emoji}", callback_data="contests:on_off"))
    kb.append(InlineKeyboardButton(f"Мульти-язычность | {lang_emoji}", callback_data="multi_lang:on_off"))
    kb.append(InlineKeyboardButton(f"Увед. О новых юзерах | {notify_emoji}", callback_data="notify:on_off"))
    kb.append(InlineKeyboardButton(f"Проверка подписки | {sub_emoji}", callback_data="sub:on_off"))
    kb.append(InlineKeyboardButton(f"Главное меню | {key}", callback_data="keyboard:on_off"))
    kb.append(InlineKeyboardButton(texts.back, callback_data="settings_back"))

    keyboard.add(kb[0], kb[1])
    keyboard.add(kb[2])
    keyboard.add(kb[3], kb[4])
    keyboard.add(kb[5])
    keyboard.add(kb[6])
    keyboard.add(kb[7])
    keyboard.add(kb[8])
    keyboard.add(kb[9])

    return keyboard


def choose_type_position():
    keyboard = InlineKeyboardMarkup()
    types = [{'text': "Фото", "type": 'photo'}, {'text': "Файл", "type": 'file'}, {'text': "Текст", "type": 'text'}]

    for _type in types:
        keyboard.add(InlineKeyboardButton(_type['text'], callback_data=f"position_type:{_type['type']}"))

    return keyboard


async def choose_languages_kb_adm():
    keyboard = InlineKeyboardMarkup(row_width=2)
    langs = await db.get_all_languages()

    for lang in langs:
        keyboard.add(InlineKeyboardButton(lang['name'], callback_data=f"edit_default_language:{lang['language']}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"settings"))

    return keyboard


def stats_inl():
    keyboard = InlineKeyboardMarkup()

    kb1 = InlineKeyboardButton("Получить юзеров и их баланс > 0 в txt файле", callback_data="get_users_and_balances")
    kb2 = InlineKeyboardButton(texts.back, callback_data="settings_back")

    keyboard.add(kb1)
    keyboard.add(kb2)

    return keyboard

async def settings_inl():
    keyboard = InlineKeyboardMarkup()
    kb = []
    s = await db.get_settings()
    faq = s['faq']
    support = s['support']
    chat = s['chat']
    news = s['news']
    ref_percent_1 = s['ref_percent_1']
    ref_percent_2 = s['ref_percent_2']
    ref_percent_3 = s['ref_percent_3']
    default_language_s = s['default_lang']
    default_language = await db.get_language(name=default_language_s)
    currency = s['currency']
    curr = currencies[currency]

    if faq is None or faq == "-" or faq == "None":
        faq_emoji = "❌"
    else:
        faq_emoji = "✅"

    if support is None or support == "-" or support == "None":
        sup_emoji = "❌"
    else:
        sup_emoji = "✅"

    if chat is None or chat == "-" or chat == "None":
        chat_emoji = "❌"
    else:
        chat_emoji = "✅"

    if news is None or news == "-" or news == "None":
        news_emoji = "❌"
    else:
        news_emoji = '✅'

    kb.append(InlineKeyboardButton(f"FAQ | {faq_emoji}", callback_data="faq:edit"))
    kb.append(InlineKeyboardButton(f"Тех. Поддержка | {sup_emoji}", callback_data="sup:edit"))
    kb.append(InlineKeyboardButton(f"Чат | {chat_emoji}", callback_data="chat:edit"))
    kb.append(InlineKeyboardButton(f"Новостной | {news_emoji}", callback_data="news:edit"))
    kb.append(InlineKeyboardButton(f"Реф. Процент 1 лвл. | {ref_percent_1}%", callback_data="ref_percent:edit:1"))
    kb.append(InlineKeyboardButton(f"Реф. Процент 2 лвл. | {ref_percent_2}%", callback_data="ref_percent:edit:2"))
    kb.append(InlineKeyboardButton(f"Реф. Процент 3 лвл. | {ref_percent_3}%", callback_data="ref_percent:edit:3"))
    kb.append(InlineKeyboardButton(f"Язык по умолчанию | {default_language['name']}", callback_data="default_lang:edit"))
    kb.append(InlineKeyboardButton(f"Валюта в боте | {curr['sign']}", callback_data="currency:edit"))
    kb.append(InlineKeyboardButton(texts.back, callback_data="settings_back"))

    keyboard.add(kb[0], kb[1])
    keyboard.add(kb[2], kb[3])
    keyboard.add(kb[4])
    keyboard.add(kb[5])
    keyboard.add(kb[6])
    keyboard.add(kb[7])
    keyboard.add(kb[8])
    keyboard.add(kb[9])

    return keyboard


def currencies_kb():
    keyboard = InlineKeyboardMarkup()

    kb1 = InlineKeyboardButton(f"Рубль | {currencies['rub']['text']} | {currencies['rub']['sign']}",
                               callback_data="set_curr:rub")
    kb2 = InlineKeyboardButton(f"Доллар | {currencies['usd']['text']} | {currencies['usd']['sign']}",
                               callback_data="set_curr:usd")
    kb3 = InlineKeyboardButton(f"Евро | {currencies['eur']['text']} | {currencies['eur']['sign']}",
                               callback_data="set_curr:eur")
    kb4 = InlineKeyboardButton(texts.back, callback_data="settings")

    keyboard.add(kb1)
    keyboard.add(kb2)
    keyboard.add(kb3)
    keyboard.add(kb4)

    return keyboard



def find_back():
    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(texts.back, callback_data="find:"))

    return keyboard


async def profile_adm_inl(user_id):
    keyboard = InlineKeyboardMarkup()
    kb = []

    user = await db.get_user(id=user_id)

    kb.append(InlineKeyboardButton("💰 Выдать баланс", callback_data=f"user:balance_add:{user_id}"))
    kb.append(InlineKeyboardButton("💰 Изменить баланс", callback_data=f"user:balance_edit:{user_id}"))
    if user['is_ban'] == "True":
        kb.append(InlineKeyboardButton("⛔ Разблокировать", callback_data=f"user:is_ban_unban:{user_id}"))
    elif user['is_ban'] == "False":
        kb.append(InlineKeyboardButton("⛔ Заблокировать", callback_data=f"user:is_ban_ban:{user_id}"))
    kb.append(InlineKeyboardButton("⭐ Отправить уведомление", callback_data=f"user:sms:{user_id}"))

    keyboard.add(kb[0], kb[1])
    keyboard.add(kb[2])
    keyboard.add(kb[3])


    return keyboard


def find_settings():
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton("👤 Профиль", callback_data="find:profile"))
    kb.append(InlineKeyboardButton("🧾 Чек", callback_data="find:receipt"))
    kb.append(InlineKeyboardButton(texts.back, callback_data="settings_back"))

    keyboard.add(kb[0])
    keyboard.add(kb[1])
    keyboard.add(kb[2])

    return keyboard

def payments_settings():
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(texts.qiwi_text, callback_data="payments:qiwi"))
    kb.append(InlineKeyboardButton(texts.yoomoney_text, callback_data="payments:yoomoney"))
    kb.append(InlineKeyboardButton(texts.lava_text, callback_data="payments:lava"))
    kb.append(InlineKeyboardButton(texts.lzt_text, callback_data="payments:lzt"))
    kb.append(InlineKeyboardButton(texts.crystalPay_text, callback_data="payments:crystalPay"))
    kb.append(InlineKeyboardButton(texts.cryptoBot_text, callback_data="payments:cryptoBot"))
    kb.append(InlineKeyboardButton(texts.payok_text, callback_data="payments:payok"))
    kb.append(InlineKeyboardButton(texts.aaio_text, callback_data="payments:aaio"))
    kb.append(InlineKeyboardButton(texts.back, callback_data="settings_back"))

    keyboard.add(kb[0])
    keyboard.add(kb[1])
    keyboard.add(kb[2])
    keyboard.add(kb[3])
    keyboard.add(kb[4])
    keyboard.add(kb[5])
    keyboard.add(kb[6])
    keyboard.add(kb[7])
    keyboard.add(kb[8])

    return keyboard


def payments_settings_info(way, status):
    keyboard = InlineKeyboardMarkup()
    kb = []

    if status == "True":
        kb.append(InlineKeyboardButton("❌ Выключить", callback_data=f"payments_on_off:{way}:off"))
    else:
        kb.append(InlineKeyboardButton("✅ Включить", callback_data=f"payments_on_off:{way}:on"))
    kb.append(InlineKeyboardButton("💰 Узнать баланс", callback_data=f"payments_balance:{way}"))
    kb.append(InlineKeyboardButton("📌 Показать информацию", callback_data=f"payments_info:{way}"))
    kb.append(InlineKeyboardButton(texts.back, callback_data="payments"))

    keyboard.add(kb[0])
    keyboard.add(kb[1], kb[2])
    keyboard.add(kb[3])

    return keyboard

def set_back():
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(texts.back, callback_data="settings"))

    keyboard.add(kb[0])

    return keyboard

def payments_back():
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(texts.back, callback_data="payments"))

    keyboard.add(kb[0])

    return keyboard

def mail_types():
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton("💎 Просто текст", callback_data=f"mail:text"))
    kb.append(InlineKeyboardButton("📌 Текст с картинкой", callback_data=f"mail:photo"))
    kb.append(InlineKeyboardButton(texts.back, callback_data="settings_back"))

    keyboard.add(kb[0], kb[1])
    keyboard.add(kb[2])

    return keyboard

def opr_mail_text():
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton("✅ Да, хочу", callback_data=f"mail_start_text:yes"))
    kb.append(InlineKeyboardButton("❌ Нет, не хочу", callback_data=f"mail_start_text:no"))

    keyboard.add(kb[0], kb[1])

    return keyboard

def opr_mail_photo():
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton("✅ Да, хочу", callback_data=f"mail_start_photo:yes"))
    kb.append(InlineKeyboardButton("❌ Нет, не хочу", callback_data=f"mail_start_photo:no"))

    keyboard.add(kb[0], kb[1])

    return keyboard

def products_edits():
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton("➕ | Категорию", callback_data=f"add_cat"))
    kb.append(InlineKeyboardButton("⚙️ | Категорию", callback_data=f"edit_cat"))
    kb.append(InlineKeyboardButton("🗑️ | ВСЕ Категории", callback_data=f"del_all_cats"))

    kb.append(InlineKeyboardButton("➕ | Под-Категорию", callback_data=f"add_pod_cat"))
    kb.append(InlineKeyboardButton("⚙️ | Под-Категорию", callback_data=f"edit_pod_cat"))
    kb.append(InlineKeyboardButton("🗑️ | ВСЕ Под-Категории", callback_data=f"del_all_pod_cats"))

    kb.append(InlineKeyboardButton("➕ | Позицию", callback_data=f"add_pos"))
    kb.append(InlineKeyboardButton("⚙️ | Позицию", callback_data=f"edit_pos"))
    kb.append(InlineKeyboardButton("🗑️ | ВСЕ Позиции", callback_data=f"del_all_poss"))

    kb.append(InlineKeyboardButton("➕ | Товары", callback_data=f"add_items"))
    kb.append(InlineKeyboardButton("🗑️ | ВСЕ Товары", callback_data=f"del_all_items"))

    kb.append(InlineKeyboardButton(texts.back, callback_data="settings_back"))

    keyboard.add(kb[0], kb[1], kb[2])
    keyboard.add(kb[3], kb[4], kb[5])
    keyboard.add(kb[6], kb[7], kb[8])
    keyboard.add(kb[9], kb[10])
    keyboard.add(kb[11])

    return keyboard

def back_pr_edits():
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(texts.back, callback_data="pr_edit"))

    keyboard.add(kb[0])

    return keyboard

async def open_cats_for_edit():
    keyboard = InlineKeyboardMarkup()

    for category in await db.get_all_categories():
        name = category['name']
        cat_id = category['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"cat_edit:{cat_id}"))

    return keyboard


async def open_cats_for_add_mail_btn():
    keyboard = InlineKeyboardMarkup()

    for category in await db.get_all_categories():
        name = category['name']
        cat_id = category['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"cat_add_mail:{cat_id}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"back_mail_btn_type"))

    return keyboard


async def open_cats_for_pod_cat_add_mail_btn():
    keyboard = InlineKeyboardMarkup()

    for category in await db.get_all_categories():
        name = category['name']
        cat_id = category['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"cat_pod_add_mail:{cat_id}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"back_mail_btn_type"))

    return keyboard

async def open_pod_cats_for_add_mail_btn(cat_id):
    keyboard = InlineKeyboardMarkup()

    for pod_category in await db.get_pod_categories(cat_id):
        name = pod_category['name']
        pod_cat_id = pod_category['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"podss_cat_add_mail:{pod_cat_id}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"add_mail_buttons:pod_category"))

    return keyboard


async def open_cats_for_pos_add_mail():
    keyboard = InlineKeyboardMarkup()

    for category in await db.get_all_categories():
        name = category['name']
        cat_id = category['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"pos_cat_add_mail:{cat_id}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"back_mail_btn_type"))

    return keyboard

async def open_pod_cats_for_pos_add_mail(cat_id):
    keyboard = InlineKeyboardMarkup()

    for pod_category in await db.get_pod_categories(cat_id):
        name = pod_category['name']
        pod_cat_id = pod_category['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"pod_cat_pos_add_mail:{pod_cat_id}:{cat_id}"))
    for position in await db.get_positions(cat_id):
        name = position['name']
        pos_id = position['id']
        settings = await db.get_settings()
        if settings['currency'] == 'rub':
            price = position['price_rub']
        elif settings['currency'] == 'usd':
            price = position['price_dollar']
        elif settings['currency'] == 'eur':
            price = position['price_euro']
        items = f"{len(await db.get_items(position_id=pos_id))}шт"
        if position['infinity'] == "+":
            items = "[Безлимит]"
        if position['pod_category_id'] is not None:
            continue
        keyboard.add(InlineKeyboardButton(f"{name} | {price}{currencies[settings['currency']]['sign']} | {items}", callback_data=f"pos_add_mail:{pos_id}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"add_mail_buttons:position"))

    return keyboard

async def open_positions_for_pos_add_mail(cat_id, pod_cat_id = None):
    keyboard = InlineKeyboardMarkup()

    if pod_cat_id is None:
        for position in await db.get_positions(cat_id):
            name = position['name']
            pos_id = position['id']
            settings = await db.get_settings()
            if settings['currency'] == 'rub':
                price = position['price_rub']
            elif settings['currency'] == 'usd':
                price = position['price_dollar']
            elif settings['currency'] == 'eur':
                price = position['price_euro']
            items = await db.get_items(position_id=pos_id)
            keyboard.add(InlineKeyboardButton(f"{name} | {price}{currencies[settings['currency']]['sign']} | {len(items)}шт.", callback_data=f"pos_add_mail:{pos_id}"))
    else:
        for position in await db.get_positions(cat_id, pod_cat_id):
            name = position['name']
            pos_id = position['id']
            settings = await db.get_settings()
            if settings['currency'] == 'rub':
                price = position['price_rub']
            elif settings['currency'] == 'usd':
                price = position['price_dollar']
            elif settings['currency'] == 'eur':
                price = position['price_euro']
            items = await db.get_items(position_id=pos_id)
            keyboard.add(InlineKeyboardButton(f"{name} | {price}{currencies[settings['currency']]['sign']} | {len(items)}шт.", callback_data=f"pos_add_mail:{pos_id}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"pos_cat_add_mail:{cat_id}"))

    return keyboard


async def open_cats_for_edit_pod_cat():
    keyboard = InlineKeyboardMarkup()

    for category in await db.get_all_categories():
        name = category['name']
        cat_id = category['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"pods_cat_edit:{cat_id}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"pr_edit"))

    return keyboard

async def open_pod_cats_for_edit(cat_id):
    keyboard = InlineKeyboardMarkup()

    for pod_category in await db.get_pod_categories(cat_id):
        name = pod_category['name']
        pod_cat_id = pod_category['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"podss_cat_edit:{pod_cat_id}"))

    return keyboard

async def open_cats_for_add_pod_cat():
    keyboard = InlineKeyboardMarkup()

    for category in await db.get_all_categories():
        name = category['name']
        cat_id = category['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"add_pod_cat_cat:{cat_id}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"pr_edit"))

    return keyboard

def edit_cat_inl(cat_id):
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(f"Изменить название", callback_data=f"edit_cat_name:{cat_id}"))
    kb.append(InlineKeyboardButton(f"Удалить", callback_data=f"del_cat:{cat_id}"))
    kb.append(InlineKeyboardButton(texts.back, callback_data=f"edit_cat"))

    keyboard.add(kb[0], kb[1])
    keyboard.add(kb[2])

    return keyboard

def choose_del_cat(cat_id):
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(f"✅ Да, хочу", callback_data=f"dels_cat:yes:{cat_id}"))
    kb.append(InlineKeyboardButton(f"❌ Нет, не хочу", callback_data=f"dels_cat:no:{cat_id}"))

    keyboard.add(kb[0], kb[1])

    return keyboard

def choose_del_all_cats():
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(f"✅ Да, хочу", callback_data=f"dels_all_cat:yes"))
    kb.append(InlineKeyboardButton(f"❌ Нет, не хочу", callback_data=f"dels_all_cat:no"))

    keyboard.add(kb[0], kb[1])

    return keyboard

def update_pod_cat_inl(pod_cat_id):
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(f"Изменить название", callback_data=f"edit_pod_cat_name:{pod_cat_id}"))
    kb.append(InlineKeyboardButton(f"Удалить", callback_data=f"del_pod_cat:{pod_cat_id}"))
    kb.append(InlineKeyboardButton(texts.back, callback_data=f"edit_pod_cat"))

    keyboard.add(kb[0], kb[1])
    keyboard.add(kb[2])

    return keyboard

def choose_del_pod_cat(pod_cat_id):
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(f"✅ Да, хочу", callback_data=f"dels_pod_cat:yes:{pod_cat_id}"))
    kb.append(InlineKeyboardButton(f"❌ Нет, не хочу", callback_data=f"dels_pod_cat:no:{pod_cat_id}"))

    keyboard.add(kb[0], kb[1])

    return keyboard

def choose_del_all_pod_cats():
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(f"✅ Да, хочу", callback_data=f"dels_all_pod_cats:yes"))
    kb.append(InlineKeyboardButton(f"❌ Нет, не хочу", callback_data=f"dels_all_pod_cats:no"))

    keyboard.add(kb[0], kb[1])

    return keyboard

async def open_cats_for_add_pos():
    keyboard = InlineKeyboardMarkup()

    for category in await db.get_all_categories():
        name = category['name']
        cat_id = category['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"add_pos_cat:{cat_id}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"pr_edit"))

    return keyboard

async def open_pod_cats_for_add_pos(cat_id):
    keyboard = InlineKeyboardMarkup()

    for pod_category in await db.get_pod_categories(cat_id):
        name = pod_category['name']
        pod_cat_id = pod_category['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"pod_cat_add_pos:{pod_cat_id}:{cat_id}"))

    keyboard.add(InlineKeyboardButton(f"💎 Выбрать эту категорию", callback_data=f"add_poss_cat:{cat_id}"))
    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"add_pos"))

    return keyboard


async def open_cats_for_edit_pos():
    keyboard = InlineKeyboardMarkup()

    for category in await db.get_all_categories():
        name = category['name']
        cat_id = category['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"edit_pos_cat:{cat_id}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"pr_edit"))

    return keyboard

async def open_pod_cats_for_edit_pos(cat_id):
    keyboard = InlineKeyboardMarkup()

    for pod_category in await db.get_pod_categories(cat_id):
        name = pod_category['name']
        pod_cat_id = pod_category['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"pod_cat_edit_pos:{pod_cat_id}:{cat_id}"))
    for position in await db.get_positions(cat_id):
        name = position['name']
        pos_id = position['id']
        settings = await db.get_settings()
        if settings['currency'] == 'rub':
            price = position['price_rub']
        elif settings['currency'] == 'usd':
            price = position['price_dollar']
        elif settings['currency'] == 'eur':
            price = position['price_euro']
        items = f"{len(await db.get_items(position_id=pos_id))}шт"
        if position['infinity'] == "+":
            items = "[Безлимит]"
        if position['pod_category_id'] is not None:
            continue
        keyboard.add(InlineKeyboardButton(f"{name} | {price}{currencies[settings['currency']]['sign']} | {items}", callback_data=f"edit_pos:{pos_id}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"edit_pos"))

    return keyboard

async def open_positions_for_edit(cat_id, pod_cat_id = None):
    keyboard = InlineKeyboardMarkup()

    if pod_cat_id is None:
        for position in await db.get_positions(cat_id):
            name = position['name']
            pos_id = position['id']
            settings = await db.get_settings()
            if settings['currency'] == 'rub':
                price = position['price_rub']
            elif settings['currency'] == 'usd':
                price = position['price_dollar']
            elif settings['currency'] == 'eur':
                price = position['price_euro']
            items = await db.get_items(position_id=pos_id)
            keyboard.add(InlineKeyboardButton(f"{name} | {price}{currencies[settings['currency']]['sign']} | {len(items)}шт.", callback_data=f"edit_pos:{pos_id}"))
    else:
        for position in await db.get_positions(cat_id, pod_cat_id):
            name = position['name']
            pos_id = position['id']
            settings = await db.get_settings()
            if settings['currency'] == 'rub':
                price = position['price_rub']
            elif settings['currency'] == 'usd':
                price = position['price_dollar']
            elif settings['currency'] == 'eur':
                price = position['price_euro']
            items = await db.get_items(position_id=pos_id)
            keyboard.add(InlineKeyboardButton(f"{name} | {price}{currencies[settings['currency']]['sign']} | {len(items)}шт.", callback_data=f"edit_pos:{pos_id}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"edit_pos"))

    return keyboard

def edit_pos_inl(pos_id):
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(f"Цена", callback_data=f"edit_price_pos:{pos_id}"))
    kb.append(InlineKeyboardButton(f"Название", callback_data=f"edit_name_pos:{pos_id}"))
    kb.append(InlineKeyboardButton(f"Описание", callback_data=f"edit_desc_pos:{pos_id}"))
    kb.append(InlineKeyboardButton(f"Фото", callback_data=f"edit_photo_pos:{pos_id}"))
    kb.append(InlineKeyboardButton(f"Тип товара", callback_data=f"edit_infinity_pos:{pos_id}"))
    kb.append(InlineKeyboardButton(f"Удалить", callback_data=f"edit_del_pos:{pos_id}"))
    kb.append(InlineKeyboardButton(f"Очистить товары", callback_data=f"edit_clear_items_pos:{pos_id}"))
    kb.append(InlineKeyboardButton(f"Загрузить товары", callback_data=f"edit_upload_items_pos:{pos_id}"))


    keyboard.add(kb[0], kb[1])
    keyboard.add(kb[2], kb[3], kb[4])
    keyboard.add(kb[5])
    keyboard.add(kb[7], kb[6])
    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"edit_pos"))

    return keyboard

def choose_del_pos(pos_id):
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(f"✅ Да, хочу", callback_data=f"dels_pos:yes:{pos_id}"))
    kb.append(InlineKeyboardButton(f"❌ Нет, не хочу", callback_data=f"dels_pos:no:{pos_id}"))

    keyboard.add(kb[0], kb[1])

    return keyboard

def choose_del_all_pos():
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(f"✅ Да, хочу", callback_data=f"dels_all_poss:yes"))
    kb.append(InlineKeyboardButton(f"❌ Нет, не хочу", callback_data=f"dels_all_poss:no"))

    keyboard.add(kb[0], kb[1])

    return keyboard

async def open_cats_for_add_items():
    keyboard = InlineKeyboardMarkup()

    for category in await db.get_all_categories():
        name = category['name']
        cat_id = category['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"add_items_cat:{cat_id}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"pr_edit"))

    return keyboard

async def open_pod_cats_for_add_items(cat_id):
    keyboard = InlineKeyboardMarkup()

    for pod_category in await db.get_pod_categories(cat_id):
        name = pod_category['name']
        pod_cat_id = pod_category['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"pod_cat_add_items:{pod_cat_id}:{cat_id}"))
    for position in await db.get_positions(cat_id):
        name = position['name']
        pos_id = position['id']
        settings = await db.get_settings()
        if settings['currency'] == 'rub':
            price = position['price_rub']
        elif settings['currency'] == 'usd':
            price = position['price_dollar']
        elif settings['currency'] == 'eur':
            price = position['price_euro']
        items = f"{len(await db.get_items(position_id=pos_id))}шт"
        if position['infinity'] == "+":
            items = "[Безлимит]"
        if position['pod_category_id'] is not None:
            continue
        keyboard.add(InlineKeyboardButton(f"{name} | {price}{currencies[settings['currency']]['sign']} | {items}", callback_data=f"pos_add_items:{pos_id}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"edit_pos"))

    return keyboard

async def open_positions_for_add_items(cat_id, pod_cat_id = None):
    keyboard = InlineKeyboardMarkup()
    settings = await db.get_settings()
    if pod_cat_id is None:
        for position in await db.get_positions(cat_id):
            name = position['name']
            pos_id = position['id']
            if settings['currency'] == 'rub':
                price = position['price_rub']
            elif settings['currency'] == 'usd':
                price = position['price_dollar']
            elif settings['currency'] == 'eur':
                price = position['price_euro']
            items = await db.get_items(position_id=pos_id)
            keyboard.add(InlineKeyboardButton(f"{name} | {price}{currencies[settings['currency']]['sign']} | {len(items)}шт.", callback_data=f"spos_add_items:{pos_id}"))
    else:
        for position in await db.get_positions(cat_id, pod_cat_id):
            name = position['name']
            pos_id = position['id']
            if settings['currency'] == 'rub':
                price = position['price_rub']
            elif settings['currency'] == 'usd':
                price = position['price_dollar']
            elif settings['currency'] == 'eur':
                price = position['price_euro']
            items = await db.get_items(position_id=pos_id)
            keyboard.add(InlineKeyboardButton(f"{name} | {price}{currencies[settings['currency']]['sign']} | {len(items)}шт.", callback_data=f"spos_add_items:{pos_id}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"edit_pos"))

    return keyboard

def stop_add_items():
    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(f"❌ Закончить загрузку", callback_data=f"stop_add_items"))

    return keyboard

def choose_del_all_items():
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(f"✅ Да, хочу", callback_data=f"dels_all_items:yes"))
    kb.append(InlineKeyboardButton(f"❌ Нет, не хочу", callback_data=f"dels_all_items:no"))

    keyboard.add(kb[0], kb[1])

    return keyboard

def choose_clear_items_pos(pos_id):
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(f"✅ Да, хочу", callback_data=f"clear_items:yes:{pos_id}"))
    kb.append(InlineKeyboardButton(f"❌ Нет, не хочу", callback_data=f"clear_items:no:{pos_id}"))

    keyboard.add(kb[0], kb[1])

    return keyboard