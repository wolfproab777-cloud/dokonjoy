const express = require('express');
const TelegramBot = require('node-telegram-bot-api');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');

// ==========================================
// 1. TELEGRAM BOT SOZLAMALARI
// ==========================================
const API_TOKEN = 'BOT_TOKENINGIZNI_SHUYERGA_YOZING';

// Botni Polling rejimida ishga tushiramiz
const bot = new TelegramBot(API_TOKEN, { polling: true });

// Kodlarni vaqtincha saqlash uchun obyekt
const userCodes = {};

// /start komandasi uchun handler
bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    const firstName = msg.from.first_name || 'Foydalanuvchi';

    const opts = {
        reply_markup: {
            keyboard: [
                [{ text: "📱 Telefon raqamni yuborish", request_contact: true }]
            ],
            resize_keyboard: true,
            one_time_keyboard: true
        },
        parse_mode: 'HTML'
    };

    bot.sendMessage(
        chatId,
        `Xush kelibsiz, <b>${firstName}</b>!\nRo'yxatdan o'tish uchun telefon raqamingizni yuboring:`,
        opts
    );
});

// Kontakt (telefon raqami) qabul qilish handler
bot.on('contact', (msg) => {
    const chatId = msg.chat.id;
    let phone = msg.contact.phone_number;

    if (!phone.startsWith('+')) {
        phone = '+' + phone;
    }

    // 6 xonali random kod generatsiyasi
    const code = Math.floor(100000 + Math.random() * 900000).toString();
    userCodes[phone] = code;

    const fullName = `${msg.from.first_name || ''} ${msg.from.last_name || ''}`.trim();

    bot.sendMessage(
        chatId,
        `👤 <b>Foydalanuvchi:</b> ${fullName}\n✅ Tasdiqlash kodingiz: <b>${code}</b>`,
        { parse_mode: 'HTML' }
    );
});

// Telegram WebApp orqali kelgan ma'lumotni ushlash
bot.on('message', (msg) => {
    if (msg.web_app_data) {
        const chatId = msg.chat.id;
        const data = msg.web_app_data.data;
        bot.sendMessage(chatId, `📩 Saytdan qabul qilingan ma'lumot:\n<code>${data}</code>`, { parse_mode: 'HTML' });
    }
});


// ==========================================
// 2. EXPRESS SERVER SOZLAMALARI (WEB SERVER)
// ==========================================
const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Statik fayllarni (index.html, css, js) ulash
app.use(express.static(path.join(__dirname, 'public')));

// Bosh sahifa
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Telegram orqali yuborilgan kodni API orqali tekshirish marshruti
app.post('/api/verify-code', (req, res) => {
    const { phone, code } = req.body;

    if (!phone || !code) {
        return res.status(400).json({ success: false, message: "Telefon raqam va kod kiritilishi shart!" });
    }

    // Kodni tekshirish
    if (userCodes[phone] && userCodes[phone] === code) {
        delete userCodes[phone]; // Kod bir marta ishlatilgach o'chiriladi
        return res.json({ success: true, message: "Kod to'g'ri tasdiqlandi!" });
    } else {
        return res.json({ success: false, message: "Kod noto'g'ri yoki muddati o'tgan!" });
    }
});

// Serverni ishga tushirish
app.listen(PORT, () => {
    console.log(`🚀 Server http://localhost:${PORT} manzilida ishlamoqda...`);
    console.log(`🤖 Telegram Bot faollashtirildi.`);
});
