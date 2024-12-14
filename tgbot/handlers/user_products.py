import asyncio
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from tgbot.keyboards.inline_user import back_to_user_menu, open_products, open_positions, open_pod_cat_positions, \
    pos_buy_inl, choose_buy_items
from tgbot.data.config import db, currencies
from tgbot.data.loader import dp, bot
from tgbot.utils.utils_functions import split_messages, get_date, get_unix, send_admins, get_exchange, update_balance, \
    get_language
from contextlib import suppress
from aiogram.utils.exceptions import MessageCantBeDeleted
from tgbot.states.users import UserProducts, SearchPositions
from tgbot.data import config


@dp.callback_query_handler(text="products:open", state="*")
async def open_products_users(call: CallbackQuery, state: FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    if len(await db.get_all_categories()) < 1:
        await call.message.delete()
        if texts.products_photo:
            await call.message.answer_photo(photo=texts.products_photo, caption=texts.no_cats,
                                            reply_markup=back_to_user_menu(texts))
        else:
            await call.message.answer(texts.no_cats, reply_markup=back_to_user_menu(texts))

    else:
        await call.message.delete()
        if texts.products_photo:
            await call.message.answer_photo(photo=texts.products_photo, caption=texts.available_cats,
                                            reply_markup=await open_products(texts))
        else:
            await call.message.answer(texts.available_cats, reply_markup=await open_products(texts))


@dp.callback_query_handler(text_startswith="mail_cat_open:", state='*')
async def mail_cat_open(call: CallbackQuery, state: FSMContext):
    texts = await get_language(call.from_user.id)
    await state.finish()
    cat_id = call.data.split(":")[1]

    if len(await db.get_positions(cat_id)) < 1:
        await call.message.answer(texts.no_products, reply_markup=back_to_user_menu(texts))
    else:
        cat = await db.get_category(cat_id)
        await call.message.answer(texts.current_cat.format(name=cat['name']),
                                  reply_markup=await open_positions(texts, cat_id))


@dp.callback_query_handler(text_startswith="mail_pod_cat_open:", state='*')
async def mail_pod_cat_open(call: CallbackQuery, state: FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    pod_cat_id = call.data.split(":")[1]

    if len(await db.get_positions(pod_cat_id=pod_cat_id)) < 1:
        await call.message.answer(texts.no_products)
    else:
        pod_cat = await db.get_pod_category(pod_cat_id)
        await call.message.answer(texts.current_pod_cat.format(name=pod_cat['name']),
                                  reply_markup=await open_pod_cat_positions(texts, pod_cat_id))


@dp.callback_query_handler(text_startswith="mail_pos_open:", state="*")
async def mail_pos_open(call: CallbackQuery, state: FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    pos_id = call.data.split(":")[1]
    pos = await db.get_position(pos_id)
    cat_id = pos['category_id']
    cat = await db.get_category(cat_id)
    items = f"{len(await db.get_items(position_id=pos_id))}шт."
    if pos['infinity'] == "+":
        items = "Безлимит"
    settings = await db.get_settings()
    if settings['currency'] == 'rub':
        price = pos['price_rub']
    elif settings['currency'] == 'usd':
        price = pos['price_dollar']
    elif settings['currency'] == 'eur':
        price = pos['price_euro']
    msg = texts.open_pos_text.format(cat_name=cat['name'], pos_name=pos['name'], price=price,
                                     cur=currencies[settings['currency']]['sign'], items=items,
                                     desc=pos['description'])

    if pos['photo'] is None or pos['photo'] == "-":
        await call.message.answer(msg, reply_markup=await pos_buy_inl(texts, pos_id))
    else:
        await bot.send_photo(chat_id=call.from_user.id, photo=pos['photo'], caption=msg,
                             reply_markup=await pos_buy_inl(texts, pos_id))


@dp.callback_query_handler(text_startswith="open_category:", state="*")
async def open_cat_for_buy(call: CallbackQuery, state: FSMContext):
    await state.finish()
    cat_id = call.data.split(":")[1]
    texts = await get_language(call.from_user.id)
    if len(await db.get_positions(cat_id)) < 1:
        await call.message.delete()
        await call.message.answer(texts.no_products, reply_markup=back_to_user_menu(texts))
    else:
        await call.message.delete()
        cat = await db.get_category(cat_id)
        await call.message.answer(texts.current_cat.format(name=cat['name']),
                                  reply_markup=await open_positions(texts, cat_id))


@dp.callback_query_handler(text_startswith="open_pod_cat:", state="*")
async def open_pod_cat(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pod_cat_id = call.data.split(":")[1]
    texts = await get_language(call.from_user.id)
    if len(await db.get_positions(pod_cat_id=pod_cat_id)) < 1:
        await call.message.delete()
        await call.message.answer(texts.no_products)
    else:
        await call.message.delete()
        pod_cat = await db.get_pod_category(pod_cat_id)
        await call.message.answer(texts.current_pod_cat.format(name=pod_cat['name']),
                                  reply_markup=await open_pod_cat_positions(texts, pod_cat_id))


@dp.callback_query_handler(text_startswith="open_pos:", state="*")
async def open_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    pos_id = call.data.split(":")[1]
    pos = await db.get_position(pos_id)
    cat_id = pos['category_id']
    cat = await db.get_category(cat_id)
    items = f"{len(await db.get_items(position_id=pos_id))}шт."
    if pos['infinity'] == "+":
        items = "Безлимит"
    settings = await db.get_settings()
    if settings['currency'] == 'rub':
        price = pos['price_rub']
    elif settings['currency'] == 'usd':
        price = pos['price_dollar']
    elif settings['currency'] == 'eur':
        price = pos['price_euro']
    msg = texts.open_pos_text.format(cat_name=cat['name'], pos_name=pos['name'], price=price,
                                     cur=currencies[settings['currency']]['sign'], items=items,
                                     desc=pos['description'])

    if pos['photo'] is None or pos['photo'] == "-":
        await call.message.edit_text(msg, reply_markup=await pos_buy_inl(texts, pos_id))
    else:
        await call.message.delete()
        await bot.send_photo(chat_id=call.from_user.id, photo=pos['photo'], caption=msg,
                             reply_markup=await pos_buy_inl(texts, pos_id))


@dp.callback_query_handler(text_startswith='buy_pos:', state="*")
async def pos_buy(call: CallbackQuery, state: FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    pos_id = call.data.split(":")[1]
    pos = await db.get_position(pos_id)
    items = await db.get_items(position_id=pos_id)
    user = await db.get_user(id=call.from_user.id)
    balance, price = 0, 0
    settings = await db.get_settings()
    if settings['currency'] == 'rub':
        balance = user['balance_rub']
        price = pos['price_rub']
    elif settings['currency'] == 'usd':
        balance = user['balance_dollar']
        price = pos['price_dollar']
    elif settings['currency'] == 'eur':
        balance = user['balance_euro']
        price = pos['price_euro']
    await state.update_data(cache_pos_id_for_buy=pos_id)

    if balance < price:
        return await call.answer(texts.no_balance, True)

    if len(items) > 1:
        await call.message.delete()
        await call.message.answer(texts.here_count_products)
        await UserProducts.here_amount_to_buy.set()

    elif len(items) == 1:
        if balance >= price:
            await call.message.delete()
            await call.message.answer(texts.choose_buy_product.format(name=pos['name']),
                                      reply_markup=choose_buy_items(pos_id, 1))
        else:
            await call.answer(texts.no_balance, True)
    else:
        await call.answer(texts.no_product, True)


@dp.message_handler(state=UserProducts.here_amount_to_buy)
async def here_amount_to_buy(msg: Message, state: FSMContext):
    amount = msg.text
    user = await db.get_user(id=msg.from_user.id)
    async with state.proxy() as data:
        pos_id = data['cache_pos_id_for_buy']
    texts = await get_language(msg.from_user.id)
    pos = await db.get_position(pos_id)
    settings = await db.get_settings()
    if settings['currency'] == 'rub':
        balance = user['balance_rub']
        price = pos['price_rub']
    elif settings['currency'] == 'usd':
        balance = user['balance_dollar']
        price = pos['price_dollar']
    elif settings['currency'] == 'eur':
        balance = user['balance_euro']
        price = pos['price_euro']
    if not amount.isdigit():
        await msg.delete()
        await msg.answer(texts.no_num_count)
    else:
        if balance >= price:
            await state.finish()
            await msg.delete()
            await msg.answer(texts.choose_buy_products.format(name=pos['name'], amount=amount),
                             reply_markup=choose_buy_items(pos_id, amount))
        else:
            await msg.reply(texts.no_balance)


# Подтверждение покупки товара
@dp.callback_query_handler(text_startswith="buy_items:", state="*")
async def user_purchase_confirm(call: CallbackQuery, state: FSMContext):
    await state.finish()
    action = call.data.split(":")[1]
    pos_id = call.data.split(":")[2]
    amount = call.data.split(":")[3]
    amount = int(amount)
    texts = await get_language(call.from_user.id)
    settings = await db.get_settings()
    if action == "yes":
        await call.message.edit_text(texts.gen_products)

        pos = await db.get_position(pos_id)
        _type = pos['type']
        items = await db.get_items(position_id=pos_id)
        user = await db.get_user(id=call.from_user.id)
        amount_pay, balance, cur = 0, 0, ""
        if settings['currency'] == "rub":
            cur = "rub"
            balance = user['balance_rub']
            amount_pay = (float(pos['price_rub'] * amount))
        elif settings['currency'] == 'usd':
            cur = "dollar"
            balance = user['balance_dollar']
            amount_pay = (float(pos['price_dollar'] * amount))
        elif settings['currency'] == 'euro':
            cur = "euro"
            balance = user['balance_euro']
            amount_pay = (float(pos['price_euro'] * amount))

        if 1 <= int(amount) <= len(items):
            if balance >= amount_pay:
                if _type == "text":
                    infinity = pos['infinity']
                    save_items, send_count, split_len = await db.buy_item(items, amount, infinity)

                    if amount != send_count:
                        amount_pay = (float(pos[f'price_{cur}'] * send_count))
                        amount = send_count

                    receipt = get_unix()
                    buy_time = get_date()

                    with suppress(MessageCantBeDeleted):
                        await call.message.delete()
                    if split_len == 0:
                        await call.message.answer("\n\n".join(save_items), parse_mode="None")
                    else:
                        for item in split_messages(save_items, split_len):
                            await call.message.answer("\n\n".join(item), parse_mode="None")
                            await asyncio.sleep(0.3)
                    tovs = "\n".join(save_items)

                    amounts, amount_rub, amount_usd, amount_eur = 0, 0, 0, 0
                    if settings['currency'] == "rub":
                        amount_rub = amount_pay
                        amount_usd = await get_exchange(amount_rub, 'RUB', 'USD')
                        amount_eur = await get_exchange(amount_rub, 'RUB', 'EUR')
                        amounts = amount_rub
                    elif settings['currency'] == 'usd':
                        amount_usd = amount_pay
                        amount_rub = await get_exchange(amount_usd, 'USD', 'RUB')
                        amount_eur = await get_exchange(amount_usd, 'USD', 'EUR')
                        amounts = amount_usd
                    elif settings['currency'] == 'eur':
                        amount_eur = amount_pay
                        amount_rub = await get_exchange(amount_eur, 'EUR', 'RUB')
                        amount_usd = await get_exchange(amount_eur, 'EUR', 'USD')
                        amounts = amount_eur

                    msg = f"""
💰 Новая покупка!
👤 Пользователь: <b>@{user['user_name']}</b> | <a href='tg://user?id={user['id']}'>{user['first_name']}</a> | <code>{user['id']}</code>
💵 Сумма: <code>{amounts}{currencies[settings['currency']]['sign']}</code>
🧾 Чек: <code>{receipt}</code>
⚙️ Товар: <code>{pos['name']}</code>
🎲 Содержимое товара:
{tovs}"""

                    await send_admins(msg, True)
                    await db.update_user(user['id'], balance_rub=float(user['balance_rub']-amount_rub),
                                         balance_dollar=float(user['balance_dollar']-amount_usd),
                                         balance_euro=float(user['balance_euro']-amount_eur))
                    await db.add_purchase(user['id'], user['first_name'], user['user_name'], receipt, amount,
                                          amount_rub, amount_usd, amount_eur, pos['id'], pos['name'],
                                          "\n".join(save_items), buy_time, receipt)
                else:
                    infinity = pos['infinity']
                    save_items, send_count = await db.buy_item_file(items, amount, infinity)

                    if amount != send_count:
                        amount_pay = (float(pos[f'price_{cur}'] * send_count))
                        amount = send_count

                    receipt = get_unix()
                    buy_time = get_date()

                    with suppress(MessageCantBeDeleted):
                        await call.message.delete()

                    for item in save_items:
                        __type = item.split(":")[0]

                        if __type == "photo":
                            await call.message.answer_photo(photo=item.split(":")[1])
                        elif __type == "file":
                            await call.message.answer_document(document=item.split(":")[1])
                        await asyncio.sleep(0.3)

                    amounts, amount_rub, amount_usd, amount_eur = 0, 0, 0, 0
                    if settings['currency'] == "rub":
                        amount_rub = amount_pay
                        amount_usd = await get_exchange(amount_rub, 'RUB', 'USD')
                        amount_eur = await get_exchange(amount_rub, 'RUB', 'EUR')
                        amounts = amount_rub
                    elif settings['currency'] == 'usd':
                        amount_usd = amount_pay
                        amount_rub = await get_exchange(amount_usd, 'USD', 'RUB')
                        amount_eur = await get_exchange(amount_usd, 'USD', 'EUR')
                        amounts = amount_usd
                    elif settings['currency'] == 'eur':
                        amount_eur = amount_pay
                        amount_rub = await get_exchange(amount_eur, 'EUR', 'RUB')
                        amount_usd = await get_exchange(amount_eur, 'EUR', 'USD')
                        amounts = amount_eur

                    msg = f"""
💰 Новая покупка!
👤 Пользователь: <b>@{user['user_name']}</b> | <a href='tg://user?id={user['id']}'>{user['first_name']}</a> | <code>{user['id']}</code>
💵 Сумма: <code>{amounts}{currencies[settings['currency']]['sign']}</code>
🧾 Чек: <code>{receipt}</code>
⚙️ Товар: <code>{pos['name']}</code>
🎲 Содержимое товара:"""

                    await send_admins(msg, True)
                    for item in save_items:
                        __type = item.split(":")[0]
                        if __type == "photo":
                            await send_admins(None, True, photo=item.split(":")[1])
                        elif __type == "file":
                            await send_admins(None, True, file=item.split(":")[1])
                        await asyncio.sleep(0.3)

                    await db.update_user(user['id'], balance_rub=float(user['balance_rub'] - amount_rub),
                                         balance_dollar=float(user['balance_dollar'] - amount_usd),
                                         balance_euro=float(user['balance_euro'] - amount_eur))
                    await db.add_purchase(user['id'], user['first_name'], user['user_name'], receipt, amount,
                                          amount_rub, amount_usd, amount_eur, pos['id'], pos['name'],
                                          ",\n".join(save_items), buy_time, receipt)

                msg = texts.yes_buy_items.format(receipt=receipt, name=pos['name'], amount=amount,
                                                 amount_pay=amounts, cur=currencies[settings['currency']]['sign'],
                                                 buy_time=buy_time)
                await call.message.answer(msg)
            else:
                await call.answer(texts.no_balance, True)
        else:
            await call.message.answer(texts.edit_prod)
    else:
        await call.message.edit_text(texts.otmena_buy)


@dp.callback_query_handler(text="search_pos", state="*")
async def search_pos(call : CallbackQuery, state : FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    await call.message.delete()
    search_message = await call.message.answer(texts.search_request_text)
    await state.update_data(search_message_id=search_message.message_id)
    await state.set_state(SearchPositions.query)
    


@dp.message_handler(state=SearchPositions.query)
async def postsearch_pos(message: Message, state : FSMContext):
    await state.update_data({"query":message.text})
    await message.delete()
    texts = await get_language(message.from_user.id)
    async with state.proxy() as data:
        query = data['query']
        id = data['search_message_id']
        await message.bot.delete_message(chat_id=message.chat.id, message_id=id)
    result = await db.search_positions(query)
    if len(result) == 0:
        text = texts.nothing_search
    else:
        text = texts.result_search
    keyboard = InlineKeyboardMarkup()
    for pos in result:
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
        
    keyboard.add(
        InlineKeyboardButton(texts.back, callback_data="products:open")
    )
    await message.answer(text, reply_markup=keyboard)
    await state.finish()