# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from tgbot.data.config import db, currencies
from tgbot.data import config
from tgbot.data.loader import dp, bot
from tgbot.utils.utils_functions import get_admins, get_channels, convert_words
import time
from datetime import datetime, timedelta

def sub():
    s = InlineKeyboardMarkup()
    s.row(InlineKeyboardButton(text='Подписаться', url=config.channel_url))
    s.row(InlineKeyboardButton(text="Проверить ✅", callback_data='subprov'))

    return s


async def mail_btn():
    btns = await db.get_all_mail_buttons()
    kb = InlineKeyboardMarkup()

    for btn in btns:
        name = btn['name']
        tip = str(btn['type']).split("|")[0]
        value = str(btn['type']).split("|")[1]

        if tip == 'link':
            kb.add(InlineKeyboardButton(name, url=value))
        elif tip == 'category_open':
            kb.add(InlineKeyboardButton(name, callback_data=f'mail_cat_open:{value}'))
        elif tip == 'pod_category_open':
            kb.add(InlineKeyboardButton(name, callback_data=f'mail_pod_cat_open:{value}'))
        elif tip == 'position_open':
            kb.add(InlineKeyboardButton(name, callback_data=f'mail_pos_open:{value}'))
        elif tip == "contest_open":
            kb.add(InlineKeyboardButton(name, callback_data=f'mail_contest_view:{value}'))

    return kb


async def user_menu(texts, user_id):
    s = await db.get_settings()
    pr_buttons = await db.get_all_pr_buttons()
    if s['keyboard'] == 'Inline':
        keyboard = InlineKeyboardMarkup()
        kb = []

        kb.append(InlineKeyboardButton(texts.products, callback_data="products:open"))
        kb.append(InlineKeyboardButton(texts.profile, callback_data="profile"))
        kb.append(InlineKeyboardButton(texts.faq, callback_data="faq:open"))
        kb.append(InlineKeyboardButton(texts.support, callback_data="support:open"))
        kb.append(InlineKeyboardButton(texts.refill, callback_data="refill"))
        kb.append(InlineKeyboardButton(texts.contest, callback_data="contests"))
        kb.append(InlineKeyboardButton("⚙️ Меню Администратора", callback_data="admin_menu"))

        keyboard.add(kb[0], kb[1])
        keyboard.add(kb[2], kb[3])
        keyboard.add(kb[4])
        if s['contests_is_on'] == "True":
            keyboard.add(kb[5])

        if user_id in get_admins():
            keyboard.add(kb[6])

        for button in pr_buttons:
            keyboard.add(InlineKeyboardButton(button['name'], callback_data=f"pr_button_user:{button['id']}"))

        return keyboard
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

        keyboard.row(texts.products, texts.profile)
        keyboard.row(texts.faq, texts.support)
        keyboard.row(texts.refill)
        if s['contests_is_on'] == "True":
            keyboard.row(texts.contest)

        if user_id in get_admins():
            keyboard.row("⚙️ Меню Администратора")

        for button in pr_buttons:
            keyboard.add(button['name'])

        return keyboard


async def contest_inl(texts, con_id, user):
    kb = InlineKeyboardMarkup()

    count, count_conds, c_count = 0, 0, 0
    conds = []
    contest = await db.get_contest(con_id)
    settings = await db.get_contests_settings()

    if contest['refills_num'] > 0:
        count_conds += 1
        conds.append("refills_num")
    if contest['purchases_num'] > 0:
        count_conds += 1
        conds.append("purchases_num")
    if len(get_channels(contest['channels_ids'])) > 0:
        count_conds += 1
        conds.append("channels_ids")

    if user['count_refills'] >= contest['refills_num'] and "refills_num" in conds:
        count += 1
    if len(await db.get_user_purchases(user['id'])) >= contest['purchases_num'] and "purchases_num" in conds:
        count += 1
    # проверка на подписку канала

    channels_ids = get_channels(contest['channels_ids'])
    for channel_id in channels_ids:
        user_status = await bot.get_chat_member(chat_id=channel_id, user_id=user['id'])
        if user_status["status"] == 'left':
            pass
        else:
            c_count += 1

    if c_count == len(channels_ids) and "channels_ids" in conds:
        count += 1

    if count == count_conds:
        kb.add(InlineKeyboardButton(texts.contest_enter, callback_data=f'contest_enter:{con_id}'))
    else:
        kb.add(InlineKeyboardButton(f"❗ Вы не выполнили все условия! Выполнено {count} из {count_conds}",
                                    callback_data=f'contest_enter3453tfdh'))

    return kb


async def faq_inl(texts):
    keyboard = InlineKeyboardMarkup()
    kb = []
    s = await db.get_settings()
    news = s['news']
    chat = s['chat']

    kb.append(InlineKeyboardButton(texts.faq_chat_inl, url=chat))
    kb.append(InlineKeyboardButton(texts.faq_news_inl, url=news))

    keyboard.add(kb[0], kb[1])

    return keyboard


