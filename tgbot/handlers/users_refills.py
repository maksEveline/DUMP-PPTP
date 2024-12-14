# - *- coding: utf- 8 - *-
import random
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from tgbot.services.crystal import CrystalPay
from tgbot.services.lolz import Lolz
from tgbot.services.lava import Lava
from tgbot.services.yoomoney_api import YooMoney
from tgbot.services.qiwi import Qiwi
from tgbot.services.crypto_bot import CryptoBot
from tgbot.services.payok import PayOk
from tgbot.services.aaio import Aaio
from tgbot.utils.utils_functions import send_admins, get_unix
from tgbot.data.config import db
from tgbot.keyboards.inline_user import refill_inl, refill_open_inl, choose_asset_crypto
from tgbot.data.loader import dp, bot
from tgbot.data import config
from tgbot.utils.utils_functions import update_balance, get_exchange, get_language
from tgbot.states.users import UserRefills
import math
from traceback import print_exc

try:
    payok = PayOk(
        api_id=config.payok_api_id,
        api_key=config.payok_api_key,
        secret=config.payok_secret,
        shop_id=config.payok_shop_id,
    )
    aaio = Aaio(
        aaio_api_key=config.aaio_api_key,
        aaio_id_shop=config.aaio_id_shop,
        aaio_secret_key=config.aaio_secret_key_1
    )
    crystal = CrystalPay(config.crystal_Cassa, config.crystal_Token)
    lzt = Lolz(access_token=config.lolz_token)
    qiwi = Qiwi(config.qiwi_token, config.qiwi_login, config.qiwi_secret)
    lava = Lava(shop_id=config.lava_project_id, secret_token=config.lava_secret_key)
    yoo = YooMoney(token=config.yoomoney_token, number=config.yoomoney_number)
    crypto = CryptoBot(api_token=config.crypto_bot_token)
except:
    pass


@dp.callback_query_handler(text="crypto_bot", state="*")
async def cryt(call: CallbackQuery, state: FSMContext):
    texts  = await get_language(call.message.chat.id)
    await state.finish()
    await call.message.delete()
    texts = await get_language(call.from_user.id)
    await call.message.answer(texts.choose_crypto, reply_markup=choose_asset_crypto(texts))


async def success_refill(call: CallbackQuery, way, amount, id, user_id, pay_amount):
    try:
        texts = await get_language(user_id)
        if await db.get_refill(id) is not None:
            return await call.answer(texts.error_refill)

        user = await db.get_user(id=user_id)
        curr = (await db.get_settings())['currency']
        amount_rub, amount_euro, amount_dollar, ref_percent, ref_amount, main_amount = 0, 0, 0, 0, 0, 0

        pay_amount = float(pay_amount)

        await db.add_refill(amount, way, user_id, user['user_name'], user['first_name'], comment=id)

        amount_rub = float(amount)
        amount_euro = await get_exchange(amount_rub, 'RUB', 'EUR')
        amount_dollar = float(amount)

        if curr == "rub":
            pay_rub = user['balance_rub'] + pay_amount
            pay_dollar = user['balance_dollar'] + await get_exchange(pay_amount, 'RUB', 'USD')
            pay_euro = user['balance_euro'] + await get_exchange(pay_amount, 'RUB', 'EUR')
        elif curr == "usd":
            pay_dollar = user['balance_dollar'] + pay_amount
            pay_rub = user['balance_rub'] + await get_exchange(pay_amount, 'USD', 'RUB')
            pay_euro = user['balance_euro'] + await get_exchange(pay_amount, 'USD', 'EUR')
        elif curr == "euro":
            pay_euro = user['balance_euro'] + pay_amount
            pay_rub = user['balance_rub'] + await get_exchange(pay_amount, 'EUR', 'RUB')
            pay_dollar = user['balance_dollar'] + await get_exchange(pay_amount, 'EUR', 'USD')

        msg = f"💰 Произошло пополнение баланса! \n" \
              f"👤 Пользователь: <b>@{user['user_name']}</b> | <a href='tg://user?id={user['id']}'>{user['first_name']}</a> | <code>{user['id']}</code>\n" \
              f"💵 Сумма пополнения: <code>{pay_amount}{config.currencies[curr]['sign']}</code>\n" \
              f"🧾 Чек: <code>{id}</code> \n" \
              f"⚙️ Способ: <code>{way}</code>"

        await send_admins(msg, True)
        await db.update_user(id=user_id, total_refill=int(user['total_refill']) + float(amount_rub),
                             count_refills=int(user['count_refills']) + 1)

        await db.update_user(user_id, balance_rub=pay_rub, balance_dollar=pay_dollar, balance_euro=pay_euro)
        await call.message.delete()
        await call.message.answer(texts.refill_success_text(way, pay_amount, id, config.currencies[curr]['sign']))

        s = await db.get_settings()
        if s['is_ref'] == "False":
            pass
        elif s['is_ref'] == "True":
            if user['ref_id'] is None:
                pass
            else:
                reffer = await db.get_user(id=user['ref_id'])

                if reffer['ref_lvl'] == 1:
                    ref_percent = s['ref_percent_1']
                elif reffer['ref_lvl'] == 2:
                    ref_percent = s['ref_percent_2']
                elif reffer['ref_lvl'] == 3:
                    ref_percent = s['ref_percent_3']

                ref_amount_rub = int(amount_rub) / 100 * int(ref_percent)
                ref_amount_euro = int(amount_euro) / 100 * int(ref_percent)
                ref_amount_dollar = int(amount_dollar) / 100 * int(ref_percent)

                if curr == 'rub':
                    ref_amount = ref_amount_rub
                elif curr == 'eur':
                    ref_amount = ref_amount_euro
                elif curr == 'usd':
                    ref_amount = ref_amount_dollar

                reffer_id = user['ref_id']
                reffer = await db.get_user(id=reffer_id)

                ref_earn_rub = reffer['ref_earn_rub']
                ref_earn_euro = reffer['ref_earn_euro']
                ref_earn_dollar = reffer['ref_earn_dollar']

                add_balance_rub = round(reffer['balance_rub'] + round(ref_amount_rub, 1), 2)
                add_balance_euro = round(reffer['balance_euro'] + round(ref_amount_euro, 1), 2)
                add_balance_dollar = round(reffer['balance_dollar'] + round(ref_amount_dollar, 1), 2)

                name = f"<a href='tg://user?id={user['id']}'>{user['user_name']}</a>"

                await db.update_user(reffer_id, balance_rub=add_balance_rub, balance_euro=add_balance_euro,
                                     balance_dollar=add_balance_dollar,
                                     ref_earn_rub=ref_earn_rub + round(ref_amount_rub, 1),
                                     ref_earn_dollar=ref_earn_dollar + round(ref_amount_dollar, 1),
                                     ref_earn_euro=ref_earn_euro + round(ref_amount_euro, 1),)

                await bot.send_message(reffer_id,
                                       texts.yes_refill_ref.format(name=name, amount=amount,
                                                                   ref_amount=round(ref_amount, 1),
                                                                   cur=config.currencies[curr]['sign']))
    except:
        print_exc()


