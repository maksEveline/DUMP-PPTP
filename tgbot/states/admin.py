from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminContests(StatesGroup):
    here_winner_count_contests = State()
    here_prize_contests = State()
    here_members_contests = State()
    here_end_time_contests = State()
    edit_con_conds = State()


class AdminMail(StatesGroup):
    here_text_mail_text = State()
    here_text_mail_photo = State()
    here_photo_mail_photo = State()
    here_name_for_add_mail_button = State()
    here_new_name_for_mail_button = State()
    here_link_for_add_mail_button = State()
    here_category_for_open_mail = State()
    here_category_for_pod_open_mail = State()
    here_category_for_pos_open_mail = State()
    here_pod_category_for_pod_open_mail = State()


class AdminFind(StatesGroup):
    here_user = State()
    here_receipt = State()


class AdminSettingsEdit(StatesGroup):
    here_faq = State()
    here_ref_percent = State()
    here_support = State()
    here_chat = State()
    here_news = State()
    here_count_lvl_ref = State()


class AdminPrButtons(StatesGroup):
    here_name_pr_button_create = State()
    here_name_pr_button_delete = State()
    here_txt_pr_button_create = State()
    here_photo_pr_button_create = State()


class AdminCoupons(StatesGroup):
    here_name_promo = State()
    here_uses_promo = State()
    here_discount_promo = State()
    here_name_for_delete_promo = State()


class AdminEditUser(StatesGroup):
    here_msg_to_send = State()
    here_amount_to_add = State()
    here_amount_to_edit = State()


class AdminCatsEdit(StatesGroup):
    here_name_cat = State()
    here_new_cat_name = State()


class AdminPodCatsEdit(StatesGroup):
    here_name_pod_cat = State()
    here_new_name_for_pod_cat = State()


class AdminPosEdit(StatesGroup):
    here_name_add_pos = State()
    here_price_add_pos = State()
    here_type_add_pos = State()
    here_desc_add_pos = State()
    here_photo_add_pos = State()
    here_infinity_add_pos = State()
    here_new_price_pos = State()
    here_new_name_pos = State()
    here_new_desc_pos = State()
    here_new_photo_pos = State()
    here_new_infinity_pos = State()


class AdminItemsEdit(StatesGroup):
    here_data_items = State()