async def support_inll(texts):
    keyboard = InlineKeyboardMarkup()
    kb = []
    s = await db.get_settings()
    kb.append(InlineKeyboardButton(texts.support_inl, url=s['support']))

    keyboard.add(kb[0])

    return keyboard


async def chat_inl(texts):
    keyboard = InlineKeyboardMarkup()
    kb = []
    s = await db.get_settings()
    link = s['chat']

    kb.append(InlineKeyboardButton(texts.faq_chat_inl, url=link))

    keyboard.add(kb[0])

    return keyboard


async def news_inl(texts):
    keyboard = InlineKeyboardMarkup()
    kb = []
    s = await db.get_settings()
    link = s['news']

    kb.append(InlineKeyboardButton(texts.faq_news_inl, url=link))

    keyboard.add(kb[0])

    return keyboard


async def profile_inl(texts):
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(texts.ref_system, callback_data="ref_system"))
    kb.append(InlineKeyboardButton(texts.promocode, callback_data="promo_act"))
    kb.append(InlineKeyboardButton(texts.last_purchases_text, callback_data="last_purchases"))
    kb.append(InlineKeyboardButton(texts.change_language, callback_data="change_language"))
    kb.append(InlineKeyboardButton(texts.back, callback_data="back_to_user_menu"))

    keyboard.add(kb[0])
    keyboard.add(kb[1], kb[2])
    if (await db.get_settings())['multi_lang'] == "True":
        keyboard.add(kb[3])
    keyboard.add(kb[4])

    return keyboard


async def choose_contest(contests):
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
                                   callback_data=f"contest_view:{contest['id']}"))
    return k


def choose_asset_crypto(texts):
    k = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton("USDT", callback_data=f"refill:crypto_bot:USDT"))
    kb.append(InlineKeyboardButton("BTC", callback_data=f"refill:crypto_bot:BTC"))
    kb.append(InlineKeyboardButton("ETH", callback_data=f"refill:crypto_bot:ETH"))
    kb.append(InlineKeyboardButton("USDC", callback_data=f"refill:crypto_bot:USDC"))
    kb.append(InlineKeyboardButton("TON", callback_data=f"refill:crypto_bot:TON"))
    kb.append(InlineKeyboardButton(texts.back, callback_data=f"refill"))

    k.add(kb[0], kb[1], kb[2])
    k.add(kb[3], kb[4])
    k.add(kb[5])

    return k


def back_to_profile(texts):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(texts.back, callback_data="profile"))

    return keyboard


def back_to_user_menu(texts):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(texts.back, callback_data="back_to_user_menu"))

    return keyboard


def refill_open_inl(texts, way, amount, link, id, second_amount):
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(texts.refill_link_inl, url=link))
    kb.append(InlineKeyboardButton(texts.refill_check_inl, callback_data=f"check_opl:{way}:{amount}:{id}:{second_amount}"))

    keyboard.add(kb[0])
    keyboard.add(kb[1])

    return keyboard


async def refill_inl(texts):
    keyboard = InlineKeyboardMarkup()
    kb = []
    s = await db.get_payments()
    qiwi = s['pay_qiwi']
    yoomoney = s['pay_yoomoney']
    lava = s['pay_lava']
    crystal = s['pay_crystal']
    lolz = s['pay_lolz']
    crypto = s['pay_crypto']
    payok = s['pay_payok']
    aaio = s['pay_aaio']

    if qiwi == "True":
        kb.append(InlineKeyboardButton(texts.qiwi_text, callback_data="refill:qiwi"))
    if yoomoney == "True":
        kb.append(InlineKeyboardButton(texts.yoomoney_text, callback_data="refill:yoomoney"))
    if lava == "True":
        kb.append(InlineKeyboardButton(texts.lava_text, callback_data="refill:lava"))
    if lolz == "True":
        kb.append(InlineKeyboardButton(texts.lzt_text, callback_data="refill:lolz"))
    if crystal == "True":
        kb.append(InlineKeyboardButton(texts.crystalPay_text, callback_data="refill:crystal"))
    if crypto == 'True':
        kb.append(InlineKeyboardButton(texts.cryptoBot_text, callback_data='crypto_bot'))
    if payok == 'True':
        kb.append(InlineKeyboardButton(texts.payok_text, callback_data='refill:payok'))
    if aaio == "True":
        kb.append(InlineKeyboardButton(texts.aaio_text, callback_data='refill:aaio'))

    if len(kb) == 8:
        keyboard.add(kb[0], kb[1])
        keyboard.add(kb[2], kb[3])
        keyboard.add(kb[4], kb[5])
        keyboard.add(kb[6], kb[7])
    elif len(kb) == 7:
        keyboard.add(kb[0], kb[1])
        keyboard.add(kb[2], kb[3])
        keyboard.add(kb[4], kb[5])
        keyboard.add(kb[6])
    elif len(kb) == 6:
        keyboard.add(kb[0], kb[1])
        keyboard.add(kb[2], kb[3])
        keyboard.add(kb[4], kb[5])
    elif len(kb) == 5:
        keyboard.add(kb[0])
        keyboard.add(kb[1], kb[2])
        keyboard.add(kb[3], kb[4])
    elif len(kb) == 4:
        keyboard.add(kb[0], kb[1])
        keyboard.add(kb[2], kb[3])
    elif len(kb) == 3:
        keyboard.add(kb[0])
        keyboard.add(kb[1], kb[2])
    elif len(kb) == 2:
        keyboard.add(kb[0], kb[1])
    elif len(kb) == 1:
        keyboard.add(kb[0])

    keyboard.add(InlineKeyboardButton(texts.back, callback_data="back_to_user_menu"))

    return keyboard


