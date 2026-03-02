# handlers/user.py

from aiogram import Router, F, types, Bot
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from config import ADMIN_ID
from database import register_user

user_router = Router()


@user_router.message(CommandStart(), F.chat.type == "private")
async def user_start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        return
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    register_user(chat_id=message.from_user.id, username=username)


async def notify_player(bot: Bot, username: str, limit: int):
    from database import get_chat_id_by_username
    chat_id = get_chat_id_by_username(username)
    if not chat_id:
        return
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=(
                f"🎲 <b>Твой ход!</b>\n\n"
                f"Иди в группу и кидай <b>{limit}</b> кубика!\n\n"
                f"Не тормози — тебя ждут 🔥"
            )
        )
    except TelegramForbiddenError:
        pass
    except TelegramBadRequest:
        pass
