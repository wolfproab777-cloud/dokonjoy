const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const https = require('https');
const { spawn } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Barcha statik fayllarni (index.html va boshqalar) ulash
app.use(express.static(__dirname));

// Bosh sahifaga kirganda index.html ni ko'rsatish
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// ==========================================
// NODE.JS ICHIDAN PYTHON BOTNI (main.py) ISHGA TUSHIRISH
// ==========================================
const pythonProcess = spawn('python3', ['main.py']);

pythonProcess.stdout.on('data', (data) => {
    console.log(`[Python Bot Log]: ${data}`);
});

pythonProcess.stderr.on('data', (data) => {
    console.error(`[Python Bot Error]: ${data}`);
});

pythonProcess.on('close', (code) => {
    console.log(`Python bot jarayoni yakunlandi. Kod: ${code}`);
});


// ==========================================
// RENDER SERVERNI 24/7 ONLAYN USHLASH (AVTO-PING)
// ==========================================
const SERVER_URL = 'https://dokonjoylashuuz.onrender.com';

setInterval(() => {
    https.get(SERVER_URL, (res) => {
        console.log(`[Auto-Ping] Server faol. Status: ${res.statusCode}`);
    }).on('error', (err) => {
        console.error('[Auto-Ping Error]:', err.message);
    });
}, 14 * 60 * 1000); // Har 14 daqiqada ping yuboradi


// Asosiy Express serverni ishga tushirish
app.listen(PORT, () => {
    console.log(`🚀 Asosiy Server (Node.js) http://localhost:${PORT} portida ishga tushdi`);
});
