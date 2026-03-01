# database.py
import sqlite3

DB_NAME = "game.db"

def init_db():
    """Создает базу данных и таблицу, если их еще нет"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Создаем таблицу: id (автоматический номер), username (уникальное имя), status (статус в игре)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            status TEXT DEFAULT 'ожидает'
        )
    ''')
    conn.commit()
    conn.close()

def add_player(username: str) -> bool:
    """Добавляет игрока. Возвращает True, если успешно, и False, если такой уже есть."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO players (username) VALUES (?)", (username,))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        # Ошибка IntegrityError срабатывает, если мы пытаемся добавить неуникальный username
        success = False 
    conn.close()
    return success

def get_all_players():
    """Возвращает список всех игроков"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, status FROM players ORDER BY id ASC")
    players = cursor.fetchall()
    conn.close()
    return players

def clear_db():
    """Полностью очищает список игроков и сбрасывает счетчик ID"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='players'") # Сброс нумерации
    conn.commit()
    conn.close()

def get_next_waiting_player():
    """Находит первого игрока в очереди со статусом 'ожидает'"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM players WHERE status = 'ожидает' ORDER BY id ASC LIMIT 1")
    player = cursor.fetchone()
    conn.close()
    return player

def get_current_playing_player():
    """Находит того, кто сейчас кидает кубики (статус '🎲 играет')"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # ИСПРАВЛЕННЫЙ ЗАПРОС: теперь точно ищет с кубиком!
    cursor.execute("SELECT id, username FROM players WHERE status = '🎲 играет' LIMIT 1")
    player = cursor.fetchone()
    conn.close()
    return player

def update_player_status(player_id: int, new_status: str):
    """Меняет статус конкретному игроку"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET status = ? WHERE id = ?", (new_status, player_id))
    conn.commit()
    conn.close()

def reorder_active_players():
    """Удаляет вылетевших и пересобирает список, чтобы ID снова шли с 1"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Достаем всех, КРОМЕ вылетевших, сохраняя их текущий статус
    cursor.execute("SELECT username, status FROM players WHERE status != '❌ вылетел' ORDER BY id ASC")
    active_players = cursor.fetchall()
    
    # 2. Полностью очищаем таблицу и сбрасываем счетчик ID
    cursor.execute("DELETE FROM players")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='players'")
    
    # 3. Записываем выживших обратно (они получат новые ID: 1, 2, 3...)
    for player in active_players:
        username, status = player
        cursor.execute("INSERT INTO players (username, status) VALUES (?, ?)", (username, status))
        
    conn.commit()
    conn.close()

def reset_statuses():
    """Сбрасывает статус всех выживших игроков на 'ожидает' для нового круга"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Меняем статус всем, кто остался в таблице
    cursor.execute("UPDATE players SET status = 'ожидает'")
    conn.commit()
    conn.close()
