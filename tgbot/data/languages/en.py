# Удаление отступов у текста
def ots(get_text: str):
    if get_text is not None:
        split_text = get_text.split("\n")
        if split_text[0] == "":
            split_text.pop(0)
        if split_text[-1] == "":
            split_text.pop(-1)
        save_text = []

        for text in split_text:
            while text.startswith(" "):
                text = text[1:]

            save_text.append(text)
        get_text = "\n".join(save_text)

    return get_text


class Texts:
    ##################################                #####################################
    ##################################     /start     #####################################
    ##################################                #####################################

    # Фото, оставьте пустым если хотите убрать (прямая ссылка на фото)
    start_photo = (
        "https://i.pinimg.com/736x/4b/1f/56/4b1f569542fe133647f3c495191e13bd.jpg"
    )
    profile_photo = (
        "https://i-zdrav.ru/upload/iblock/ca8/ca83b3878fa97ce94bb3ad4c375a80ce.png"
    )
    products_photo = (
        "https://i.pinimg.com/736x/32/26/b8/3226b8f970e693c1c25b963a4f2fcf37.jpg"
    )
    faq_photo = (
        "https://i.pinimg.com/736x/28/a6/12/28a6125000accf422e6eddfa562242aa.jpg"
    )
    support_photo = "https://img.freepik.com/free-vector/flat-design-illustration-customer-support_23-2148887720.jpg"
    refill_photo = "https://cdni.iconscout.com/illustration/premium/thumb/young-man-showing-top-up-balance-on-mobile-illustration-download-in-svg-png-gif-file-formats--bank-digital-wallet-payment-application-pack-business-illustrations-10692820.png?f=webp"
    contest_photo = "https://i.imgur.com/zlblPgk.jpg"

    # Стартовый текст
    start_text = """
Welcome {user_name}! Thank you for using our Store
Main menu:
    """

    error_refill = "❌ Error, refill has already occurred!"
    choose_crypto = "<b>⚙️ Select cryptocurrency:</b>"
    ref_s = ["referral", "referral", "referrals"]  # не трогать скобки
    day_s = ["day", "days", "days"]  # не трогать скобки
    member_s = ["member", "members", "members"]  # не трогать скобки
    winner_s = ["winner", "winners", "winners"]  # не трогать скобки
    refill_s = ["refill", "refills", "refills"]  # не трогать скобки
    purchase_s = ["purchase", "purchases", "purchases"]  # не трогать скобки
    channel_s = ["channel", "channels", "channels"]  # не трогать скобки
    conditions = "\n\n<b>❗ Conditions: </b>\n\n"  # не трогать \n\n !!!
    nobody = "<code>Nobody</code>"
    change_language = "🔗 Change language"
    choose_language = "<b>❗ Choose a language</b>"

    no_sub = "<b>❗ Error!\nYou have not subscribed to the channel.</b>"

    is_buy_text = "❌ Shopping is temporarily disabled!"
    is_ban_text = f"<b>❌ You have been blocked from the bot!</b>"
    is_work_text = f"<b>❌ The bot is on those. works!</b>"
    is_refill_text = f"❌ Refills are temporarily disabled!"
    is_ref_text = f"❗ Referral system is disabled!"
    is_contests_text = f"❌ Giveaways are temporarily disabled!"

    yes_reffer = f"<b>❗ You already have a refer!</b>"
    invite_yourself = "<b>❗ You can't invite yourself!</b>"
    new_refferal = """
<b>💎 You have a new referral! @{user_name}
⚙️ Now you have <code>{user_ref_count}</code> {convert_ref}!</b>"""

    ##################################               #####################################
    ################################## Inline-Кнопки #####################################
    ##################################               #####################################

    # Меню пользователя
    products = "🛍️ Buy"
    profile = "👤 Profile"
    refill = "💰 Refill balance"
    faq = "📌 FAQ"
    support = "💎 Support"
    back = "⬅ Back"
    contest = "🎁 Giveaways"

    payok_text = "🪙 PayOK"
    cryptoBot_text = "💡 CryptoBot"
    qiwi_text = "🔥 Qiwi"
    yoomoney_text = "📌 ЮMoney"
    lava_text = "💰 Lava"
    lzt_text = "💚 Lolz"
    crystalPay_text = "💎 CrystalPay"
    aaio_text = "💳 Bank Card (РФ, УК, КЗ)"
    aaio_short_text = "Bank Card"  # текст должен быть не больше 18 символов!

    support_inl = "⚙️ Support"

    buy = "🛍️ Buy"  # При открытии позиции

    #####################################         #####################################
    ##################################### Профиль #####################################
    #####################################         #####################################

    # Кнопки Профиля
    ref_system = "💎 Referral system"
    promocode = "💰 Activate promocode"
    last_purchases_text = "⭐ Last purchases"

    open_profile_text = """
<b>👤 Your profile:
💎 User: {user_name}
🆔 ID: <code>{user_id}</code>
💰 Balance: <code>{balance}{curr}</code>
💵 Total refill: <code>{total_refill}{curr}</code>
📌 Date of registration: <code>{reg_date}</code>
👥 Referrals: <code>{ref_count}</code></b>"""

    last_10_purc = "⚙️ Last 10 purchases"
    no_purcs = "❗ You have no purchases"
    last_purc_text = """
<b>🧾 Receipt: <code>{receipt}</code>
💎 Product: <code>{name} | {count}шт | {price}{curr}</code>
🕰 Purchase date: <code>{date}</code>
💚 Item(s):
{link_items}</b>"""

    promo_act = "<b>📩 To activate the promo code, write its name</b>\n<b>⚙️ Example: promo2023</b>"
    no_uses_coupon = "<b>❌ You did not have time to activate the promo code!</b>"
    no_coupon = "<b>❌ Promo code <code>{coupon}</code> does not exist!</b>"
    yes_coupon = "<b>✅ You have successfully activated the promo code and received <code>{discount}{curr}</code>!</b>"
    yes_uses_coupon = "<b>❌ You have already activated this promo code!</b>"

    new_ref_lvl = "<b>💚 You have a new referral level, {new_lvl}! Up to {next_lvl} level left {remain_refs} {convert_ref}</b>"
    max_ref_lvl = f"<b>💚 You have a new referral level, 3! Max level!</b>"
    cur_max_lvl = f"💚 You have the maximum level!</b>"
    next_lvl_remain = "💚 Until the next level left to invite referrals: <code>{remain_refs}</code></b>"
    ref_text = """
<b>💎 Referral System
        
🔗 Link: 
{ref_link} 
      
📔 Our referral system will allow you to earn a large amount without investment. You only need to give your link to your friends and you will receive lifetime <code>{ref_percent}%</code> from their deposits in the bot.

⚙️ Invited you: {reffer}
💵 Total earned <code>{ref_earn}{curr}</code> from {convert_ref}
📌 All you have <code>{ref_count}</code> {convert_ref}
🎲 Referral Level: <code>{ref_lvl}</code>
{mss}"""
    yes_refill_ref = "<b>💎 Your referral {name} topped up the balance with <code>{amount}{cur}</code> and from this you are credited with <code>{ref_amount}{cur}</code></b>"

    #####################################         #####################################
    #####################################   FAQ   #####################################
    #####################################         #####################################

    no_faq_text = "<b>⚙️ FAQ Not configured, please contact support!</b>"
    faq_chat_inl = "💎 Chat"
    faq_news_inl = "📩 News"

    ################################                    ################################
    ################################   Тех. Поддержка   ################################
    ################################                    ################################

    no_support = "<b>⚙️ The owner of the bot did not leave a link to support!</b>"
    yes_support = "<b>📩 To contact Support press the bottom button:</b>"

    #######################################
    #     Мин./Макс. Сумма пополнения     #
    #                                     #
    min_amount = 0.35  #
    max_amount = 100000  #
    #                                     #
    #                                     #
    #######################################

    ################################                  ################################
    ################################    Пополнения    ################################
    ################################                  ################################

    refill_text = "<b>💰 Choose a refill method:</b>"
    refill_amount_text = "<b>💰 Enter the top-up amount (From {min_amount}{curr} to {max_amount}{curr})</b>"
    refill_link_inl = "💵 Proceed to payment"
    refill_check_inl = "💎 Check payment"
    refill_check_no = "❌ Payment not found"
    no_int_amount = "<b>❗ The top-up amount must be a number!</b>"
    min_max_amount = "<b>❗ The top-up amount must be greater than or equal to <code>{min_amount}{curr}</code> but less than or equal to <code>{max_amount}{curr}</code></b>"

    def refill_gen_text(self, way, amount, id, curr):
        msg = f"""
<b>⭐ Refill via: <code>{way}</code>
💰 Amount: <code>{amount}{curr}</code>
🆔 Payment ID: <code>{id}</code>
💎 Click the button below to pay:</b>
        """

        return ots(msg)

    def refill_success_text(self, way, amount, receipt, curr):
        msg = f"""
<b>⭐ You have successfully topped up your balance with the amount <code>{amount}{curr}</code>
💎 Method: <code>{way}</code>
🧾 Receipt: <code>{receipt}</code></b>
        """

        return ots(msg)

    ##########################                                 ############################
    ##########################    Открытие категорий/Товары    ############################
    ##########################                                 ############################

    open_pos_text = """
<b>💎 Category: <code>{cat_name}</code>

🛍️ Product: <code>{pos_name}</code>
💰 Cost: <code>{price}{cur}</code>
⚙️ Quantity: <code>{items}</code>
🎲 Description: </b>
{desc}"""

    no_cats = f"<b>Sorry, there are no categories at the moment :(</b>"
    available_cats = f"<b>Currently available categories:</b>"
    current_cat = "<b>Current category: <code>{name}</code>:</b>"

    no_products = f"<b>Sorry, there are no products at the moment :(</b>"
    no_product = f"Unfortunately, this product is currently unavailable :("
    gen_products = "Preparation of goods..."

    current_pod_cat = "<b>Current sub-category: <code>{name}</code></b>"

    here_count_products = f"<b>❗ Enter the number of products you want to buy:</b>"

    choose_buy_product = "<b>❓ Are you sure you want to buy <code>{name}</code> in quantity <code>1 pcs.</code>?</b>"
    choose_buy_products = "<b>❓ Are you sure you want to buy <code>{name}</code> in the amount of <code>{amount}pcs</code>?</b>"

    no_num_count = "<b>❗ Quantity must be a number!</b>"

    yes_buy_items = """
<b>✅ You have successfully purchased the item(s)</b>

🧾 Receipt: <code>{receipt}</code>
💎 Product: <code>{name} | {amount}pcs | {amount_pay}{cur}</code>
🎲 Date: <code>{buy_time}</code>"""

    no_balance = "❗ You don't have enough funds. Top up your balance!"
    edit_prod = (
        "<b>❗️ The product you wanted to buy is out of stock or has changed.</b>"
    )
    otmena_buy = "<b>❗ You have canceled the purchase of goods.</b>"

    #######################                             ###########################
    #######################          Розыгрыши          ###########################
    #######################                             ###########################

    contest_text = """
<b>🎁 Giveaway

💰 Amount: <code>{}{}</code>
 
🕒 End in <code>{}</code> 

🎉 {} {} 
👥 {} {}</b>"""

    conditions_refills = "<b>💳 {num} {refills} - {status}</b>\n"
    conditions_purchases = "<b>🛒 {num} {purchases} - {status}</b>\n"
    conditions_channels = "<b>✨ Subscribe to {num} {channels_text}: \n\n{channels}</b>"

    no_contests = "❗ There are no giveaways at the moment!"

    contest_enter = "🎉 Participate"

    choose_contest = "<b>❗ Select a draw:</b>"
    u_win_the_contest = "<b>🎉 Congratulations, you have won the giveaway! \n💰 A prize of {}{} has been awarded!</b>"
    u_didnt_have_time_to_enter_contest = "You didn't have time to participate! 💥"
    success = "✅ Success"
    error = "⚠ An error occurred, try again later!"
    u_already_enter_contest = "❌ You are already participating!"
    contest_already_ended = "💥 The giveaway has already ended!"
    pcs = "pcs."
    search = "🔎 Search positions"
    search_request_text = (
        "<b>Enter the name or part of the name of the position to search for!</b>"
    )
    inf = "[Infinity]"
    result_search = "Result of search!"
    nothing_search = "Nothing found!"
