# 🚀 Tez Boshlash (Quick Start Guide)

## ⚡ 5 Daqiqada Tizimni Ishga Tushirish

### 1️⃣ Server Ishga Tushirish
```bash
cd d:\Xampp\htdocs\infografmaker.uz
python app.py
```

**Natija:**
```
Loaded 16037 rows from file
Analysis initialized - Data source: file
Running on http://127.0.0.1:5000
```

### 2️⃣ Dashboard Ochish
```
http://localhost:5000
```

### 3️⃣ Ma'lumot Manbasini Tanlash

Header'da 3 ta variant:
```
📁 File          ← Yuklanmis Excel fayldan (DEFAULT)
🌐 BUXDU API     ← Real-time BUXDU systemasidan
🔗 Birlashtirilgan ← File + API birlashtirib
```

### 4️⃣ "Ma'lumot Manbasini Yangilash" Bosmak
- Server avtomatik tahlillarni qayta qiladi
- Charts yangilanadi
- Status ko'rsatiladi

### 5️⃣ Dashboard Jadvallari

| Qisim | Tavsifi |
|-------|---------|
| 📊 Statistika | Jami loglar, adminlar, IP'lar |
| 📈 Grafiklar | Admin activity, actions, IPs |
| ⚠️ Notekislar | Anomalies, risk scores |
| 🤖 AI Insights | Smart recommendations |
| 👤 Adminlar | Admin profiles va rollar |
| 📊 Tahlillar | Data movement, behavior |

---

## 📋 Asosiy Operatsiyalar

### 1. Loglarni Filtrlash

```
Filtrlash Qismi'da:
1. Admin nomi kiriting
2. IP manzil kiriting
3. Amal turini tanlang
4. Sana diapazonini belgilang
5. "Filtrlash" tugmasini bosing
```

### 2. Admin Profileni Ko'rish

```
Admin Profillari qismida:
1. Admin kartasini topish
2. "Batafsil" tugmasini bosing
3. Admin amallarini ko'rish
4. Risk ballarini tekshirish
```

### 3. Eksport Qilish

```
Tugmalar'da:
- "PDF ga Eksport Qilish" → PDF hisobot
- API Endpoints:
  - /api/export/csv → CSV fayl
  - /api/export/excel → Excel fayl
  - /api/export/json → JSON data
```

### 4. AI Insights Olish

```
Dashboard'da:
- AI Insights kartalarini ko'rish
- Recommendations qismi
- Predictions tahlili
- Risk assessment natijalar
```

---

## 🔌 API Endpoint'larni Test Qilish

### Curl Orqali Test

```bash
# Statistika olish
curl http://localhost:5000/api/stats

# Risk scores
curl http://localhost:5000/api/risk-scores

# BUXDU API status
curl http://localhost:5000/api/buxdu/health

# Admin profili
curl http://localhost:5000/api/admin/profile/Ali%20Shodmonov

# Data source
curl http://localhost:5000/api/data-source
```

### Browser Console'da

```javascript
// Statistika
fetch('/api/stats').then(r => r.json()).then(d => console.log(d))

// AI insights
fetch('/api/ai/insights').then(r => r.json()).then(d => console.log(d))

// Barcha admin rollar
fetch('/api/behavior/user-roles').then(r => r.json()).then(d => console.log(d))

// BUXDU API dan ma'lumot olish
fetch('/api/buxdu/fetch-data', {method:'POST'})
    .then(r => r.json()).then(d => console.log(d))
```

---

## 🛠️ Troubleshooting

### Server Ishga Tushmaydi

**Xato:**
```
ModuleNotFoundError: No module named 'requests'
```

**Yechim:**
```bash
pip install requests
```

### BUXDU API Ulanmaydi

**Status:**
```
BUXDU API not available
```

**Yechim:**
1. VPN ni tekshiring
2. Internet ulanishini tekshiring
3. BUXDU API URL'sini tekshiring

### Charts Ko'rinmaydi

**Yechim:**
1. F12 → Console'ni ochish
2. Xatolarni tekshirish
3. Browser cache tozalash (Ctrl+Shift+Del)

