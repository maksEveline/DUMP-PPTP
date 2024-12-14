# - *- coding: utf- 8 - *-
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from tgbot.data.loader import dp, bot
from tgbot.filters.filters import IsAdmin
from tgbot.keyboards.inline_admin import (products_edits, back_pr_edits, open_cats_for_add_items,
                                          open_cats_for_add_pod_cat, open_cats_for_add_pos,
                                          open_cats_for_edit, open_cats_for_edit_pod_cat, open_cats_for_edit_pos,
                                          open_pod_cats_for_add_items, open_pod_cats_for_add_pos, edit_cat_inl,
                                          choose_clear_items_pos, choose_del_all_cats, choose_del_all_items,
                                          choose_del_all_pod_cats, choose_del_all_pos, choose_del_cat,
                                          choose_del_pod_cat, choose_del_pos, open_pod_cats_for_edit,
                                          open_pod_cats_for_edit_pos, open_positions_for_add_items,
                                          open_positions_for_edit, update_pod_cat_inl, edit_pos_inl, stop_add_items,
                                          choose_type_position)
from tgbot.data.config import db, currencies
from tgbot.utils.utils_functions import send_admins, get_unix, get_exchange
from tgbot.states.admin import AdminCatsEdit, AdminPodCatsEdit, AdminPosEdit, AdminItemsEdit


