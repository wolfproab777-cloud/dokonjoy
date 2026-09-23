import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils import executor

API_TOKEN = 'BOT_TOKENINGIZNI_SHUYERGA_YOZING'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_codes = {}

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True))
    
    # WebApp tugmasini ham ulashingiz mumkin
    await message.answer(
        f"Xush kelibsiz, <b>{message.from_user.first_name}</b>!\n"
        "Ro'yxatdan o'tish uchun telefon raqamingizni yuboring:", 
        reply_markup=kb, 
        parse_mode="HTML"
    )

@dp.message_handler(content_types=['contact'])
async def handle_contact(message: types.Message):
    phone = message.contact.phone_number
    if not phone.startswith('+'):
        phone = '+' + phone
        
    code = str(random.randint(100000, 999999))
    user_codes[phone] = code
    
    await message.answer(
        f"👤 <b>Foydalanuvchi:</b> {message.from_user.full_name}\n"
        f"✅ Tasdiqlash kodingiz: <b>{code}</b>", 
        parse_mode="HTML"
    )

# Saytdan geolokatsiya yoki profil ma'lumotlari yuborilganda qabul qilish
@dp.message_handler(content_types=['web_app_data'])
async def handle_web_app_data(message: types.Message):
    data = message.web_app_data.data
    await message.answer(f"📩 Saytdan qabul qilingan ma'lumot:\n<code>{data}</code>", parse_mode="HTML")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
