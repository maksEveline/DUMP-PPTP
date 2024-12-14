import colorama
import asyncio
import logging

from aiogram import executor, Dispatcher
from tgbot.handlers import dp
from tgbot.middlewares import setup_middlewares
from tgbot.data.config import db
from tgbot.data.loader import scheduler
from tgbot.utils.other_functions import (
    update_profit_week,
    update_profit_day,
    autobackup_db,
)
from tgbot.utils.utils_functions import check_updates, check_contests, check_rates

from api_requests import add_valid_pptps

logging.basicConfig(
    format="%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s",
    level=logging.INFO,
)
colorama.init()


# Запуск заданий
async def scheduler_start():
    scheduler.add_job(update_profit_week, "cron", day_of_week="mon", hour=00)
    scheduler.add_job(update_profit_day, "cron", hour=00)
    scheduler.add_job(autobackup_db, "cron", hour=00)
    scheduler.add_job(check_updates, "interval", minutes=30)
    scheduler.add_job(check_rates, "cron", hour=00)
    scheduler.add_job(
        add_valid_pptps, "interval", minutes=5
    )  # получение данных с бэкенда и добавление в базу


# Выполнение функции после запуска бота
async def on_startup(dp: Dispatcher):
    await scheduler_start()

    setup_middlewares(dp)

    print(colorama.Fore.GREEN + "=======================")
    print(colorama.Fore.RED + "Bot Was Started")
    print(colorama.Fore.LIGHTBLUE_EX + "Developer: https://t.me/endwaysu")
    print(colorama.Fore.LIGHTBLUE_EX + "TG Channel: https://t.me/endwaysu")
    print(colorama.Fore.LIGHTBLUE_EX + "Forum: https://endway.su")
    print(colorama.Fore.RESET)


# Выполнение функции после выключения бота
async def on_shutdown(dp: Dispatcher):

    await dp.storage.close()
    await dp.storage.wait_closed()
    await (await dp.bot.get_session()).close()


if __name__ == "__main__":
    scheduler.start()
    loop = asyncio.get_event_loop()

    loop.create_task(db.create_db())
    loop.create_task(check_rates())
    loop.create_task(check_contests())
    loop.create_task(check_updates())

    executor.start_polling(
        dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True
    )
