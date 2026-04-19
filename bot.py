import asyncio
import random
import time
import sqlite3
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

COOLDOWN = 20 * 60 * 60  # 20 часов

# =========================
# DATABASE
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

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "😏 Привіт! Я твій бот\nНапиши /boobs щоб грати 🔥"
    )


@dp.message(Command("boobs"))
async def boobs(message: Message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    now = time.time()

    user = get_user(user_id)

    size = user[1]
    last = user[2]

    if now - last < COOLDOWN:
        remaining = COOLDOWN - (now - last)
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)

        await message.answer(
            f"⏳ Спокійно 😏\nСпробуй через {hours} год {minutes} хв"
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

    await message.answer(f"{text}\n📏 Тепер: {size} см")


# =========================
# START
# =========================

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
