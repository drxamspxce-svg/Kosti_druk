import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

async def main():
    bot = Bot(token="8603624102:AAGW7c1A1YWsH6Z5aTLOSFLAV2IVaMg1FTE")
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start(message: Message):
        print(f"ПОЛУЧЕНО /start от {message.from_user.id}")
        await message.answer("Работает!")

    print("Тест запущен")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())
