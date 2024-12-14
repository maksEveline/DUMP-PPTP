from aiopayok import Payok


class PayOk():
    def __init__(self, api_id: int, api_key: str, secret: str, shop_id: int):
        self.payok = Payok(api_id, api_key, secret, shop_id)

    async def get_link(self, payment_id: int, summ: float, currency: str = 'RUB'):
        res = await self.payok.create_pay(amount=summ, payment=payment_id, currency=currency, desc='Оплата заказа')
        return res

    async def get_pay(self, order_id):
        res = await self.payok.get_transactions(int(order_id))
        if res.transaction_status == 1:
            return True
        else:
            return False

    async def get_balance(self):
        return await self.payok.get_balance()