def back_to_user_menu(texts):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(texts.back, callback_data="back_to_user_menu"))

    return keyboard


async def open_products(texts):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(texts.search, callback_data='search_pos'))

    for category in await db.get_all_categories():
        name = category['name']
        cat_id = category['id']
        keyboard.add(InlineKeyboardButton(name, callback_data=f"open_category:{cat_id}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data="back_to_user_menu"))

    return keyboard


async def open_pod_cat_positions(texts, pod_cat_id):
    keyboard = InlineKeyboardMarkup()

    for pos in await db.get_positions(pod_cat_id=pod_cat_id):
        name = pos['name']
        pos_id = pos['id']
        items = f"{len(await db.get_items(position_id=pos_id))} {texts.pcs}"
        if pos['infinity'] == "+":
            items = texts.inf
        settings = await db.get_settings()
        if settings['currency'] == 'rub':
            price = pos['price_rub']
        elif settings['currency'] == 'usd':
            price = pos['price_dollar']
        elif settings['currency'] == 'eur':
            price = pos['price_euro']
        keyboard.add(
            InlineKeyboardButton(f"{name} | {price}{config.currencies[settings['currency']]['sign']} | {items}",
                                 callback_data=f"open_pos:{pos_id}"))

    pod_cat = await db.get_pod_category(pod_cat_id)

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"open_category:{pod_cat['cat_id']}"))

    return keyboard


async def open_positions(texts, cat_id):
    keyboard = InlineKeyboardMarkup()

    for pod_cat in await db.get_pod_categories(cat_id): 
        pod_cat_id = pod_cat['id']
        pod_cat_len = await db.get_positions_len(pod_cat_id)
        name = pod_cat['name'] + f" | {pod_cat_len} {texts.pcs}"
        keyboard.add(InlineKeyboardButton(name, callback_data=f"open_pod_cat:{pod_cat_id}"))
    for pos in await db.get_positions(cat_id):
        if pos['pod_category_id'] is not None:
            continue
        name = pos['name']
        pos_id = pos['id']
        settings = await db.get_settings()
        if settings['currency'] == 'rub':
            price = pos['price_rub']
        elif settings['currency'] == 'usd':
            price = pos['price_dollar']
        elif settings['currency'] == 'eur':
            price = pos['price_euro']
        items = f"{len(await db.get_items(position_id=pos_id))} {texts.pcs}"
        if pos['infinity'] == "+":
            items = texts.inf
        keyboard.add(
            InlineKeyboardButton(f"{name} | {price}{config.currencies[settings['currency']]['sign']} | {items}",
                                 callback_data=f"open_pos:{pos_id}"))

    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"products:open"))

    return keyboard


async def pos_buy_inl(texts, pos_id):
    keyboard = InlineKeyboardMarkup()
    pos = await db.get_position(pos_id)
    keyboard.add(InlineKeyboardButton(texts.buy, callback_data=f"buy_pos:{pos_id}"))
    keyboard.add(InlineKeyboardButton(texts.back, callback_data=f"open_category:{pos['category_id']}"))

    return keyboard


async def choose_languages_kb():
    keyboard = InlineKeyboardMarkup(row_width=2)
    langs = await db.get_all_languages()

    for lang in langs:
        keyboard.add(InlineKeyboardButton(lang['name'], callback_data=f"change_language:{lang['language']}"))

    return keyboard



def choose_buy_items(pos_id, amount):
    keyboard = InlineKeyboardMarkup()
    kb = []

    kb.append(InlineKeyboardButton(f"✅ Да, хочу", callback_data=f"buy_items:yes:{pos_id}:{amount}"))
    kb.append(InlineKeyboardButton(f"❌ Нет, не хочу", callback_data=f"buy_items:no:{pos_id}:{amount}"))

    keyboard.add(kb[0], kb[1])

    return keyboard
