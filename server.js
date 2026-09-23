const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Statik fayllarni (index.html va boshqalar) ulash
app.use(express.static(path.join(__dirname, '.')));

// Barcha sahifalarga index.html ni qaytarish
app.get(/(.*)/, (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Serverni ishga tushirish
app.listen(PORT, () => {
    console.log(`Server ishladi: http://localhost:${PORT}`);
});
