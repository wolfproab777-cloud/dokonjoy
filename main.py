import os
import random
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

CODES_FILE = "codes.json"

def save_code(phone, code):
    data = {}
    if os.path.exists(CODES_FILE):
        try:
            with open(CODES_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            data = {}
    
    data[phone] = code
    with open(CODES_FILE, "w") as f:
        json.dump(data, f)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)
    keyboard.add(button)
    
    await message.answer(
        f"Salom, {message.from_user.first_name}!\n\nSaytdan ro'yxatdan o'tish uchun telefon raqamingizni yuboring:",
        reply_markup=keyboard
    )

@dp.message_handler(content_types=types.ContentType.CONTACT)
async def process_contact(message: types.Message):
    phone = message.contact.phone_number
    if not phone.startswith('+'):
        phone = '+' + phone

    code = str(random.randint(100000, 999999))
    
    # Сохраняем код для проверки через server.js
    save_code(phone, code)

    await message.answer(
        f"✅ Tasdiqlash kodingiz: <b>{code}</b>\n\nUshbu kodni saytga kiriting.",
        parse_mode="HTML"
    )

if __name__ == '__main__':
    print("🤖 Python Telegram-boti ishga tushdi!")
    executor.start_polling(dp, skip_updates=True)
