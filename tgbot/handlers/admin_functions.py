# - *- coding: utf- 8 - *-
import nest_asyncio
import asyncio
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from tgbot.keyboards.inline_admin import (
    pr_buttons_back,
    pr_buttons_inl,
    admin_menu,
    mail_types,
    opr_mail_photo,
    opr_mail_text,
    settings_inl,
    on_off_inl,
    find_settings,
    find_back,
    profile_adm_inl,
    set_back,
    back_sett,
    extra_back,
    extra_settings_inl,
    contests_inl,
    contests_conditions_inl,
    mail_buttons_inl,
    mail_buttons_type_inl,
    open_cats_for_add_mail_btn,
    open_pod_cats_for_add_mail_btn,
    open_cats_for_pod_cat_add_mail_btn,
    open_cats_for_pos_add_mail,
    open_pod_cats_for_pos_add_mail,
    open_positions_for_pos_add_mail,
    mail_buttons_edit_inl,
    mail_buttons_current_inl,
    cancel_contest_now_yes_no,
    choose_contest_for_cancel,
    choose_languages_kb_adm,
    stats_inl,
    currencies_kb,
    mail_buttons_contest_yes_no,
    choose_contest_for_mail_button,
)
from tgbot.data.config import db, currencies
from tgbot.data.config import lang_ru as texts
from tgbot.keyboards.inline_user import mail_btn
from tgbot.filters.filters import IsAdmin
from tgbot.data.loader import dp, bot
from tgbot.utils.utils_functions import (
    send_admins,
    get_admins,
    get_exchange,
    convert_words,
    end_contest,
    get_users_and_their_balances_in_file,
)
import time
from datetime import datetime, timedelta
from tgbot.states.admin import (
    AdminContests,
    AdminMail,
    AdminFind,
    AdminSettingsEdit,
    AdminPrButtons,
    AdminCoupons,
    AdminEditUser,
    ChangeNewsChannel,
)
from tgbot.utils.json_utils import update_public_news_id

nest_asyncio.apply()


async def mail_start_text(call: CallbackQuery, msg):
    await send_admins(
        f"<b>❗ Администратор @{call.from_user.username} запустил рассылку!</b>", True
    )
    users = await db.all_users()
    yes_users, no_users = 0, 0
    for user in users:
        try:
            user_id = user["id"]
            await bot.send_message(
                chat_id=user_id, text=msg, reply_markup=await mail_btn()
            )
            yes_users += 1
        except:
            no_users += 1

    new_msg = f"""
<b>💎 Всего пользователей: <code>{len(await db.all_users())}</code>
✅ Отправлено: <code>{yes_users}</code>
❌ Не отправлено (Бот заблокирован): <code>{no_users}</code></b>
    """

    await call.message.answer(new_msg)


async def mail_start_photo(call: CallbackQuery, msg, file_id):
    await send_admins(
        f"<b>❗ Администратор @{call.from_user.username} запустил рассылку!</b>", True
    )
    users = await db.all_users()
    yes_users, no_users = 0, 0
    for user in users:
        try:
            user_id = user["id"]
            await bot.send_photo(
                chat_id=user_id,
                photo=file_id,
                caption=msg,
                reply_markup=await mail_btn(),
            )
            yes_users += 1
        except:
            no_users += 1

    new_msg = f"""
<b>💎 Всего пользователей: <code>{len(await db.all_users())}</code>
✅ Отправлено: <code>{yes_users}</code>
❌ Не отправлено (Бот заблокирован): <code>{no_users}</code></b>
    """

    await call.message.answer(new_msg)


