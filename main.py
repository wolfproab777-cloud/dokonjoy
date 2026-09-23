import random
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext

app = FastAPI()

# CORS sozlamalari (Frontend serverga ulanishi uchun)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# SQLite Ma'lumotlar bazasini yaratish
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Vaqtinchalik SMS kodlarini saqlash
sms_codes = {}

class PhoneModel(BaseModel):
    phone: str

class VerifyCodeModel(BaseModel):
    phone: str
    code: str

class RegisterModel(BaseModel):
    phone: str
    code: str
    password: str

class LoginModel(BaseModel):
    phone: str
    password: str

# 1. SMS Kod Yuborish
@app.post("/api/send-code")
def send_code(data: PhoneModel):
    code = str(random.randint(100000, 999999))
    sms_codes[data.phone] = code
    
    print("\n" + "="*40)
    print(f"📱 [{data.phone}] uchun SMS Kod: {code}")
    print("="*40 + "\n")
    
    return {"status": "success", "message": "SMS kod yuborildi"}

# 2. Kodni Tekshirish
@app.post("/api/verify-code")
def verify_code(data: VerifyCodeModel):
    if data.phone in sms_codes and sms_codes[data.phone] == data.code:
        return {"status": "success", "message": "Kod to'g'ri"}
    raise HTTPException(status_code=400, detail="Xato kod kiritildi!")

# 3. Ro'yxatdan o'tish va Parolni Bazaga Saqlash
@app.post("/api/register")
def register(data: RegisterModel):
    if data.phone not in sms_codes or sms_codes[data.phone] != data.code:
        raise HTTPException(status_code=400, detail="SMS kod noto'g'ri yoki muddati o'tgan!")

    hashed_password = pwd_context.hash(data.password)

    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (phone, password_hash) VALUES (?, ?)", (data.phone, hashed_password))
        conn.commit()
        conn.close()
        
        del sms_codes[data.phone]
        return {"status": "success", "message": "Ro'yxatdan o'tdingiz!"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Bu telefon raqam allaqachon ro'yxatdan o'tgan!")

# 4. Tizimga Kirish (Login)
@app.post("/api/login")
def login(data: LoginModel):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE phone = ?", (data.phone,))
    user = cursor.fetchone()
    conn.close()

    if not user or not pwd_context.verify(data.password, user[0]):
        raise HTTPException(status_code=400, detail="Telefon raqam yoki parol xato!")

    return {"status": "success", "message": "Muvaffaqiyatli kirdingiz!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
