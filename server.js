const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');

// ==========================================
// EXPRESS SERVER SOZLAMALARI (WEB SERVER)
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

// Test API marshrut
app.get('/api/status', (req, res) => {
    res.json({ success: true, message: "Server muvaffaqiyatli ishlamoqda!" });
});

// Serverni ishga tushirish
app.listen(PORT, () => {
    console.log(`🚀 Server http://localhost:${PORT} manzilida ishlamoqda...`);
});
