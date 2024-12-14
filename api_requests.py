import os
import json
import random
import aiohttp
import asyncio

from config import BASE_URL, US_STATES
from tgbot.data.config import db
from tgbot.utils.utils_functions import get_unix
from tgbot.services.db import get_date


async def add_pptp_to_db(ip):
    with open("all_valid_pptps.json", "r") as f:
        data = json.load(f)
        ip_data = data[ip]

    is_position = await db.get_position_id_by_postal_id(ip_data["postal_code"])

    # если позиции нет в базе данных, нужно добавить
    if not is_position:
        try:
            state_code = US_STATES[ip_data["subdivisions"]]
            pod_cat_id = await db.get_pod_category_id_by_name(state_code)
            pos_id = get_unix(True)  # генерируем позишн айди
            name = ip_data["postal_code"]  # имя (почтовый индекс штата)
            price_rub = 317
            price_usd = 3.5
            price_eur = 3.17
            description = f"{ip_data['subdivisions']} State high quality PPTP"
            photo = "-"
            date = get_date()
            cat_id = await db.get_category_id_by_name("PPTP USA")
            _type = "text"

            # print(state_code)
            # print(pod_cat_id)
            # print(pos_id)
            # print(name)
            # print(description)
            # print(date)
            # print(cat_id)

            await db.add_position(
                _type,
                name,
                price_rub,
                price_usd,
                price_eur,
                description,
                photo,
                cat_id,
                "-",
                pos_id,
                pod_cat_id,
            )

            print(f"Added position: {pos_id}")

            is_position = pos_id

        # если это не штат - выбрасываем исключение
        except:
            print(f"State code not found for: {ip_data['subdivisions']} | {ip}")
            return 1
    try:
        state_code = US_STATES[ip_data["subdivisions"]]
        cat_id = await db.get_category_id_by_name("PPTP USA")
        item_data = (
            f"{ip} - {ip_data['login_data']} - {state_code}/{ip_data['postal_code']}"
        )

        await db.add_new_item(
            category_id=cat_id, position_id=is_position, item_data=item_data
        )
        print(f"Added item: {item_data}")
        with open("added_ips.txt", "a") as f:
            f.write(f"{ip}\n")
        return 0
    except:
        print("Failed to add PPTP to bot database")
        return 1


async def download_valid_pptps():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/get_valid_pptps") as response:
            if response.status == 200:
                content = await response.read()
                with open("all_valid_pptps.json", "wb") as f:
                    f.write(content)
                return 0
            else:
                print(f"Failed to fetch data. Status code: {response.status}")
                return 1


async def add_valid_pptps():
    server_status = await download_valid_pptps()
    if server_status == 1:
        print("[api_requests.py] Failed to fetch data.")
        return

    need_to_add = []
    added_ips = []

    dirs = os.listdir()
    if "added_ips.txt" not in dirs:
        with open("added_ips.txt", "w") as f:
            f.write("")

    with open("added_ips.txt", "r") as f:
        for line in f:
            added_ips.append(line.replace("\n", ""))

    with open("all_valid_pptps.json", "r") as f:
        data = json.load(f)
        valid_ips = list(data.keys())

    for ip in valid_ips:
        if ip not in added_ips:
            need_to_add.append(ip)

    if len(need_to_add) == 0:
        print("[api_requests.py] No new PPTPs to add.")
        return

    print(need_to_add)
    for ip in need_to_add:
        await add_pptp_to_db(ip)


if __name__ == "__main__":
    asyncio.run(add_valid_pptps())
