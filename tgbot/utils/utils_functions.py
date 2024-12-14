# - *- coding: utf- 8 - *-
import time, random, configparser, aiohttp, asyncio, os
from datetime import datetime
from traceback import print_exc
from tgbot.data import config
from tgbot.data.loader import bot
from tgbot.data.config import db, currencies
from bs4 import BeautifulSoup as bs
from rates import get_def_exchanges

#Языки
from tgbot.data.config import lang_en, lang_ru, lang_ua


# Получение текущего unix времени
def get_unix(full=False):
    if full:
        return time.time_ns()
    else:
        return int(time.time())


async def update_balance(user_id, amount, add=True):
    user = await db.get_user(id=user_id)
    if add:
        amount_eur = float(user['balance_euro']) + float(await get_exchange(amount, 'RUB', 'EUR'))
        amount_usd = float(user['balance_dollar']) + float(await get_exchange(amount, 'RUB', 'USD'))
        amount_rub = float(user['balance_rub']) + float(amount)
    else:
        amount_eur = float(user['balance_euro']) - float(await get_exchange(amount, 'RUB', 'EUR'))
        amount_usd = float(user['balance_dollar']) - float(await get_exchange(amount, 'RUB', 'USD'))
        amount_rub = float(user['balance_rub']) - float(amount)

    await db.update_user(id=user_id, balance_euro=amount_eur, balance_dollar=amount_usd, balance_rub=amount_rub)


# Получение текущей даты
def get_date():
    this_date = datetime.today().replace(microsecond=0)
    this_date = this_date.strftime("%d.%m.%Y %H:%M:%S")

    return this_date


# Получение админов
def get_admins():
    read_admins = configparser.ConfigParser()
    read_admins.read("settings.ini")

    admins = read_admins['settings']['admin_id'].strip().replace(" ", "")

    if "," in admins:
        admins = admins.split(",")
    else:
        if len(admins) >= 1:
            admins = [admins]
        else:
            admins = []

    while "" in admins:
        admins.remove("")
    while " " in admins:
        admins.remove(" ")

    admins = list(map(int, admins))

    return admins


def get_channels(channels):
    try:
        channels = str(channels)

        if channels == "-":
            return []

        if "," in channels:
            channels = channels.split(",")
        else:
            if len(channels) >= 1:
                channels = [channels]
            else:
                channels = []
        while "" in channels:
            channels.remove("")
        while " " in channels:
            channels.remove(" ")

        channels = list(map(int, channels))

        return channels
    except Exception as err:
        print(err)
        return []


# Разбив списка по количеству переданных значений
def split_messages(get_list, count):
    return [get_list[i:i + count] for i in range(0, len(get_list), count)]


def convert_time(time, type):
    time = int(time)
    seconds = ['секунда', 'секунды', 'секунд']
    hours = ['час', 'часа', 'часов']
    days = ['день', 'дня', 'дней']
    years = ['год', 'года', 'лет']
    weeks = ['неделя', 'недели', 'недель']
    months = ['месяц', 'месяца', 'месяцев']

    if time % 10 == 1 and time % 100 != 11:
        count = 0
    elif 2 <= time % 10 <= 4 and (time % 100 < 10 or time % 100 >= 20):
        count = 1
    else:
        count = 2

    if type == "days":
        return days[count]
    elif type == "seconds":
        return seconds[count]
    elif type == "hours":
        return hours[count]
    elif type == "weeks":
        return weeks[count]
    elif type == "years":
        return years[count]
    elif type == "seconds":
        return seconds[count]
    elif type == 'months':
        return months[count]


def convert_words(num, words):
    num = int(num)

    if num % 10 == 1 and num % 100 != 11:
        count = 0
    elif 2 <= num % 10 <= 4 and (num % 100 < 10 or num % 100 >= 20):
        count = 1
    else:
        count = 2

    return f"{words[count]}"


async def send_admins(msg, channel, photo=None, file=None):
    channel_id = config.logs_channel_id
    if channel_id == "":
        for admin in get_admins():
            if photo:
                await bot.send_photo(chat_id=admin, photo=photo, caption=msg)
            elif file:
                await bot.send_document(chat_id=admin, document=file, caption=msg)
            else:
                await bot.send_message(chat_id=admin, text=msg)
    else:
        if channel == True:
            if photo:
                await bot.send_photo(chat_id=channel_id, photo=photo, caption=msg)
            elif file:
                await bot.send_document(chat_id=channel_id, document=file, caption=msg)
            else:
                await bot.send_message(chat_id=channel_id, text=msg)
        elif channel == False:
            for admin in get_admins():
                if photo:
                    await bot.send_photo(chat_id=admin, photo=photo, caption=msg)
                elif file:
                    await bot.send_document(chat_id=admin, document=file, caption=msg)
                else:
                    await bot.send_message(chat_id=admin, text=msg)


async def check_rates():
    rate_usd_to_rub, rate_usd_to_eur, rate_eur_to_rub, rate_eur_to_usd, rate_rub_to_usd, rate_rub_to_eur = await get_def_exchanges()

    await db.update_rates(usd_rub=rate_usd_to_rub, usd_eur=rate_usd_to_eur, eur_rub=rate_eur_to_rub,
                          eur_usd=rate_eur_to_usd, rub_usd=rate_rub_to_usd, rub_eur=rate_rub_to_eur)


