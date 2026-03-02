# state.py
from database import get_all_players

game_state = {
    "header": "<b>Список участников:</b>\n<tg-emoji emoji-id='5368324170671202286'>🏆</tg-emoji> Начинаем игру!",
    "list_msg_id": None,
    "group_chat_id": None,

    # Шаблон анонса — настраивается через личку с ботом
    # Доступные переменные: {username} {number} {limit}
    "announce_template": (
        "━━━━━━━━━━━━━━━━━━\n"
        "🎲 Ход игрока №{number}\n"
        "👤 {username}\n"
        "Кидай {limit} кубика!\n"
        "━━━━━━━━━━━━━━━━━━"
    )
}


def get_list_text():
    """Живой список — каждый статус отображается по-своему"""
    players = get_all_players()

    text = f"{game_state['header']}\n\n"

    if not players:
        text += "<i>Список пока пуст...</i>"
        return text

    for p_id, username, status in players:
        if status == "🎲 играет":
            # Текущий игрок — жирный и выделен
            text += f"▶️ <b>{p_id}. {username}</b> 🎲\n"

        elif status == "✅ прошел":
            # Прошедшие — зачёркнуты
            text += f"✅ <s>{p_id}. {username}</s>\n"

        elif status == "❌ вылетел":
            # Вылетевшие — зачёркнуты
            text += f"❌ <s>{p_id}. {username}</s>\n"

        elif status == "🏆 Победитель":
            # Победитель — жирный с трофеем
            text += f"🏆 <b>{p_id}. {username}</b>\n"

        elif status.startswith("🎯"):
            # Финальные очки — показываем сумму
            score = status.replace("🎯", "").strip()
            text += f"🎯 <b>{p_id}. {username}</b> — {score} очков\n"

        else:
            # Ожидает — обычная строка
            text += f"{p_id}. {username}\n"

    return text