### Slow Performance

**Yechim:**
1. Browser'ni restart qilish
2. Terminal'da Flask server'ni restart qilish
3. System resurslarini tekshirish

---

## 📊 Sample Queries

### 1. Eng Faol Adminlarni Topish
```
GET /api/admin-activity
```

**Natija:**
```json
{
    "labels": ["Ali Shodmonov", "Zokir Abdullayev", ...],
    "data": [1250, 980, 750, ...]
}
```

### 2. Anomaliyalarni Bilish
```
GET /api/anomalies
```

**Natija:**
```json
{
    "anomalies": [
        {
            "admin": "Ali Shodmonov",
            "type": "multi_ip_access",
            "severity": "medium"
        }
    ]
}
```

### 3. Risk Scores Olish
```
GET /api/risk-scores
```

**Natija:**
```json
{
    "scores": [
        {
            "admin": "Ali Shodmonov",
            "risk_score": 65,
            "level": "medium"
        }
    ]
}
```

---

## 🎯 Common Use Cases

### Use Case 1: Shubhali Faollikni Kuzatish

```
1. Dashboard'ga kirich
2. "Notekis Faollik" qismiga o'ting
3. Suspicious sequences'ni ko'ring
4. Admin profilini batafsil tahlil qiling
5. Risk factors'ni o'rganish
```

### Use Case 2: Haftalik Hisobot Yaratish

```
1. Sana diapazonini belgilang
2. "PDF ga Eksport Qilish" tugmasini bosing
3. PDF fayl yuklab olinadi
4. Email orqali jo'nating
```

### Use Case 3: Yangi Admin'ni Tekshirish

```
1. Admin nomini "Filtrlash"'ga kiriting
2. Admin profileni achish
3. Tipik saatlarni ko'rish
4. Asosiy amallarini tahlil qilish
5. Risk level'ni aniqlash
```

---

## 🔑 Muhim Qisqartmalar

| Qisqartma | Mazmuni |
|-----------|---------|
| Ctrl+Shift+Del | Cache tozalash |
| F12 | Developer Tools |
| Ctrl+Shift+I | Inspector |
| Ctrl+Shift+K | Console |
| Ctrl+Shift+E | Network |

---

## 📱 Dashboard Sections

### Statistics (Statistika)
```
[Jami Loglar]  [Adminlar]  [IP Manzilar]  [Amallar]
     16K            12         8             50
```

### Charts (Grafiklar)
```
Bar Chart: Top 10 Admins
Pie Chart: Action Distribution
Line Chart: Timeline Trends
```

### Filters (Filtrlash)
```
[Admin Search] [IP] [Action Type] [Date Range]
                          [Filtrlash]
```

### Anomalies (Notekislar)
```
- Multi IP access
- Failed logins
- Odd hours activity
- Bulk operations
```

### Risk Scores (Xavf Ballari)
```
Admin Name      Risk Score    Level
Ali Shodmonov      75        HIGH
Zokir Abdullayev   45        MEDIUM
Farida Karimova    20        LOW
```

### AI Insights (AI Tushuncha)
```
- Pattern Analysis
- Smart Recommendations
- Risk Predictions
- Behavior Insights
```

---

## 🌍 BUXDU API Integration

### Modes:

**File Mode** (Default)
```
Excel fayli → Tahlil → Dashboard
```

**API Mode**
```
BUXDU API → Normallashtirich → Tahlil → Dashboard
```

**Combined Mode**
```
File + API → Birlashtirich → Tahlil → Dashboard
```

### Switching Between Modes:

```javascript
// File Mode
document.querySelector('input[value="file"]').click();
loadDataSource();

// API Mode
document.querySelector('input[value="api"]').click();
loadDataSource();

// Combined Mode
document.querySelector('input[value="combined"]').click();
loadDataSource();
```

---

## 📖 Key Concepts

### Admin Risk Score (0-100)
```
0-25:   LOW (Yeşil)
25-50:  MEDIUM (Sariq)
50-100: HIGH (Qizil)
```

