import json


def get_public_news_id():
    with open("bot_settings.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data["public_news_id"]


def get_all_valid_ips():
    with open("all_valid_pptps.json") as f:
        data = json.load(f)
        all_ips = []

        for i in data:
            all_ips.append(i)

        return all_ips


def update_public_news_id(new_id):
    with open("bot_settings.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    data["public_news_id"] = new_id

    with open("bot_settings.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
