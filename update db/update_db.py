import sqlite3

PATH_DATABASE = "database.db"


# Преобразование полученного списка в словарь
def dict_factory(cursor, row):
    save_dict = {}

    for idx, col in enumerate(cursor.description):
        save_dict[col[0]] = row[idx]

    return save_dict


def rebuild_db():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory

    # Языки
    con.execute("CREATE TABLE languages("
                               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                               "language TEXT,"
                               "name TEXT)")
    con.execute("INSERT INTO languages("
                               "language, name) "
                               "VALUES (?, ?)", ['ru', '🇷🇺 Русский'])
    con.execute("INSERT INTO languages("
                               "language, name) "
                               "VALUES (?, ?)", ['en', '🇺🇸 English'])
    con.execute("INSERT INTO languages("
                               "language, name) "
                               "VALUES (?, ?)", ['ua', '🇺🇦 Український'])

    # Курс валют
    con.execute("CREATE TABLE rates("
                               "usd_rub INTEGER,"
                               "usd_eur INTEGER,"
                               "eur_rub INTEGER,"
                               "eur_usd INTEGER,"
                               "rub_usd INTEGER,"
                               "rub_eur INTEGER)")
    con.execute("INSERT INTO rates("
                               "usd_rub, usd_eur, eur_usd, eur_rub, rub_usd, rub_eur) "
                               "VALUES (?, ?, ?, ?, ?, ?)",
                               [0, 0, 0, 0, 0, 0])

    # Рекламные кнопки
    con.execute("CREATE TABLE pr_buttons("
                               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                               "name TEXT,"
                               "txt TEXT,"
                               "photo TEXT)")

    # Кнопки в рассылках
    con.execute("CREATE TABLE mail_buttons("
                               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                               "name TEXT,"
                               "type TEXT)")

    # Розыгрыши
    con.execute("CREATE TABLE contests("
                               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                               "prize INTEGER,"
                               "members_num INTEGER,"
                               "end_time INTEGER,"
                               "winners_num INTEGER,"
                               "channels_ids TEXT,"
                               "refills_num INTEGER DEFAULT 0,"
                               "purchases_num INTEGER DEFAULT 0)")

    # Участники розыгрышей
    con.execute("CREATE TABLE contests_members("
                               "contest_id INTEGER,"
                               "user_id INTEGER)")

    # Настройки розыгрышей
    con.execute("CREATE TABLE contests_settings("
                               "winners_num INTEGER,"
                               "prize INTEGER,"
                               "purchases_num INTEGER,"
                               "refills_num INTEGER,"
                               "channels_ids TEXT,"
                               "members_num INTEGER,"
                               "end_time INTEGER)")
    con.execute("INSERT INTO contests_settings("
                               "winners_num, prize, purchases_num, refills_num,"
                               "channels_ids, members_num, end_time) VALUES ("
                               "?, ?, ?, ?, ?, ?, ?)", [
                                   1, 100, 0, 0, "-", 10, 3600
                               ])


    # users
    con.execute("ALTER TABLE users RENAME COLUMN balance TO balance_rub")
    con.execute("ALTER TABLE users ADD COLUMN balance_dollar INTEGER DEFAULT 0")
    con.execute("ALTER TABLE users ADD COLUMN balance_euro INTEGER DEFAULT 0")
    con.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'ru'")
    con.execute("ALTER TABLE users RENAME COLUMN ref_earn TO ref_earn_rub")
    con.execute("ALTER TABLE users ADD COLUMN ref_earn_dollar INTEGER DEFAULT 0")
    con.execute("ALTER TABLE users ADD COLUMN ref_earn_euro INTEGER DEFAULT 0")

    # settings
    con.execute("ALTER TABLE settings ADD COLUMN currency TEXT DEFAULT 'rub'")
    con.execute("ALTER TABLE settings ADD COLUMN keyboard TEXT DEFAULT 'Inline'")
    con.execute("ALTER TABLE settings ADD COLUMN multi_lang TEXT DEFAULT 'True'")
    con.execute("ALTER TABLE settings ADD COLUMN default_lang TEXT DEFAULT 'ru'")
    con.execute("ALTER TABLE settings ADD COLUMN contests_is_on TEXT DEFAULT 'True'")

    # purchases
    con.execute("ALTER TABLE purchases RENAME COLUMN price TO price_rub")
    con.execute("ALTER TABLE purchases ADD COLUMN price_dollar INTEGER")
    con.execute("ALTER TABLE purchases ADD COLUMN price_euro INTEGER")

    # positions
    con.execute("ALTER TABLE positions ADD COLUMN type TEXT DEFAULT 'text'")
    con.execute("ALTER TABLE positions RENAME COLUMN price TO price_rub")
    con.execute("ALTER TABLE positions ADD COLUMN price_dollar INTEGER")
    con.execute("ALTER TABLE positions ADD COLUMN price_euro INTEGER")

    # payments
    con.execute("ALTER TABLE payments ADD COLUMN pay_crypto TEXT DEFAULT 'False'")
    con.execute("ALTER TABLE payments ADD COLUMN pay_payok TEXT DEFAULT 'False'")
    con.execute("ALTER TABLE payments ADD COLUMN pay_aaio TEXT DEFAULT 'False'")

    # items
    con.execute("ALTER TABLE items ADD COLUMN file_id TEXT")

    # coupons
    con.execute("ALTER TABLE coupons RENAME COLUMN discount TO discount_rub")
    con.execute("ALTER TABLE coupons ADD COLUMN discount_dollar INTEGER")
    con.execute("ALTER TABLE coupons ADD COLUMN discount_euro INTEGER")

    con.commit()

    print("База Данных успешно перекодирована!")


if __name__ == "__main__":
    rebuild_db()
