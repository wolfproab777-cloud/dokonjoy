const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const fs = require('fs');
const https = require('https');
const { spawn } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(__dirname));

// Хранилище зарегистрированных пользователей (в памяти)
const registeredUsers = new Set();

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// API проверки кода и регистрации
app.post('/api/verify', (req, res) => {
    let { phone, code } = req.body;

    if (!phone || !code) {
        return res.status(400).json({ success: false, message: "Telefon raqam va kod kiritilishi shart!" });
    }

    // Форматирование номера
    phone = phone.trim();
    if (!phone.startsWith('+')) {
        phone = '+' + phone;
    }

    // 1. Проверка на повторную регистрацию
    if (registeredUsers.has(phone)) {
        return res.json({ 
            success: false, 
            registered: true,
            message: "Sizning nomeringiz ro'yxatdan o'tgan!" 
        });
    }

    // 2. Чтение активных кодов из codes.json
    let activeCodes = {};
    const codesFilePath = path.join(__dirname, 'codes.json');
    if (fs.existsSync(codesFilePath)) {
        try {
            activeCodes = JSON.parse(fs.readFileSync(codesFilePath, 'utf8'));
        } catch (e) {
            activeCodes = {};
        }
    }

    // 3. Строгая проверка соответствия кода
    if (activeCodes[phone] && activeCodes[phone] === code.toString().trim()) {
        // Удаляем использованный код
        delete activeCodes[phone];
        fs.writeFileSync(codesFilePath, JSON.stringify(activeCodes));

        // Регистрируем номер
        registeredUsers.add(phone);

        return res.json({ 
            success: true, 
            message: "Muvaffaqiyatli ro'yxatdan o'tdingiz!" 
        });
    } else {
        return res.json({ 
            success: false, 
            message: "Kod noto'g'ri kiritildi! Iltimos, Telegram botdan kelgan kodni kiriting." 
        });
    }
});

// Запуск бота на Python
const pythonProcess = spawn('python3', ['main.py']);

pythonProcess.stdout.on('data', (data) => {
    console.log(`[Python Bot Log]: ${data}`);
});

pythonProcess.stderr.on('data', (data) => {
    console.error(`[Python Bot Error]: ${data}`);
});

// Авто-пинг для поддержания активности на Render
const SERVER_URL = 'https://dokonjoylashuuz.onrender.com';
setInterval(() => {
    https.get(SERVER_URL, (res) => {
        console.log(`[Auto-Ping] Status: ${res.statusCode}`);
    }).on('error', (err) => {
        console.error('[Auto-Ping Error]:', err.message);
    });
}, 14 * 60 * 1000);

app.listen(PORT, () => {
    console.log(`🚀 Server http://localhost:${PORT} portida ishga tushdi`);
});
