import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Забираем их по ИМЕНАМ переменных
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

