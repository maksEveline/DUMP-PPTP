from aiogram.types import Message
from aiogram.dispatcher.filters import BoundFilter
from tgbot.data.config import db
from tgbot.utils.utils_functions import get_admins
from tgbot.data import config
from tgbot.data.loader import bot


class IsAdmin(BoundFilter):
    async def check(self, message: Message) -> bool:
        user_id = message.from_user.id
        return user_id in get_admins()


class IsContestOn(BoundFilter):
    async def check(self, message: Message) -> bool:
        s = await db.get_settings()
        if s['contests_is_on'] == "True":
            return False
        else:
            return True


class IsBan(BoundFilter):
    async def check(self, message: Message) -> bool:
        user = await db.get_user(id=message.from_user.id)
        if user['is_ban'] == "True" and not user['id'] in get_admins():
            return True
        else:
            return False


class IsBuy(BoundFilter):
    async def check(self, message: Message) -> bool:
        s = await db.get_settings()
        if s['is_buy'] == "True":
            return False
        else:
            return True


class IsRefill(BoundFilter):
    async def check(self, message: Message) -> bool:
        s = await db.get_settings()
        if s['is_refill'] == "True":
            return False
        else:
            return True


class IsSub(BoundFilter):
    async def check(self, message: Message):
        s = await db.get_settings()
        issub = s['is_sub']
        channel_id = config.channel_id
        if channel_id == "":
            return False
        else:
            user_status = await bot.get_chat_member(chat_id=channel_id, user_id=message.from_user.id)
            if issub == "True":
                if user_status["status"] == 'left':
                    return True
                else:
                    return False
            else:
                return False


class IsWork(BoundFilter):
    async def check(self, message: Message) -> bool:
        s = await db.get_settings()
        user = await db.get_user(id=message.from_user.id)
        if s['is_work'] == "True" and not user['id'] in get_admins():
            return True
        else:
            return False