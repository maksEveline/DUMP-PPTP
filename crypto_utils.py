import aiohttp
import asyncio
import json


async def convert_usdt_to_crypto(amount_usdt, target_crypto):
    crypto_ids = {
        "USDT": "tether",
        "ETH": "ethereum",
        "LTC": "litecoin",
        "BTC": "bitcoin",
        "BNB": "binancecoin",
        "TON": "toncoin",
        "USDC": "usd-coin",
        "BUSD": "binance-usd",
    }
    target_crypto = target_crypto.upper()
    if target_crypto not in crypto_ids:
        raise ValueError("Указанная криптовалюта не поддерживается или не найдена.")
    if target_crypto == "USDT":
        return float(amount_usdt)
    crypto_id = crypto_ids[target_crypto]
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
        ) as response:
            text = await response.text()
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                data = json.loads(text.replace("'", '"'))
            if crypto_id in data:
                crypto_price_in_usd = data[crypto_id]["usd"]
                return float(amount_usdt) / float(crypto_price_in_usd)
            else:
                raise ValueError(
                    "Не удалось получить данные о цене выбранной криптовалюты."
                )


async def convert_usdt_to_ton(amount_usdt):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.coinpaprika.com/v1/tickers/ton-toncoin"
        ) as response:
            data = await response.json()
            ton_price = data["quotes"]["USD"]["price"]
            return float(amount_usdt) / float(ton_price)


# async def main():
#     amount_usdt = 100
#     target_crypto = "TON"
#     result = await convert_usdt_to_crypto(amount_usdt, target_crypto)
#     if result is not None:
#         print(f"Количество {target_crypto.upper()} равно {result}")
#     else:
#         print("Произошла ошибка при конвертации.")


# if __name__ == "__main__":
#     asyncio.run(main())