@dp.callback_query_handler(IsAdmin(), text="contests_admin", state="*")
async def contests(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text("Розыгрыши", reply_markup=await contests_inl())


@dp.callback_query_handler(IsAdmin(), text="contest_conditions", state="*")
async def contests_conditions(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(
        "Условия розыгрышей", reply_markup=await contests_conditions_inl()
    )


@dp.callback_query_handler(IsAdmin(), text="create_contest", state="*")
async def contest_create(call: CallbackQuery, state: FSMContext):
    await state.finish()

    db_settings = await db.get_contests_settings()

    await db.create_contest(
        db_settings["prize"],
        db_settings["members_num"],
        time.time() + db_settings["end_time"],
        db_settings["winners_num"],
        db_settings["channels_ids"],
        db_settings["refills_num"],
        db_settings["purchases_num"],
    )
    await call.answer(f"Розыгрыш был запущен!")


@dp.callback_query_handler(IsAdmin(), text_startswith="cancel_contest:", state="*")
async def cancel_contest_id(call: CallbackQuery, state: FSMContext):
    await state.finish()
    contest_id = call.data.split(":")[1]
    contest = await db.get_contest(contest_id)
    bot_settings = await db.get_settings()
    a = contest["end_time"] - time.time()
    a1 = datetime.today()
    a2 = a1 + timedelta(seconds=a)
    end_time_ = a2 - a1
    end_time = str(end_time_).split(".")[0]
    if len(end_time.split(",")) == 2:
        day = end_time.split(",")[0]
        day = day.split(" ")[0]
        day_text = convert_words(int(day), ["день", "дня", "дней"])
        end_time = f"{day} {day_text}, {end_time.split(', ')[1]}"
    else:
        end_time = f"{end_time.split(', ')[0]}"

    text = """
<b>🎁 Розыгрыш

💰 Сумма: <code>{}{}</code>

🕒 Конец через <code>{}</code></b>""".format(
        contest["prize"], currencies[bot_settings["currency"]]["sign"], end_time
    )

    await call.message.edit_text(
        text=text, reply_markup=cancel_contest_now_yes_no(contest_id)
    )


@dp.callback_query_handler(text="edit_winners_contest")
async def edit_winners_contest(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(
        "<b>❗ Введите кол-во победителей:</b>", reply_markup=back_sett()
    )
    await AdminContests.here_winner_count_contests.set()


@dp.message_handler(state=AdminContests.here_winner_count_contests)
async def here_winners_count_contests(msg: Message, state: FSMContext):
    count = msg.text
    if count.isdigit() and int(count) > 0:
        await state.finish()
        await db.update_contests_settings(winners_num=count)
        await msg.reply("Успешно!")
    else:
        await msg.answer("Ответ должен быть числом больше 0! Введите еще раз:")


@dp.callback_query_handler(text="edit_prize_contest")
async def edit_prize_contest(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(
        "<b>❗ Введите сумму приза:</b>", reply_markup=back_sett()
    )
    await AdminContests.here_prize_contests.set()


@dp.message_handler(state=AdminContests.here_prize_contests)
async def here_prize_contests(msg: Message, state: FSMContext):
    count = msg.text
    if count.isdigit() and int(count) > 0:
        await state.finish()
        await db.update_contests_settings(prize=count)
        await msg.reply("Успешно!")
    else:
        await msg.answer("Ответ должен быть числом больше 0! Введите еще раз:")


@dp.callback_query_handler(text="edit_members_contest")
async def edit_members_contest(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(
        "<b>❗ Введите кол-во участников розыгрыша:</b>", reply_markup=back_sett()
    )
    await AdminContests.here_members_contests.set()


@dp.message_handler(state=AdminContests.here_members_contests)
async def here_members_contests(msg: Message, state: FSMContext):
    count = msg.text
    if count.isdigit() and int(count) > 0:
        await state.finish()
        await db.update_contests_settings(members_num=count)
        await msg.reply("Успешно!")
    else:
        await msg.answer("Ответ должен быть числом больше 0! Введите еще раз:")


@dp.callback_query_handler(text="edit_end_time_contest")
async def edit_end_time_contest(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(
        "<b>❗ Введите через какое кол-во секунд будет конец розыгрыша:</b>",
        reply_markup=back_sett(),
    )
    await AdminContests.here_end_time_contests.set()


@dp.message_handler(state=AdminContests.here_end_time_contests)
async def here_end_time_contests(msg: Message, state: FSMContext):
    count = msg.text
    if count.isdigit() and int(count) > 0:
        await state.finish()
        await db.update_contests_settings(end_time=count)
        await msg.reply("Успешно!")
    else:
        await msg.answer("Ответ должен быть числом больше 0! Введите еще раз:")


@dp.callback_query_handler(text_startswith="edit_con_conds:")
async def edit_con_conds(call: CallbackQuery, state: FSMContext):
    await state.finish()
    action = call.data.split(":")[1]
    await state.update_data(action=action)
    await AdminContests.edit_con_conds.set()
    if action == "purchases":
        await call.message.edit_text(
            "<b>❗ Введите кол-во покупок:</b>", reply_markup=back_sett()
        )
    elif action == "refills":
        await call.message.edit_text(
            "<b>❗ Введите кол-во пополнений:</b>", reply_markup=back_sett()
        )
    else:
        await call.message.edit_text(
            "<b>❗ Введите ID каналов для подписки через запятую. \nПример: -12345678910, -12423562345 \n\nВведите <code>-</code> Если не хотите ставить.</b>",
            reply_markup=back_sett(),
        )


@dp.message_handler(text="-", state=AdminContests.edit_con_conds)
@dp.message_handler(state=AdminContests.edit_con_conds)
async def edit_con_conds_(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        action = data["action"]
    count = msg.text
    if action == "purchases":
        if count.isdigit():
            await state.finish()
            await db.update_contests_settings(purchases_num=count)
            await msg.reply("Успешно!")
        else:
            await msg.answer("Ответ должен быть числом! Введите еще раз:")
    elif action == "refills":
        if count.isdigit():
            await state.finish()
            await db.update_contests_settings(refills_num=count)
            await msg.reply("Успешно!")
        else:
            await msg.answer("Ответ должен быть числом! Введите еще раз:")
    else:
        await state.finish()
        await db.update_contests_settings(channels_ids=count)
        await msg.reply("Успешно!")


@dp.callback_query_handler(IsAdmin(), text="cancel_contest_now", state="*")
async def cancel_contest_now(call: CallbackQuery, state: FSMContext):
    await state.finish()
    contests = await db.get_contests()
    if len(contests) > 1:
        await call.message.edit_text(
            text="Выберите розыгрыш",
            reply_markup=await choose_contest_for_cancel(contests),
        )
    elif len(contests) == 1:
        bot_settings = await db.get_settings()
        a = contests[0]["end_time"] - time.time()
        a1 = datetime.today()
        a2 = a1 + timedelta(seconds=a)
        end_time_ = a2 - a1
        end_time = str(end_time_).split(".")[0]
        if len(end_time.split(",")) == 2:
            day = end_time.split(",")[0]
            day = day.split(" ")[0]
            day_text = convert_words(int(day), ["день", "дня", "дней"])
            end_time = f"{day} {day_text}, {end_time.split(', ')[1]}"
        else:
            end_time = f"{end_time.split(', ')[0]}"

        text = """
<b>🎁 Розыгрыш

💰 Сумма: <code>{}{}</code>

🕒 Конец через <code>{}</code></b>""".format(
            contests[0]["prize"], currencies[bot_settings["currency"]]["sign"], end_time
        )

        await call.message.edit_text(
            text=text, reply_markup=cancel_contest_now_yes_no(contests[0]["id"])
        )
    else:
        await call.answer(texts.no_contests, True)


@dp.callback_query_handler(IsAdmin(), text_startswith="cancel_contest_:", state="*")
async def cancel_contest_(call: CallbackQuery, state: FSMContext):
    await state.finish()
    action = call.data.split(":")[1]
    contest_id = call.data.split(":")[2]

    if action == "yes":
        await end_contest(contest_id)
        await call.message.delete()
    else:
        await call.answer("❗ Вы отказались заканчивать розыгрыш!")
        await call.message.delete()


@dp.callback_query_handler(IsAdmin(), text="admin_menu", state="*")
async def admin_menu_send(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.delete()
    await call.message.answer(
        "Добро пожаловать в меню Администратора", reply_markup=admin_menu()
    )


@dp.callback_query_handler(IsAdmin(), text="settings_back", state="*")
async def admin_menu_send(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(
        "Добро пожаловать в меню Администратора", reply_markup=admin_menu()
    )


@dp.callback_query_handler(IsAdmin(), text="mail_start", state="*")
async def adm_mail_start(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(
        "<b>❗ Выберите тип рассылки</b>", reply_markup=mail_types()
    )


@dp.callback_query_handler(text_startswith="mail:", state="*")
async def mail_types_chosen(call: CallbackQuery, state: FSMContext):
    await state.finish()

    tip = call.data.split(":")[1]
    if tip == "text":
        await call.message.edit_text(
            "<b>❗ Введите текст для рассылки \n📌 Можно использовать разметку Telegram.</b>"
        )
        await AdminMail.here_text_mail_text.set()
    elif tip == "photo":
        await call.message.edit_text(
            "<b>❗ Введите текст для рассылки \n📌 Можно использовать разметку Telegram.</b>"
        )
        await AdminMail.here_text_mail_photo.set()


@dp.message_handler(IsAdmin(), state=AdminMail.here_text_mail_text)
async def mail_text_start(message: Message, state: FSMContext):
    msg = message.parse_entities()
    await message.answer(
        f"<b>❗ Вы точно хотите запустить рассылку с таким текстом?</b>"
    )
    await message.answer(
        msg, reply_markup=opr_mail_text(), disable_web_page_preview=True
    )
    await state.update_data(here_text_mail_text=msg)


@dp.callback_query_handler(IsAdmin(), text="mail_buttons", state="*")
async def mail_buttons(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Настройки", reply_markup=mail_buttons_inl())


@dp.callback_query_handler(IsAdmin(), text_startswith="mail_buttons:", state="*")
async def mail_buttons_(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]

    if action == "add":
        await call.message.edit_text("<b>❗ Введите название кнопки:</b>")
        await AdminMail.here_name_for_add_mail_button.set()
    elif action == "current":
        if len(await db.get_all_mail_buttons()) > 0:
            await call.message.edit_text(
                "<b>❗ Выберите кнопку:</b>",
                reply_markup=await mail_buttons_current_inl(),
            )
        else:
            await call.answer("❗ На данный момент кнопок нет!")


@dp.callback_query_handler(IsAdmin(), text_startswith="edit_mail_button:", state="*")
async def edit_mail_button(call: CallbackQuery, state: FSMContext):
    await state.finish()

    btn_id = call.data.split(":")[1]
    btn = await db.get_mail_button(btn_id)

    await call.message.edit_text(
        f"<b>✨ Кнопка: {btn['name']}</b>", reply_markup=mail_buttons_edit_inl(btn_id)
    )


@dp.callback_query_handler(IsAdmin(), text_startswith="edits_mail_btn:", state="*")
async def edits_mail_btn(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]
    btn_id = call.data.split(":")[2]

    async with state.proxy() as data:
        data["btn_id"] = btn_id

    if action == "edit_name":
        await call.message.edit_text("<b>❗ Введите новое название для кнопки:</b>")
        await AdminMail.here_new_name_for_mail_button.set()
    elif action == "del":
        await db.delete_mail_button(btn_id)
        if len(await db.get_all_mail_buttons()) > 0:
            await call.message.edit_text(
                "<b>❗ Выберите кнопку:</b>",
                reply_markup=await mail_buttons_current_inl(),
            )
        else:
            await call.message.edit_text("Настройки", reply_markup=mail_buttons_inl())


@dp.message_handler(IsAdmin(), state=AdminMail.here_new_name_for_mail_button)
async def here_new_name_for_mail_button(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        btn_id = data["btn_id"]

    await state.finish()
    await db.update_mail_button(btn_id, name=msg.text)
    await msg.reply("<b>✅ Успешно!</b>")
    if len(await db.get_all_mail_buttons()) > 0:
        await msg.answer(
            "<b>❗ Выберите кнопку:</b>", reply_markup=await mail_buttons_current_inl()
        )
    else:
        await msg.answer("Настройки", reply_markup=mail_buttons_inl())


@dp.message_handler(IsAdmin(), state=AdminMail.here_name_for_add_mail_button)
async def mail_buttons__(msg: Message, state: FSMContext):
    await state.finish()

    async with state.proxy() as data:
        data["name_mail_btn"] = msg.text

    await msg.reply(
        "<b>❗ Выберите тип кнопки:</b>", reply_markup=mail_buttons_type_inl()
    )


@dp.callback_query_handler(IsAdmin(), text="back_mail_btn_type", state="*")
async def _mail_buttons_235(call: CallbackQuery):
    await call.message.edit_text(
        "<b>❗ Выберите тип кнопки:</b>", reply_markup=mail_buttons_type_inl()
    )


@dp.callback_query_handler(IsAdmin(), text_startswith="add_mail_buttons:", state="*")
async def _mail_buttons_(call: CallbackQuery):

    typ = call.data.split(":")[1]

    if typ == "link":
        await call.message.edit_text("<b>❗ Введите ссылку:</b>")
        await AdminMail.here_link_for_add_mail_button.set()
    elif typ == "category":
        if len(await db.get_all_categories()) < 1:
            await call.answer("❗ Нет категорий для открытия", True)
        else:
            await call.message.edit_text(
                "<b>❗ Выберите категорию для открытия:</b>",
                reply_markup=await open_cats_for_add_mail_btn(),
            )
            await AdminMail.here_category_for_open_mail.set()
    elif typ == "pod_category":
        if len(await db.get_all_pod_categories()) < 1:
            await call.answer(f"❗ Нет под-категорий для открытия", True)
        else:
            if len(await db.get_all_categories()) < 1:
                await call.answer(f"❗ Нет категорий для открытия под-категории", True)
            else:
                await call.message.edit_text(
                    "<b>❗ Выберите категорию для открытия под-категории:</b>",
                    reply_markup=await open_cats_for_pod_cat_add_mail_btn(),
                )
                await AdminMail.here_category_for_pod_open_mail.set()
    elif typ == "position":
        if len(await db.get_all_categories()) < 1:
            await call.answer("❗ Нет категорий для открытия позиции", True)
        else:
            if len(await db.get_all_positions()) < 1:
                await call.answer("❗ Нет позиций для открытия", True)
            else:
                await call.message.edit_text(
                    "<b>❗ Выберите категорию для открытия позиции:</b>",
                    reply_markup=await open_cats_for_pos_add_mail(),
                )
                await AdminMail.here_category_for_pos_open_mail.set()
    elif typ == "contest":
        contests = await db.get_contests()

        if len(contests) == 0:
            await call.answer("❗ Нет розыгрышей для открытия!", True)
        elif len(contests) == 1:
            contest_id = contests[0]["id"]
            contest = await db.get_contest(contest_id)
            bot_settings = await db.get_settings()
            a = contest["end_time"] - time.time()
            a1 = datetime.today()
            a2 = a1 + timedelta(seconds=a)
            end_time_ = a2 - a1
            end_time = str(end_time_).split(".")[0]
            if len(end_time.split(",")) == 2:
                day = end_time.split(",")[0]
                day = day.split(" ")[0]
                day_text = convert_words(int(day), ["день", "дня", "дней"])
                end_time = f"{day} {day_text}, {end_time.split(', ')[1]}"
            else:
                end_time = f"{end_time.split(', ')[0]}"

            text = """
<b>🎁 Розыгрыш

💰 Сумма: <code>{}{}</code>

🕒 Конец через <code>{}</code></b>""".format(
                contest["prize"], currencies[bot_settings["currency"]]["sign"], end_time
            )

            await call.message.answer(
                "❓ Вы точно хотите создать кнопку с открытием этого розыгрыша?"
            )
            await call.message.answer(
                text, reply_markup=mail_buttons_contest_yes_no(contest_id)
            )
        elif len(contests) > 1:
            await call.message.answer(
                "❗ Выберите розыгрыш, чтобы создать кнопку открытия:",
                reply_markup=await choose_contest_for_mail_button(contests),
            )


@dp.callback_query_handler(
    IsAdmin(), text_startswith="mail_button_contest_create:", state="*"
)
async def mail_button_contest_create(call: CallbackQuery):
    contest_id = call.data.split(":")[1]
    contest = await db.get_contest(contest_id)
    bot_settings = await db.get_settings()
    a = contest["end_time"] - time.time()
    a1 = datetime.today()
    a2 = a1 + timedelta(seconds=a)
    end_time_ = a2 - a1
    end_time = str(end_time_).split(".")[0]
    if len(end_time.split(",")) == 2:
        day = end_time.split(",")[0]
        day = day.split(" ")[0]
        day_text = convert_words(int(day), ["день", "дня", "дней"])
        end_time = f"{day} {day_text}, {end_time.split(', ')[1]}"
    else:
        end_time = f"{end_time.split(', ')[0]}"

    text = """
<b>🎁 Розыгрыш

💰 Сумма: <code>{}{}</code>

🕒 Конец через <code>{}</code></b>""".format(
        contest["prize"], currencies[bot_settings["currency"]]["sign"], end_time
    )

    await call.message.answer(
        "❓ Вы точно хотите создать кнопку с открытием этого розыгрыша?"
    )
    await call.message.answer(
        text, reply_markup=mail_buttons_contest_yes_no(contest_id)
    )


@dp.callback_query_handler(
    IsAdmin(), text_startswith="mail_button_create_contest:", state="*"
)
async def mail_button_create_contest(call: CallbackQuery, state: FSMContext):
    action = call.data.split(":")[1]
    contest_id = call.data.split(":")[2]

    async with state.proxy() as data:
        name = data["name_mail_btn"]
    await state.finish()

    if action == "yes":
        await db.create_mail_button(name, f"contest_open|{contest_id}")
        await call.message.edit_text("<b>✅ Успешно!</b>")
    else:
        await call.message.edit_text("<b>❌ Вы отменили создание кнопки!</b>")


@dp.callback_query_handler(
    text_startswith="pos_cat_add_mail:", state=AdminMail.here_category_for_pos_open_mail
)
async def edit_pos_open(call: CallbackQuery):

    cat_id = call.data.split(":")[1]

    if len(await db.get_pod_categories(cat_id)) != 0:
        await call.message.edit_text(
            f"<b>❗ Выберите под-категорию или позицию для ее открытия</b>",
            reply_markup=await open_pod_cats_for_pos_add_mail(cat_id),
        )
    else:
        await call.message.edit_text(
            f"<b>❗ Выберите позицию для открытия:</b>",
            reply_markup=await open_positions_for_pos_add_mail(cat_id),
        )


@dp.callback_query_handler(text_startswith="pod_cat_pos_add_mail:", state="*")
async def edit_pos_pod_cat(call: CallbackQuery):

    pod_cat_id = call.data.split(":")[1]
    cat_id = call.data.split(":")[2]

    await call.message.edit_text(
        f"<b>❗ Выберите позицию для открытия:</b>",
        reply_markup=await open_positions_for_pos_add_mail(cat_id, pod_cat_id),
    )


@dp.callback_query_handler(IsAdmin(), text_startswith="pos_add_mail:", state="*")
async def here_category(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        name = data["name_mail_btn"]
    await state.finish()

    pos_id = call.data.split(":")[1]
    await db.create_mail_button(name, f"position_open|{pos_id}")
    await call.message.edit_text("<b>✅ Успешно!</b>")


@dp.callback_query_handler(
    IsAdmin(),
    text_startswith="cat_pod_add_mail:",
    state=AdminMail.here_category_for_pod_open_mail,
)
async def here_category_for_pod_open_mail(call: CallbackQuery, state: FSMContext):
    cat_id = call.data.split(":")[1]

    if len(await db.get_pod_categories(cat_id)) < 1:
        await call.answer(f"❗ В этой категории нет под-категорий!")
    else:
        await call.message.edit_text(
            "<b>❗ Выберите под-категорию для открытия:</b>",
            reply_markup=await open_pod_cats_for_add_mail_btn(cat_id),
        )
        await AdminMail.here_pod_category_for_pod_open_mail.set()


@dp.callback_query_handler(
    IsAdmin(),
    text_startswith="podss_cat_add_mail:",
    state=AdminMail.here_pod_category_for_pod_open_mail,
)
async def here_category(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        name = data["name_mail_btn"]
    await state.finish()

    pod_cat_id = call.data.split(":")[1]
    await db.create_mail_button(name, f"pod_category_open|{pod_cat_id}")
    await call.message.edit_text("<b>✅ Успешно!</b>")


@dp.callback_query_handler(
    IsAdmin(),
    text_startswith="cat_add_mail:",
    state=AdminMail.here_category_for_open_mail,
)
async def here_category(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        name = data["name_mail_btn"]
    await state.finish()
    cat_id = call.data.split(":")[1]
    await db.create_mail_button(name, f"category_open|{cat_id}")
    await call.message.edit_text("<b>✅ Успешно!</b>")


@dp.message_handler(state=AdminMail.here_link_for_add_mail_button)
async def __mail_buttons__(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        name = data["name_mail_btn"]

    if "http://" in msg.text or "https://" in msg.text:
        try:
            await db.create_mail_button(name, f"link|{msg.text}")
        except BaseException as err:
            print(err)

        await msg.reply("<b>✅ Успешно!</b>")
        await state.finish()
    else:
        await msg.reply("Введите ссылку!")


@dp.callback_query_handler(text_startswith="mail_start_text:", state="*")
async def mail_opr(call: CallbackQuery, state: FSMContext):
    way = call.data.split(":")[1]

    async with state.proxy() as data:
        msg = data["here_text_mail_text"]

    if way == "no":
        await call.message.edit_text(
            "<b>❗ Введите новый текст для рассылки \n📌 Можно использовать HTML-Разметку.</b>"
        )
        await AdminMail.here_text_mail_text.set()
    elif way == "yes":
        loop = asyncio.get_event_loop()
        a1 = loop.create_task(mail_start_text(call, msg))
        loop.run_until_complete(a1)


###################################################################################


@dp.message_handler(IsAdmin(), state=AdminMail.here_text_mail_photo)
async def mail_photo_start(message: Message, state: FSMContext):
    msg = message.parse_entities()
    await message.answer(f"<b>❗ Отправьте фото для рассылки</b>")
    await state.update_data(here_text_mail_photo=msg)
    await AdminMail.here_photo_mail_photo.set()


@dp.message_handler(
    IsAdmin(), content_types=["photo"], state=AdminMail.here_photo_mail_photo
)
async def mail_photo_starts(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    msg = (await state.get_data())["here_text_mail_photo"]
    await state.update_data(here_photo_mail_photo=photo)

    await message.answer(
        f"<b>❗ Вы точно хотите запустить рассылку с таким текстом?</b>"
    )
    await bot.send_photo(
        chat_id=message.from_user.id,
        photo=photo,
        caption=msg,
        reply_markup=opr_mail_photo(),
    )


@dp.callback_query_handler(text_startswith="mail_start_photo:", state="*")
async def mail_opr(call: CallbackQuery, state: FSMContext):
    way = call.data.split(":")[1]

    msg = (await state.get_data())["here_text_mail_photo"]
    file_id = (await state.get_data())["here_photo_mail_photo"]

    if way == "no":
        await call.message.edit_text(
            "<b>❗ Введите новый текст для рассылки \n📌 Можно использовать HTML-Разметку.</b>"
        )
        await AdminMail.here_text_mail_photo.set()
    elif way == "yes":
        loop = asyncio.get_event_loop()
        a1 = loop.create_task(mail_start_photo(call, msg, file_id))
        loop.run_until_complete(a1)


@dp.callback_query_handler(IsAdmin(), text_startswith="settings", state="*")
async def settings_open(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(
        "<b>⚙️ Основные настройки бота.</b>", reply_markup=await settings_inl()
    )


@dp.callback_query_handler(IsAdmin(), text_startswith="on_off", state="*")
async def on_off_open(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(
        "<b>⚙️ Выберите что хотите выключить/включить \n❌ - Выкл. | ✅ - Вкл.</b>",
        reply_markup=await on_off_inl(),
    )


@dp.callback_query_handler(IsAdmin(), text="currency:edit", state="*")
async def currency_edit(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(
        "<b>❗ Выберите новую валюту бота. \n\nP.S. При смене валюты цены на товары конвертируются из текущей валюты в новую.</b>",
        reply_markup=currencies_kb(),
    )


@dp.callback_query_handler(IsAdmin(), text_startswith="set_curr:", state="*")
async def set_curr(call: CallbackQuery, state: FSMContext):
    await state.finish()
    curr = call.data.split(":")[1]
    await db.update_settings(currency=curr)

    await call.message.edit_text(
        "<b>⚙️ Основные настройки бота.</b>", reply_markup=await settings_inl()
    )


@dp.callback_query_handler(IsAdmin(), text="find:", state="*")
async def find_open(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(
        "<b>⚙️ Выберите что хотите найти</b>", reply_markup=find_settings()
    )


@dp.callback_query_handler(IsAdmin(), text="find:profile", state="*")
async def find_profile_open(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(
        "<b>❗ Введите ID, имя или @username пользователя</b>", reply_markup=find_back()
    )
    await AdminFind.here_user.set()


@dp.message_handler(state=AdminFind.here_user)
async def find_profile_op(message: Message, state: FSMContext):
    if message.text.isdigit():
        user = await db.get_user(id=message.text)
    elif message.text.startswith("@"):
        user = await db.get_user(user_name=message.text.split("@")[1])
    else:
        user = await db.get_user(first_name=message.text)

    if user is None:
        await message.reply("<b>❗ Такого пользователя нет! Перепроверьте данные!</b>")
    else:
        await state.finish()

        user_name = user["user_name"]
        user_id = user["id"]
        total_refill = user["total_refill"]
        reg_date = user["reg_date"]
        ref_count = user["ref_count"]
        settings = await db.get_settings()
        if settings["currency"] == "rub":
            balance = user["balance_rub"]
            tr = total_refill
        elif settings["currency"] == "usd":
            balance = user["balance_dollar"]
            tr = total_refill
        elif settings["currency"] == "eur":
            balance = user["balance_euro"]
            tr = total_refill
        cur = currencies[settings["currency"]]["sign"]
        msg = f"""
<b>👤 Профиль:
💎 Юзер: @{user_name}
🆔 ID: <code>{user_id}</code>
💰 Баланс: <code>{balance}{cur}</code>
💵 Всего пополнено: <code>{tr}{cur}</code>
📌 Дата регистрации: <code>{reg_date}</code>
👥 Рефералов: <code>{ref_count} чел</code></b>
"""
        await message.answer(msg, reply_markup=await profile_adm_inl(user_id))


@dp.callback_query_handler(IsAdmin(), text="find:receipt", state="*")
async def find_receipt(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text("<b>❗ Введите чек</b>", reply_markup=find_back())
    await AdminFind.here_receipt.set()


@dp.message_handler(state=AdminFind.here_receipt)
async def find_receipt_op(message: Message, state: FSMContext):
    if (
        await db.get_refill(receipt=message.text) is not None
        and await db.get_purchase(receipt=message.text) is None
    ):
        await state.finish()

        refill = await db.get_refill(receipt=message.text)
        settings = await db.get_settings()
        if settings["currency"] == "rub":
            summ = refill["amount"]
        elif settings["currency"] == "usd":
            summ = await get_exchange(refill["amount"], "RUB", "USD")
        elif settings["currency"] == "eur":
            summ = await get_exchange(refill["amount"], "RUB", "EUR")
        cur = currencies[settings["currency"]]["sign"]
        msg = f"""
<b>⭐ Чек <code>{message.text}</code>:

⚙️ Тип: <code>Пополнение</code>
💎 Юзер: @{refill['user_name']} | <a href='tg://user?id={refill['user_id']}'>{refill['user_full_name']}</a> | <code>{refill['user_id']}</code>
📌 Способ: <code>{refill['way']}</code>
💰 Сумма: <code>{summ}{cur}</code>
🎲 Дата: <code>{refill['date']}</code></b>
        """

        await message.answer(msg)

    elif (
        await db.get_refill(receipt=message.text) is None
        and await db.get_purchase(receipt=message.text) is not None
    ):
        await state.finish()

        purchase = await db.get_purchase(receipt=message.text)
        pos = await db.get_position(purchase["position_id"])
        settings = await db.get_settings()
        if settings["currency"] == "rub":
            summ = purchase["price_rub"]
        elif settings["currency"] == "usd":
            summ = purchase["price_dollar"]
        elif settings["currency"] == "eur":
            summ = purchase["price_euro"]
        cur = currencies[settings["currency"]]["sign"]
        if pos["type"] == "text":
            msg = f"""
<b>⭐ Чек <code>{message.text}</code>:

⚙️ Тип: <code>Покупка</code>
💎 Юзер: @{purchase['user_name']} | <a href='tg://user?id={purchase['user_id']}'>{purchase['user_full_name']}</a> | <code>{purchase['user_id']}</code>
📌 Позиция: <code>{purchase['position_name']}</code>
💰 Цена: <code>{summ}{cur}</code>
💚 Кол-во: <code>{purchase['count']} Шт.</code>
🎲 Дата: <code>{purchase['date']}</code>
🛍️ Сам товар:</b>

{purchase['item']}"""
            await message.answer(msg)
        else:
            msg = f"""
<b>⭐ Чек <code>{message.text}</code>:

⚙️ Тип: <code>Покупка</code>
💎 Юзер: @{purchase['user_name']} | <a href='tg://user?id={purchase['user_id']}'>{purchase['user_full_name']}</a> | <code>{purchase['user_id']}</code>
📌 Позиция: <code>{purchase['position_name']}</code>
💰 Цена: <code>{summ}{cur}</code>
💚 Кол-во: <code>{purchase['count']} Шт.</code>
🎲 Дата: <code>{purchase['date']}</code>
🛍️ Сам товар:</b>"""
            await message.answer(msg)
            files_ids = purchase["item"].replace("\n", "").split(",")
            for file_id in files_ids:
                if pos["type"] == "photo":
                    await message.answer_photo(photo=file_id.split(":")[1])
                elif pos["type"] == "file":
                    await message.answer_document(document=file_id.split(":")[1])
                await asyncio.sleep(0.3)

    elif (
        await db.get_refill(receipt=message.text) is None
        and await db.get_purchase(receipt=message.text) is None
    ):
        await message.answer("<b>❗ Такого чека нет! Перепроверьте данные!</b>")


@dp.callback_query_handler(IsAdmin(), text_startswith="faq:edit", state="*")
async def settings_set_faq(call: CallbackQuery):
    await AdminSettingsEdit.here_faq.set()
    await call.message.edit_text(
        "<b>⚙️ Введите новый текст для FAQ \n"
        "❕ Вы можете использовать Telegram разметку:</b> \n"
        "❕ Отправьте <code>-</code> чтобы оставить пустым.",
        reply_markup=set_back(),
    )


@dp.callback_query_handler(IsAdmin(), text_startswith="ref_percent:edit:", state="*")
async def settings_set_faq(call: CallbackQuery, state: FSMContext):
    await state.update_data(cache_ref_lvl_to_edit_percent=call.data.split(":")[2])
    await AdminSettingsEdit.here_ref_percent.set()
    await call.message.edit_text(
        f"<b>⚙️ Введите новый процент для {call.data.split(':')[2]} реферального уровня:</b>",
        reply_markup=set_back(),
    )


@dp.callback_query_handler(IsAdmin(), text_startswith="sup:edit", state="*")
async def settings_set_sup(call: CallbackQuery):
    await AdminSettingsEdit.here_support.set()
    await call.message.edit_text(
        "<b>⚙️ Введите ссылку на пользователя (https://t.me/юзернейм)</b>"
        "❕ Отправьте <code>-</code> чтобы оставить пустым.",
        reply_markup=set_back(),
    )


@dp.callback_query_handler(IsAdmin(), text_startswith="chat:edit", state="*")
async def settings_set_chat(call: CallbackQuery):
    await AdminSettingsEdit.here_chat.set()
    await call.message.edit_text(
        "<b>⚙️ Отправьте ссылку на чат:</b>"
        "❕ Отправьте <code>-</code> чтобы оставить пустым.",
        reply_markup=set_back(),
    )


@dp.callback_query_handler(IsAdmin(), text_startswith="news:edit", state="*")
async def settings_set_news(call: CallbackQuery):
    await AdminSettingsEdit.here_news.set()
    await call.message.edit_text(
        "<b>⚙️ Отправьте ссылку на канал:</b>"
        "❕ Отправьте <code>-</code> чтобы оставить пустым.",
        reply_markup=set_back(),
    )


@dp.callback_query_handler(IsAdmin(), text_startswith="refills:on_off", state="*")
async def settings_vkl_refill(call: CallbackQuery, state: FSMContext):
    await state.finish()
    s = await db.get_settings()
    status_refill = s["is_refill"]

    if status_refill == "True":
        await db.update_settings(is_refill="False")
    if status_refill == "False":
        await db.update_settings(is_refill="True")

    msg = "<b>⚙️ Выберите что хотите выключить/включить \n❌ - Выкл. | ✅ - Вкл.</b>"
    kb = await on_off_inl()

    await call.message.edit_text(msg, reply_markup=kb)


@dp.callback_query_handler(IsAdmin(), text_startswith="work:on_off", state="*")
async def settings_vkl_work(call: CallbackQuery, state: FSMContext):
    await state.finish()
    s = await db.get_settings()
    status_work = s["is_work"]

    if status_work == "True":
        await db.update_settings(is_work="False")
    if status_work == "False":
        await db.update_settings(is_work="True")

    msg = "<b>⚙️ Выберите что хотите выключить/включить \n❌ - Выкл. | ✅ - Вкл.</b>"
    kb = await on_off_inl()

    await call.message.edit_text(msg, reply_markup=kb)


@dp.callback_query_handler(IsAdmin(), text_startswith="contests:on_off", state="*")
async def settings_vkl_work(call: CallbackQuery, state: FSMContext):
    await state.finish()
    s = await db.get_settings()
    status_contests = s["contests_is_on"]

    if status_contests == "True":
        await db.update_settings(contests_is_on="False")
    if status_contests == "False":
        await db.update_settings(contests_is_on="True")

    msg = "<b>⚙️ Выберите что хотите выключить/включить \n❌ - Выкл. | ✅ - Вкл.</b>"
    kb = await on_off_inl()

    await call.message.edit_text(msg, reply_markup=kb)


@dp.callback_query_handler(IsAdmin(), text_startswith="multi_lang:on_off", state="*")
async def settings_vkl_work(call: CallbackQuery, state: FSMContext):
    await state.finish()
    s = await db.get_settings()
    multi_lang = s["multi_lang"]

    if multi_lang == "True":
        await db.update_settings(multi_lang="False")
    if multi_lang == "False":
        await db.update_settings(multi_lang="True")

    msg = "<b>⚙️ Выберите что хотите выключить/включить \n❌ - Выкл. | ✅ - Вкл.</b>"
    kb = await on_off_inl()

    await call.message.edit_text(msg, reply_markup=kb)


@dp.callback_query_handler(IsAdmin(), text="default_lang:edit", state="*")
async def default_language_edit(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(
        "<b>❗ Выберите новый язык по умолчанию:</b>",
        reply_markup=await choose_languages_kb_adm(),
    )


@dp.callback_query_handler(
    IsAdmin(), text_startswith="edit_default_language:", state="*"
)
async def edit_default_language_(call: CallbackQuery, state: FSMContext):
    await state.finish()
    lang_name = call.data.split(":")[1]
    lang = await db.get_language(name=lang_name)

    await db.update_settings(default_lang=lang["language"])
    await call.message.edit_text(
        "<b>⚙️ Основные настройки бота.</b>", reply_markup=await settings_inl()
    )


@dp.callback_query_handler(IsAdmin(), text_startswith="ref:on_off", state="*")
async def settings_vkl_work(call: CallbackQuery, state: FSMContext):
    await state.finish()
    s = await db.get_settings()
    status_ref = s["is_ref"]

    if status_ref == "True":
        await db.update_settings(is_ref="False")
    if status_ref == "False":
        await db.update_settings(is_ref="True")

    msg = "<b>⚙️ Выберите что хотите выключить/включить \n❌ - Выкл. | ✅ - Вкл.</b>"
    kb = await on_off_inl()

    await call.message.edit_text(msg, reply_markup=kb)


@dp.callback_query_handler(IsAdmin(), text_startswith="keyboard:on_off", state="*")
async def settings_vkl_work(call: CallbackQuery, state: FSMContext):
    await state.finish()
    s = await db.get_settings()
    status_ref = s["keyboard"]

    if status_ref == "Inline":
        await db.update_settings(keyboard="Reply")
    if status_ref == "Reply":
        await db.update_settings(keyboard="Inline")

    msg = "<b>⚙️ Выберите что хотите выключить/включить \n❌ - Выкл. | ✅ - Вкл.</b>"
    kb = await on_off_inl()

    await call.message.edit_text(msg, reply_markup=kb)


@dp.callback_query_handler(IsAdmin(), text_startswith="notify:on_off", state="*")
async def settings_vkl_work(call: CallbackQuery, state: FSMContext):
    await state.finish()
    s = await db.get_settings()
    is_notify = s["is_notify"]

    if is_notify == "True":
        await db.update_settings(is_notify="False")
    if is_notify == "False":
        await db.update_settings(is_notify="True")

    msg = "<b>⚙️ Выберите что хотите выключить/включить \n❌ - Выкл. | ✅ - Вкл.</b>"
    kb = await on_off_inl()

    await call.message.edit_text(msg, reply_markup=kb)


@dp.callback_query_handler(IsAdmin(), text_startswith="sub:on_off", state="*")
async def settings_vkl_work(call: CallbackQuery, state: FSMContext):
    await state.finish()
    s = await db.get_settings()
    is_sub = s["is_sub"]

    if is_sub == "True":
        await db.update_settings(is_sub="False")
    if is_sub == "False":
        await db.update_settings(is_sub="True")

    msg = "<b>⚙️ Выберите что хотите выключить/включить \n❌ - Выкл. | ✅ - Вкл.</b>"
    kb = await on_off_inl()

    await call.message.edit_text(msg, reply_markup=kb)


@dp.callback_query_handler(IsAdmin(), text_startswith="buys:on_off", state="*")
async def settings_vkl_buys(call: CallbackQuery, state: FSMContext):
    await state.finish()
    s = await db.get_settings()
    status_buy = s["is_buy"]

    if status_buy == "True":
        await db.update_settings(is_buy="False")
    if status_buy == "False":
        await db.update_settings(is_buy="True")

    msg = "<b>⚙️ Выберите что хотите выключить/включить \n❌ - Выкл. | ✅ - Вкл.</b>"
    kb = await on_off_inl()

    await call.message.edit_text(msg, reply_markup=kb)


@dp.message_handler(IsAdmin(), state=AdminSettingsEdit.here_faq)
@dp.message_handler(IsAdmin(), text="-", state=AdminSettingsEdit.here_faq)
async def settings_faq_set(message: Message, state: FSMContext):
    await state.finish()

    await db.update_settings(faq=message.parse_entities(as_html=True))
    await send_admins(
        f"<b>❗ Администратор  @{message.from_user.username} Изменил FAQ на: \n{message.parse_entities(as_html=True)}</b>",
        True,
    )
    await message.answer("<b>✅ Готово! FAQ Было изменено!</b>")


@dp.message_handler(IsAdmin(), state=AdminSettingsEdit.here_ref_percent)
async def settings_ref_per_set(message: Message, state: FSMContext):
    async with state.proxy() as data:
        lvl = data["cache_ref_lvl_to_edit_percent"]

    await state.finish()

    if not message.text.isdigit():
        return await message.answer("<b>❌ Введите число!</b>")

    if lvl == "1":
        await db.update_settings(ref_percent_1=int(message.text))
    elif lvl == "2":
        await db.update_settings(ref_percent_2=int(message.text))
    elif lvl == "3":
        await db.update_settings(ref_percent_3=int(message.text))

    await send_admins(
        f"<b>❗ Администратор  @{message.from_user.username} изменил процент для {lvl} реферального уровня на: \n{message.text}</b>",
        True,
    )
    await message.answer(
        f"<b>✅ Готово! Процент для {lvl} реферального уровня изменен!</b>"
    )


@dp.message_handler(IsAdmin(), state=AdminSettingsEdit.here_support)
@dp.message_handler(IsAdmin(), text="-", state=AdminSettingsEdit.here_support)
async def settings_sup_set(message: Message, state: FSMContext):
    await state.finish()

    if message.text.startswith("https://t.me/") or message.text == "-":
        await db.update_settings(support=message.text)
        await send_admins(
            f"<b>❗ Администратор  @{message.from_user.username} изменил Тех. Поддержку на: \n{message.text}</b>",
            True,
        )
        await message.answer("<b>✅ Готово! Тех. Поддержка была изменена!</b>")
    else:
        await message.answer("<b>❌ Введите ссылку! (https://t.me/юзернейм)</b> ")


@dp.message_handler(IsAdmin(), state=AdminSettingsEdit.here_chat)
@dp.message_handler(IsAdmin(), text="-", state=AdminSettingsEdit.here_chat)
async def settings_chat_set(message: Message, state: FSMContext):
    await state.finish()

    if message.text.startswith("https://t.me/") or message.text == "-":
        await db.update_settings(chat=message.text)
        await send_admins(
            f"<b>❗ Администратор  @{message.from_user.username} изменил Чат на: \n{message.text}</b>",
            True,
        )
        await message.answer("<b>✅ Готово! Чат был изменен!</b>")
    else:
        await message.answer("<b>❌ Введите ссылку! (https://t.me/название_чата)</b>")


@dp.message_handler(IsAdmin(), state=AdminSettingsEdit.here_news)
@dp.message_handler(IsAdmin(), text="-", state=AdminSettingsEdit.here_news)
async def settings_news_set(message: Message, state: FSMContext):
    await state.finish()

    if message.text.startswith("https://t.me/") or message.text == "-":
        await db.update_settings(news=message.text)
        await send_admins(
            f"<b>❗ Администратор  @{message.from_user.username} изменил Новостной канал на: \n{message.text}</b>",
            True,
        )
        await message.answer("<b>✅ Готово! Новостной канал был изменен!</b>")
    else:
        await message.answer("<b>❌ Введите ссылку! (https://t.me/название_канала)</b>")


@dp.callback_query_handler(IsAdmin(), text="stats")
async def stats_open(call: CallbackQuery, state: FSMContext):
    await state.finish()

    show_refill_amount_all, show_refill_amount_day, show_refill_amount_week = 0, 0, 0
    show_refill_count_all, show_refill_count_day, show_refill_count_week = 0, 0, 0
    show_profit_amount_all, show_profit_amount_day, show_profit_amount_week = 0, 0, 0
    show_profit_count_all, show_profit_count_day, show_profit_count_week = 0, 0, 0
    show_users_all, show_users_day, show_users_week, show_users_money = 0, 0, 0, 0

    get_purchases = await db.all_purchases()
    get_refill = await db.all_refills()
    get_users = await db.all_users()
    s = await db.get_settings()
    cur = currencies[s["currency"]]["sign"]
    for purchase in get_purchases:
        if s["currency"] == "rub":
            purchase_price = purchase["price_rub"]
        elif s["currency"] == "usd":
            purchase_price = purchase["price_dollar"]
        elif s["currency"] == "eur":
            purchase_price = purchase["price_euro"]
        show_profit_amount_all += purchase_price
        show_profit_count_all += purchase["count"]

        if purchase["unix"] - s["profit_day"] >= 0:
            show_profit_amount_day += purchase_price
            show_profit_count_day += purchase["count"]
        if purchase["unix"] - s["profit_week"] >= 0:
            show_profit_amount_week += purchase_price
            show_profit_count_week += purchase["count"]

    for refill in get_refill:
        if s["currency"] == "rub":
            refill_amount = refill["amount"]
        elif s["currency"] == "usd":
            refill_amount = refill["amount"]
        elif s["currency"] == "eur":
            refill_amount = refill["amount"]
        show_refill_amount_all += refill_amount
        show_refill_count_all += 1

        if refill["date_unix"] - s["profit_day"] >= 0:
            show_refill_amount_day += refill_amount
            show_refill_count_day += 1
        if refill["date_unix"] - s["profit_week"] >= 0:
            show_refill_amount_week += refill_amount
            show_refill_count_week += 1

    for user in get_users:
        if s["currency"] == "rub":
            user_balance = user["balance_rub"]
        elif s["currency"] == "usd":
            user_balance = user["balance_dollar"]
        elif s["currency"] == "eur":
            user_balance = user["balance_euro"]
        show_users_money += user_balance
        show_users_all += 1

        if user["reg_date_unix"] - s["profit_day"] >= 0:
            show_users_day += 1
        if user["reg_date_unix"] - s["profit_week"] >= 0:
            show_users_week += 1

    msg = f"""
<b>📊 Статистика:</b>


<b>👤 Юзеры:</b>

👤 За День: <code>{show_users_day}</code>
👤 За Неделю: <code>{show_users_week}</code>
👤 За Всё время: <code>{show_users_all}</code>

👤 Сумма балансов всех юзеров: <code>{round(show_users_money, 2)}{cur}</code>

<b>💸 Продажи:</b>

💸 За День: <code>{show_profit_count_day}шт</code> (<code>{round(show_profit_amount_day, 2)}{cur}</code>)
💸 За Неделю: <code>{show_profit_count_week}шт</code> (<code>{round(show_profit_amount_week, 2)}{cur}</code>)
💸 За Всё время: <code>{show_profit_count_all}шт</code> (<code>{round(show_profit_amount_all, 2)}{cur}</code>)

<b>💰 Пополнения:</b>

💰 Пополнений за День: <code>{show_refill_count_day}шт</code> (<code>{round(show_refill_amount_day, 2)}{cur}</code>)
💰 Пополнений за Неделю: <code>{show_refill_count_week}шт</code> (<code>{round(show_refill_amount_week, 2)}{cur}</code>)
💰 Пополнений за Всё время: <code>{show_refill_count_all}шт</code> (<code>{round(show_refill_amount_all, 2)}{cur}</code>)

<b>⚙️ Админы: </b>

⚙️ Всего админов: <code>{len(get_admins())} чел</code>
⚙️ Админы: \n
"""
    for admin in get_admins():
        user = await db.get_user(id=admin)
        msg += f"@{user['user_name']}\n "

    await call.message.edit_text(msg, reply_markup=stats_inl())


@dp.callback_query_handler(text="get_users_and_balances", state="*")
async def get_users_and_balances(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await get_users_and_their_balances_in_file(call)


@dp.callback_query_handler(text="pr_buttons", state="*")
async def pr_buttons(c: CallbackQuery, state: FSMContext):
    await state.finish()

    await c.message.edit_text(
        f"<b>❗ Выберите действие:</b>", reply_markup=pr_buttons_inl()
    )


@dp.callback_query_handler(text_startswith="pr_button:", state="*")
async def pr_buttons2(c: CallbackQuery, state: FSMContext):
    await state.finish()
    if c.data.split(":")[1] == "create":
        await c.message.edit_text(
            f"<b>❗ Введите название кнопки:</b>", reply_markup=pr_buttons_back()
        )
        await AdminPrButtons.here_name_pr_button_create.set()
    elif c.data.split(":")[1] == "delete":
        await c.message.edit_text(
            f"<b>❗ Введите название кнопки:</b>", reply_markup=pr_buttons_back()
        )
        await AdminPrButtons.here_name_pr_button_delete.set()


@dp.message_handler(state=AdminPrButtons.here_name_pr_button_create)
async def pr_buttons3(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        data["name_pr_button_create"] = msg.text

    await msg.reply(
        "<b>❗ Теперь введи текст кнопки: \n❗Можно использовать Telegram Разметку</b> "
    )
    await AdminPrButtons.here_txt_pr_button_create.set()


@dp.message_handler(state=AdminPrButtons.here_txt_pr_button_create)
async def pr_buttons4(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        data["txt_pr_button_create"] = msg.parse_entities(as_html=True)
    await msg.reply(
        "<b>❗ Теперь отправь фото кнопки: \n"
        "❗ Если не хотите, чтоб было фото, отправьте <code>-</code></b>"
    )
    await AdminPrButtons.here_photo_pr_button_create.set()


@dp.message_handler(
    state=AdminPrButtons.here_photo_pr_button_create, content_types=["photo"]
)
@dp.message_handler(state=AdminPrButtons.here_photo_pr_button_create, text="-")
async def pr_buttons5(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        name = data["name_pr_button_create"]
        txt = data["txt_pr_button_create"]
    await state.finish()
    try:
        photo = msg.photo[-1].file_id
    except:
        photo = msg.text

    await db.create_pr_button(name, txt, photo)
    await msg.reply("<b>✅ Кнопка успешно создана!</b>")


@dp.message_handler(state=AdminPrButtons.here_name_pr_button_delete)
async def pr_buttons6(msg: Message, state: FSMContext):
    await state.finish()
    try:
        await db.delete_pr_button(msg.text)
        await msg.reply("<b>✅ Кнопка успешно удалена!</b>")
    except Exception as err:
        await msg.reply(f"<b>❗ Произошла ошибка при удалении кнопки: {err}</b>")


@dp.callback_query_handler(text="extra_settings", state="*")
async def extra_settings(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(
        f"<b>❗ Выберите действие:</b>", reply_markup=extra_settings_inl()
    )


@dp.callback_query_handler(text="promo_create", state="*")
async def promo_create(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(
        f"<b>❗ Введите название промокода</b>", reply_markup=extra_back()
    )
    await AdminCoupons.here_name_promo.set()


@dp.message_handler(state=AdminCoupons.here_name_promo)
async def here_name_promo(msg: Message, state: FSMContext):
    name = msg.text

    await msg.answer(f"<b>❗ Введите кол-во использований</b>")
    await state.update_data(cache_name_for_add_promo=name)
    await AdminCoupons.here_uses_promo.set()


@dp.message_handler(state=AdminCoupons.here_uses_promo)
async def here_uses_promo(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        await msg.answer(
            "<b>❗ Введите скидку в рублях / если доллары в долларах! (Они зачисляться после ввода промокода)</b>"
        )
        await state.update_data(cache_uses_for_add_promo=int(msg.text))
        await AdminCoupons.here_discount_promo.set()
    else:
        await msg.answer("<b>❗ Кол-во использований должно быть числом!</b>")


@dp.message_handler(state=AdminCoupons.here_discount_promo)
async def here_discount_promo(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        async with state.proxy() as data:
            name = data["cache_name_for_add_promo"]
            uses = data["cache_uses_for_add_promo"]
        await state.finish()
        s = await db.get_settings()
        if s["currency"] == "rub":
            discount_rub = int(msg.text)
            discount_dollar = await get_exchange(discount_rub, "RUB", "USD")
            discount_euro = await get_exchange(discount_rub, "RUB", "EUR")
        elif s["currency"] == "usd":
            discount_dollar = int(msg.text)
            discount_rub = await get_exchange(discount_dollar, "USD", "RUB")
            discount_euro = await get_exchange(discount_dollar, "USD", "EUR")
        elif s["currency"] == "eur":
            discount_euro = int(msg.text)
            discount_dollar = await get_exchange(discount_euro, "EUR", "USD")
            discount_rub = await get_exchange(discount_euro, "EUR", "RUB")

        await db.create_coupon(name, uses, discount_rub, discount_dollar, discount_euro)
        await msg.answer(
            f"<b>✅ Промокод <code>{name}</code> с кол-вом использований <code>{uses}</code> и скидкой <code>{int(msg.text)}{currencies[s['currency']]['sign']}</code> был создан!</b>"
        )
        await send_admins(
            f"<b>❗ Администратор  @{msg.from_user.username} создал Промокод <code>{name}</code> с кол-вом использований <code>{uses}</code> и скидкой <code>{int(msg.text)}{currencies[s['currency']]['sign']}</code></b>",
            True,
        )
    else:
        await msg.answer("<b>❗ Скидка должна быть числом!</b>")


@dp.callback_query_handler(text="promo_delete", state="*")
async def promo_create(call: CallbackQuery, state: FSMContext):
    await state.finish()

    await call.message.edit_text(
        f"<b>❗ Введите название промокода</b>", reply_markup=extra_back()
    )
    await AdminCoupons.here_name_for_delete_promo.set()


@dp.message_handler(state=AdminCoupons.here_name_for_delete_promo)
async def promo_delete(msg: Message, state: FSMContext):
    try:
        await db.delete_coupon(msg.text)
        await state.finish()
        await msg.answer(f"<b>✅ Промокод <code>{msg.text}</code> был удален</b>")
        await send_admins(
            f"<b>❗ Администратор  @{msg.from_user.username} удалил Промокод <code>{msg.text}</code></b>",
            True,
        )
    except:
        await msg.answer(f"<b>❌ Промокода <code>{msg.text}</code> не существует!</b>")


@dp.callback_query_handler(text_startswith="ref_lvl_edit:", state="*")
async def ref_lvl_edit(call: CallbackQuery, state: FSMContext):
    await state.finish()

    lvl = call.data.split(":")[1]

    await call.message.edit_text(
        f"<b>❗ Введите кол-во рефералов для {lvl} уровня</b>",
        reply_markup=extra_back(),
    )
    await state.update_data(cache_lvl_for_edit_lvls=lvl)
    await AdminSettingsEdit.here_count_lvl_ref.set()


@dp.message_handler(state=AdminSettingsEdit.here_count_lvl_ref)
async def here_count_lvl_ref(msg: Message, state: FSMContext):
    if msg.text.isdigit():
        async with state.proxy() as data:
            lvl = data["cache_lvl_for_edit_lvls"]
        count = int(msg.text)

        if lvl == "1":
            await db.update_settings(ref_lvl_1=count)
        elif lvl == "2":
            await db.update_settings(ref_lvl_2=count)
        else:
            await db.update_settings(ref_lvl_3=count)

        await msg.answer(
            f"<b>✅ Вы изменили кол-во рефералов для <code>{lvl}</code> уровня на <code>{count} чел</code></b>"
        )
        await send_admins(
            f"<b>❗ Администратор  @{msg.from_user.username} изменил кол-во рефералов для <code>{lvl}</code> уровня на <code>{count} чел</code></b>",
            True,
        )


@dp.callback_query_handler(text_startswith="user:", state="*")
async def user_balance_add(call: CallbackQuery, state: FSMContext):
    await state.finish()

    action = call.data.split(":")[1]
    user_id = call.data.split(":")[2]
    user = await db.get_user(id=user_id)

    if action == "balance_add":
        await call.message.edit_text(f"<b>💰 Введите сумму, которую хотите выдать:</b>")
        await state.update_data(cache_user_id_for_bal_add=user_id)
        await AdminEditUser.here_amount_to_add.set()
    elif action == "balance_edit":
        await call.message.edit_text(
            f"<b>💰 Введите сумму, на которую хотите изменить:</b>"
        )
        await AdminEditUser.here_amount_to_edit.set()
        await state.update_data(cache_user_id_for_bal_edit=user_id)
    elif action == "is_ban_ban":
        await db.update_user(id=user_id, is_ban="True")
        await call.message.edit_text(
            f"<b>✅ Вы забанили пользователя @{user['user_name']}</b>"
        )
        user_name = user["user_name"]
        user_id = user["id"]
        total_refill = user["total_refill"]
        reg_date = user["reg_date"]
        ref_count = user["ref_count"]
        s = await db.get_settings()
        if s["currency"] == "rub":
            balance = user["balance_rub"]
            tr = total_refill
        elif s["currency"] == "usd":
            balance = user["balance_dollar"]
            tr = await get_exchange(total_refill, "RUB", "USD")
        elif s["currency"] == "eur":
            balance = user["balance_euro"]
            tr = await get_exchange(total_refill, "RUB", "EUR")
        cur = currencies[s["currency"]]["sign"]

        msgg = f"""
<b>👤 Профиль:
💎 Юзер: @{user_name}
🆔 ID: <code>{user_id}</code>
💰 Баланс: <code>{balance}{cur}</code>
💵 Всего пополнено: <code>{tr}{cur}</code>
📌 Дата регистрации: <code>{reg_date}</code>
👥 Рефералов: <code>{ref_count} чел</code></b>"""

        await call.message.answer(msgg, reply_markup=await profile_adm_inl(user_id))
    elif action == "is_ban_unban":
        await db.update_user(id=user_id, is_ban="False")
        await call.message.edit_text(
            f"<b>✅ Вы разбанили пользователя @{user['user_name']}</b>"
        )
        user_name = user["user_name"]
        user_id = user["id"]
        total_refill = user["total_refill"]
        reg_date = user["reg_date"]
        ref_count = user["ref_count"]
        s = await db.get_settings()
        if s["currency"] == "rub":
            balance = user["balance_rub"]
            tr = total_refill
        elif s["currency"] == "usd":
            balance = user["balance_dollar"]
            tr = await get_exchange(total_refill, "RUB", "USD")
        elif s["currency"] == "eur":
            balance = user["balance_euro"]
            tr = await get_exchange(total_refill, "RUB", "EUR")
        cur = currencies[s["currency"]]["sign"]
        msgg = f"""
<b>👤 Профиль:
💎 Юзер: @{user_name}
🆔 ID: <code>{user_id}</code>
💰 Баланс: <code>{balance}{cur}</code>
💵 Всего пополнено: <code>{tr}{cur}</code>
📌 Дата регистрации: <code>{reg_date}</code>
👥 Рефералов: <code>{ref_count} чел</code></b>"""

        await call.message.answer(msgg, reply_markup=await profile_adm_inl(user_id))
    elif action == "sms":
        await call.message.edit_text(
            f"<b>❗ Введите сообщение, которое хотите отправить пользователю</b>"
        )
        await state.update_data(cache_user_id_for_send_msg=user_id)
        await AdminEditUser.here_msg_to_send.set()


@dp.message_handler(state=AdminEditUser.here_amount_to_add)
async def here_amount_to_add(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        user_id = data["cache_user_id_for_bal_add"]

    s = await db.get_settings()

    if msg.text.isdigit() or msg.text.replace(".", "", 1).isdigit():
        await state.finish()
        user = await db.get_user(id=user_id)
        await bot.send_message(
            chat_id=user_id,
            text=f"<b>💰 Администратор выдал вам <code>{msg.text}{currencies[s['currency']]['sign']}</code></b>",
        )
        user_name = user["user_name"]
        user_id = user["id"]
        total_refill = user["total_refill"]
        reg_date = user["reg_date"]
        ref_count = user["ref_count"]

        balance, tr = 0, 0
        if s["currency"] == "rub":
            price_rub = float(user["balance_rub"]) + float(msg.text)
            price_euro = float(user["balance_euro"]) + await get_exchange(
                float(msg.text), "RUB", "EUR"
            )
            price_dollar = float(user["balance_dollar"]) + await get_exchange(
                float(msg.text), "RUB", "USD"
            )
            balance = price_rub
            await db.update_user(
                id=user_id,
                balance_rub=price_rub,
                balance_dollar=price_dollar,
                balance_euro=price_euro,
            )
            tr = total_refill
        elif s["currency"] == "usd":
            price_dollar = float(user["balance_dollar"]) + float(msg.text)
            price_euro = float(user["balance_euro"]) + await get_exchange(
                float(msg.text), "USD", "EUR"
            )
            price_rub = float(user["balance_rub"]) + await get_exchange(
                float(msg.text), "USD", "RUB"
            )
            balance = price_dollar
            await db.update_user(
                id=user_id,
                balance_rub=price_rub,
                balance_dollar=price_dollar,
                balance_euro=price_euro,
            )
            tr = await get_exchange(total_refill, "RUB", "USD")
        elif s["currency"] == "eur":
            price_euro = float(user["balance_euro"]) + float(msg.text)
            price_dollar = float(user["balance_dollar"]) + await get_exchange(
                float(msg.text), "EUR", "USD"
            )
            price_rub = float(user["balance_rub"]) + await get_exchange(
                float(msg.text), "EUR", "RUB"
            )
            balance = price_euro
            await db.update_user(
                id=user_id,
                balance_rub=price_rub,
                balance_dollar=price_dollar,
                balance_euro=price_euro,
            )
            tr = await get_exchange(total_refill, "RUB", "EUR")
        await asyncio.sleep(1)

        curr = currencies[s["currency"]]["sign"]

        msgg = f"""
<b>👤 Профиль:
💎 Юзер: @{user_name}
🆔 ID: <code>{user_id}</code>
💰 Баланс: <code>{balance}{curr}</code>
💵 Всего пополнено: <code>{tr}{curr}</code>
📌 Дата регистрации: <code>{reg_date}</code>
👥 Рефералов: <code>{ref_count} чел</code></b>"""

        await msg.answer(msgg, reply_markup=await profile_adm_inl(user_id))
    else:
        await msg.answer("<b>❗ Сумма должна быть числом!</b>")


@dp.message_handler(state=AdminEditUser.here_amount_to_edit)
async def here_amount_to_add(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        user_id = data["cache_user_id_for_bal_edit"]
    s = await db.get_settings()
    if msg.text.isdigit() or msg.text.replace(".", "", 1).isdigit():
        await state.finish()
        user = await db.get_user(id=user_id)
        user_name = user["user_name"]
        user_id = user["id"]
        total_refill = user["total_refill"]
        reg_date = user["reg_date"]
        ref_count = user["ref_count"]
        price_rub, price_dollar, price_euro, tr = 0, 0, 0, 0

        if s["currency"] == "rub":
            price_rub = float(msg.text)
            price_euro = await get_exchange(price_rub, "RUB", "EUR")
            price_dollar = await get_exchange(price_rub, "RUB", "USD")
            tr = total_refill
        elif s["currency"] == "usd":
            price_dollar = float(msg.text)
            price_euro = await get_exchange(price_dollar, "USD", "EUR")
            price_rub = await get_exchange(price_dollar, "USD", "RUB")
            tr = await get_exchange(total_refill, "RUB", "USD")
        elif s["currency"] == "eur":
            price_euro = float(msg.text)
            price_dollar = await get_exchange(price_euro, "EUR", "USD")
            price_rub = await get_exchange(price_euro, "EUR", "RUB")
            tr = await get_exchange(total_refill, "RUB", "EUR")

        await db.update_user(
            id=user_id,
            balance_rub=price_rub,
            balance_dollar=price_dollar,
            balance_euro=price_euro,
        )
        await bot.send_message(
            chat_id=user_id,
            text=f"<b>💰 Администратор изменил вам баланс на <code>{msg.text}{currencies[s['currency']]['sign']}</code></b>",
        )

        cur = currencies[s["currency"]]["sign"]
        msgg = f"""
<b>👤 Профиль:
💎 Юзер: @{user_name}
🆔 ID: <code>{user_id}</code>
💰 Баланс: <code>{float(msg.text)}{cur}</code>
💵 Всего пополнено: <code>{tr}{cur}</code>
📌 Дата регистрации: <code>{reg_date}</code>
👥 Рефералов: <code>{ref_count} чел</code></b>"""

        await msg.answer(msgg, reply_markup=await profile_adm_inl(user_id))
    else:
        await msg.answer("<b>❗ Сумма должна быть числом!</b>")


@dp.message_handler(state=AdminEditUser.here_msg_to_send)
async def here_msg_to_send(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        user_id = data["cache_user_id_for_send_msg"]

    await state.finish()
    user = await db.get_user(id=user_id)
    await bot.send_message(
        chat_id=user_id,
        text=f"<b>⭐ Вам пришло сообщение от администратора: \n{msg.text}</b>",
    )
    await msg.answer(
        f"<b>⭐ Вы отправили сообщение пользователю @{user['user_name']}</b>"
    )
    user_name = user["user_name"]
    user_id = user["id"]
    total_refill = user["total_refill"]
    reg_date = user["reg_date"]
    ref_count = user["ref_count"]
    s = await db.get_settings()
    if s["currency"] == "rub":
        balance = user["balance_rub"]
        tr = total_refill
    elif s["currency"] == "usd":
        balance = user["balance_dollar"]
        tr = await get_exchange(total_refill, "RUB", "USD")
    elif s["currency"] == "eur":
        balance = user["balance_euro"]
        tr = await get_exchange(total_refill, "RUB", "EUR")
    cur = currencies[s["currency"]]["sign"]
    msgg = f"""
<b>👤 Профиль:
💎 Юзер: @{user_name}
🆔 ID: <code>{user_id}</code>
💰 Баланс: <code>{balance}{cur}</code>
💵 Всего пополнено: <code>{tr}{cur}</code>
📌 Дата регистрации: <code>{reg_date}</code>
👥 Рефералов: <code>{ref_count} чел</code></b>"""

    await msg.answer(msgg, reply_markup=await profile_adm_inl(user_id))


from tgbot.utils.json_utils import get_public_news_id


### EVELINE
@dp.callback_query_handler(text="change_news_channel")
async def start_change_news_channel(call: CallbackQuery, state: FSMContext):
    public_channel_id = get_public_news_id()
    user_id = call.from_user.id

    await bot.delete_message(user_id, call.message.message_id)
    msg = await bot.send_message(
        chat_id=user_id,
        text=f"Текущий канал для новостей: <code>{public_channel_id}</code>\n\nНапишите новый ID",
        reply_markup=pr_buttons_back(),
        parse_mode="HTML",
    )

    await state.update_data({"msg_id": msg.message_id})

    await ChangeNewsChannel.new_id.set()


@dp.message_handler(state=ChangeNewsChannel.new_id)
async def end_change_new_channel_id(msg: Message, state: FSMContext):
    new_id = msg.text
    user_id = msg.from_user.id
    data = await state.get_data()

    update_public_news_id(new_id)

    await bot.delete_message(user_id, msg.message_id)
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=data["msg_id"],
        text=f"Вы успешно установили новый id: <b>{new_id}</b>",
        parse_mode="HTML",
        reply_markup=admin_menu(),
    )

    await state.finish()
