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
app.use(express.static(__dirname));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Python (FastAPI + Telegram Bot) fonda ishga tushiriladi
const pythonProcess = spawn('python', ['main.py']);

pythonProcess.stdout.on('data', (data) => {
    console.log(`[Python Bot Log]: ${data}`);
});

pythonProcess.stderr.on('data', (data) => {
    console.error(`[Python Bot Error]: ${data}`);
});

pythonProcess.on('close', (code) => {
    console.log(`Python jarayoni tugadi, kod: ${code}`);
});

// Render uchun avto-ping (inaktivlikdan saqlash)
const SERVER_URL = process.env.RENDER_EXTERNAL_URL || 'https://dokonjoylashuuz.onrender.com';
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
