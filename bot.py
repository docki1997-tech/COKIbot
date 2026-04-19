import telebot
import random
import time
import sqlite3
import os

API_TOKEN = os.getenv("8724617956:AAHMNujCaIwa-nmtGzy-4rPW0RQqG6GfZHQ")

bot = telebot.TeleBot(API_TOKEN)

COOLDOWN = 20 * 60 * 60

conn = sqlite3.connect("bot.db", check_same_thread=False)
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


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "😏 Привіт! Напиши /boobs щоб грати")


@bot.message_handler(commands=['boobs'])
def boobs(message):
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

        bot.reply_to(
            message,
            f"⏳ Спробуй через {hours} год {minutes} хв"
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

    bot.reply_to(message, f"{text}\n📏 Тепер: {size} см")


bot.infinity_polling()