async def get_exchange(amount: float, cur1: str, cur2: str):
    try:
        rate_usd_to_rub, rate_usd_to_eur, rate_eur_to_rub, rate_eur_to_usd, rate_rub_to_usd, rate_rub_to_eur = await db.get_rates()

        if amount == 0.0 or amount == 0:
            return 0
        if cur1.upper() == 'RUB' and cur2.upper() == 'USD':
            return round(float(rate_rub_to_usd * amount), 2)
        elif cur1.upper() == 'RUB' and cur2.upper() == 'EUR':
            return round(float(rate_rub_to_eur * amount), 2)
        elif cur1.upper() == 'USD' and cur2.upper() == 'RUB':
            return round(float(rate_usd_to_rub * amount), 2)
        elif cur1.upper() == 'EUR' and cur2.upper() == 'RUB':
            return round(float(rate_eur_to_rub * amount), 2)
        elif cur1.upper() == 'USD' and cur2.upper() == 'EUR':
            return round(float(rate_usd_to_eur * amount), 2)
        elif cur1.upper() == 'EUR' and cur2.upper() == 'USD':
            return round(float(rate_eur_to_usd * amount), 2)
    except:
        print_exc()


async def check_updates():
    async with aiohttp.ClientSession() as session:
        ress = await session.get(f'https://sites.google.com/view/tosa-projects/главная-страница')
        res = await ress.text()
        soup = bs(res, "html.parser")
        res2 = soup.findAll('p', class_='zfr3Q CDt4Ke')
        ress = str(res2[1])
        res3 = ress.split("Актуальная версия: ")[1]
        current_version = res3.split('</span></p>')[0]
        if config.bot_version != current_version:
            msg = f"""
<b>❗❗❗ Обновление AutoShop'а ❗❗❗

🧩 Ваша текущая версия: <code>{config.bot_version}</code>

⭐ Новая версия: <code>{current_version}</code>

https://zelenka.guru/threads/4980786/
https://zelenka.guru/threads/4980786/
https://zelenka.guru/threads/4980786/

<u>Данное оповещение видят только администраторы бота!</u></b>
                """
            for admin in get_admins():
                await bot.send_message(chat_id=admin, text=msg)
                

async def end_contest(contest_id):
    settings = await db.get_settings()
    cur = currencies[settings['currency']]['sign']
    contest = await db.get_contest(contest_id)
    members = await db.get_contest_members(contest_id)
    all_members = []
    for member in members:
        all_members.append(member['user_id'])
    winners_num = contest['winners_num']
    winners_ids = []
    if len(all_members) == 0:
        msg = f"""
❗ В розыгрыше на {contest['prize']}{cur} никто не выиграл, т.к. участников 0!
        """
        await db.delete_contest(contest_id)
        await send_admins(msg, True)
        return await send_admins(msg, False)

    if winners_num == 1:
        random.shuffle(all_members)
        winners_ids.append(random.choice(all_members))
    else:
        winners_ids = []
        while len(winners_ids) <= (winners_num - 1):
            random.shuffle(all_members)
            winner_id = random.choice(all_members)
            if winner_id in winners_ids:
                continue
            else:
                winners_ids.append(winner_id)
    msg = f"""
❗ В розыгрыше на {contest['prize']}{cur} выиграли:
            """
    for winner in winners_ids:
        await db.delete_contest(contest_id)
        member = await bot.get_chat(winner)
        msg += f"@{member.username} | [<code>{member.id}</code>]" if member.username else f"@{member.get_mention(as_html=True)} | [<code>{member.id}</code>]"
        msg += f"\n\n❗ Приз был выдан! ❗"
        await send_admins(msg, True)
        await send_admins(msg, False)
        await update_balance(winner, contest['prize'], True)
        try:
            texts = await get_language(winner)
            await bot.send_message(chat_id=winner, text=texts.u_win_the_contest.format(contest['prize'], cur))
        except:
            pass


async def check_contests():
    while True:
        await asyncio.sleep(3)
        contests = await db.get_contests()
        for contest in contests:
            contest_id = contest['id']
            now_time = time.time()
            members = await db.get_contest_members_id(contest_id)
            if len(members) == contest['members_num']:
                await end_contest(contest_id)
            elif contest['end_time'] < now_time:
                await end_contest(contest_id)
            else:
                continue


async def get_language(user_id):
    settings = await db.get_settings()
    if settings['multi_lang'] == 'True':
        lang = (await db.get_user(id=user_id))['language']
    else:
        lang = settings['default_lang']

    if lang == "ru":
        return lang_ru
    elif lang == "en":
        return lang_en
    elif lang == 'ua':
        return lang_ua


async def get_users_and_their_balances_in_file(call):
    try:
        msg = ""

        user_sum = await db.sum_balances()
        users_balances = await db.get_all_users_and_their_balance()

        for user in users_balances:
            if int(user['rub']) == 0:
                continue
            try:
                chat = await bot.get_chat(chat_id=user['user_id'])
            except:
                continue
            msg += f"{chat.full_name} @{chat.username} (ID: {chat.id}) - {round(user['rub'], 2)}₽ | {round(user['usd'], 2)}$ | {round(user['eur'], 2)}€\n"

        with open('users_balances.txt', 'w', encoding="utf-8") as f:
            f.write(f"Сумма: {round(user_sum['rub'], 2)}₽ | {round(user_sum['usd'], 2)}$ | {round(user_sum['eur'], 2)}€\n\n"
                    f"Все юзеры и их балансы больше 0:\n\n"
                    f"{msg}")
            f.close()

        await bot.send_document(call.message.chat.id, open('users_balances.txt', 'rb'), caption="Все юзеры и их балансы")

        os.remove("users_balances.txt")
    except:
        print_exc()
