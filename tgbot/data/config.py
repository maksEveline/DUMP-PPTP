# - *- coding: utf- 8 - *-
import configparser
from tgbot.services.db import DB
import asyncio
from tgbot.data.languages import en, ru, ua

async def main_db():
    db = await DB()

    return db

loop = asyncio.get_event_loop()
task = loop.create_task(main_db())
db = loop.run_until_complete(task)
lang_ru = ru.Texts()
lang_en = en.Texts()
lang_ua = ua.Texts()

read_config = configparser.ConfigParser()
read_config.read("settings.ini")

# TELEGRAM BOT
bot_token = read_config['settings']['token'].strip().replace(" ", "")  # Токен бота
path_database = "tgbot/data/database.db"  # Путь к Базе Данных
bot_version = "2.4"  # Версия бота | НЕ МЕНЯТЬ

# CrystalPay
crystal_Cassa = read_config['settings']['Crystal_Cassa'].replace(" ", "") # имя кассы (то что в скобках)
crystal_Token = read_config['settings']['Crystal_Token'].replace(" ", "") # первый токен

# Lolzteam Market
lolz_token = read_config['settings']['lolz_token'].strip().replace(" ", "") # лолз токен
lolz_id = read_config['settings']['lolz_id'].strip().replace(" ", "") # лолз id
lolz_nick = read_config['settings']['lolz_nick'].strip().replace(" ", "") # лолз ник

# Qiwi
qiwi_login = read_config['settings']['qiwi_login'].strip().replace(" ", "") # киви номер
qiwi_nick = read_config['settings']['qiwi_nick'].strip().replace(" ", "") # киви ник
qiwi_secret = read_config['settings']['qiwi_secret'].strip().replace(" ", "") # киви секретный p2p-ключ
qiwi_token = read_config['settings']['qiwi_token'].strip().replace(" ", "") # киви токен

# ЮMoney
yoomoney_token = read_config['settings']['yoomoney_token'].strip().replace(" ", "") # юмани токен
yoomoney_number = read_config['settings']['yoomoney_number'].strip().replace(" ", "") # юмани номер

# Lava
lava_secret_key = read_config['settings']['lava_secret_key'].strip().replace(" ", "") # лава секретный ключ
lava_project_id = read_config['settings']['lava_project_id'].strip().replace(" ", "") # лава ID проекта

# Каналы
channel_id = read_config['settings']['channel_id'].strip().replace(" ", "") # айди канала для подписки
channel_url = read_config['settings']['channel_url'].strip().replace(" ", "") # ссылка на канал
logs_channel_id = read_config['settings']['logs_channel_id'].strip().replace(" ", "") # айди канала для логов

# CryptoBot
crypto_bot_token = read_config['settings']['crypto_bot_token'].strip().replace(" ", "")

# PayOK
payok_api_id = read_config['settings']['payok_api_id'].strip().replace(" ", "")
payok_api_key = read_config['settings']['payok_api_key'].strip().replace(" ", "")
payok_secret = read_config['settings']['payok_secret'].strip().replace(" ", "")
payok_shop_id = read_config['settings']['payok_shop_id'].strip().replace(" ", "")

# Aaio
aaio_api_key = read_config['settings']['aaio_api_key'].strip().replace(" ", "") # api ключ
aaio_id_shop = read_config['settings']['aaio_id_shop'].strip().replace(" ", "") # id магазина
aaio_secret_key_1 = read_config['settings']['aaio_secret_key_1'].strip().replace(" ", "") # первый секретный ключ

# Валюты

currencies = {
    "rub": {
        'txt': 'rub',
        "text": 'RUB',
        'sign': '₽'
    },
    "eur": {
        'txt': 'eur',
        "text": "EUR",
        'sign': "€"
    },
    "usd": {
        'txt': 'usd',
        'text': "USD",
        "sign": "$"
    }
}

