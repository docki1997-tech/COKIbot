import os
import random
import time
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = os.getenv("8724617956:AAH-sjzN6fZjcjxpz9fHpeJsGEqS2NijeaA")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

COOLDOWN = 20 * 60 * 60  # 20 часов

# =========================
# DATABASE (SQLite)
# =========================

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    size INTEGER,
    last REAL
)
""")

conn.commit()


def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row is None:
        cursor.execute(
            "INSERT INTO users (user_id, size, last) VALUES (?, ?, ?)",
            (user_id, 0, 0)
        )
        conn.commit()
        return (user_id, 0, 0)

    return row


def update_user(user_id, size, last):
    cursor.execute(
        "UPDATE users SET size = ?, last = ? WHERE user_id = ?",
        (size, last, user_id)
    )
    conn.commit()


# =========================
# COMMANDS
# =========================

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply(
        "😏 Привіт! Я твій бот\n"
        "Напиши /boobs щоб грати 🔥"
    )


@dp.message_handler(commands=['boobs'])
async def boobs(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    now = time.time()

    user = get_user(user_id)

    size = user[1]
    last = user[2]

    # cooldown
    if now - last < COOLDOWN:
        remaining = COOLDOWN - (now - last)
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)

        await message.reply(
            f"⏳ Спокійно 😏\n"
            f"Спробуй через {hours} год {minutes} хв"
        )
        return

    change = random.randint(-10, 10)
    size += change

    if size < 0:
        size = 0

    update_user(user_id, size, now)

    if change > 0:
        text = f"📈 {name}, +{change} 😏"
    elif change < 0:
        text = f"📉 {name}, {change} 💀"
    else:
        text = f"😐 {name}, без змін"

    await message.reply(
        f"{text}\n"
        f"📏 Тепер: {size} см"
    )


# =========================
# START BOT
# =========================

if __name__ == "__main__":
    executor.start_polling(dp)
