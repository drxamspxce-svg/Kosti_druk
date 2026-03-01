import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Импортируем наши настройки и роутеры
from config import TOKEN
from handlers.private import private_router
from handlers.group import group_router

# Импортируем функцию инициализации нашей новой базы данных
from database import init_db

async def main():
    # 1. Создаем/проверяем базу данных ПЕРЕД запуском бота
    init_db()
    
    # 2. Инициализируем бота и диспетчер
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # 3. Подключаем наши папки с логикой к главному диспетчеру
    dp.include_router(private_router)
    dp.include_router(group_router)

    print("Бот запущен! База данных SQLite подключена 🚀")
    
    # Пропускаем старые апдейты (чтобы бот не отвечал на старые сообщения)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