@dp.callback_query_handler(text="refill", state="*")
async def refill_open(call: CallbackQuery, state: FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    await call.message.delete()

    if texts.refill_photo:
        await call.message.answer_photo(photo=texts.refill_photo, caption=texts.refill_text,
                                        reply_markup=await refill_inl(texts))
    else:
        await call.message.answer(texts.refill_text, reply_markup=await refill_inl(texts))


@dp.callback_query_handler(text_startswith="refill:", state="*")
async def refill_(call: CallbackQuery, state: FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    way = call.data.split(":")[1]

    try:
        asset = call.data.split(":")[2]
        await state.update_data(cache_asset=asset)
    except:
        pass

    await state.update_data(here_way=way)
    await UserRefills.here_amount.set()
    curr = (await db.get_settings())['currency']
    if curr == 'rub':
        min_amount = texts.min_amount
        max_amount = texts.max_amount
    elif curr == 'usd':
        min_amount = texts.min_amount
        max_amount = texts.max_amount
    elif curr == 'eur':
        min_amount = await get_exchange(texts.min_amount, 'RUB', 'EUR')
        max_amount = await get_exchange(texts.max_amount, 'RUB', 'EUR')
    await call.message.answer(texts.refill_amount_text.format(min_amount=min_amount,
                                                              curr=config.currencies[curr]['sign'],
                                                              max_amount=max_amount))


@dp.message_handler(state=UserRefills.here_amount)
async def refill_pay(message: Message, state: FSMContext):
    texts = await get_language(message.from_user.id)
    amount = message.text
    async with state.proxy() as data:
        way = data['here_way']
        try:
            asset = data['cache_asset']
        except:
            pass
    await state.finish()
    bota = await bot.get_me()
    bot_name = bota.username
    us = await db.get_user(id=message.from_user.id)
    user_name = us['user_name']
    pay_amount = float(amount)
    curr = (await db.get_settings())['currency']
    if curr == 'usd':
        pay_amount = amount
    elif curr == 'eur':
        pay_amount = await get_exchange(float(amount), 'EUR', 'RUB')
    if amount.isdigit() or amount.replace(".", "").isdigit():
        if texts.min_amount <= float(pay_amount) <= texts.max_amount:
            if way == "crystal":
                way = "CrystalPay"
                crys = await crystal.generate_pay_link(amount=pay_amount)
                link = crys['url']
                id = crys['id']
            elif way == "qiwi":
                way = "Qiwi"
                bill_id = get_unix(True)
                bill = await qiwi.create_bill(amount=pay_amount, comment=bill_id)
                id = bill['billId']
                link = bill['payUrl']
            elif way == "lolz":
                way = "Lolz"
                comment = lzt.get_random_string()
                pay_amount = math.ceil(float(pay_amount))
                link = lzt.get_link(amount=float(pay_amount), comment=comment)
                id = comment
            elif way == "lava":
                way = "Lava"
                invoice = await lava.create_invoice(amount=float(pay_amount),
                                                    comment=f"Пополнение аккаунта {user_name} на сумму {pay_amount}{config.currencies[curr]['sign']} в боте {bot_name}",
                                                    success_url=f"https://t.me/{bot_name}")
                link = invoice['data']['url']
                id = invoice['data']['id']
            elif way == "yoomoney":
                way = "ЮMoney"
                order = random.randint(1111111, 9999999)
                form = yoo.create_yoomoney_link(amount=pay_amount, comment=order)
                link = form['link']
                id = form['comment']
            elif way == "crypto_bot":
                way = "CryptoBot"
                user = await db.get_user(id=message.chat.id)
                curr = (await db.get_settings())['currency']

                bill = await crypto.create_bill(amount=pay_amount, asset=asset)
                id = bill['result']['invoice_id']
                link = bill['result']['pay_url']
            elif way == "payok":
                way = "PayOK"
                cur = await db.get_settings()
                pay_amount = int(amount)
                id = get_unix(True)
                link = await payok.get_link(payment_id=id, summ=pay_amount, currency=cur['currency'].upper())
            elif way == "aaio":
                cur = await db.get_settings()
                way = texts.aaio_short_text
                id = get_unix(True)
                pay_amount = int(amount)
                link = str(await aaio.create_payment(pay_amount, id, cur['currency'].upper()))

            await message.answer(texts.refill_gen_text(way=way, amount=message.text, id=id,
                                                       curr=config.currencies[curr]['sign']),
                                 reply_markup=refill_open_inl(texts=texts,
                                                              way=way,
                                                              amount=pay_amount,
                                                              link=link, id=id, second_amount=message.text))
            await state.finish()
        else:
            if curr == 'rub':
                min_amount = texts.min_amount
                max_amount = texts.max_amount
            elif curr == 'usd':
                min_amount = texts.min_amount
                max_amount = texts.max_amount
            elif curr == 'eur':
                min_amount = await get_exchange(texts.min_amount, 'RUB', 'EUR')
                max_amount = await get_exchange(texts.max_amount, 'RUB', 'EUR')
            await message.answer(texts.min_max_amount.format(min_amount=min_amount,
                                                             curr=config.currencies[curr]['sign'],
                                                             max_amount=max_amount))
    else:
        await message.answer(texts.no_int_amount)


@dp.callback_query_handler(text_startswith="check_opl:", state='*')
async def check_refill(call: CallbackQuery, state: FSMContext):
    await state.finish()
    data = call.data.split(':')
    amount = data[2]
    way = data[1]
    id = data[3]
    pay_amount1 = data[4]
    texts = await get_language(call.from_user.id)
    if way == "CrystalPay":
        status = await crystal.get_pay_status(invoice_id=id)
        refill = await db.get_refill(receipt=id)
        if status and not refill:
            await success_refill(call, way, amount, id, call.from_user.id, pay_amount1)
        else:
            await call.answer(texts.refill_check_no, True)
    elif way == "Qiwi":
        status = await qiwi.check_bill(bill_id=id)
        refill = await db.get_refill(receipt=id)
        if status and not refill:
            await success_refill(call, way, amount, id, call.from_user.id, pay_amount1)
        else:
            await call.answer(texts.refill_check_no, True)
    elif way == "Lava":
        status = await lava.status_invoice(invoice_id=id)
        refill = await db.get_refill(receipt=id)
        if status and not refill:
            await success_refill(call, way, amount, id, call.from_user.id, pay_amount1)
        else:
            await call.answer(texts.refill_check_no, True)
    elif way == "Lolz":
        status = await lzt.check_payment(amount=float(amount), comment=id)
        refill = await db.get_refill(receipt=id)
        if status is True and not refill:
            await success_refill(call, way, amount, id, call.from_user.id, pay_amount1)
        else:
            if status is False:
                await call.answer(texts.refill_check_no, True)
            else:
                await call.answer(status, True)
    elif way == "ЮMoney":
        status = yoo.check_yoomoney_payment(comment=id)
        refill = await db.get_refill(receipt=id)
        if status and not refill:
            await success_refill(call, way, amount, id, call.from_user.id, pay_amount1)
        else:
            await call.answer(texts.refill_check_no, True)
    elif way == "CryptoBot":
        status = await crypto.check_bill(bill_id=id)
        refill = await db.get_refill(receipt=id)
        if status and not refill:
            await success_refill(call, way, amount, id, call.from_user.id, pay_amount1)
        else:
            await call.answer(texts.refill_check_no, True)
    elif way == 'PayOK':
        status = await payok.get_pay(order_id=id)
        refill = await db.get_refill(receipt=id)
        if status and not refill:
            await success_refill(call, way, amount, id, call.from_user.id, pay_amount1)
        else:
            await call.answer(texts.refill_check_no, True)
    elif way == texts.aaio_short_text:
        status = await aaio.check_payment(order_id=id)
        refill = await db.get_refill(receipt=id)
        if status and not refill:
            await success_refill(call, way, amount, id, call.from_user.id, pay_amount1)
        else:
            await call.answer(texts.refill_check_no, True)
