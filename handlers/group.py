# handlers/group.py

from aiogram import Router, F, types, Bot
from aiogram.enums import DiceEmoji
from aiogram.exceptions import TelegramBadRequest # <--- Импортируем обработчик этой ошибки
from config import ADMIN_ID
from state import game_state, get_list_text
from keyboards.reply_inline import get_list_ikb

from database import (
    add_player, 
    get_next_waiting_player, 
    get_current_playing_player, 
    update_player_status,
    reorder_active_players,
    reset_statuses
)

group_router = Router()

# === УМНОЕ ОБНОВЛЕНИЕ СПИСКА (Без крашей) ===
async def update_list_msg(bot: Bot):
    if game_state.get("list_msg_id"):
        try:
            await bot.edit_message_text(
                chat_id=game_state["group_chat_id"],
                message_id=game_state["list_msg_id"],
                text=get_list_text(),
                reply_markup=get_list_ikb()
            )
        except TelegramBadRequest:
            pass # Если текст не изменился, просто молча игнорируем ошибку

# --- 1. ВЫВОД СПИСКА ---
@group_router.message(F.text == "/sendlist", F.chat.type.in_({"group", "supergroup"}))
async def send_list_to_group(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    msg = await message.answer(get_list_text(), reply_markup=get_list_ikb())
    game_state["group_chat_id"] = msg.chat.id
    game_state["list_msg_id"] = msg.message_id
    await message.delete()

# --- 2. ДОБАВЛЕНИЕ ИГРОКА (+) ---
@group_router.business_message(F.text == "+")
async def add_player_from_business(message: types.Message, bot: Bot):
    if message.from_user.id == ADMIN_ID and message.reply_to_message:
        client = message.reply_to_message.from_user
        username = f"@{client.username}" if client.username else client.first_name
        if add_player(username):
            await update_list_msg(bot)

# --- 3. ВЫЗОВ ИГРОКА (/go) ---
@group_router.message(F.text == "/go", F.chat.type.in_({"group", "supergroup"}))
async def call_next_player(message: types.Message, bot: Bot):
    if message.from_user.id != ADMIN_ID: return
    current = get_current_playing_player()
    if current:
        await message.answer(f"⏳ Заверши ход игрока {current[1]} (/win или /lose)")
        return
    next_player = get_next_waiting_player()
    if not next_player:
        await message.answer("🎉 Очередь пуста!")
        return
    p_id, username = next_player
    update_player_status(p_id, "🎲 играет")
    
    await update_list_msg(bot)
    
    # Очищаем память кубиков только для этого игрока
    if "scores" not in game_state: game_state["scores"] = {}
    game_state["scores"][p_id] = {"total": 0, "count": 0}

    await message.answer(f"{username}")
    limit = 5 if game_state.get("is_final") else 3
    await message.answer(f"Кидай {limit}")
    await message.answer_dice(emoji=DiceEmoji.DICE)

# --- 4. ИГРОК ПРОШЕЛ (/win) ---
@group_router.message(F.text == "/win", F.chat.type.in_({"group", "supergroup"}))
async def player_win(message: types.Message, bot: Bot):
    if message.from_user.id != ADMIN_ID: return
    current = get_current_playing_player()
    if not current: return
    update_player_status(current[0], "✅ прошел")
    await call_next_player(message, bot)

# --- 5. ИГРОК ВЫЛЕТЕЛ (/lose) ---
@group_router.message(F.text == "/lose", F.chat.type.in_({"group", "supergroup"}))
async def player_lose(message: types.Message, bot: Bot):
    if message.from_user.id != ADMIN_ID: return
    current = get_current_playing_player()
    if not current: return
    update_player_status(current[0], "❌ вылетел")
    await call_next_player(message, bot)

# --- 6. ВОЗВРАТ ИГРОКА (/restore номер) ---
@group_router.message(F.text.startswith("/restore"), F.chat.type.in_({"group", "supergroup"}))
async def restore_player(message: types.Message, bot: Bot):
    if message.from_user.id != ADMIN_ID: return
    try:
        p_id = int(message.text.split()[1])
        update_player_status(p_id, "ожидает")
        await update_list_msg(bot)
        await message.delete()
    except:
        await message.answer("⚠️ Пиши так: /restore 5")

# --- 7. ОБЫЧНЫЙ РАУНД (/round) ---
@group_router.message(F.text == "/round", F.chat.type.in_({"group", "supergroup"}))
async def start_new_round(message: types.Message, bot: Bot):
    if message.from_user.id != ADMIN_ID: return
    game_state["is_final"] = False
    reset_statuses()
    await update_list_msg(bot)
    await message.answer("🔄 Обычный раунд! Статусы сброшены. Кидаем по 3 кубика. Пиши /go")

# --- 8. ЗАПУСК ФИНАЛА (/final) ---
@group_router.message(F.text == "/final", F.chat.type.in_({"group", "supergroup"}))
async def start_final_mode(message: types.Message, bot: Bot):
    if message.from_user.id != ADMIN_ID: return
    game_state["is_final"] = True
    game_state["scores"] = {}
    reset_statuses()
    await update_list_msg(bot)
    await message.answer("🏆 <b>ФИНАЛ НАЧАЛСЯ!</b>\nТеперь игроки кидают по 5 кубиков, а очки идут в зачет. Пиши /go")

# --- 9. УПОРЯДОЧИВАНИЕ (Кнопка) ---
@group_router.callback_query(F.data == "reorder")
async def reorder_list_callback(callback: types.CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID: return
    reorder_active_players()
    await update_list_msg(bot)
    await callback.answer("Список очищен и упорядочен!")

# --- 10. МАГИЯ: АВТОПОДСЧЕТ КУБИКОВ 🎲 ---
@group_router.message(F.dice)
async def handle_dice(message: types.Message):
    if message.dice.emoji != "🎲": return 
    current = get_current_playing_player()
    if not current: return 
    p_id, username = current
    
    user_name_check = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    if user_name_check != username: return
        
    if "scores" not in game_state: game_state["scores"] = {}
    if p_id not in game_state["scores"]: game_state["scores"][p_id] = {"total": 0, "count": 0}
        
    is_final = game_state.get("is_final", False)
    limit = 5 if is_final else 3

    if game_state["scores"][p_id]["count"] >= limit: return 
        
    val = message.dice.value
    game_state["scores"][p_id]["total"] += val
    game_state["scores"][p_id]["count"] += 1
    
    total = game_state["scores"][p_id]["total"]
    count = game_state["scores"][p_id]["count"]
    
    if not is_final:
        if count == 3:
            await message.reply(f"🎯 <b>3 броска сделано!</b> (Сумма: {total})\n<i>Судья, жми /win или /lose</i>")
        else:
            await message.reply(f"🎰 Бросок {count}/3: выпало <b>{val}</b>.")
    else:
        if count == 5:
            await message.reply(f"🏁 <b>5 бросков завершены!</b>\n🔥 Итоговая сумма для топа: <b>{total}</b>")
        else:
            await message.reply(f"🎰 Бросок {count}/5: выпало <b>{val}</b>. Текущая сумма: <b>{total}</b>")

# --- 11. ОПРЕДЕЛЕНИЕ ПОБЕДИТЕЛЕЙ (/winners X) ---
@group_router.message(F.text.startswith("/winners"), F.chat.type.in_({"group", "supergroup"}))
async def define_winners(message: types.Message, bot: Bot):
    if message.from_user.id != ADMIN_ID: return
    if not game_state.get("is_final"):
        await message.answer("⚠️ Эта команда работает только в Финале!")
        return

    try: num_winners = int(message.text.split()[1])
    except:
        await message.answer("⚠️ Напиши команду правильно: /winners 2")
        return

    if "scores" not in game_state or not game_state["scores"]:
        await message.answer("⚠️ Нет данных о бросках!")
        return

    from database import get_all_players
    players = get_all_players()
    player_dict = {p[0]: p[1] for p in players}

    results = []
    for p_id, data in game_state["scores"].items():
        if p_id in player_dict and data["count"] > 0:
            results.append((p_id, player_dict[p_id], data["total"]))

    results.sort(key=lambda x: x[2], reverse=True)
    if not results: return

    winners = results[:num_winners]
    losers = results[num_winners:]

    text = f"🏆 <b>ИТОГИ ФИНАЛА (Топ-{num_winners}):</b>\n\n"
    for i, (p_id, uname, score) in enumerate(winners, 1):
        update_player_status(p_id, "🏆 Победитель")
        text += f"🥇 {i} место: {uname} — <b>{score}</b> очков\n"

    text += "\nОстальные финалисты:\n"
    for p_id, uname, score in losers:
        update_player_status(p_id, "❌ вылетел")
        text += f"• {uname} — <b>{score}</b> очков\n"

    await update_list_msg(bot)
    await message.answer(text)
    game_state["scores"] = {}
