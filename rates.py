import aiohttp


async def get_exchanges(amount: float, cur1: str, cur2: str):
    if amount == 0.0 or amount == 0:
        return 0.00

    async with aiohttp.ClientSession() as session:
        ress = await session.get(f'https://api.exchangerate-api.com/v4/latest/{cur1}')
        res = await ress.json()
        await session.close()

        rate = res['rates'][cur2]

    return float(rate)


async def get_def_exchanges():
    rate_usd_to_rub = float(await get_exchanges(1, 'USD', 'RUB'))
    rate_usd_to_eur = float(await get_exchanges(1, 'USD', 'EUR'))
    rate_eur_to_rub = float(await get_exchanges(1, 'EUR', 'RUB'))
    rate_eur_to_usd = float(await get_exchanges(1, 'EUR', 'USD'))
    rate_rub_to_usd = float(await get_exchanges(1, 'RUB', 'USD'))
    rate_rub_to_eur = float(await get_exchanges(1, 'RUB', 'EUR'))

    return rate_usd_to_rub, rate_usd_to_eur, rate_eur_to_rub, rate_eur_to_usd, rate_rub_to_usd, rate_rub_to_eur
