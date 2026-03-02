import sqlite3

DB_NAME = "game.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            status TEXT DEFAULT 'ожидает'
        )
    ''')
    # Новая таблица для зарегистрированных игроков
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registered_users (
            chat_id INTEGER PRIMARY KEY,
            username TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def add_player(username: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO players (username) VALUES (?)", (username,))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def get_all_players():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, status FROM players ORDER BY id ASC")
    players = cursor.fetchall()
    conn.close()
    return players

def clear_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='players'")
    conn.commit()
    conn.close()

def get_next_waiting_player():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM players WHERE status = 'ожидает' ORDER BY id ASC LIMIT 1")
    player = cursor.fetchone()
    conn.close()
    return player

def get_current_playing_player():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM players WHERE status = '🎲 играет' LIMIT 1")
    player = cursor.fetchone()
    conn.close()
    return player

def update_player_status(player_id: int, new_status: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET status = ? WHERE id = ?", (new_status, player_id))
    conn.commit()
    conn.close()

def reorder_active_players():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, status FROM players WHERE status != '❌ вылетел' ORDER BY id ASC")
    active_players = cursor.fetchall()
    cursor.execute("DELETE FROM players")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='players'")
    for player in active_players:
        username, status = player
        cursor.execute("INSERT INTO players (username, status) VALUES (?, ?)", (username, status))
    conn.commit()
    conn.close()

def reset_statuses():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET status = 'ожидает'")
    conn.commit()
    conn.close()


# ─── REGISTERED USERS ────────────────────────────────────────────────────────

def register_user(chat_id: int, username: str) -> bool:
    """Регистрирует пользователя. True если новый, False если уже есть."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO registered_users (chat_id, username) VALUES (?, ?)",
            (chat_id, username)
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def get_chat_id_by_username(username: str) -> int | None:
    """Находит chat_id по username игрока."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT chat_id FROM registered_users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_all_registered_users() -> list:
    """Возвращает всех зарегистрированных пользователей для рассылки."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM registered_users")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]
