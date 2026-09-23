const express = require('express');
const path = require('path');
const proxy = require('express-http-proxy');

const app = express();
const PORT = process.env.PORT || 3000;

// /api bilan kelgan barcha so'rovlarni Python FastAPI (8000-port) ga yo'naltirish
app.use('/api', proxy('http://localhost:8000'));

// Statik fayllarni (index.html va boshqalar) tarqatish
app.use(express.static(path.join(__dirname, '.')));

// SPA (Single Page Application) yo'naltirishi
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Serverni ishga tushirish
app.listen(PORT, () => {
    console.log(`Node.js Frontend server ishga tushdi: http://localhost:${PORT}`);
    console.log(`API so'rovlari http://localhost:8000 ga yo'naltiriladi`);
});
