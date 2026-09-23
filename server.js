const express = require('express');
const path = require('path');
const cors = require('cors');
const { spawn } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Statik fayllar uchun
app.use(express.static(path.join(__dirname, '.')));

// Python orqali SMS yuborish API endpointi
app.post('/api/send-sms', (req, res) => {
    const { phone } = req.body;

    if (!phone) {
        return res.status(400).json({ success: false, message: 'Telefon raqam kiritilmadi' });
    }

    // 6 xonali tasdiqlash kodi
    const code = Math.floor(100000 + Math.random() * 900000).toString();
    const message = `DokonJoy: Sizning tasdiqlash kodingiz: ${code}`;

    // Python skriptini chaqiramiz va argument sifatida phone hamda message uzatamiz
    // (Agar kompyuteringizda python3 bo'lsa, 'python' o'rniga 'python3' deb yozing)
    const pythonProcess = spawn('python', ['sms.py', phone, message]);

    let pythonData = '';

    pythonProcess.stdout.on('data', (data) => {
        pythonData += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python xatosi: ${data}`);
    });

    pythonProcess.on('close', (exitCode) => {
        const result = pythonData.trim();

        if (result === 'SUCCESS') {
            res.json({
                success: true,
                message: 'SMS muvaffaqiyatli yuborildi!',
                code: code
            });
        } else {
            res.status(500).json({
                success: false,
                message: 'SMS yuborishda xatolik yuz berdi',
                details: result
            });
        }
    });
});

// Qolgan barcha marshrutlar uchun index.html qaytarish
app.get(/(.*)/, (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