### Anomaly Types
```
1. Multi-IP: Bir admin ko'p IP'dan kirish
2. Failed: Ko'p login xataları
3. Odd Hours: 2-5 AM'da faollik
4. Bulk Ops: Ko'p amallar birdan
```

### User Roles
```
1. Super Admin: Barchaga huquq
2. System Admin: System operatsiyalari
3. Data Manager: Import/Export
4. Content Editor: CREATE/UPDATE
5. Viewer: Faqat ko'rish
6. Approver: Tasdiqlash/Rad etish
```

---

## 💡 Tips & Tricks

### Tip 1: Realtime Updates
```javascript
setInterval(() => {
    fetch('/api/stats').then(r => r.json()).then(updateUI)
}, 5000); // Har 5 sekundda
```

### Tip 2: Export with Filters
```javascript
// Filtered data ni eksport qilish
const filters = {
    admin: 'Ali Shodmonov',
    date_range: ['2025-01-01', '2025-01-15']
};
fetch('/api/export/csv', {
    method: 'POST',
    body: JSON.stringify(filters)
});
```

### Tip 3: Bulk Analysis
```javascript
// Bir nechta admin'ni birda tahlil qilish
const admins = ['Ali', 'Zokir', 'Farida'];
Promise.all(
    admins.map(a => fetch(`/api/admin/profile/${a}`))
);
```

---

## 🔗 Foydali Linklar

**Local Dashboard:**
```
http://localhost:5000
```

**API Endpoints:**
```
http://localhost:5000/api/stats
http://localhost:5000/api/admin-activity
http://localhost:5000/api/anomalies
http://localhost:5000/api/risk-scores
http://localhost:5000/api/buxdu/health
```

**Documentation:**
```
FEATURES.md              - Hammasini bilish
BUXDU_API_INTEGRATION.md - API haqida
README.md                - Umum ma'lumot
```

---

## ⚙️ Configuration

### Flask Settings (app.py)
```python
EXCEL_FILE = 'Log-22_09_2025_12_09_24.xlsx'  # Data file
DEBUG = True                                  # Debug mode
HOST = '0.0.0.0'                            # Bind address
PORT = 5000                                  # Port
```

### BUXDU API Settings (buxdu_api_client.py)
```python
BASE_URL = "https://student.buxdu.uz"       # API URL
API_ENDPOINT = "/rest"                       # API path
TIMEOUT = 10                                 # Timeout (sec)
RATE_LIMIT = 0.1                            # Rate limit (sec)
```

---

## 🎓 Learning Path

**Boshlang'ich Foydalanuvchi:**
1. Dashboard'ni tahlil qilish
2. Filtrlarni foydalanish
3. Admin profilelarni ko'rish

**O'rta Foydalanuvchi:**
1. API endpoint'larni test qilish
2. Export operatsiyalari
3. AI insights'ni o'rganish

**Advanced Foydalanuvchi:**
1. API integration
2. Custom analysis
3. Database integration

---

## ✅ Checklist

- [ ] Server ishga tushgan
- [ ] Dashboard ochilgan
- [ ] Statistika ko'rinishi
- [ ] Charts yangilanishi
- [ ] Filtrlash ishlashi
- [ ] Export ishlashi
- [ ] Admin profilesi ko'rinishi
- [ ] BUXDU API tekshirish
- [ ] Combined mode test

---

## 🎉 Done!

**Tabriklaymiz!** Siz bilan HEMIS Log Tahlili Tizimi ishga tushdi!

🚀 **Keyingi Qadamlar:**
- [ ] Loglarni tahlil qilishni boshlash
- [ ] Anomaliyalarni kuzatish
- [ ] Reports yaratish
- [ ] Team bilan ulashish

**Yordam kerak bo'lsa:** Dokumentatsiyani o'qing yoki server logs'ni tekshiring.

**Rahmat foydalanganingiz uchun!** 🙏

---

*Soxta: Quick Start Guide v1.0*  
*Oxirgi yangilash: 2025-01-15*