@dp.callback_query_handler(IsAdmin(), text="pr_edit", state="*")
async def edits_prods(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(f"<b>⚙️ Выберите что хотите сделать \n➕ - Добавить/Создать \n⚙️ - Редактировать \n🗑️ - Удалить</b>", reply_markup=products_edits())


@dp.callback_query_handler(text="add_cat", state="*")
async def add_cat_op(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer(f"<b>❗ Введите название категории</b>", reply_markup=back_pr_edits())
    await AdminCatsEdit.here_name_cat.set()


@dp.message_handler(state=AdminCatsEdit.here_name_cat)
async def here_name_add_cat(msg: Message, state: FSMContext):
    await state.finish()

    name = msg.text
    await db.add_category(name)

    await msg.answer(f"<b>✅ Категория <code>{name}</code> Была создана!</b>")
    await send_admins(f"<b>❗ Администратор @{msg.from_user.username} создал категорию <code>{name}</code>!</b>", True)


@dp.callback_query_handler(text="edit_cat", state="*")
async def edit_cat_op(call: CallbackQuery, state: FSMContext):
    await state.finish()
    if len(await db.get_all_categories()) < 1:
        await call.answer(f"❗ Нет категорий для изменения")
    else:
        await call.message.answer(f"<b>❗ Выберите категорию для изменения:</b>", reply_markup=await open_cats_for_edit())


@dp.callback_query_handler(text_startswith="cat_edit:", state="*")
async def edit_cat_ope(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cat_id = call.data.split(":")[1]
    category = await db.get_category(cat_id)

    await call.message.answer(f"<b>Категория: {category['name']}</b>", reply_markup=edit_cat_inl(cat_id))


@dp.callback_query_handler(text_startswith="edit_cat_name:", state="*")
async def edit_cat_name(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cat_id = call.data.split(":")[1]

    await call.message.answer(f"<b>❗ Введите новое название для категории</b>")

    await AdminCatsEdit.here_new_cat_name.set()
    await state.update_data(cache_edit_cat_id=cat_id)


@dp.message_handler(state=AdminCatsEdit.here_new_cat_name)
async def here_edit_name_cat(msg: Message, state: FSMContext):

    async with state.proxy() as data:
        cat_id = data['cache_edit_cat_id']

    await state.finish()
    cat = await db.get_category(cat_id)
    await db.update_category(cat_id=cat_id, name=msg.text)

    await msg.answer(f"<b>✅ Название для категории изменено на <code>{msg.text}</code></b>")
    await send_admins(f"<b>❗ Администратор @{msg.from_user.username} изменил имя категории с <code>{cat['name']}</code> на <code>{msg.text}</code>!</b>", True)


@dp.callback_query_handler(text_startswith="del_cat:", state="*")
async def del_cat_op(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cat_id = call.data.split(":")[1]

    await call.message.answer(f"<b>❓ Вы точно хотите удалить эту категорию?</b>", reply_markup=choose_del_cat(cat_id))


@dp.callback_query_handler(text_startswith="dels_cat:", state="*")
async def del_cat_ope(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]
    cat_id = call.data.split(":")[2]

    if action == "yes":
        cat = await db.get_category(cat_id=cat_id)
        name = cat['name']
        await db.del_category(cat_id=cat_id)
        await call.message.answer(f"<b>✅ Вы успешно удалили категорию <code>{name}</code></b>")
        await send_admins(
            f"<b>❗ Администратор @{call.from_user.username} удалил категорию <code>{name}</code>!</b>", True)
    else:
        await call.message.answer(f"<b>❌ Вы отменили удаление категории</b>")


@dp.callback_query_handler(text="del_all_cats", state="*")
async def del_all_cats_op(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer(f"<b>❓ Вы точно хотите удалить <u>ВСЕ</u> категории?</b>", reply_markup=choose_del_all_cats())


@dp.callback_query_handler(text_startswith="dels_all_cat:", state="*")
async def dels_all_cats_choose(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]
    if action == "yes":
        await db.del_all_cats()
        await call.message.answer(f"<b>✅ Вы успешно удалили все категории</b>")
        await send_admins(
            f"<b>❗ Администратор @{call.from_user.username} удалил ВСЕ категории!</b>", True)
    else:
        await call.message.answer(f"<b>❌ Вы отменили удаление всех категорий</b>")


#############################################################################
########################        Под-категории        ########################
#############################################################################

@dp.callback_query_handler(text="add_pod_cat", state="*")
async def add_cat_opee(call: CallbackQuery, state: FSMContext):
    await state.finish()

    if len(await db.get_all_categories()) < 1:
        await call.answer(f"❗ Нет категорий для создания под-категории")
    else:
        await call.message.answer(f"<b>❗ Выберите категорию для создания под-категории</b>", reply_markup=await open_cats_for_add_pod_cat())


@dp.callback_query_handler(text_startswith="add_pod_cat_cat:", state="*")
async def add_cat_openn(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cat_id = call.data.split(":")[1]
    await state.update_data(cache_cat_id_for_pod_cat=cat_id)

    await call.message.answer(f"<b>❗ Введите название под-категории</b>", reply_markup=back_pr_edits())
    await AdminPodCatsEdit.here_name_pod_cat.set()


@dp.message_handler(state=AdminPodCatsEdit.here_name_pod_cat)
async def here_name_add_cat(msg: Message, state: FSMContext):

    async with state.proxy() as data:
        cat_id = data['cache_cat_id_for_pod_cat']

    await state.finish()

    name = msg.text
    await db.add_pod_category(name, cat_id)

    await msg.answer(f"<b>✅ Под-Категория <code>{name}</code> Была создана!</b>")
    await send_admins(
        f"<b>❗ Администратор @{msg.from_user.username} создал под-категорию <code>{msg.text}</code>!</b>", True)


@dp.callback_query_handler(text="edit_pod_cat", state="*")
async def edit_cat_op(call: CallbackQuery, state: FSMContext):
    await state.finish()

    if len(await db.get_all_pod_categories()) < 1:
        await call.answer(f"❗ Нет под-категорий для изменения")
    else:
        if len(await db.get_all_categories()) < 1:
            await call.answer(f"❗ Нет категорий для изменения под-категории")
        else:
            await call.message.answer(f"<b>❗ Выберите категорию для изменения под-категории:</b>", reply_markup=await open_cats_for_edit_pod_cat())


@dp.callback_query_handler(text_startswith="pods_cat_edit:", state="*")
async def pods_cat_edittt(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cat_id = call.data.split(":")[1]
    await state.update_data(cache_cat_id_for_edit_pod_cat=cat_id)

    if len(await db.get_pod_categories(cat_id)) < 1:
        await call.answer(f"❗ В этой категории нет под-категорий!")
    else:
        await call.message.answer(f"<b>❗ Выберите под-категорию для изменения:</b>", reply_markup=await open_pod_cats_for_edit(cat_id))


@dp.callback_query_handler(text_startswith="podss_cat_edit:", state="*")
async def podss_cat_editt(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pod_cat_id = call.data.split(":")[1]

    pod_cat = await db.get_pod_category(pod_cat_id)
    cat = await db.get_category(pod_cat['cat_id'])

    await call.message.answer(f"<b>💎 Под-категория: <code>{pod_cat['name']}</code> \n⚙️ Категория: <code>{cat['name']}</code></b>", reply_markup=update_pod_cat_inl(pod_cat_id))


@dp.callback_query_handler(text_startswith="edit_pod_cat_name:", state="*")
async def edit_pod_cat_name(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pod_cat_id = call.data.split(":")[1]
    await state.update_data(cache_pod_cat_id_for_edit_name=pod_cat_id)

    await call.message.answer(f"<b>❗ Введите новое название для под-категории</b>")
    await AdminPodCatsEdit.here_new_name_for_pod_cat.set()


@dp.message_handler(state=AdminPodCatsEdit.here_new_name_for_pod_cat)
async def here_new_name_pod_cat(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        pod_cat_id = data['cache_pod_cat_id_for_edit_name']

    await state.finish()
    cat = await db.get_pod_category(pod_cat_id)
    await db.update_pod_category(pod_cat_id=pod_cat_id, name=msg.text)

    await msg.answer(f"<b>✅ Вы успешно изменили название под-категории на <code>{msg.text}</code></b>")
    await send_admins(
        f"<b>❗ Администратор @{msg.from_user.username} изменил имя под-категории с <code>{cat['name']}</code> на <code>{msg.text}</code>!</b>", True)


@dp.callback_query_handler(text_startswith="del_pod_cat:", state="*")
async def del_pod_cat(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pod_cat_id = call.data.split(":")[1]

    await call.message.answer(f"<b>❓ Вы точно хотите удалить под категорию?</b>", reply_markup=choose_del_pod_cat(pod_cat_id))


@dp.callback_query_handler(text_startswith="dels_pod_cat:", state='*')
async def del_pod_cat_yes_no(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]
    pod_cat_id = call.data.split(":")[2]

    if action == "yes":
        pod_cat = await db.get_pod_category(pod_cat_id)
        await db.del_pod_category(pod_cat_id)
        await call.message.answer(f"<b>✅ Вы удалили под-категорию <code>{pod_cat['name']}</code></b>")
        await send_admins(
            f"<b>❗ Администратор @{call.from_user.username} удалил под-категорию <code>{pod_cat['name']}</code>!</b>", True)
    else:
        await call.message.answer(f"<b>❌ Вы отменили удаление под-категории</b>")


@dp.callback_query_handler(text="del_all_pod_cats", state="*")
async def del_all_pods_cats(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.answer(f"<b>❓ Вы точно хотите удалить <u>ВСЕ</u> под-категории?</b>",
                            reply_markup=choose_del_all_pod_cats())


@dp.callback_query_handler(text_startswith="dels_all_pod_cats:", state="*")
async def dels_all_cats_choose(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]
    if action == "yes":
        await db.del_all_pod_cats()
        await call.message.answer(f"<b>✅ Вы успешно удалили все под-категории</b>")
        await send_admins(
            f"<b>❗ Администратор @{call.from_user.username} удалил ВСЕ под-категории!</b>", True)
    else:
        await call.message.answer(f"<b>❌ Вы отменили удаление всех под-категорий</b>")


########################################################################################
############################         Позиции         ###################################
########################################################################################
@dp.callback_query_handler(text="add_pos", state="*")
async def add_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.answer(f"<b>❗ Выберите категорию для создания позиции</b>", reply_markup=await open_cats_for_add_pos())


@dp.callback_query_handler(text_startswith="add_pos_cat:", state="*")
async def add_posss(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cat_id = call.data.split(":")[1]

    if len(await db.get_pod_categories(cat_id)) != 0:
        await call.message.answer(f"<b>❗ Выберите под-категорию (Или категорию) для создания позиции</b>",
                                reply_markup=await open_pod_cats_for_add_pos(cat_id))
    else:
        await call.message.answer(f"<b>❗ Введите название для позиции</b>")
        await AdminPosEdit.here_name_add_pos.set()
        await state.update_data(cache_cat_id_for_add_pos=cat_id)
        await state.update_data(cache_pod_cat_id_for_add_pos=None)


@dp.callback_query_handler(text_startswith="add_poss_cat:", state="*")
async def add_possss(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cat_id = call.data.split(":")[1]

    await call.message.answer(f"<b>❗ Введите название для позиции</b>")
    await AdminPosEdit.here_name_add_pos.set()
    await state.update_data(cache_cat_id_for_add_pos=cat_id)
    await state.update_data(cache_pod_cat_id_for_add_pos=None)


@dp.callback_query_handler(text_startswith="pod_cat_add_pos:", state="*")
async def add_poss(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pod_cat_id = call.data.split(":")[1]
    cat_id = call.data.split(":")[2]

    await call.message.answer(f"<b>❗ Введите название для позиции</b>")
    await AdminPosEdit.here_name_add_pos.set()
    await state.update_data(cache_pod_cat_id_for_add_pos=pod_cat_id)
    await state.update_data(cache_cat_id_for_add_pos=cat_id)


@dp.message_handler(state=AdminPosEdit.here_name_add_pos)
async def here_name_addd_pos(msg: Message, state: FSMContext):
    name = msg.text

    await msg.answer(f"<b>❗ Введите цену для позиции</b>")
    await AdminPosEdit.here_price_add_pos.set()
    await state.update_data(cache_name_add_pos=name)


@dp.message_handler(state=AdminPosEdit.here_price_add_pos)
async def here_name_addd_pos(msg: Message, state: FSMContext):
    if msg.text.isdigit() or msg.text.replace(".", "").isdigit():
        price = float(msg.text)
        await msg.answer(f"<b>❗ Введите тип позиции \n\n<u>‼ Примечание:</u> После этого шага изменить тип позиции невозможно!!!</b>",
                         reply_markup=choose_type_position())
        await AdminPosEdit.here_type_add_pos.set()
        await state.update_data(cache_price_add_pos=price)
    else:
        await msg.answer(f"<b>❗ Цена должна быть числом!</b>")


@dp.callback_query_handler(text_startswith="position_type:", state=AdminPosEdit.here_type_add_pos)
async def position_type_add_pos(call: CallbackQuery, state: FSMContext):
    _type = call.data.split(":")[1]
    await AdminPosEdit.here_desc_add_pos.set()
    await state.update_data(cache_type_add_pos=_type)
    await call.message.edit_text(f"<b>❗ Введите описание для позиции \nЧтобы не ставить, отправьте <code>-</code></b>")


@dp.message_handler(state=AdminPosEdit.here_desc_add_pos)
async def here_name_addd_pos(msg: Message, state: FSMContext):
    desc = msg.parse_entities(as_html=True)

    if desc == "-":
        desc = "<code>❗ Не поставлено</code>"

    await msg.answer(f"<b>❗ Отправьте фото для позиции \nЧтобы не ставить, отправьте <code>-</code></b>")
    await AdminPosEdit.here_photo_add_pos.set()
    await state.update_data(cache_desc_add_pos=desc)


@dp.message_handler(state=AdminPosEdit.here_photo_add_pos, content_types=['photo'])
@dp.message_handler(state=AdminPosEdit.here_photo_add_pos, text='-')
async def here_name_addd_pos(msg: Message, state: FSMContext):

    if msg.text == "-":
        photo = "-"
    else:
        photo = msg.photo[-1].file_id

    await msg.answer(f"<b>❗ Отправьте <code>+</code> если хотите чтоб товар был бесконечным \nЕсли не хотите введите <code>-</code></b>")
    await AdminPosEdit.here_infinity_add_pos.set()
    await state.update_data(cache_photo_add_pos=photo)


@dp.message_handler(state=AdminPosEdit.here_infinity_add_pos, text=['+', '-'])
async def here_name_addd_pos(msg: Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            cat_id = data['cache_cat_id_for_add_pos']
            pod_cat_id = data['cache_pod_cat_id_for_add_pos']
            name = data['cache_name_add_pos']
            price = data['cache_price_add_pos']
            desc = data['cache_desc_add_pos']
            photo = data['cache_photo_add_pos']
            _type = data['cache_type_add_pos']

        infinity = msg.text

        settings = await db.get_settings()
        price_rub, price_dollar, price_euro = 0, 0, 0
        if settings['currency'] == 'rub':
            price_rub = price
            price_euro = await get_exchange(price_rub, 'RUB', 'EUR')
            price_dollar = await get_exchange(price_rub, 'RUB', 'USD')
        elif settings['currency'] == 'usd':
            price_dollar = price
            price_euro = await get_exchange(price_dollar, 'USD', 'EUR')
            price_rub = await get_exchange(price_dollar, 'USD', 'RUB')
        elif settings['currency'] == 'eur':
            price_euro = price
            price_dollar = await get_exchange(price_euro, 'EUR', 'USD')
            price_rub = await get_exchange(price_euro, 'EUR', 'RUB')

        cat = await db.get_category(cat_id)
        pos_id = get_unix(True)
        curr = currencies[settings['currency']]['sign']
        if pod_cat_id is not None:
            await db.add_position(_type, name, price_rub, price_dollar, price_euro, desc, photo, cat_id, infinity, pos_id, pod_cat_id)
            pod_cat = await db.get_pod_category(pod_cat_id)
            msgg = f"""
<b>💎 Категория: <code>{cat['name']}</code>
🎲 Под-категория: <code>{pod_cat['name']}</code>
⚙️ Позиция: <code>{name}</code>
💰 Цена: <code>{price}{curr}</code>
⭐ Бесконечный товар: <code>{infinity}</code>
🛒 Тип: <code>{_type}</code>
💚 Описание: <code>{desc}</code></b>
                    """
            await send_admins(
                f"<b>❗ Администратор @{msg.from_user.username} создал позицию: \n{msgg}</b>", True
            )
        else:
            await db.add_position(_type, name, price_rub, price_dollar, price_euro, desc, photo, cat_id, infinity, pos_id)
            msgg = f"""
<b>💎 Категория: <code>{cat['name']}</code>
⚙️ Позиция: <code>{name}</code>
💰 Цена: <code>{price}{curr}</code>
⭐ Бесконечный товар: <code>{infinity}</code>
🛒 Тип: <code>{_type}</code>
💚 Описание: <code>{desc}</code></b>
            """
            await send_admins(
                f"<b>❗ Администратор @{msg.from_user.username} создал позицию: \n{msgg}</b>", True
            )
        if photo == "-":
            await msg.answer(msgg, reply_markup=edit_pos_inl(pos_id))
        else:
            await bot.send_photo(chat_id=msg.from_user.id, photo=photo, caption=msgg, reply_markup=edit_pos_inl(pos_id))
    except Exception as err:
        print(err)


@dp.callback_query_handler(IsAdmin(), text='edit_pos', state="*")
async def edit_pos_choose(call: CallbackQuery, state: FSMContext):
    await state.finish()

    if len(await db.get_all_categories()) < 1:
        await call.answer("❗ Нет категорий для изменения позиции")
    else:
        if len(await db.get_all_positions()) < 1:
            await call.answer("❗ Нет позиций для изменения")
        else:
            await call.message.edit_text(f"<b>❗ Выберите категорию для изменения позиции:</b>", reply_markup=await open_cats_for_edit_pos())


@dp.callback_query_handler(text_startswith="edit_pos_cat:", state="*")
async def edit_pos_open(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cat_id = call.data.split(":")[1]

    if len(await db.get_pod_categories(cat_id)) != 0:
        await call.message.edit_text(f"<b>❗ Выберите под-категорию (Или категорию) для изменения позиции</b>",
                                reply_markup=await open_pod_cats_for_edit_pos(cat_id))
    else:
        await call.message.edit_text(f"<b>❗ Выберите позицию для изменения:</b>", reply_markup=await open_positions_for_edit(cat_id))


@dp.callback_query_handler(text_startswith="pod_cat_edit_pos:", state='*')
async def edit_pos_pod_cat(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pod_cat_id = call.data.split(":")[1]
    cat_id = call.data.split(":")[2]

    await call.message.edit_text(f"<b>❗ Выберите позицию для изменения:</b>",
                                 reply_markup=await open_positions_for_edit(cat_id, pod_cat_id))


@dp.callback_query_handler(text_startswith="edit_pos:", state="*")
async def edit_pos_open_(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]
    pos = await db.get_position(pos_id)
    cat = await db.get_category(pos['category_id'])
    _type = pos['type']
    items = f"{len(await db.get_items(position_id=pos_id))}шт"
    settings = await db.get_settings()
    if settings['currency'] == 'rub':
        cur = 'rub'
        price = pos['price_rub']
    elif settings['currency'] == 'usd':
        cur = 'usd'
        price = pos['price_dollar']
    elif settings['currency'] == 'eur':
        cur = 'eur'
        price = pos['price_euro']

    curr = currencies[cur]['sign']

    if pos['infinity'] == "+":
        items = "Безлимит"

    msg = f"""
<b>💎 Категория: <code>{cat['name']}</code>
⚙️ ️Позиция: <code>{pos['name']}</code>
💰 Цена: <code>{price}{curr}</code>
🎲 Количество: <code>{items}</code>
🛒 Тип: <code>{_type}</code>
⭐ Описание:
{pos['description']}</b>
    """

    if pos['pod_category_id'] is not None:
        pod_cat = await db.get_pod_category(pos['pod_category_id'])
        msg = f"""
<b>💎 Категория: <code>{cat['name']}</code>
💚 Под-Категория: <code>{pod_cat['name']}</code>
⚙️ Позиция: <code>{pos['name']}</code>
💰 Цена: <code>{price}{curr}</code>
🎲 Количество: <code>{items}</code>
🛒 Тип: <code>{_type}</code>
⭐ Описание:
{pos['description']}</b>
            """

    if pos['photo'] == "-":
        await call.message.edit_text(msg, reply_markup=edit_pos_inl(pos_id))
    else:
        await bot.send_photo(chat_id=call.from_user.id, photo=pos['photo'], caption=msg, reply_markup=edit_pos_inl(pos_id))


@dp.callback_query_handler(text_startswith="edit_price_pos:", state="*")
async def edit_price_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]

    await call.message.delete()
    await call.message.answer(f"<b>❗ Введите новую цену для позиции</b>")
    await AdminPosEdit.here_new_price_pos.set()
    await state.update_data(cache_pos_id_for_edit_price=pos_id)


@dp.callback_query_handler(text_startswith="edit_name_pos:", state="*")
async def edit_price_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]

    await call.message.delete()
    await call.message.answer(f"<b>❗ Введите новое название для позиции</b>")
    await AdminPosEdit.here_new_name_pos.set()
    await state.update_data(cache_pos_id_for_edit_name=pos_id)


@dp.callback_query_handler(text_startswith="edit_desc_pos:", state="*")
async def edit_price_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]

    await call.message.delete()
    await call.message.answer(f"<b>❗ Введите новое описание для позиции</b>")
    await AdminPosEdit.here_new_desc_pos.set()
    await state.update_data(cache_pos_id_for_edit_desc=pos_id)


@dp.callback_query_handler(text_startswith="edit_photo_pos:", state="*")
async def edit_price_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]

    await call.message.delete()
    await call.message.answer(f"<b>❗ Отправьте новое изображение для позиции</b>")
    await AdminPosEdit.here_new_photo_pos.set()
    await state.update_data(cache_pos_id_for_edit_photo=pos_id)


@dp.callback_query_handler(text_startswith="edit_infinity_pos:", state="*")
async def edit_price_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]

    await call.message.delete()
    await call.message.answer(f"<b>❗ Отправьте <code>+</code> если хотите чтоб товар был бесконечным \nЕсли не хотите введите <code>-</code></b>")
    await AdminPosEdit.here_new_infinity_pos.set()
    await state.update_data(cache_pos_id_for_edit_infinity=pos_id)


@dp.message_handler(state=AdminPosEdit.here_new_price_pos)
async def here_new_price(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        pos_id = data['cache_pos_id_for_edit_price']
    if isinstance(float(msg.text), (float, int)):

        await state.finish()
        settings = await db.get_settings()

        price_rub, price_dollar, price_euro = 0, 0, 0
        if settings['currency'] == 'rub':
            price_rub = float(msg.text)
            price_euro = await get_exchange(price_rub, 'RUB', 'EUR')
            price_dollar = await get_exchange(price_rub, 'RUB', 'USD')
        elif settings['currency'] == 'usd':
            price_dollar = float(msg.text)
            price_euro = await get_exchange(price_dollar, 'USD', 'EUR')
            price_rub = await get_exchange(price_dollar, 'USD', 'RUB')
        elif settings['currency'] == 'eur':
            price_euro = float(msg.text)
            price_dollar = await get_exchange(price_euro, 'EUR', 'USD')
            price_rub = await get_exchange(price_euro, 'EUR', 'RUB')

        if settings['currency'] == 'rub':
            await db.update_position(pos_id, price_rub=price_rub, price_dollar=price_dollar, price_euro=price_euro)
        elif settings['currency'] == 'usd':
            await db.update_position(pos_id, price_rub=price_rub, price_dollar=price_dollar, price_euro=price_euro)
        elif settings['currency'] == 'eur':
            await db.update_position(pos_id, price_rub=price_rub, price_dollar=price_dollar, price_euro=price_euro)

        curr = currencies[settings['currency']]['sign']
        await msg.answer(f"<b>✅ Вы изменили цену позиции на <code>{msg.text}{curr}</code></b>")
        await send_admins(
            f"<b>❗ Администратор @{msg.from_user.username} изменил цену позиции на <code>{msg.text}{curr}</code></b>", True
        )
    else:
        await msg.answer(f"<b>❌ Цена должна быть числом!</b>")


@dp.message_handler(state=AdminPosEdit.here_new_name_pos)
async def here_new_price(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        pos_id = data['cache_pos_id_for_edit_name']

    await state.finish()
    await db.update_position(pos_id, name=msg.text)
    await msg.answer(f"<b>✅ Вы изменили название позиции на <code>{msg.text}</code></b>")
    await send_admins(
        f"<b>❗ Администратор @{msg.from_user.username} изменил название позиции на <code>{msg.text}</code></b>", True
    )


@dp.message_handler(state=AdminPosEdit.here_new_desc_pos)
async def here_new_price(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        pos_id = data['cache_pos_id_for_edit_desc']

    desc = msg.parse_entities(as_html=True)

    if desc == "-":
        desc = "<code>❗ Не поставлено</code>"

    await state.finish()
    await db.update_position(pos_id, description=desc)
    await msg.answer(f"<b>✅ Вы изменили описание позиции на</b> \n{desc}")
    await send_admins(
        f"<b>❗ Администратор @{msg.from_user.username} изменил описание позиции на</b> \n{desc}", True
    )


@dp.message_handler(state=AdminPosEdit.here_new_photo_pos, content_types=['photo'])
@dp.message_handler(state=AdminPosEdit.here_new_photo_pos, text='-')
async def here_new_price(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        pos_id = data['cache_pos_id_for_edit_photo']

    if msg.text == "-":
        photo = "-"
    else:
        photo = msg.photo[-1].file_id

    await state.finish()
    pos = await db.get_position(pos_id)
    await db.update_position(pos_id, photo=photo)
    if photo == "-":
        await msg.answer(f"<b>✅ Вы убрали фото позиции</b>")
        await send_admins(
            f"<b>❗ Администратор @{msg.from_user.username} убрал фото у позиции: <code>{pos['name']}</code></b>", True
        )
    else:
        await send_admins(
            f"<b>❗ Администратор @{msg.from_user.username} изменил фото позиции <code>{pos['name']}</code></b>", True
        )
        await msg.answer(f"<b>✅ Вы изменили фото позиции на</b>")
        await bot.send_photo(chat_id=msg.from_user.id, photo=photo)


@dp.message_handler(state=AdminPosEdit.here_new_infinity_pos, text=['-', '+'])
async def here_new_price(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        pos_id = data['cache_pos_id_for_edit_infinity']

    await state.finish()
    pos = await db.get_position(pos_id)
    await db.update_position(pos_id, infinity=msg.text)

    if msg.text == "+":
        await msg.answer(f"<b>✅ Вы изменили тип товаров позиции на <code>Бесконечный</code></b>")
        await send_admins(
            f"<b>❗ Администратор @{msg.from_user.username} изменил тип товаров позиции <code>{pos['name']}</code> на <code>Бесконечный</code></b>", True
        )
    else:
        await send_admins(
            f"<b>❗ Администратор @{msg.from_user.username} изменил тип товаров позиции <code>{pos['name']}</code> на <code>Обычный</code></b>", True
        )
        await msg.answer(f"<b>✅ Вы изменили тип товаров позиции на <code>Обычный</code></b>")


@dp.callback_query_handler(text_startswith="edit_del_pos:", state="*")
async def edit_del_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]
    await call.message.delete()
    await call.message.answer(f"<b>❓ Вы точно хотите удалить позицию?</b>", reply_markup=choose_del_pos(pos_id))


@dp.callback_query_handler(text_startswith="dels_pos:", state="*")
async def dels_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]
    pos_id = call.data.split(":")[2]

    if action == "yes":
        pos = await db.get_position(pos_id)
        await db.del_position(pos_id)
        await call.message.delete()
        await call.message.answer(f"<b>✅ Вы удалили позицию <code>{pos['name']}</code></b>")
        await send_admins(
            f"<b>❗ Администратор @{call.from_user.username} удалил позицию <code>{pos['name']}</code></b>", True
        )
    else:
        await call.message.delete()
        await call.message.answer(f"<b>❌ Вы отменили удаление позиции</b>")


@dp.callback_query_handler(text="del_all_poss", state='*')
async def del_all_poss(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text(f"<b>❓ Вы точно хотите удалить <u>ВСЕ</u> позиции?</b>", reply_markup=choose_del_all_pos())


@dp.callback_query_handler(text_startswith="dels_all_poss:", state="*")
async def del_all_posss(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]

    if action == "yes":
        await db.del_all_positions()
        await call.message.edit_text(f"<b>✅ Вы удалили все позиции</b>")
        await send_admins(
            f"<b>❗ Администратор @{call.from_user.username} удалил ВСЕ позиции</b>", True
        )
    else:
        await call.message.edit_text(f"<b>❌ Вы отменили удаление всех позиций</b>")


@dp.callback_query_handler(text_startswith="edit_clear_items_pos:", state="*")
async def edit_clear_it_pos(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]

    await call.message.delete()
    await call.message.answer(f"<b>❓ Вы точно хотите очистить товары позиции?</b>", reply_markup=choose_clear_items_pos(pos_id))


@dp.callback_query_handler(text_startswith="clear_items:", state="*")
async def clear_itemss(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]
    pos_id = call.data.split(":")[2]

    if action == "yes":
        await db.remove_item(position_id=pos_id)
        await call.message.delete()
        await call.message.answer(f"<b>✅ Вы очистили товары позиции</b>")
    else:
        await call.message.delete()
        await call.message.answer(f"<b>❌ Вы отменили чистку товаров позиции</b>")


@dp.callback_query_handler(text_startswith="edit_upload_items_pos:", state='*')
async def edit_upload_items(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pos_id = call.data.split(":")[1]
    pos = await db.get_position(pos_id)
    _type = pos['type']
    msg = ""

    if _type == "text":
        msg = f"""
<b>⚙️ Введите данные товаров 
❗ Чтобы отделить товары, оставить между ними пустую строку 
⭐ Если товар бесконечный, то разделение работать не будет! (Будет отображаться только первый товар!) Пример:


<code>Товар #1...</code>

<code>Товар #2...</code>

<code>Товар #3...</code></b>"""
    elif _type == "photo":
        msg = f"""
<b>⚙️ Отправьте фото товара

❗ Загружайте по одному</b>"""
    elif _type == "file":
        msg = f"""
<b>⚙️ Отправьте файл товара

❗ Загружайте по одному</b>"""

    await call.message.answer(msg,
        reply_markup=back_pr_edits())

    await state.update_data(cache_pos_id_for_add_items=pos_id)
    await state.update_data(here_count_add_items=0)
    await AdminItemsEdit.here_data_items.set()


########################################################################################
############################          Товары          ##################################
########################################################################################

@dp.callback_query_handler(IsAdmin(), text='add_items', state="*")
async def edit_pos_choose(call: CallbackQuery, state: FSMContext):
    await state.finish()

    if len(await db.get_all_categories()) < 1:
        await call.answer("❗ Нет категорий для добавления товаров")
    else:
        if len(await db.get_all_positions()) < 1:
            await call.answer("❗ Нет позиций для добавления товаров")
        else:
            await call.message.edit_text(f"<b>❗ Выберите категорию для добавления товаров:</b>", reply_markup=await open_cats_for_add_items())


@dp.callback_query_handler(text_startswith="add_items_cat:", state="*")
async def edit_pos_open(call: CallbackQuery, state: FSMContext):
    await state.finish()

    cat_id = call.data.split(":")[1]

    if len(await db.get_pod_categories(cat_id)) != 0:
        await call.message.edit_text(f"<b>❗ Выберите под-категорию (Или категорию) для добавления товаров</b>",
                                  reply_markup=await open_pod_cats_for_add_items(cat_id))
    else:
        await call.message.edit_text(f"<b>❗ Выберите позицию для добавления товаров:</b>", reply_markup=await open_positions_for_add_items(cat_id))


@dp.callback_query_handler(text_startswith="pod_cat_add_items:", state='*')
async def edit_pos_pod_cat(call: CallbackQuery, state: FSMContext):
    await state.finish()

    pod_cat_id = call.data.split(":")[1]
    cat_id = call.data.split(":")[2]

    await call.message.edit_text(f"<b>❗ Выберите позицию для добавления товаров:</b>",
                                 reply_markup=await open_positions_for_add_items(cat_id, pod_cat_id))


@dp.callback_query_handler(text_startswith="spos_add_items", state="*")
@dp.callback_query_handler(text_startswith="pos_add_items", state="*")
async def pos_add_items(call: CallbackQuery, state: FSMContext):
    await state.finish()
    pos_id = call.data.split(":")[1]
    pos = await db.get_position(pos_id)
    _type = pos['type']
    msg = ""

    if _type == "text":
        msg = f"""
<b>⚙️ Введите данные товаров 
❗ Чтобы отделить товары, оставить между ними пустую строку 
⭐ Если товар бесконечный, то разделение работать не будет! (Будет отображаться только первый товар!) Пример:


<code>Товар #1...</code>

<code>Товар #2...</code>

<code>Товар #3...</code></b>"""
    elif _type == "photo":
        msg = f"""
<b>⚙️ Отправьте фото товара

❗ Загружайте по одному</b>"""
    elif _type == "file":
        msg = f"""
<b>⚙️ Отправьте файл товара

❗ Загружайте по одному</b>"""

    await call.message.answer(msg,
                              reply_markup=back_pr_edits())

    await state.update_data(cache_pos_id_for_add_items=pos_id)
    await state.update_data(here_count_add_items=0)
    await AdminItemsEdit.here_data_items.set()


@dp.message_handler(content_types=['photo', 'document'], state=AdminItemsEdit.here_data_items)
@dp.message_handler(state=AdminItemsEdit.here_data_items)
async def here_data_items(message: Message, state: FSMContext):
    cache_msg = await message.answer("<b>⌛ Ждите, товары добавляются...</b>")
    count_add = 0

    async with state.proxy() as data:
        pos_id = data['cache_pos_id_for_add_items']

    pos = await db.get_position(pos_id)
    _type = pos['type']

    if _type == "text":
        get_all_items = message.text.split("\n\n")
        for check_item in get_all_items:
            if not check_item.isspace() and check_item != "": count_add += 1
        async with state.proxy() as data:
            data['here_count_add_items'] += count_add

        await db.add_item(pos['category_id'], pos['id'], get_all_items, False)
    elif _type == "photo" and message.content_type == "photo":
        file_id = message.photo[-1].file_id
        get_all_items = f"photo:{file_id}"
        count_add += 1
        async with state.proxy() as data:
            data['here_count_add_items'] += count_add
        await db.add_item(pos['category_id'], pos['id'], get_all_items, True)
    elif _type == "file" and message.content_type == "document":
        file_id = message.document.file_id
        get_all_items = f"file:{file_id}"
        count_add += 1
        async with state.proxy() as data:
            data['here_count_add_items'] += count_add
        await db.add_item(pos['category_id'], pos['id'], get_all_items, True)
    else:
        return await cache_msg.edit_text(f"<b>❗ Отправьте нужный тип товара!</b>")

    await cache_msg.edit_text(f"<b>✅ Товары в кол-ве <code>{count_add}шт</code> были успешно добавлены</b>",
                              reply_markup=stop_add_items())


@dp.callback_query_handler(text="stop_add_items", state="*")
async def product_item_load_finish(call: CallbackQuery, state: FSMContext):
    items = 0

    try:
        async with state.proxy() as data:
            items = data['here_count_add_items']
    except:
        pass

    await state.finish()
    await call.message.edit_text("<b>✅ Загрузка товаров была успешно завершена \n"
                        f"⚙️ Загружено товаров: <code>{items}шт</code></b>")


@dp.callback_query_handler(text="del_all_items", state="*")
async def del_all_itemss(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(f"<b>❓ Вы точно хотите удалить <u>ВСЕ</u> товары?</b>", reply_markup=choose_del_all_items())


@dp.callback_query_handler(text_startswith="dels_all_items:", state="*")
async def dels_all_items(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]

    if action == "yes":
        await db.del_all_items()
        await call.message.edit_text(f"<b>✅ Вы удалили все товары</b>")
        await send_admins(
            f"<b>❗ Администратор @{call.from_user.username} удалил ВСЕ товары</b>", True
        )
    else:
        await call.message.edit_text(f"<b>❌ Вы отменили удаление всех товаров</b>")

