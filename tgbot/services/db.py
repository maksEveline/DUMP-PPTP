# - *- coding: utf- 8 - *-
import aiosqlite
import math
import random
import time
from async_class import AsyncClass
from datetime import datetime

path_db = "tgbot/data/database.db"


# Получение текущего unix времени
def get_unix(full=False):
    if full:
        return time.time_ns()
    else:
        return int(time.time())


# Получение текущей даты
def get_date():
    this_date = datetime.today().replace(microsecond=0)
    this_date = this_date.strftime("%d.%m.%Y %H:%M:%S")

    return this_date


# Преобразование полученного списка в словарь
def dict_factory(cursor, row):
    save_dict = {}

    for idx, col in enumerate(cursor.description):
        save_dict[col[0]] = row[idx]

    return save_dict


# Форматирование запроса без аргументов
def query(sql, parameters: dict):
    if "XXX" not in sql:
        sql += " XXX "
    values = ", ".join([f"{item} = ?" for item in parameters])
    sql = sql.replace("XXX", values)

    return sql, list(parameters.values())


# Форматирование запроса с аргументами
def query_args(sql, parameters: dict):
    sql = f"{sql} WHERE "

    sql += " AND ".join([f"{item} = ?" for item in parameters])

    return sql, list(parameters.values())


