# handlers/private.py

from aiogram import Router, F, types
from aiogram.filters import CommandStart
from config import ADMIN_ID
from keyboards.reply_inline import get_admin_menu

# Подключаем функцию очистки нашей базы данных
from database import clear_db

private_router = Router()

@private_router.message(CommandStart(), F.chat.type == "private")
async def start_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        "Привет! Я твой помощник. Используй кнопки ниже для управления списками.",
        reply_markup=get_admin_menu()
    )

@private_router.message(F.text == "📝 Создать новый список", F.chat.type == "private")
async def create_new_list_prompt(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    # Очищаем настоящую базу данных!
    clear_db()
    
    await message.answer("Список полностью очищен! Теперь добавь меня в группу и напиши там команду /sendlist, чтобы я вывел пустой шаблон.")

# Подключаем функцию добавления из базы
from database import add_player

# --- ИМПОРТ СПИСКА ИГРОКОВ ---
@private_router.message(F.text, F.chat.type == "private")
async def mass_import(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    
    # Если это какая-то команда (начинается с /), игнорируем
    if message.text.startswith('/'): return
    
    lines = message.text.split('\n')
    added_count = 0
    
    for line in lines:
        username = line.strip()
        if username:
            # Если в нике нет @, добавляем его для красоты
            if not username.startswith('@') and not username.startswith('http'):
                username = '@' + username
                
            # Пытаемся добавить. Если такой уже есть, add_player вернет False
            if add_player(username):
                added_count += 1
                
    await message.answer(f"✅ Массовый импорт завершен!\nНовых игроков добавлено: {added_count}")
