import aiohttp
import asyncio


async def send_welcome_message(user_id: int, bot_token: str):
    """
    Отправляет приветственное сообщение пользователю в Telegram.

    :param user_id: ID пользователя, которому отправляется сообщение.
    :param bot_token: Токен Telegram-бота.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": user_id, "text": "Привет! Добро пожаловать!"}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                print("Сообщение успешно отправлено")
            else:
                print(f"Ошибка при отправке сообщения: {response.status}")
                response_text = await response.text()
                print(f"Ответ сервера: {response_text}")


# Пример использования:
asyncio.run(
    send_welcome_message(7742837753, "7250446074:AAFh4FZ7aDWxGEZmZZOzNPnUKyK1osVm7bI")
)
