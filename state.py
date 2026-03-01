# state.py
from database import get_all_players

# Сохраняем ID сообщения со списком, чтобы бот мог его обновлять
game_state = {
    "header": "<b>Список участников:</b>\n<tg-emoji emoji-id='5368324170671202286'>🏆</tg-emoji> Начинаем игру!",
    "list_msg_id": None,
    "group_chat_id": None
}

def get_list_text():
    """Формирует красивый текст сообщения со списком игроков из БД"""
    players = get_all_players()
    
    text = f"{game_state['header']}\n\n"
    
    if not players:
        text += "<i>Список пока пуст...</i>"
    else:
        for player in players:
            p_id, username, status = player
            # Формируем строку вида: "1. @username [ожидает]"
            text += f"{p_id}. {username} [{status}]\n"
            
    return text

