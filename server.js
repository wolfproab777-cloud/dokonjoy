const express = require('express');
const TelegramBot = require('node-telegram-bot-api');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const https = require('https');

// ==========================================
// 1. TELEGRAM BOT SOZLAMALARI
// ==========================================
// BotFather bergan API tokenni shu yerga kiriting
const BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE';
const bot = new TelegramBot(BOT_TOKEN, { polling: true });

// Tasdiqlash kodlarini saqlash uchun xotira
const activeCodes = {};

// /start buyrug'i kelganda
bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(
        chatId,
        `Salom, ${msg.from.first_name}!\n\nSaytdan ro'yxatdan o'tish uchun telefon raqamingizni yuboring:`,
        {
            reply_markup: {
                keyboard: [[{ text: "📱 Telefon raqamni yuborish", request_contact: true }]],
                resize_keyboard: true,
                one_time_keyboard: true
            }
        }
    );
});

// Kontakt qabul qilinganda
bot.on('contact', (msg) => {
    const chatId = msg.chat.id;
    let phone = msg.contact.phone_number;

    if (!phone.startsWith('+')) {
        phone = '+' + phone;
    }

    // 6 xonali tasodifiy kod
    const code = Math.floor(100000 + Math.random() * 900000).toString();
    activeCodes[phone] = code;

    bot.sendMessage(
        chatId,
        `✅ Tasdiqlash kodingiz: <b>${code}</b>\n\nUshbu kodni saytga kiriting.`,
        { parse_mode: 'HTML' }
    );
});

// WebApp orqali kelgan ma'lumotlarni ushlash
bot.on('message', (msg) => {
    if (msg.web_app_data) {
        const chatId = msg.chat.id;
        const data = msg.web_app_data.data;
        bot.sendMessage(chatId, `📩 Saytdan qabul qilingan ma'lumot:\n<code>${data}</code>`, { parse_mode: 'HTML' });
    }
});


// ==========================================
// 2. EXPRESS WEB SERVER SOZLAMALARI
// ==========================================
const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Barcha statik fayllarni ildiz papkadan ulash
app.use(express.static(__dirname));

// Bosh sahifa
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Kodni tekshirish uchun API marshruti
app.post('/api/verify', (req, res) => {
    const { phone, code } = req.body;

    if (!phone || !code) {
        return res.status(400).json({ success: false, message: "Telefon va kod kiritilishi shart!" });
    }

    if (activeCodes[phone] && activeCodes[phone] === code) {
        delete activeCodes[phone]; // Kod ishlatilgach o'chiriladi
        return res.json({ success: true, message: "Muvaffaqiyatli tasdiqlandi!" });
    }

    return res.json({ success: false, message: "Kod noto'g'ri yoki muddati o'tgan!" });
});


// ==========================================
// 3. RENDER UYQUGA KETMASLIGI UCHUN AVTO-PING
// ==========================================
// Render manzilini ko'rsating
const SERVER_URL = 'https://dokonjoylashuuz.onrender.com';

setInterval(() => {
    https.get(SERVER_URL, (res) => {
        console.log(`[Auto-Ping] Server faol ushlanmoqda. Status: ${res.statusCode}`);
    }).on('error', (err) => {
        console.error('[Auto-Ping Error]:', err.message);
    });
}, 14 * 60 * 1000); // Har 14 daqiqada ping beradi


// Serverni ishga tushirish
app.listen(PORT, () => {
    console.log(`🚀 Server http://localhost:${PORT} manzilida ishlamoqda`);
});
