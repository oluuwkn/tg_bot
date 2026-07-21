import aiosqlite
import hashlib
from datetime import datetime

DB_NAME = "users.db"

# Расширенная коллекция цитат и вдохновляющих пожеланий
QUOTES = [
    "Сегодня идеальный день, чтобы сделать первый шаг к своей цели.",
    "Маленькие шаги каждый день приводят к большим результатам.",
    "Не жди идеального момента, бери момент и делай его идеальным.",
    "Помни, что отдых — это тоже важная часть продуктивности.",
    "Ты не должен быть великим, чтобы начать, но ты должен начать, чтобы стать великим.",
    "Твое единственное ограничение — это ты сам. Поверь в свои возможности!",
    "Каждый новый день — это чистый лист и шанс написать лучшую главу.",
    "Делай то, что можешь, с тем, что имеешь, там, где ты находишься.",
    "Успех — это сумма небольших усилий, повторяемых день изо дня.",
    "Сфокусируйся на процессе, и результат обязательно придет.",
    "Сегодня прекрасный день, чтобы похвалить себя за пройденный путь.",
    "Смелость — это не отсутствие страха, а уверенность в том, что есть что-то важнее.",
    "Будь добр к себе сегодня. Ты делаешь всё, что в твоих силах."
]

# Расширенная коллекция персональных комплиментов
COMPLIMENTS = [
    "Ты обладаешь невероятной внутренней силой!",
    "У тебя отличный вкус и прекрасное чувство баланса.",
    "Твоя улыбка может осветить даже самый пасмурный день.",
    "Ты справляешься с трудностями лучше, чем думаешь.",
    "Твоя целеустремленность действительно вдохновляет!",
    "В тебе есть редкое сочетание ума, доброты и чувства юмора.",
    "С тобой всегда тепло, уютно и надежно.",
    "Твое умение находить выход из сложных ситуаций восхищает!",
    "Ты делаешь этот мир лучше просто тем, что ты в нем есть.",
    "У тебя потрясающий потенциал — продолжай двигаться вперед!",
    "Твоя искренность и открытость притягивают замечательных людей.",
    "Ты умеешь видеть красивое даже в самых обычных деталях."
]

async def init_db():
    """Создает таблицы пользователей и логов сообщений, если их еще нет."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                city TEXT,
                zodiac TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                text TEXT,
                timestamp TEXT
            )
        """)
        await db.commit()

async def add_user(user_id: int, name: str, city: str, zodiac: str):
    """Добавляет или обновляет данные пользователя."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO users (user_id, name, city, zodiac) 
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET 
                name=excluded.name, 
                city=excluded.city, 
                zodiac=excluded.zodiac
        """, (user_id, name, city, zodiac))
        await db.commit()

async def log_message(user_id: int, name: str, text: str):
    """Сохраняет сообщение пользователя в базу данных."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO messages (user_id, name, text, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user_id, name, text, timestamp))
        await db.commit()

async def get_all_users():
    """Получает список всех пользователей для рассылки."""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()

async def get_user(user_id: int):
    """Получает данные одного пользователя."""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

def get_daily_quote(user_id: int = 0) -> str:
    """Возвращает цитату, которая обновляется каждый день и не повторяется сутки."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    seed_str = f"{date_str}_quote_{user_id}"
    hash_val = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    return QUOTES[hash_val % len(QUOTES)]

def get_daily_compliment(user_id: int = 0) -> str:
    """Возвращает комплимент, обновляющийся ежедневно."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    seed_str = f"{date_str}_compliment_{user_id}"
    hash_val = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    return COMPLIMENTS[hash_val % len(COMPLIMENTS)]