class DB(AsyncClass):
    async def __ainit__(self):
        self.con = await aiosqlite.connect(path_db)
        self.con.row_factory = dict_factory

    ##############################################################################################
    ################################            Другое            ################################
    ##############################################################################################

    async def update_rates(self, **kwargs):
        queryy = "UPDATE rates SET"
        queryy, parameters = query(queryy, kwargs)
        await self.con.execute(queryy, parameters)
        await self.con.commit()

    async def get_rates(self):
        row = await self.con.execute("SELECT * FROM rates")
        rates = await row.fetchone()

        return (
            rates["usd_rub"],
            rates["usd_eur"],
            rates["eur_rub"],
            rates["eur_usd"],
            rates["rub_usd"],
            rates["rub_eur"],
        )

    async def get_all_languages(self):
        row = await self.con.execute("SELECT * FROM languages")
        return await row.fetchall()

    async def get_language(self, name=None, lang_id=None):
        row = None
        if name:
            row = await self.con.execute(
                "SELECT * FROM languages WHERE language = ?", (name,)
            )
        if lang_id:
            row = await self.con.execute(
                "SELECT * FROM languages WHERE id = ?", (lang_id,)
            )

        return await row.fetchone()

    # Получение балансов всех пользователей
    async def get_user_balances(self):
        row = await self.con.execute("SELECT * FROM users")
        return await row.fetchall()

    # Получение стоимостей всех позиций
    async def get_positions_prices(self):
        row = await self.con.execute("SELECT * FROM positions")
        return await row.fetchall()

    # Получение сумм всех промокодов
    async def get_coupons_discounts(self):
        row = await self.con.execute("SELECT * FROM coupons")
        return await row.fetchall()

    async def create_mail_button(self, name: str, typ: str):
        await self.con.execute(
            "INSERT INTO mail_buttons(name, type) VALUES (?,?)", (name, typ)
        )
        await self.con.commit()

    async def delete_mail_button(self, id: str):
        await self.con.execute("DELETE FROM mail_buttons WHERE id = ?", (id,))

    async def get_mail_button(self, id: int):
        row = await self.con.execute("SELECT * FROM mail_buttons WHERE id = ?", (id,))
        return await row.fetchone()

    async def get_all_mail_buttons(self):
        row = await self.con.execute("SELECT * FROM mail_buttons")
        return await row.fetchall()

    async def update_mail_button(self, id, **kwargs):
        queryy = f"UPDATE mail_buttons SET"
        queryy, params = query(queryy, kwargs)
        params.append(id)
        await self.con.execute(queryy + "WHERE id = ?", params)
        await self.con.commit()

    ###############################################################################################
    ################################           Розыгрыши           ################################
    ###############################################################################################

    async def create_contest(
        self,
        prize,
        members_num,
        end_time,
        winners_num,
        channels_ids,
        refills_num,
        purchases_num,
    ):
        values = [
            prize,
            members_num,
            end_time,
            winners_num,
            channels_ids,
            refills_num,
            purchases_num,
        ]
        await self.con.execute(
            "INSERT INTO contests(prize, members_num, end_time, winners_num, channels_ids, refills_num, purchases_num) VALUES (?, ?, ?, ?, ?, ?, ?)",
            values,
        )
        await self.con.commit()

    async def get_contests(self):
        row = await self.con.execute("SELECT * FROM contests")
        return await row.fetchall()

    async def get_contest(self, con_id):
        row = await self.con.execute("SELECT * FROM contests WHERE id = ?", (con_id,))
        return await row.fetchone()

    async def get_contests_settings(self):
        row = await self.con.execute("SELECT * FROM contests_settings")
        return await row.fetchone()

    async def update_contests_settings(self, **kwargs):
        queryy = "UPDATE contests_settings SET"
        queryy, parameters = query(queryy, kwargs)
        await self.con.execute(queryy, parameters)
        await self.con.commit()

    async def get_contest_members(self, contest_id: int):
        row = await self.con.execute(
            "SELECT * FROM contests_members WHERE contest_id = ?", (contest_id,)
        )
        return await row.fetchall()

    async def add_contest_member(self, userId: int, contestId: int):
        try:
            await self.con.execute(
                "INSERT INTO contests_members(user_id, contest_id) VALUES (?,?)",
                (userId, contestId),
            )
            await self.con.commit()
            return True
        except:
            return False

    async def get_contest_members_id(self, contest_id: int):
        members = await self.get_contest_members(contest_id)

        users_ids = []

        for user in members:
            users_ids.append(user["user_id"])

        return users_ids

    async def delete_contest(self, contest_id):
        await self.con.execute("DELETE FROM contests WHERE id = ?", (contest_id,))
        await self.con.execute(
            "DELETE FROM contests_members WHERE contest_id = ?", (contest_id,)
        )
        await self.con.commit()

    ################################################################################################
    ##################################           Юзеры            ##################################
    ################################################################################################

    # Регистрация пользователя в БД
    async def register_user(self, id, user_name, first_name):
        await self.con.execute(
            "INSERT INTO users("
            "id, is_ban, user_name, first_name, balance_rub, balance_euro, balance_dollar, count_refills, reg_date, reg_date_unix) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            [id, "False", user_name, first_name, 0, 0, 0, 0, get_date(), get_unix()],
        )
        await self.con.commit()

    # Получение пользователя из БД
    async def get_user(self, **kwargs):
        queryy = "SELECT * FROM users"
        queryy, params = query_args(queryy, kwargs)
        row = await self.con.execute(queryy, params)
        return await row.fetchone()

    # Редактирование пользователя
    async def update_user(self, id, **kwargs):
        queryy = f"UPDATE users SET"
        queryy, params = query(queryy, kwargs)
        params.append(id)
        await self.con.execute(queryy + "WHERE id = ?", params)
        await self.con.commit()

    # Удаление пользователя из БД
    async def delete_user(self, id):
        await self.con.execute("DELETE FROM users WHERE id = ?", id)
        await self.con.commit()

    # Получение всех пользователей из БД
    async def all_users(self):
        row = await self.con.execute("SELECT * FROM users")

        return await row.fetchall()

    # Получение суммы всех балансов
    async def sum_balances(self):
        row1 = await self.con.execute(f"SELECT SUM(balance_rub) FROM users")
        row2 = await self.con.execute(f"SELECT SUM(balance_dollar) FROM users")
        row3 = await self.con.execute(f"SELECT SUM(balance_euro) FROM users")

        rub = await row1.fetchone()
        usd = await row2.fetchone()
        eur = await row3.fetchone()

        return {
            "rub": rub["SUM(balance_rub)"],
            "usd": usd["SUM(balance_dollar)"],
            "eur": eur["SUM(balance_euro)"],
        }

    # Получение юзеров и их балансы
    async def get_all_users_and_their_balance(self):
        us = []
        row = await self.con.execute(
            "SELECT id, balance_rub, balance_dollar, balance_euro FROM users"
        )
        users = await row.fetchall()
        for user in users:
            us.append(
                {
                    "user_id": user["id"],
                    "rub": user["balance_rub"],
                    "usd": user["balance_dollar"],
                    "eur": user["balance_euro"],
                }
            )

        return us

    #############################################################################################
    ###############################            Покупки            ###############################
    #############################################################################################

    # Добавление покупки
    async def add_purchase(
        self,
        user_id,
        first_name,
        user_name,
        receipt,
        count,
        price_rub,
        price_dollar,
        price_euro,
        position_id,
        position_name,
        item,
        date,
        date_unix,
    ):
        await self.con.execute(
            "INSERT INTO purchases "
            "(user_id, user_full_name, user_name, receipt, count, price_rub, price_dollar, price_euro, position_id, "
            "position_name, item, date, unix) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                user_id,
                first_name,
                user_name,
                receipt,
                count,
                price_rub,
                price_dollar,
                price_euro,
                position_id,
                position_name,
                item,
                date,
                date_unix,
            ],
        )
        await self.con.commit()

    # Получение покупки
    async def get_purchase(self, receipt):
        row = await self.con.execute(
            "SELECT * FROM purchases WHERE receipt = ?", (receipt,)
        )

        return await row.fetchone()

    # Редактирование покупки
    async def update_purchase(self, id, **kwargs):
        queryy = f"UPDATE purchases SET"
        queryy, params = query(queryy, kwargs)
        params.append(id)
        await self.con.execute(queryy + "WHERE receipt = ?", params)
        await self.con.commit()

    # Получение всех покупок
    async def all_purchases(self):
        sql = "SELECT * FROM purchases"
        row = await self.con.execute(sql)

        return await row.fetchall()

    # Последние N покупок
    async def last_purchases(self, user_id, count):
        sql = f"SELECT * FROM purchases WHERE user_id = ? ORDER BY increment DESC LIMIT {count}"
        row = await self.con.execute(sql, [user_id])

        return await row.fetchall()

    async def get_user_purchases(self, user_id):
        row = await self.con.execute(
            "SELECT * FROM purchases WHERE user_id = ?", (user_id,)
        )
        return await row.fetchall()

    ###############################################################################################
    ###############################            Настройки            ###############################
    ###############################################################################################

    # Получение настроек
    async def get_settings(self):
        row = await self.con.execute("SELECT * FROM settings")
        return await row.fetchone()

    # Изменение настроек
    async def update_settings(self, **kwargs):
        queryy = "UPDATE settings SET"
        queryy, parameters = query(queryy, kwargs)
        await self.con.execute(queryy, parameters)
        await self.con.commit()

    ##############################################################################################
    ###############################            Платежки            ###############################
    ##############################################################################################

    # Изменение платежек
    async def update_payments(self, **kwargs):
        queryy = "UPDATE payments SET"
        queryy, parameters = query(queryy, kwargs)
        await self.con.execute(queryy, parameters)
        await self.con.commit()

    # Получение платежек
    async def get_payments(self):
        row = await self.con.execute("SELECT * FROM payments")

        return await row.fetchone()

    ###############################################################################################
    #############################            Пополнения            ################################
    ###############################################################################################

    # Добавление пополнения
    async def add_refill(self, amount, way, user_id, user_name, first_name, comment):
        await self.con.execute(
            "INSERT INTO refills("
            "user_id, user_name, user_full_name, comment, amount, receipt, way, date, date_unix) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            [
                user_id,
                user_name,
                first_name,
                comment,
                amount,
                comment,
                way,
                get_date(),
                get_unix(),
            ],
        )
        await self.con.commit()

    # Получение пополнения
    async def get_refill(self, receipt):
        row = await self.con.execute(
            "SELECT * FROM refills WHERE receipt = ?", (receipt,)
        )

        return await row.fetchone()

    # Получение всех пополнений
    async def all_refills(self):
        sql = "SELECT * FROM refills"
        row = await self.con.execute(sql)

        return await row.fetchall()

    ##############################################################################################
    ######################               Рекламные кнопки             ############################
    ##############################################################################################

    # Получение всех кнопок
    async def get_all_pr_buttons(self):
        row = await self.con.execute(f"SELECT * FROM pr_buttons")

        return await row.fetchall()

    # Получение кнопки
    async def get_pr_button(self, btn_id):
        row = await self.con.execute(
            f"SELECT * FROM pr_buttons WHERE id = ?", (btn_id,)
        )

        return await row.fetchone()

    # Создание кнопки
    async def create_pr_button(self, name, txt, photo):
        values = [name, txt, photo]
        await self.con.execute(
            "INSERT INTO pr_buttons(name, txt, photo) VALUES (?, ?, ?)", values
        )
        await self.con.commit()

    # Удаление кнопки
    async def delete_pr_button(self, name):
        await self.con.execute("DELETE FROM pr_buttons WHERE name = ?", (name,))
        await self.con.commit()

    ##############################################################################################
    #############################            Промокоды            ################################
    ##############################################################################################

    # Получение промокода
    async def get_coupon_search(self, **kwargs):
        sql = "SELECT * FROM coupons"
        sql, parameters = query_args(sql, kwargs)
        row = await self.con.execute(sql, parameters)

        return await row.fetchone()

    # Получение активироного промокода
    async def get_activate_coupon(self, **kwargs):
        sql = "SELECT * FROM activ_coupons"
        sql, parameters = query_args(sql, kwargs)
        row = await self.con.execute(sql, parameters)

        return await row.fetchone()

    # Активировать промокод
    async def activate_coupon(self, user_id, coupon):
        await self.con.execute(
            """UPDATE activ_coupons SET coupon_name = ? WHERE user_id = ?""",
            (
                coupon,
                user_id,
            ),
        )
        await self.con.commit()

    # Добавить id юзера который ввел промокод
    async def add_activ_coupon(self, user_id):
        await self.con.execute(
            f"INSERT INTO activ_coupons(user_id) VALUES (?)", (user_id,)
        )
        await self.con.commit()

    # Редактирование промокода
    async def update_coupon(self, coupon, **kwargs):
        sql = f"UPDATE coupons SET"
        sql, parameters = query(sql, kwargs)
        parameters.append(coupon)
        await self.con.execute(sql + "WHERE coupon = ?", parameters)
        await self.con.commit()

    # Создание промокода
    async def create_coupon(
        self, coupon, uses, discount_rub, discount_dollar, discount_euro
    ):
        await self.con.execute(
            "INSERT INTO coupons "
            "(coupon, uses, discount_rub, discount_dollar, discount_euro) "
            "VALUES (?, ?, ?, ?, ?)",
            [coupon, uses, discount_rub, discount_dollar, discount_euro],
        )
        await self.con.commit()

    # Удаление промокода
    async def delete_coupon(self, coupon):
        await self.con.execute("DELETE FROM coupons WHERE coupon = ?", (coupon,))
        await self.con.execute(
            "DELETE FROM activ_coupons WHERE coupon_name = ?", (coupon,)
        )
        await self.con.commit()

    ##############################################################################################
    #############################            Категории            ################################
    ##############################################################################################

    # Создать категорию
    async def add_category(self, name):
        await self.con.execute(
            "INSERT INTO categories (id, name) VALUES (?, ?)", (get_unix(True), name)
        )
        await self.con.commit()

    # Удалить все категории
    async def del_all_cats(self):
        await self.con.execute("DELETE FROM categories")
        await self.con.commit()

    # Получение всех категорий
    async def get_all_categories(self):
        row = await self.con.execute("SELECT * FROM categories")

        return await row.fetchall()

    # Получение категории
    async def get_category(self, cat_id):
        row = await self.con.execute("SELECT * FROM categories WHERE id = ?", (cat_id,))

        return await row.fetchone()

    # Изменение категории
    async def update_category(self, cat_id, **kwargs):
        queryy = f"UPDATE categories SET"
        queryy, params = query(queryy, kwargs)
        params.append(cat_id)
        await self.con.execute(queryy + "WHERE id = ?", params)
        await self.con.commit()

    # Удаление категории
    async def del_category(self, cat_id):
        await self.con.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
        await self.con.commit()

    ##############################################################################################
    ############################            Под-Категории            #############################
    ##############################################################################################

    # Удаление всех под-категорий
    async def del_all_pod_cats(self):
        await self.con.execute("DELETE FROM pod_categories")
        await self.con.commit()

    # Получение под-категорий
    async def get_pod_categories(self, cat_id):
        row = await self.con.execute(
            "SELECT * FROM pod_categories WHERE cat_id = ?", (cat_id,)
        )

        return await row.fetchall()

    # Создание под-категории
    async def add_pod_category(self, name, cat_id):
        await self.con.execute(
            "INSERT INTO pod_categories (id, name, cat_id) VALUES (?, ?, ?)",
            (get_unix(True), name, cat_id),
        )
        await self.con.commit()

    # Получение всех под-категорий
    async def get_all_pod_categories(self):
        sql = "SELECT * FROM pod_categories"
        row = await self.con.execute(sql)

        return await row.fetchall()

    # Получение под-категории
    async def get_pod_category(self, pod_cat_id):
        row = await self.con.execute(
            "SELECT * FROM pod_categories WHERE id = ?", (pod_cat_id,)
        )
        return await row.fetchone()

    # Изменение под-категории
    async def update_pod_category(self, pod_cat_id, **kwargs):
        queryy = f"UPDATE pod_categories SET"
        queryy, params = query(queryy, kwargs)
        params.append(pod_cat_id)
        await self.con.execute(queryy + "WHERE id = ?", params)
        await self.con.commit()

    # Удаление под-категории
    async def del_pod_category(self, pod_cat_id):
        await self.con.execute("DELETE FROM pod_categories WHERE id = ?", (pod_cat_id,))
        await self.con.commit()

    #######################################################################################
    ############################            Позиции            ############################
    #######################################################################################

    # Создание позиции
    async def add_position(
        self,
        _type,
        name,
        price_rub,
        price_dollar,
        price_euro,
        desc,
        photo,
        cat_id,
        infinity,
        pos_id,
        pod_cat_id=None,
    ):
        try:
            sql = "INSERT INTO positions (id, name, price_rub, price_dollar, price_euro, description, photo, date, category_id, pod_category_id, infinity, type) VALUES (?, ?,?,?, ?, ?, ?, ?, ?, ?, ?, ?)"
            await self.con.execute(
                sql,
                (
                    pos_id,
                    name,
                    price_rub,
                    price_dollar,
                    price_euro,
                    desc,
                    photo,
                    get_date(),
                    cat_id,
                    pod_cat_id,
                    infinity,
                    _type,
                ),
            )
            await self.con.commit()
        except Exception as err:
            print(err)

    # Получение позиции
    async def get_position(self, pos_id):
        row = await self.con.execute("SELECT * FROM positions WHERE id = ?", (pos_id,))

        return await row.fetchone()

    # Изменение позиции
    async def update_position(self, pos_id, **kwargs):
        queryy = f"UPDATE positions SET"
        queryy, params = query(queryy, kwargs)
        params.append(pos_id)
        await self.con.execute(queryy + "WHERE id = ?", params)
        await self.con.commit()

    # Получение всех позиций
    async def get_all_positions(self):
        sql1 = "SELECT * FROM positions"
        row = await self.con.execute(sql1)

        return await row.fetchall()

    # Получение позиций
    async def get_positions(self, cat_id=None, pod_cat_id=None):
        if pod_cat_id is not None:
            row = await self.con.execute(
                "SELECT * FROM positions WHERE pod_category_id = ?", (pod_cat_id,)
            )
        else:
            row = await self.con.execute(
                "SELECT * FROM positions WHERE category_id = ?", (cat_id,)
            )

        return await row.fetchall()

    # Удаление всех позиций
    async def del_all_positions(self):
        await self.con.execute("DELETE FROM positions")
        await self.con.commit()

    # Удаление позиции
    async def del_position(self, pos_id):
        await self.con.execute("DELETE FROM positions WHERE id = ?", (pos_id,))
        await self.con.commit()

    # Количество товара в подкатегории
    async def get_positions_len(self, pod_cat_id):
        if pod_cat_id is not None:
            row = await self.con.execute(
                "SELECT * FROM positions WHERE pod_category_id = ?", (pod_cat_id,)
            )
            result = 0
            for pos in await row.fetchall():
                pos_id = pos["id"]
                items = len(await DB.get_items(self, position_id=pos_id))
                result = result + items
            return result

    # Поиск позиций
    async def search_positions(self, query):
        row = await self.con.execute(
            "SELECT * FROM positions WHERE name LIKE ?", ("%" + query + "%",)
        )
        return await row.fetchall()

    ######################################################################################
    ############################            Товары            ############################
    ######################################################################################

    # Получение товаров
    async def get_items(self, **kwargs):
        sql = f"SELECT * FROM items"
        sql, parameters = query_args(sql, kwargs)
        row = await self.con.execute(sql, parameters)

        return await row.fetchall()

    # Получение всех товаров
    async def get_all_items(self):
        sql = "SELECT * FROM items"
        row = await self.con.execute(sql)

        return await row.fetchall()

    # Очистка товаров
    async def del_all_items(self):
        sql = "DELETE FROM items"
        await self.con.execute(sql)
        await self.con.commit()

    # Удаление товаров
    async def remove_item(self, **kwargs):
        sql = "DELETE FROM items"
        sql, parameters = query_args(sql, kwargs)
        await self.con.execute(sql, parameters)
        await self.con.commit()

    # Покупка товаров (файл/фото)
    async def buy_item_file(self, get_items, get_count, infinity):
        send_count, save_items = 0, []
        if infinity == "-":
            for select_send_item in get_items:
                if send_count != get_count:
                    send_count += 1
                    select_data = select_send_item["file_id"]

                    save_items.append(select_data)
                    sql, parameters = query_args(
                        "DELETE FROM items", {"id": select_send_item["id"]}
                    )
                    await self.con.execute(sql, parameters)
                else:
                    break
            await self.con.commit()
        else:
            for select_send_item in get_items:
                if send_count != get_count:
                    send_count += 1
                    select_data = select_send_item["file_id"]

                    save_items.append(select_data)
                else:
                    break

        return save_items, send_count

    # Покупка товаров (текс)
    async def buy_item(self, get_items, get_count, infinity):
        split_len, send_count, save_items = 0, 0, []
        if infinity == "-":
            for select_send_item in get_items:
                if send_count != get_count:
                    send_count += 1
                    if get_count >= 2:
                        select_data = f"{send_count}. {select_send_item['data']}"
                    else:
                        select_data = select_send_item["data"]

                    save_items.append(select_data)
                    sql, parameters = query_args(
                        "DELETE FROM items", {"id": select_send_item["id"]}
                    )
                    await self.con.execute(sql, parameters)

                    if len(select_data) >= split_len:
                        split_len = len(select_data)
                else:
                    break
            await self.con.commit()

            split_len += 1
            get_len = math.ceil(3500 / split_len)
        else:
            for select_send_item in get_items:
                if send_count != get_count:
                    send_count += 1
                    if get_count >= 2:
                        select_data = f"{send_count}. {select_send_item['data']}"
                    else:
                        select_data = select_send_item["data"]

                    save_items.append(select_data)

                    if len(select_data) >= split_len:
                        split_len = len(select_data)
                else:
                    break

            split_len += 1
            get_len = math.ceil(3500 / split_len)

        return save_items, send_count, get_len

    # Добавление товара
    async def add_item(self, category_id, position_id, get_all_items, is_file: False):
        if not is_file:
            for item_data in get_all_items:
                if not item_data.isspace() and item_data != "":
                    await self.con.execute(
                        "INSERT INTO items "
                        "(id, data, position_id, category_id, date) "
                        "VALUES (?, ?, ?, ?, ?)",
                        [
                            random.randint(1000000000, 9999999999),
                            item_data.strip(),
                            position_id,
                            category_id,
                            get_date(),
                        ],
                    )
        else:
            await self.con.execute(
                "INSERT INTO items "
                "(id, position_id, category_id, date, file_id) "
                "VALUES (?, ?, ?, ?, ?)",
                [
                    random.randint(1000000000, 9999999999),
                    position_id,
                    category_id,
                    get_date(),
                    get_all_items,
                ],
            )
        await self.con.commit()

    #######################################################################################
    ############################            Создание            ###########################
    ############################           Базы Данных          ###########################
    #######################################################################################

    # Создание Базы Данных
    async def create_db(self):
        # Пользователи
        users = await self.con.execute("PRAGMA table_info(users)")
        if len(await users.fetchall()) == 21:
            print("database was found (users | 1/18)")
        else:
            await self.con.execute(
                "CREATE TABLE users("
                "increment INTEGER PRIMARY KEY AUTOINCREMENT,"
                "id INTEGER,"
                "is_ban TEXT,"
                "user_name TEXT,"
                "first_name TEXT,"
                "balance_rub INTEGER,"
                "balance_dollar INTEGER,"
                "balance_euro INTEGER,"
                "language TEXT DEFAULT 'ru',"
                "total_refill INTEGER DEFAULT 0,"
                "count_refills INTEGER,"
                "reg_date TIMESTAMP,"
                "reg_date_unix INTEGER,"
                "ref_lvl INTEGER DEFAULT 1,"
                "ref_id INTEGER,"
                "ref_user_name TEXT,"
                "ref_first_name TEXT,"
                "ref_count INTEGER DEFAULT 0,"
                "ref_earn_rub INTEGER DEFAULT 0,"
                "ref_earn_dollar INTEGER DEFAULT 0,"
                "ref_earn_euro INTEGER DEFAULT 0)"
            )

            print("database was not found (users | 1/18), creating...")

        # Настройки
        settings = await self.con.execute("PRAGMA table_info(settings)")
        if len(await settings.fetchall()) == 23:
            print("database was found (settings | 2/18)")
        else:
            await self.con.execute(
                "CREATE TABLE settings("
                "is_work TEXT,"
                "is_refill TEXT,"
                "is_buy TEXT,"
                "is_ref TEXT,"
                "is_notify TEXT,"
                "is_sub TEXT,"
                "faq TEXT,"
                "chat TEXT,"
                "news TEXT,"
                "support TEXT,"
                "ref_percent_1 INTEGER,"
                "ref_percent_2 INTEGER,"
                "ref_percent_3 INTEGER,"
                "ref_lvl_1 INTEGER,"
                "ref_lvl_2 INTEGER,"
                "ref_lvl_3 INTEGER,"
                "profit_day INTEGER,"
                "profit_week INTEGER,"
                "currency TEXT,"
                "keyboard TEXT,"
                "multi_lang TEXT,"
                "default_lang TEXT,"
                "contests_is_on TEXT)"
            )

            await self.con.execute(
                "INSERT INTO settings("
                "is_work, is_refill, is_buy, is_ref, is_notify, is_sub, faq, ref_percent_1, ref_percent_2, ref_percent_3, ref_lvl_1, ref_lvl_2, ref_lvl_3, support,"
                "profit_day, profit_week, currency, keyboard, multi_lang, default_lang, contests_is_on)"
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    "True",
                    "False",
                    "False",
                    "False",
                    "True",
                    "False",
                    "None",
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    "None",
                    get_unix(),
                    get_unix(),
                    "rub",
                    "Inline",
                    "True",
                    "ru",
                    "False",
                ],
            )
            print("database was not found (settings | 2/18), creating...")

        # Платежные системы
        payments = await self.con.execute("PRAGMA table_info(payments)")
        if len(await payments.fetchall()) == 8:
            print("database was found (payment systems | 3/18)")
        else:
            await self.con.execute(
                "CREATE TABLE payments("
                "pay_qiwi TEXT,"
                "pay_crystal TEXT,"
                "pay_yoomoney TEXT,"
                "pay_lolz TEXT,"
                "pay_lava TEXT,"
                "pay_crypto TEXT,"
                "pay_payok TEXT,"
                "pay_aaio TEXT)"
            )

            await self.con.execute(
                "INSERT INTO payments("
                "pay_qiwi, pay_crystal, pay_yoomoney, pay_lolz, pay_lava, pay_crypto, pay_payok, pay_aaio) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    "False",
                    "False",
                    "False",
                    "False",
                    "False",
                    "False",
                    "False",
                    "False",
                ],
            )
            print("database was not found (payment systems| 3/18), creating...")

        # Пополнения
        refills = await self.con.execute("PRAGMA table_info(refills)")
        if len(await refills.fetchall()) == 10:
            print("database was found (Refills | 4/18)")
        else:
            await self.con.execute(
                "CREATE TABLE refills("
                "increment INTEGER PRIMARY KEY AUTOINCREMENT,"
                "user_id INTEGER,"
                "user_name TEXT,"
                "user_full_name TEXT,"
                "comment TEXT,"
                "amount INTEGER,"
                "receipt TEXT,"
                "way TEXT,"
                "date TIMESTAMP,"
                "date_unix INTEGER)"
            )
            print("database was not found (Refills | 4/18), creating...")

        # Категории
        cats = await self.con.execute("PRAGMA table_info(categories)")
        if len(await cats.fetchall()) == 3:
            print("database was found (Categories | 5/18)")
        else:
            await self.con.execute(
                "CREATE TABLE categories("
                "increment INTEGER PRIMARY KEY AUTOINCREMENT,"
                "id INTEGER,"
                "name TEXT)"
            )
            print("database was not found (Categories | 5/18), creating...")

        # Под-Категории
        pod_cats = await self.con.execute("PRAGMA table_info(pod_categories)")
        if len(await pod_cats.fetchall()) == 4:
            print("database was found (Sub-Categories | 6/18)")
        else:
            await self.con.execute(
                "CREATE TABLE pod_categories("
                "increment INTEGER PRIMARY KEY AUTOINCREMENT,"
                "cat_id INTEGER,"
                "id INTEGER,"
                "name TEXT)"
            )
            print("database was not found (Sub-Categories | 6/18), creating...")

        # Позиции
        poss = await self.con.execute("PRAGMA table_info(positions)")
        if len(await poss.fetchall()) == 13:
            print("database was found (Items | 7/18)")
        else:
            await self.con.execute(
                "CREATE TABLE positions("
                "increment INTEGER PRIMARY KEY AUTOINCREMENT,"
                "id INTEGER,"
                "name TEXT,"
                "price_rub INTEGER,"
                "price_dollar INTEGER,"
                "price_euro INTEGER,"
                "description TEXT,"
                "photo TEXT,"
                "date TIMESTAMP,"
                "category_id INTEGER,"
                "pod_category_id INTEGER,"
                "infinity TEXT,"
                "type TEXT DEFAULT 'text')"
            )
            print("database was not found (Items | 7/18), creating...")

        # Товары
        goods = await self.con.execute("PRAGMA table_info(items)")
        if len(await goods.fetchall()) == 7:
            print("database was found (Goods | 8/18)")
        else:
            await self.con.execute(
                "CREATE TABLE items("
                "increment INTEGER PRIMARY KEY AUTOINCREMENT,"
                "id INTEGER,"
                "data TEXT,"
                "position_id INTEGER,"
                "category_id INTEGER,"
                "date TIMESTAMP,"
                "file_id TEXT)"
            )
            print("database was not found (Goods | 8/18), creating...")

        # Промокоды
        promos = await self.con.execute("PRAGMA table_info(coupons)")
        if len(await promos.fetchall()) == 5:
            print("database was found (Promocodes| 9/18)")
        else:
            await self.con.execute(
                "CREATE TABLE coupons("
                "coupon TEXT,"
                "uses INTEGER,"
                "discount_rub INTEGER,"
                "discount_euro INTEGER,"
                "discount_dollar INTEGER);"
            )
            print("database was not found (Promocodes | 9/18), creating...")

        # Активные промокоды
        ac_prs = await self.con.execute("PRAGMA table_info(activ_coupons)")
        if len(await ac_prs.fetchall()) == 2:
            print("database was found (Active Promocodes | 10/18)")
        else:
            await self.con.execute(
                "CREATE TABLE activ_coupons(" "coupon_name TEXT," "user_id INTEGER);"
            )
            print("database was not found (Active Promocodes | 10/18), creating...")

        # Покупки
        purs = await self.con.execute("PRAGMA table_info(purchases)")
        if len(await purs.fetchall()) == 14:
            print("database was found (Purchaches | 11/18)")
        else:
            await self.con.execute(
                "CREATE TABLE purchases("
                "increment INTEGER PRIMARY KEY AUTOINCREMENT,"
                "user_id INTEGER,"
                "user_name TEXT,"
                "user_full_name TEXT,"
                "receipt TEXT,"
                "count INTEGER,"
                "price_rub INTEGER,"
                "price_dollar INTEGER,"
                "price_euro INTEGER,"
                "position_id INTEGER,"
                "position_name TEXT,"
                "item TEXT,"
                "date TIMESTAMP,"
                "unix INTEGER)"
            )
            print("database was not found (Purchaches | 11/18), creating...")

            await self.con.commit()

        # Языки
        langs = await self.con.execute("PRAGMA table_info(languages)")
        if len(await langs.fetchall()) == 3:
            print("database was found (Languages | 12/18)")
        else:
            await self.con.execute(
                "CREATE TABLE languages("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "language TEXT,"
                "name TEXT)"
            )

            await self.con.execute(
                "INSERT INTO languages(" "language, name) " "VALUES (?, ?)",
                ["ru", "🇷🇺 Русский"],
            )
            await self.con.execute(
                "INSERT INTO languages(" "language, name) " "VALUES (?, ?)",
                ["en", "🇺🇸 English"],
            )

            print("database was not found (Languages | 12/18), creating...")

            await self.con.commit()

        # Курс валют
        rates = await self.con.execute("PRAGMA table_info(rates)")
        if len(await rates.fetchall()) == 6:
            print("database was found (Rates | 13/18)")
        else:
            await self.con.execute(
                "CREATE TABLE rates("
                "usd_rub INTEGER,"
                "usd_eur INTEGER,"
                "eur_rub INTEGER,"
                "eur_usd INTEGER,"
                "rub_usd INTEGER,"
                "rub_eur INTEGER)"
            )

            await self.con.execute(
                "INSERT INTO rates("
                "usd_rub, usd_eur, eur_usd, eur_rub, rub_usd, rub_eur) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                [0, 0, 0, 0, 0, 0],
            )

            print("database was not found (Rates | 13/18), creating...")

            await self.con.commit()

        # Рекламные кнопки
        pr_buttons = await self.con.execute("PRAGMA table_info(pr_buttons)")
        if len(await pr_buttons.fetchall()) == 4:
            print("database was found (AD Buttons | 14/18)")
        else:
            await self.con.execute(
                "CREATE TABLE pr_buttons("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "name TEXT,"
                "txt TEXT,"
                "photo TEXT)"
            )

            print("database was not found (AD Buttons | 14/18), creating...")

            await self.con.commit()

        # Кнопки в рассылках
        mail_buttons = await self.con.execute("PRAGMA table_info(mail_buttons)")
        if len(await mail_buttons.fetchall()) == 3:
            print("database was found (Mail Buttons | 15/18)")
        else:
            await self.con.execute(
                "CREATE TABLE mail_buttons("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "name TEXT,"
                "type TEXT)"
            )

            print("database was not found (Mail Buttons | 15/18), creating...")

            await self.con.commit()

        # Розыгрыши
        contests = await self.con.execute("PRAGMA table_info(contests)")
        if len(await contests.fetchall()) == 8:
            print("database was found (Contests | 16/18)")
        else:
            await self.con.execute(
                "CREATE TABLE contests("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "prize INTEGER,"
                "members_num INTEGER,"
                "end_time INTEGER,"
                "winners_num INTEGER,"
                "channels_ids TEXT,"
                "refills_num INTEGER DEFAULT 0,"
                "purchases_num INTEGER DEFAULT 0)"
            )

            print("database was not found (Contests | 16/18), creating...")

            await self.con.commit()

        # Участники розыгрышей
        contests_members = await self.con.execute("PRAGMA table_info(contests_members)")
        if len(await contests_members.fetchall()) == 2:
            print("database was found (Contests Members | 17/18)")
        else:
            await self.con.execute(
                "CREATE TABLE contests_members("
                "contest_id INTEGER,"
                "user_id INTEGER)"
            )

            print("database was not found (Contests Members | 17/18), creating...")

            await self.con.commit()

        # Настройки розыгрышей
        contests_settings = await self.con.execute(
            "PRAGMA table_info(contests_settings)"
        )
        if len(await contests_settings.fetchall()) == 7:
            print("database was found (Contests Settings | 18/18)")
        else:
            await self.con.execute(
                "CREATE TABLE contests_settings("
                "winners_num INTEGER,"
                "prize INTEGER,"
                "purchases_num INTEGER,"
                "refills_num INTEGER,"
                "channels_ids TEXT,"
                "members_num INTEGER,"
                "end_time INTEGER)"
            )

            await self.con.execute(
                "INSERT INTO contests_settings("
                "winners_num, prize, purchases_num, refills_num,"
                "channels_ids, members_num, end_time) VALUES ("
                "?, ?, ?, ?, ?, ?, ?)",
                [1, 100, 0, 0, "-", 10, 3600],
            )

            print("database was not found (Contests Settings | 18/18), creating...")

            await self.con.commit()

    #######################################################################################
    ############################            eveline             ###########################
    ############################           added ppts methods   ###########################
    #######################################################################################

    async def get_position_id_by_postal_id(self, postal_id):
        query = "SELECT id FROM positions WHERE name = ?"
        result = await self.con.execute(query, [postal_id])
        row = await result.fetchone()
        return row["id"] if row else False

    async def get_pod_category_id_by_name(self, name):
        query = "SELECT id FROM pod_categories WHERE name = ?"
        result = await self.con.execute(query, [name])
        row = await result.fetchone()
        return row["id"] if row else None

    async def get_category_id_by_name(self, name):
        query = "SELECT id FROM categories WHERE name = ?"
        result = await self.con.execute(query, [name])
        row = await result.fetchone()
        return row["id"] if row else None

    async def add_new_item(self, category_id, position_id, item_data):
        if not item_data.isspace() and item_data != "":
            await self.con.execute(
                "INSERT INTO items "
                "(id, data, position_id, category_id, date) "
                "VALUES (?, ?, ?, ?, ?)",
                [
                    random.randint(1000000000, 9999999999),
                    item_data.strip(),
                    position_id,
                    category_id,
                    get_date(),
                ],
            )

        await self.con.commit()
