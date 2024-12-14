import aiohttp
import hashlib


class Aaio:
    def __init__(self, aaio_api_key, aaio_id_shop, aaio_secret_key):
        self.api_key = aaio_api_key
        self.shop_id = aaio_id_shop
        self.secret_key = aaio_secret_key
        self.timeout = aiohttp.ClientTimeout(total=360)
        self.headers = {
            "Accept": "application/json",
            "X-Api-Key": self.api_key
        }

    async def create_payment(self, amount, order_id, currency):
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            sign = f':'.join([
                str(self.shop_id),
                str(amount),
                str(currency),
                str(self.secret_key),
                str(order_id)
            ])

            sign = hashlib.sha256(sign.encode('utf-8')).hexdigest(),

            params = {
                'merchant_id': self.shop_id,
                "amount": amount,
                "order_id": order_id,
                'sign': sign,
                'currency': currency
            }

            response = await session.post(url="https://aaio.io/merchant/pay", data=params)

            await session.close()

            return str(response.url)

    async def check_payment(self, order_id):
        async with aiohttp.ClientSession(headers=self.headers, timeout=self.timeout) as session:
            params = {
                'order_id': order_id,
                'merchant_id': self.shop_id
            }

            response = await session.post(url="https://aaio.io/api/info-pay", data=params)
            await session.close()
            resp = await response.json()

            if resp['type'] == "success":
                if resp['status'] == "success" or resp['status'] == 'hold':
                    return True
                else:
                    return False
            else:
                return False

    async def get_balance(self):
        async with aiohttp.ClientSession(headers=self.headers, timeout=self.timeout) as session:
            response = await session.get(url="https://aaio.io/api/balance")
            await session.close()

            resp = await response.json()

            if resp['type'] == "error":
                return resp['message']
            else:
                return resp