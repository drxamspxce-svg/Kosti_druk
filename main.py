import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import TOKEN
from handlers.private import private_router
from handlers.group import group_router
from handlers.user import user_router
from database import init_db

async def main():
    init_db()

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(private_router)
    dp.include_router(user_router)
    dp.include_router(group_router)

    print("Бот запущен! 🚀")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")

async def main():
    init_db()

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(private_router)
    dp.include_router(user_router)
    dp.include_router(group_router)

    print("Бот запущен! 🚀")
    print(f"private_router хэндлеры: {private_router.message.handlers}")
    print(f"user_router хэндлеры: {user_router.message.handlers}")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(
    bot,
    allowed_updates=["message", "callback_query", "business_message", "business_connection"]
)
