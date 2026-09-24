import os
import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Token Render Environment variables-dan olinadi
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

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

    await message.answer(
        f"✅ Tasdiqlash kodingiz: <b>{code}</b>\n\nUshbu kodni saytga kiriting.",
        parse_mode="HTML"
    )

if __name__ == '__main__':
    print("🤖 Python Telegram-boti muvaffaqiyatli ishga tushdi!")
    executor.start_polling(dp, skip_updates=True)
