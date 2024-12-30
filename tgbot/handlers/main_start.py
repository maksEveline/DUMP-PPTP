# - *- coding: utf- 8 - *-
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
import time
from datetime import datetime, timedelta
from tgbot.keyboards.inline_user import (
    open_products,
    refill_inl,
    sub,
    user_menu,
    back_to_profile,
    profile_inl,
    back_to_user_menu,
    chat_inl,
    news_inl,
    faq_inl,
    support_inll,
    contest_inl,
    choose_contest,
    choose_languages_kb,
)
from tgbot.keyboards.inline_admin import admin_menu
from tgbot.data.config import db, currencies, lang_ru, lang_ua, lang_en
from tgbot.data.loader import dp, bot
from tgbot.utils.other_functions import open_profile, convert_ref
from contextlib import suppress
from tgbot.filters.filters import (
    IsAdmin,
    IsBuy,
    IsBan,
    IsSub,
    IsRefill,
    IsWork,
    IsContestOn,
)
from aiogram.utils.exceptions import MessageCantBeDeleted
from tgbot.utils.utils_functions import (
    convert_words,
    get_channels,
    get_language,
    end_contest,
    send_admins,
)
from tgbot.states.users import UsersCoupons


@dp.callback_query_handler(IsBuy(), text="products:open", state="*")
async def is_buy(call: CallbackQuery, state: FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    await call.answer(texts.is_buy_text, True)


@dp.message_handler(IsBuy(), text=lang_ru.products, state="*")
@dp.message_handler(IsBuy(), text=lang_en.products, state="*")
@dp.message_handler(IsBuy(), text=lang_ua.products, state="*")
async def is_buys(msg: Message, state: FSMContext):
    await state.finish()
    texts = await get_language(msg.from_user.id)
    await msg.reply(texts.is_buy_text)


@dp.message_handler(IsContestOn(), text=lang_ru.contest, state="*")
@dp.message_handler(IsContestOn(), text=lang_en.contest, state="*")
@dp.message_handler(IsContestOn(), text=lang_ua.contest, state="*")
async def is_contests_on(msg: Message, state: FSMContext):
    await state.finish()
    texts = await get_language(msg.from_user.id)
    await msg.reply(texts.is_contests_text)


@dp.callback_query_handler(IsContestOn(), text_startswith="contest_view:", state="*")
@dp.callback_query_handler(IsContestOn(), text_startswith="contest_enter:", state="*")
@dp.callback_query_handler(IsContestOn(), text="contests", state="*")
async def is_contests_on_(call: CallbackQuery, state: FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    await call.answer(texts.is_contests_text, True)


@dp.message_handler(IsBan(), state="*")
async def is_ban(message: Message, state: FSMContext):
    await state.finish()
    texts = await get_language(message.from_user.id)
    await message.answer(texts.is_ban_text)


@dp.callback_query_handler(IsBan(), state="*")
async def is_ban(call: CallbackQuery, state: FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    await call.answer(texts.is_ban_text)


@dp.message_handler(IsWork(), state="*")
async def is_work(message: Message, state: FSMContext):
    await state.finish()
    texts = await get_language(message.from_user.id)
    await message.answer(texts.is_work_text)


@dp.callback_query_handler(IsWork(), state="*")
async def is_work(call: CallbackQuery, state: FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    await call.answer(texts.is_work_text)


@dp.callback_query_handler(IsRefill(), text="refill", state="*")
async def is_refill(call: CallbackQuery, state: FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    await call.answer(texts.is_refill_text, True)


@dp.message_handler(IsRefill(), text=lang_en.refill, state="*")
@dp.message_handler(IsRefill(), text=lang_ru.refill, state="*")
@dp.message_handler(IsRefill(), text=lang_ua.refill, state="*")
async def is_refill(msg: Message, state: FSMContext):
    await state.finish()
    texts = await get_language(msg.from_user.id)
    await msg.reply(texts.is_refill_text)


@dp.callback_query_handler(IsSub(), state="*")
async def is_subs(call: CallbackQuery, state: FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    await call.message.answer(texts.no_sub, reply_markup=sub())


@dp.message_handler(IsSub(), state="*")
async def is_subs(msg: Message, state: FSMContext):
    await state.finish()
    texts = await get_language(msg.from_user.id)
    await msg.answer(texts.no_sub, reply_markup=sub())


@dp.callback_query_handler(text=["subprov"])
async def sub_prov(call: CallbackQuery, state: FSMContext):
    await state.finish()
    if call.message.chat.type == "private":
        user = await db.get_user(id=call.from_user.id)
        lang = await get_language(call.from_user.id)
        kb = await user_menu(lang, call.from_user.id)
        if lang.start_photo == "":
            name = f"@{user['user_name']}"
            if user["user_name"] == "":
                us = await bot.get_chat(user["id"])
                name = us.get_mention(as_html=True)
            await call.message.answer(
                lang.start_text.format(user_name=name), reply_markup=kb
            )
        else:
            name = f"@{user['user_name']}"
            if user["user_name"] == "":
                us = await bot.get_chat(user["id"])
                name = us.get_mention(as_html=True)
            await bot.send_photo(
                chat_id=call.from_user.id,
                photo=lang.start_photo,
                caption=lang.start_text.format(user_name=name),
                reply_markup=kb,
            )


#####################################################################################
#####################################################################################
#####################################################################################


@dp.message_handler(commands=["start"], state="*")
async def main_start(message: Message, state: FSMContext):
    await state.finish()
    user = await db.get_user(id=message.from_user.id)
    lang = await get_language(message.from_user.id)
    print(lang)
    kb = await user_menu(lang, message.from_user.id)
    s = await db.get_settings()

    if s["is_ref"] == "True":
        if message.get_args() == "":
            if lang.start_photo == "":
                name = f"@{user['user_name']}"
                if user["user_name"] == "":
                    us = await bot.get_chat(user["id"])
                    name = us.get_mention(as_html=True)
                await message.answer(
                    lang.start_text.format(user_name=name), reply_markup=kb
                )
            else:
                name = f"@{user['user_name']}"
                if user["user_name"] == "":
                    us = await bot.get_chat(user["id"])
                    name = us.get_mention(as_html=True)
                await bot.send_photo(
                    chat_id=message.from_user.id,
                    photo=lang.start_photo,
                    caption=lang.start_text.format(user_name=name),
                    reply_markup=kb,
                )
        else:
            if await db.get_user(id=int(message.get_args())) is None:
                if lang.start_photo == "":
                    name = f"@{user['user_name']}"
                    if user["user_name"] == "":
                        us = await bot.get_chat(user["id"])
                        name = us.get_mention(as_html=True)
                    await message.answer(
                        lang.start_text.format(user_name=name), reply_markup=kb
                    )
                else:
                    name = f"@{user['user_name']}"
                    if user["user_name"] == "":
                        us = await bot.get_chat(user["id"])
                        name = us.get_mention(as_html=True)
                    await bot.send_photo(
                        chat_id=message.from_user.id,
                        photo=lang.start_photo,
                        caption=lang.start_text.format(user_name=name),
                        reply_markup=kb,
                    )
            else:
                if user["ref_id"] is not None:
                    await message.answer(lang.yes_reffer)
                else:
                    reffer = await db.get_user(id=int(message.get_args()))
                    if reffer["id"] == message.from_user.id:
                        await message.answer(lang.invite_yourself)
                    else:
                        user_ref_count = reffer.ref_count
                        msg = lang.new_refferal.format(
                            user_name=user["user_name"],
                            user_ref_count=user_ref_count + 1,
                            convert_ref=convert_ref(lang, user_ref_count + 1),
                        )

                        await db.update_user(
                            message.from_user.id,
                            ref_id=reffer["id"],
                            ref_user_name=reffer["user_name"],
                            ref_first_name=reffer["first_name"],
                        )
                        await db.update_user(reffer["id"], ref_count=user_ref_count + 1)

                        await bot.send_message(chat_id=reffer["id"], text=msg)

                        if reffer["ref_count"] + 1 == s["ref_lvl_1"]:
                            remain_refs = s["ref_lvl_2"] - (reffer["ref_count"] + 1)
                            text = lang.new_ref_lvl.format(
                                new_lvl=1,
                                next_lvl=2,
                                remain_refs=remain_refs,
                                convert_ref=convert_ref(lang, remain_refs),
                            )
                            await bot.send_message(chat_id=reffer["id"], text=text)
                            await db.update_user(reffer["id"], ref_lvl=1)
                        elif reffer["ref_count"] + 1 == s["ref_lvl_2"]:
                            remain_refs = s["ref_lvl_3"] - (reffer["ref_count"] + 1)
                            text = lang.new_ref_lvl.format(
                                new_lvl=2,
                                next_lvl=3,
                                remain_refs=remain_refs,
                                convert_ref=convert_ref(lang, remain_refs),
                            )
                            await bot.send_message(chat_id=reffer["id"], text=text)
                            await db.update_user(reffer["id"], ref_lvl=2)
                        elif reffer["ref_count"] + 1 == s["ref_lvl_3"]:
                            await bot.send_message(
                                chat_id=reffer["id"], text=lang.max_ref_lvl
                            )
                            await db.update_user(reffer["id"], ref_lvl=3)

                        if lang.start_photo == "":
                            name = f"@{user['user_name']}"
                            if user["user_name"] == "":
                                us = await bot.get_chat(user["id"])
                                name = us.get_mention(as_html=True)
                            await message.answer(
                                lang.start_text.format(user_name=name), reply_markup=kb
                            )
                        else:
                            name = f"@{user['user_name']}"
                            if user["user_name"] == "":
                                us = await bot.get_chat(user["id"])
                                name = us.get_mention(as_html=True)
                            await bot.send_photo(
                                chat_id=message.from_user.id,
                                photo=lang.start_photo,
                                caption=lang.start_text.format(user_name=name),
                                reply_markup=kb,
                            )
    else:
        if lang.start_photo == "":
            name = f"@{user['user_name']}"
            if user["user_name"] == "":
                us = await bot.get_chat(user["id"])
                name = us.get_mention(as_html=True)
            await message.answer(
                lang.start_text.format(user_name=name), reply_markup=kb
            )
        else:
            name = f"@{user['user_name']}"
            if user["user_name"] == "":
                us = await bot.get_chat(user["id"])
                name = us.get_mention(as_html=True)
            await bot.send_photo(
                chat_id=message.from_user.id,
                photo=lang.start_photo,
                caption=lang.start_text.format(user_name=name),
                reply_markup=kb,
            )


@dp.callback_query_handler(text="ref_system", state="*")
async def ref_systemm(call: CallbackQuery, state: FSMContext):
    await state.finish()
    s = await db.get_settings()
    status = s["is_ref"]
    bott = await bot.get_me()
    bot_name = bott.username
    ref_link = f"<code>https://t.me/{bot_name}?start={call.from_user.id}</code>"
    user = await db.get_user(id=call.from_user.id)
    texts = await get_language(call.from_user.id)
    ref_earn_rub = user["ref_earn_rub"]
    ref_earn_euro = user["ref_earn_euro"]
    ref_earn_dollar = user["ref_earn_dollar"]

    if s["currency"] == "rub":
        ref_earn = ref_earn_rub
    elif s["currency"] == "usd":
        ref_earn = ref_earn_dollar
    elif s["currency"] == "eur":
        ref_earn = ref_earn_euro

    ref_count = user["ref_count"]
    ref_lvl = user["ref_lvl"]
    if ref_lvl == 0:
        lvl = 1
        ref_percent = s["ref_percent_1"]
    if ref_lvl == 1:
        lvl = 2
        ref_percent = s["ref_percent_1"]
    elif ref_lvl == 2:
        lvl = 3
        ref_percent = s["ref_percent_2"]
    elif ref_lvl == 3:
        lvl = 3
        ref_percent = s["ref_percent_3"]

    remain_refs = s[f"ref_lvl_{lvl}"] - user["ref_count"]

    if ref_lvl == 3:
        mss = texts.cur_max_lvl
    else:
        mss = texts.next_lvl_remain.format(remain_refs=remain_refs)

    reffer_name = user["ref_first_name"]
    if reffer_name is None:
        reffer = texts.nobody
    else:
        reffer = f"<a href='tg://user?id={user['ref_id']}'>{reffer_name}</a>"

    curr = currencies[s["currency"]]["sign"]

    msg = texts.ref_text.format(
        ref_link=ref_link,
        ref_percent=ref_percent,
        reffer=reffer,
        ref_earn=ref_earn,
        curr=curr,
        convert_ref=convert_ref(texts, ref_count),
        ref_count=ref_count,
        ref_lvl=ref_lvl,
        mss=mss,
    )

    if status == "True":
        await call.message.delete()
        await call.message.answer(msg, reply_markup=back_to_profile(texts))
    else:
        await call.answer(texts.is_ref_text, True)


# Переключение языка
@dp.callback_query_handler(text="change_language", state="*")
async def change_language(call: CallbackQuery, state: FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    await call.message.delete()
    await call.message.answer(
        texts.choose_language, reply_markup=await choose_languages_kb()
    )


@dp.callback_query_handler(text_startswith="change_language:", state="*")
async def change_language_(call: CallbackQuery, state: FSMContext):
    await state.finish()
    lang_short_name = call.data.split(":")[1]

    await db.update_user(id=call.from_user.id, language=lang_short_name)
    await call.message.delete()
    texts = await get_language(call.from_user.id)
    user = await db.get_user(id=call.from_user.id)
    kb = await user_menu(texts, call.from_user.id)
    if texts.start_photo == "":
        name = f"@{user['user_name']}"
        if user["user_name"] == "":
            us = await bot.get_chat(user["id"])
            name = us.get_mention(as_html=True)
        await call.message.answer(
            texts.start_text.format(user_name=name), reply_markup=kb
        )
    else:
        name = f"@{user['user_name']}"
        if user["user_name"] == "":
            us = await bot.get_chat(user["id"])
            name = us.get_mention(as_html=True)
        await bot.send_photo(
            chat_id=call.from_user.id,
            photo=texts.start_photo,
            caption=texts.start_text.format(user_name=name),
            reply_markup=kb,
        )


# Просмотр истории покупок
@dp.callback_query_handler(text="last_purchases", state="*")
async def user_history(call: CallbackQuery, state: FSMContext):
    await state.finish()
    purchasess = await db.last_purchases(call.from_user.id, 10)
    texts = await get_language(call.from_user.id)
    s = await db.get_settings()
    if len(purchasess) >= 1:
        await call.answer(texts.last_10_purc)
        with suppress(MessageCantBeDeleted):
            await call.message.delete()
            for purchases in purchasess:
                link_items = purchases["item"]

                if s["currency"] == "rub":
                    price = purchases["price_rub"]
                elif s["currency"] == "eur":
                    price = purchases["price_euro"]
                elif s["currency"] == "usd":
                    price = purchases["price_dollar"]

                msg = texts.last_purc_text.format(
                    receipt=purchases["receipt"],
                    name=purchases["position_name"],
                    count=purchases["count"],
                    price=price,
                    curr=currencies[s["currency"]]["sign"],
                    date=purchases["date"],
                    link_items=link_items,
                )

                await call.message.answer(msg)

        await call.message.answer(
            await open_profile(texts, call), reply_markup=await profile_inl(texts)
        )
    else:
        await call.answer(texts.no_purcs, True)


@dp.callback_query_handler(text_startswith="promo_act", state="*")
async def user_history(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await UsersCoupons.here_coupon.set()
    texts = await get_language(call.from_user.id)
    await call.message.delete()
    await call.message.answer(texts.promo_act, reply_markup=back_to_profile(texts))


@dp.message_handler(state=UsersCoupons.here_coupon)
async def functions_profile_get(message: Message, state: FSMContext):
    await state.finish()
    s = await db.get_settings()
    coupon = message.text
    texts = await get_language(message.from_user.id)
    if await db.get_coupon_search(coupon=coupon) is None:
        await message.answer(texts.no_coupon.format(coupon=coupon))
    else:
        cop = (await db.get_coupon_search(coupon=coupon))["coupon"]
        uses = (await db.get_coupon_search(coupon=coupon))["uses"]
        discount_rub = (await db.get_coupon_search(coupon=coupon))["discount_rub"]
        discount_eur = (await db.get_coupon_search(coupon=coupon))["discount_euro"]
        discount_usd = (await db.get_coupon_search(coupon=coupon))["discount_dollar"]
        user_id = message.from_user.id
        user = await db.get_user(id=user_id)
        activ_cop = await db.get_activate_coupon(user_id=user_id, coupon_name=cop)
        if uses == 0:
            await message.answer(texts.no_uses_coupon)
            await db.delete_coupon(coupon=coupon)
        elif activ_cop is None:
            bal_eur = user["balance_euro"] + float(discount_eur)
            bal_usd = user["balance_dollar"] + float(discount_usd)
            bal_rub = user["balance_rub"] + float(discount_rub)
            main_discount = 0

            if s["currency"] == "rub":
                main_discount = discount_rub
            elif s["currency"] == "eur":
                main_discount = discount_eur
            elif s["currency"] == "usd":
                main_discount = discount_usd

            await db.update_user(
                user_id,
                balance_rub=bal_rub,
                balance_euro=bal_eur,
                balance_dollar=bal_usd,
            )
            await db.update_coupon(coupon, uses=int(uses) - 1)
            await db.add_activ_coupon(user_id)
            await db.activate_coupon(user_id=user_id, coupon=coupon)
            await message.answer(
                texts.yes_coupon.format(
                    discount=main_discount, curr=currencies[s["currency"]]["sign"]
                )
            )
        elif activ_cop["coupon_name"] == cop:
            await message.answer(texts.yes_uses_coupon)


@dp.callback_query_handler(text="back_to_user_menu", state="*")
async def again_start(call: CallbackQuery, state: FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    user = await db.get_user(id=call.from_user.id)
    kb = await user_menu(texts, call.from_user.id)
    if texts.start_photo == "":
        name = f"@{user['user_name']}"
        if user["user_name"] == "":
            us = await bot.get_chat(user["id"])
            name = us.get_mention(as_html=True)
        await call.message.answer(
            texts.start_text.format(user_name=name), reply_markup=kb
        )
    else:
        name = f"@{user['user_name']}"
        if user["user_name"] == "":
            us = await bot.get_chat(user["id"])
            name = us.get_mention(as_html=True)
        await bot.send_photo(
            chat_id=call.from_user.id,
            photo=texts.start_photo,
            caption=texts.start_text.format(user_name=name),
            reply_markup=kb,
        )


@dp.callback_query_handler(text="profile", state="*")
async def profile_open(call: CallbackQuery, state: FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    msg = await open_profile(texts, call)

    await call.message.delete()

    if texts.profile_photo:
        await call.message.answer_photo(
            photo=texts.profile_photo,
            caption=msg,
            reply_markup=await profile_inl(texts),
        )
    else:
        await call.message.answer(msg, reply_markup=await profile_inl(texts))


@dp.message_handler(text=lang_en.profile, state="*")
@dp.message_handler(text=lang_ua.profile, state="*")
@dp.message_handler(text=lang_ru.profile, state="*")
async def profile_opens(message: Message, state: FSMContext):
    await state.finish()
    texts = await get_language(message.from_user.id)
    msg = await open_profile(texts, message=message)

    await message.delete()

    if texts.profile_photo:
        await message.answer_photo(
            photo=texts.profile_photo,
            caption=msg,
            reply_markup=await profile_inl(texts),
        )
    else:
        await message.answer(msg, reply_markup=await profile_inl(texts))


@dp.callback_query_handler(text="faq:open", state="*")
async def faq_open(call: CallbackQuery, state: FSMContext):
    await state.finish()
    s = await db.get_settings()
    texts = await get_language(call.from_user.id)
    faq = s["faq"]
    if faq == "None" or faq == "-":
        faq = texts.no_faq_text
    news = s["news"]
    chat = s["chat"]

    if s["chat"] == "-":
        chat = None

    if s["news"] == "-":
        news = None

    if news is None and chat is None:
        kb = back_to_user_menu(texts)
    if news is None and chat is not None:
        kb = await chat_inl(texts)
    if news is not None and chat is None:
        kb = await news_inl(texts)
    if news is not None and chat is not None:
        kb = await faq_inl(texts)

    await call.message.delete()

    if texts.faq_photo:
        await call.message.answer_photo(
            photo=texts.faq_photo, caption=faq, reply_markup=kb
        )
    else:
        await call.message.answer(faq, reply_markup=kb)


@dp.callback_query_handler(text="support:open", state="*")
async def faq_open(call: CallbackQuery, state: FSMContext):
    await state.finish()
    s = await db.get_settings()
    texts = await get_language(call.from_user.id)
    get_support = s["support"]
    if get_support == "None" or get_support == "-":
        msg = texts.no_support
    else:
        msg = texts.yes_support

    if get_support == "None" or get_support == "-":
        kb = back_to_user_menu(texts)
    else:
        kb = await support_inll(texts)

    await call.message.delete()

    if texts.support_photo:
        await call.message.answer_photo(
            photo=texts.support_photo, caption=msg, reply_markup=kb
        )
    else:
        await call.message.answer(msg, reply_markup=kb)


@dp.callback_query_handler(text="contests", state="*")
async def contests_view_user(call: CallbackQuery, state: FSMContext):
    await state.finish()
    user = await db.get_user(id=call.from_user.id)
    texts = await get_language(call.from_user.id)
    contests = await db.get_contests()
    if len(contests) > 1:
        await call.message.delete()
        await call.message.answer(
            text=texts.choose_contest, reply_markup=await choose_contest(contests)
        )
    elif len(contests) == 1:
        await call.message.delete()
        bot_settings = await db.get_settings()
        a = contests[0]["end_time"] - time.time()
        a1 = datetime.today()
        a2 = a1 + timedelta(seconds=a)
        end_time_ = a2 - a1
        end_time = str(end_time_).split(".")[0]
        if len(end_time.split(",")) == 2:
            day = end_time.split(",")[0]
            day = day.split(" ")[0]
            day_text = convert_words(int(day), texts.day_s)
            end_time = f"{day} {day_text}, {end_time.split(', ')[1]}"
        else:
            end_time = f"{end_time.split(', ')[0]}"

        text = texts.contest_text.format(
            contests[0]["prize"],
            currencies[bot_settings["currency"]]["sign"],
            end_time,
            contests[0]["winners_num"],
            convert_words(contests[0]["winners_num"], texts.winner_s),
            contests[0]["members_num"],
            convert_words(contests[0]["members_num"], texts.member_s),
        )

        if contests[0]["purchases_num"] > 0 or contests[0]["refills_num"] > 0:
            text += texts.conditions

        status = "❌"

        if contests[0]["refills_num"] > 0:
            if user["count_refills"] >= contests[0]["refills_num"]:
                status = "✅"
            text += texts.conditions_refills.format(
                num=contests[0]["refills_num"],
                refills=convert_words(contests[0]["refills_num"], texts.refill_s),
                status=status,
            )

        if contests[0]["purchases_num"] > 0:
            if (
                len(await db.get_user_purchases(user["id"]))
                >= contests[0]["purchases_num"]
            ):
                status = "✅"
            text += texts.conditions_purchases.format(
                num=contests[0]["purchases_num"],
                purchases=convert_words(contests[0]["purchases_num"], texts.purchase_s),
                status=status,
            )
        if len(get_channels(contests[0]["channels_ids"])) > 0:
            urls_txt = ""
            ids = get_channels(contests[0]["channels_ids"])

            for c_id in ids:
                user_status = await bot.get_chat_member(
                    chat_id=c_id, user_id=call.from_user.id
                )
                channel = await bot.get_chat(chat_id=c_id)
                if user_status["status"] == "left":
                    urls_txt += f"<a href='{channel['invite_link']}'>{channel['title']}</a> - ❌\n"
                else:
                    urls_txt += f"<a href='{channel['invite_link']}'>{channel['title']}</a> - ✅\n"

            text += "\n\n" + texts.conditions_channels.format(
                num=len(get_channels(contests[0]["channels_ids"])),
                channels_text=convert_words(
                    len(get_channels(contests[0]["channels_ids"])), texts.channel_s
                ),
                channels=urls_txt,
            )
        if texts.contest_photo == "":
            await call.message.answer(
                text, reply_markup=await contest_inl(texts, contests[0]["id"], user)
            )
        else:
            await call.message.answer_photo(
                photo=texts.contest_photo,
                caption=text,
                reply_markup=await contest_inl(texts, contests[0]["id"], user),
            )
    else:
        await call.answer(texts.no_contests, True)


@dp.message_handler(text=lang_en.contest, state="*")
@dp.message_handler(text=lang_ua.contest, state="*")
@dp.message_handler(text=lang_ru.contest, state="*")
async def contest_user(msg: Message, state: FSMContext):
    await state.finish()
    user = await db.get_user(id=msg.from_user.id)
    texts = await get_language(msg.from_user.id)
    contests = await db.get_contests()
    if len(contests) > 1:
        await msg.answer(
            text=texts.choose_contest, reply_markup=await choose_contest(contests)
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
            day_text = convert_words(int(day), texts.day_s)
            end_time = f"{day} {day_text}, {end_time.split(', ')[1]}"
        else:
            end_time = f"{end_time.split(', ')[0]}"

        text = texts.contest_text.format(
            contests[0]["prize"],
            currencies[bot_settings["currency"]]["sign"],
            end_time,
            contests[0]["winners_num"],
            convert_words(contests[0]["winners_num"], texts.winner_s),
            contests[0]["members_num"],
            convert_words(contests[0]["members_num"], texts.member_s),
        )

        if contests[0]["purchases_num"] > 0 or contests[0]["refills_num"] > 0:
            text += texts.conditions

        status = "❌"

        if contests[0]["refills_num"] > 0:
            if user["count_refills"] >= contests[0]["refills_num"]:
                status = "✅"
            text += texts.conditions_refills.format(
                num=contests[0]["refills_num"],
                refills=convert_words(contests[0]["refills_num"], texts.refill_s),
                status=status,
            )

        if contests[0]["purchases_num"] > 0:
            if (
                len(await db.get_user_purchases(user["id"]))
                >= contests[0]["purchases_num"]
            ):
                status = "✅"
            text += texts.conditions_purchases.format(
                num=contests[0]["purchases_num"],
                purchases=convert_words(contests[0]["purchases_num"], texts.purchase_s),
                status=status,
            )
        if len(get_channels(contests[0]["channels_ids"])) > 0:
            urls_txt = ""
            ids = get_channels(contests[0]["channels_ids"])

            for c_id in ids:
                user_status = await bot.get_chat_member(
                    chat_id=c_id, user_id=msg.from_user.id
                )
                channel = await bot.get_chat(chat_id=c_id)
                if user_status["status"] == "left":
                    urls_txt += f"<a href='{channel['invite_link']}'>{channel['title']}</a> - ❌\n"
                else:
                    urls_txt += f"<a href='{channel['invite_link']}'>{channel['title']}</a> - ✅\n"

            text += "\n\n" + texts.conditions_channels.format(
                num=len(get_channels(contests[0]["channels_ids"])),
                channels_text=convert_words(
                    len(get_channels(contests[0]["channels_ids"])), texts.channel_s
                ),
                channels=urls_txt,
            )
        if texts.contest_photo == "":
            await msg.answer(
                text, reply_markup=await contest_inl(texts, contests[0]["id"], user)
            )
        else:
            await msg.answer_photo(
                photo=texts.contest_photo,
                caption=text,
                reply_markup=await contest_inl(texts, contests[0]["id"], user),
            )
    else:
        await msg.reply(f"<b>{texts.no_contests}</b>")


@dp.callback_query_handler(text_startswith="contest_enter:", state="*")
async def contest_enter(call: CallbackQuery, state: FSMContext):
    await state.finish()

    contest_id = int(call.data.split(":")[1])
    contest_members = await db.get_contest_members_id(contest_id)
    settings = await db.get_settings()
    cur = currencies[settings["currency"]]["sign"]
    contest = await db.get_contest(contest_id)
    texts = await get_language(call.from_user.id)

    if contest:
        if len(contest_members) == contest["members_num"]:
            if call.from_user.id not in contest_members:
                await call.answer(texts.u_didnt_have_time_to_enter_contest, True)
            return await end_contest(contest_id)
        if call.from_user.id not in contest_members:
            add = await db.add_contest_member(call.from_user.id, contest_id)
            if add:
                msg = f"""
<b>❗ Юзер {call.from_user.get_mention(as_html=True)} [<code>{call.from_user.id}</code>] участвует в розыгрыше на <code>{contest['prize']}{cur}</code></b>
                """
                await send_admins(msg, True)
                await call.answer(texts.success, True)
            contest_members_new = await db.get_contest_members_id(contest_id)
            if len(contest_members_new) == contest["members_num"]:
                return await end_contest(contest_id)
            else:
                await call.answer(texts.error, True)
        else:
            await call.answer(texts.u_already_enter_contest, True)
    else:
        await call.answer(texts.contest_already_ended, True)


@dp.callback_query_handler(text_startswith="mail_contest_view:", state="*")
@dp.callback_query_handler(text_startswith="contest_view:", state="*")
async def contest_view(call: CallbackQuery, state: FSMContext):
    await state.finish()
    texts = await get_language(call.from_user.id)
    user = await db.get_user(id=call.from_user.id)
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
        day_text = convert_words(int(day), texts.day_s)
        end_time = f"{day} {day_text}, {end_time.split(', ')[1]}"
    else:
        end_time = f"{end_time.split(', ')[0]}"

    text = texts.contest_text.format(
        contest["prize"],
        currencies[bot_settings["currency"]]["sign"],
        end_time,
        contest["winners_num"],
        convert_words(contest["winners_num"], texts.winner_s),
        contest["members_num"],
        convert_words(contest["members_num"], texts.member_s),
    )

    if contest["purchases_num"] > 0 or contest["refills_num"] > 0:
        text += texts.conditions

    status = "❌"

    if contest["refills_num"] > 0:
        if user["count_refills"] >= contest["refills_num"]:
            status = "✅"
        text += texts.conditions_refills.format(
            num=contest["refills_num"],
            refills=convert_words(contest["refills_num"], texts.refill_s),
            status=status,
        )

    if contest["purchases_num"] > 0:
        if len(await db.get_user_purchases(user["id"])) >= contest["purchases_num"]:
            status = "✅"
        text += texts.conditions_purchases.format(
            num=contest["purchases_num"],
            purchases=convert_words(contest["purchases_num"], texts.purchase_s),
            status=status,
        )

    if len(get_channels(contest["channels_ids"])) > 0:
        urls_txt = ""
        ids = get_channels(contest["channels_ids"])

        for c_id in ids:
            user_status = await bot.get_chat_member(
                chat_id=c_id, user_id=call.from_user.id
            )
            channel = await bot.get_chat(chat_id=c_id)
            if user_status["status"] == "left":
                urls_txt += (
                    f"<a href='{channel['invite_link']}'>{channel['title']}</a> - ❌\n"
                )
            else:
                urls_txt += (
                    f"<a href='{channel['invite_link']}'>{channel['title']}</a> - ✅\n"
                )

        text += "\n\n" + texts.conditions_channels.format(
            num=len(get_channels(contest["channels_ids"])),
            channels_text=convert_words(
                len(get_channels(contest["channels_ids"])), texts.channel_s
            ),
            channels=urls_txt,
        )

    if call.data.split(":")[0] == "contest_view":
        if texts.contest_photo == "":
            await call.message.edit_text(
                text, reply_markup=await contest_inl(texts, contest["id"], user)
            )
        else:
            await call.message.delete()
            await call.message.answer_photo(
                photo=texts.contest_photo,
                caption=text,
                reply_markup=await contest_inl(texts, contest["id"], user),
            )
    else:
        if texts.contest_photo == "":
            await call.message.answer(
                text, reply_markup=await contest_inl(texts, contest["id"], user)
            )
        else:
            await call.message.answer_photo(
                photo=texts.contest_photo,
                caption=text,
                reply_markup=await contest_inl(texts, contest["id"], user),
            )


@dp.message_handler(text=lang_ru.faq, state="*")
@dp.message_handler(text=lang_ua.faq, state="*")
@dp.message_handler(text=lang_en.faq, state="*")
async def faq_opens(message: Message, state: FSMContext):
    await state.finish()
    texts = await get_language(message.from_user.id)
    s = await db.get_settings()
    faq = s["faq"]
    if faq == "None" or faq == "-":
        faq = texts.no_faq_text
    news = s["news"]
    chat = s["chat"]

    if s["chat"] == "-":
        chat = None

    if s["news"] == "-":
        news = None

    if news is None and chat is None:
        kb = back_to_user_menu(texts)
    if news is None and chat is not None:
        kb = await chat_inl(texts)
    if news is not None and chat is None:
        kb = await news_inl(texts)
    if news is not None and chat is not None:
        kb = await faq_inl(texts)

    await message.delete()

    if texts.faq_photo:
        await message.answer_photo(photo=texts.faq_photo, caption=faq, reply_markup=kb)
    else:
        await message.answer(faq, reply_markup=kb)


@dp.message_handler(text=lang_ru.support, state="*")
@dp.message_handler(text=lang_ua.support, state="*")
@dp.message_handler(text=lang_en.support, state="*")
async def faq_opens(message: Message, state: FSMContext):
    await state.finish()

    s = await db.get_settings()
    texts = await get_language(message.from_user.id)
    get_support = s["support"]
    if get_support == "None" or get_support == "-":
        msg = texts.no_support
    else:
        msg = texts.yes_support

    if get_support == "None" or get_support == "-":
        kb = back_to_user_menu(texts)
    else:
        kb = await support_inll(texts)

    await message.delete()

    if texts.support_photo:
        await message.answer_photo(
            photo=texts.support_photo, caption=msg, reply_markup=kb
        )
    else:
        await message.answer(msg, reply_markup=kb)


@dp.message_handler(text=lang_ru.refill, state="*")
@dp.message_handler(text=lang_ua.refill, state="*")
@dp.message_handler(text=lang_en.refill, state="*")
async def refill_opens(message: Message, state: FSMContext):
    await state.finish()
    texts = await get_language(message.from_user.id)
    await message.delete()

    if texts.refill_photo:
        await message.answer_photo(
            photo=texts.refill_photo,
            caption=texts.refill_text,
            reply_markup=await refill_inl(texts),
        )
    else:
        await message.answer(texts.refill_text, reply_markup=await refill_inl(texts))


@dp.message_handler(text=lang_ru.products, state="*")
@dp.message_handler(text=lang_ua.products, state="*")
@dp.message_handler(text=lang_en.products, state="*")
async def open_products_users(message: Message, state: FSMContext):
    texts = await get_language(message.from_user.id)
    await state.finish()

    if len(await db.get_all_categories()) < 1:
        await message.delete()

        if texts.products_photo:
            await message.answer_photo(
                photo=texts.products_photo,
                caption=texts.no_cats,
                reply_markup=back_to_user_menu(texts),
            )
        else:
            await message.answer(texts.no_cats, reply_markup=back_to_user_menu(texts))
    else:
        await message.delete()
        if texts.products_photo:
            await message.answer_photo(
                photo=texts.products_photo,
                caption=texts.available_cats,
                reply_markup=await open_products(texts),
            )
        else:
            await message.answer(
                texts.available_cats, reply_markup=await open_products(texts)
            )


@dp.message_handler(IsAdmin(), commands=["admin", "adm", "a"], state="*")
async def admin_menu_send(message: Message, state: FSMContext):
    await state.finish()

    await message.answer(
        "Добро пожаловать в меню Администратора", reply_markup=admin_menu()
    )


@dp.message_handler(IsAdmin(), text="⚙️ Меню Администратора", state="*")
async def admin_menu_send(message: Message, state: FSMContext):
    await state.finish()

    await message.answer(
        "Добро пожаловать в меню Администратора", reply_markup=admin_menu()
    )


@dp.message_handler()
async def pr_buttons1(msg: Message, state: FSMContext):
    pr_buttons = await db.get_all_pr_buttons()
    await state.finish()
    for button in pr_buttons:
        if msg.text == button["name"]:
            if button["photo"] != "-":
                await msg.answer_photo(photo=button["photo"], caption=button["txt"])
            else:
                await msg.answer(button["txt"])


@dp.callback_query_handler(text_startswith="pr_button_user:", state="*")
async def pr_buttons2(call: CallbackQuery, state: FSMContext):
    await state.finish()
    b_id = int(call.data.split(":")[1])
    btn = await db.get_pr_button(b_id)
    texts = await get_language(call.from_user.id)
    if btn["photo"] == "-":
        await call.message.delete()
        await call.message.answer(btn["txt"], reply_markup=back_to_user_menu(texts))
    else:
        await call.message.delete()
        await call.message.answer_photo(
            photo=btn["photo"],
            caption=btn["txt"],
            reply_markup=back_to_user_menu(texts),
        )
