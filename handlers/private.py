# handlers/private.py

from aiogram import Router, F, types, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from config import ADMIN_ID
from keyboards.reply_inline import get_admin_menu
from database import clear_db, add_player, get_all_registered_users
from state import game_state

private_router = Router()

class AnnounceSetup(StatesGroup):
    waiting_template = State()

class BroadcastSetup(StatesGroup):
    waiting_content = State()

PROTECTED = [
    "📝 Создать новый список",
    "🎙 Настроить анонс",
    "🔄 Сбросить анонс",
    "📢 Рассылка",
]

@private_router.message(
    CommandStart(),
    F.chat.type == "private",
    F.from_user.id == ADMIN_ID
)
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Я твой помощник. Используй кнопки ниже.",
        reply_markup=get_admin_menu()
    )

@private_router.message(AnnounceSetup.waiting_template, F.chat.type == "private")
async def announce_setup_save(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Отменено.", reply_markup=get_admin_menu())
        return
    game_state["announce_template"] = message.html_text
    await state.clear()
    preview = (
        message.html_text
        .replace("{username}", "@example")
        .replace("{number}", "1")
        .replace("{limit}", "3")
    )
    await message.answer(
        "✅ Шаблон сохранён!\n\n<b>Превью:</b>\n\n" + preview,
        reply_markup=get_admin_menu()
    )

@private_router.message(BroadcastSetup.waiting_content, F.chat.type == "private")
async def broadcast_receive(message: types.Message, state: FSMContext, bot: Bot):
    if message.from_user.id != ADMIN_ID:
        return
    if message.text and message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Рассылка отменена.", reply_markup=get_admin_menu())
        return
    await state.clear()
    users = get_all_registered_users()
    if not users:
        await message.answer("⚠️ Нет зарегистрированных пользователей.")
        return
    await message.answer(f"📢 Начинаю рассылку на {len(users)} человек...")
    success = 0
    failed = 0
    for chat_id in users:
        try:
            await message.copy_to(chat_id=chat_id)
            success += 1
        except TelegramForbiddenError:
            failed += 1
        except TelegramBadRequest:
            failed += 1
        except Exception:
            failed += 1
    await message.answer(
        f"✅ Рассылка завершена!\n\n"
        f"📨 Отправлено: <b>{success}</b>\n"
        f"❌ Не доставлено: <b>{failed}</b>"
    )

@private_router.message(F.text == "📝 Создать новый список", F.chat.type == "private")
async def create_new_list_prompt(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    clear_db()
    await message.answer("Список полностью очищен!\nНапиши /sendlist в группе.")

@private_router.message(F.text == "🎙 Настроить анонс", F.chat.type == "private")
async def announce_setup_start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    current = game_state["announce_template"]
    await state.set_state(AnnounceSetup.waiting_template)
    await message.answer(
        "🎙 <b>Настройка анонса игрока</b>\n\n"
        "<b>Текущий шаблон:</b>\n"
        f"<code>{current}</code>\n\n"
        "<b>Доступные переменные:</b>\n"
        "<code>{username}</code> — ник игрока\n"
        "<code>{number}</code> — номер в списке\n"
        "<code>{limit}</code> — сколько кубиков кидать\n\n"
        "💎 Премиум эмодзи и скрытые ссылки поддерживаются.\n\n"
        "Отправь новый шаблон или /cancel для отмены:"
    )

@private_router.message(F.text == "🔄 Сбросить анонс", F.chat.type == "private")
async def announce_reset(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    game_state["announce_template"] = (
        "━━━━━━━━━━━━━━━━━━\n"
        "🎲 Ход игрока №{number}\n"
        "👤 {username}\n"
        "Кидай {limit} кубика!\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    await message.answer("✅ Анонс сброшен до стандартного.", reply_markup=get_admin_menu())

@private_router.message(F.text == "📢 Рассылка", F.chat.type == "private")
async def broadcast_start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    users = get_all_registered_users()
    await state.set_state(BroadcastSetup.waiting_content)
    await message.answer(
        "📢 <b>Рассылка</b>\n\n"
        f"Зарегистрировано пользователей: <b>{len(users)}</b>\n\n"
        "Отправь сообщение для рассылки — текст, фото, видео.\n"
        "Поддерживаются премиум эмодзи и скрытые ссылки.\n\n"
        "Отправь /cancel для отмены."
    )

@private_router.message(
    F.text,
    F.chat.type == "private",
    F.from_user.id == ADMIN_ID,
    ~F.text.startswith("/")
)
async def mass_import(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        return
    if message.text in PROTECTED:
        return
    lines = message.text.split("\n")
    added_count = 0
    for line in lines:
        username = line.strip()
        if username:
            if not username.startswith("@") and not username.startswith("http"):
                username = "@" + username
            if add_player(username):
                added_count += 1
    await message.answer(
        f"✅ Массовый импорт завершён!\n"
        f"Новых игроков добавлено: {added_count}"
    )
