# BUXDU API Integratsiyasi va Hybrid Ma'lumot Manbasi

## 📋 Umumiy Ma'lumot

HEMIS Log Tahlili Tizimi endi quyidagi xususiyatlarga ega:

### 🎯 Asosiy Xususiyatlar:
1. **File Rejmasi**: Foydalanuvchi Excel log faylinni yuklashi mumkin
2. **API Rejmasi**: BUXDU Student Management System API dan real-time ma'lumot olish
3. **Birlashtirilgan Rejim**: File va API ma'lumotlarini birlashtirib tahlil qilish
4. **Avtomatik Fallback**: Agar file bo'lmasa, avtomat ravishda API dan ma'lumot olish

---

## 🔌 BUXDU API Clienti (`buxdu_api_client.py`)

### BuxduAPIClient Klassi

Ma'lumot olish uchun asosiy sinf. BUXDU API bilan ulanish va ma'lumotni normallash.

#### Metodlar:

```python
# Talabalar ma'lumotlari
get_students(limit=100) -> pd.DataFrame
# Kurslar
get_courses(limit=100) -> pd.DataFrame
# Ro'yxatdan o'tishlar
get_enrollments(limit=100) -> pd.DataFrame
# Davomat
get_attendance(student_id=None, limit=100) -> pd.DataFrame
# Baholar
get_grades(limit=100) -> pd.DataFrame
# Foydalanuvchi faolliği
get_user_activities(user_id=None, limit=100) -> pd.DataFrame
# Barcha ma'lumotlar (hammasini olish)
get_all_data() -> Dict[str, pd.DataFrame]
# API holati tekshirish
check_api_health() -> bool
```

#### Xususiyatlari:
- ⏱️ **Rate Limiting**: Har bir so'rov orasida 0.1 sekund kutish
- ❌ **Error Handling**: API xatoliklarini marhamat bilan qayta ishash
- 📊 **Progress Reporting**: Katta ma'lumotlarni yuklashda progres ko'rsatish

---

### DataNormalizer Klassi

API ma'lumotlarini log formatiga aylantirish.

#### Metodlar:

```python
# API faolligini log formatiga aylantirish
normalize_activities(df: pd.DataFrame) -> pd.DataFrame

# Ro'yxatdan o'tishlardan sintetik log yaratish
create_synthetic_logs_from_enrollments(
    enrollments: pd.DataFrame, 
    students: pd.DataFrame
) -> pd.DataFrame

# File va API ma'lumotlarini birlashtirich
combine_data_sources(
    api_data: Dict,
    file_data: pd.DataFrame = None
) -> pd.DataFrame
```

#### Output Formati:
```
Ustunlar: [ID, Admin nomi, Yaratilgan, IP, Amal, So'rov, Xabar, Post]
```

---

## 🌐 Flask API Endpoints

### BUXDU Integratsiyasi Endpoints

#### 1. BUXDU API Holati
```
GET /api/buxdu/health
```

**Response:**
```json
{
    "api_available": true,
    "status": "connected",
    "timestamp": "2025-01-15T10:30:00"
}
```

#### 2. BUXDU API dan Ma'lumot Olish
```
POST /api/buxdu/fetch-data
```

**Response:**
```json
{
    "status": "success",
    "rows_fetched": 1500,
    "timestamp": "2025-01-15T10:30:00",
    "data_source": "BUXDU API"
}
```

#### 3. File va API ni Birlashtirich
```
POST /api/buxdu/combined-analysis
```

**Response:**
```json
{
    "status": "success",
    "total_rows": 17500,
    "data_source": "combined",
    "file_rows": 16037,
    "api_rows": 1463,
    "timestamp": "2025-01-15T10:30:00"
}
```

#### 4. Hozir Foydalanilayotgan Ma'lumot Manbasini Bilish
```
GET /api/data-source
```

**Response:**
```json
{
    "data_source": "file",
    "total_rows": 16037,
    "timestamp": "2025-01-15T10:30:00"
}
```

---

## 💻 Frontend Integratsiyasi

### Data Source Selector (Header)

Dashboard headerida yangi tugmalar:

```
📁 File    🌐 BUXDU API    🔗 Birlashtirilgan
```

**Ichida Tugmalar:**
- ✅ **File**: Excel log faylindan yukla
- ✅ **BUXDU API**: Tizimdagi BUXDU API dan olgan ma'lumotlarni yuklash
- ✅ **Birlashtirilgan**: File + API ma'lumotlarini birlashtirib analiz qilish

### Status Indicator

Har bir rejimda ma'lumot manbasining holati ko'rsatiladi:

```
✓ file - 16037 satir        (Muvaffaqiyatli)
✗ error - Ulanish xatosi    (Xato)
⟳ loading - Yuklanmoqda...  (Yuklanish jarayoni)
```

### JavaScript Funktsiyalari

#### `loadDataSource()`
Tanlangan ma'lumot manbasini yuklash va analiz qilish.

```javascript
// Foydalanuvchi radio tugmasini tanlaganda chaqiriladi
// Barcha tahlillarni qayta yuklaydi
loadDataSource();
```

#### `checkDataSourceStatus()`
Hozir foydalanilayotgan ma'lumot manbasini tekshirish.

```javascript
// Sahifa yuklanganda avtomatik chaqiriladi
checkDataSourceStatus();
```

---

## 🔄 Ma'lumot Almashinuvi Jarayoni

### 1. File Rejimida
```
1. Excel faylni yuklash (EXCEL_FILE)
2. Pandas DataFrame ga o'girish
3. Tahlillarni yaratish (Analytics, AI, Behavior)
4. Frontend da ko'rsatish
```

### 2. API Rejimida
```
1. BUXDU APIga ulanish
2. get_all_data() orqali barcha ma'lumot olish
3. DataNormalizer orqali log formatiga aylantirish
4. Tahlillarni yaratish
5. Frontend da ko'rsatish
```

### 3. Birlashtirilgan Rejimida
```
1. Excel faylni yukla (agar mavjud bo'lsa)
2. BUXDU API dan ma'lumot ol
3. combine_data_sources() orqali birlashtirich
4. Barcha tahlillarni qayta bajarich
5. Frontend da ko'rsatish
```

---

## ⚙️ Konfiguratsiya

### Environment O'zgaruvchilari

`.env` faylida (ixtiyoriy):
```
BUXDU_API_URL=https://student.buxdu.uz
BUXDU_API_TIMEOUT=10
BUXDU_RATE_LIMIT=0.1
```

### Python Konfiguratsiyasi

`app.py` da:
```python
EXCEL_FILE = 'Log-22_09_2025_12_09_24.xlsx'
data_source = "file"  # Boshlang'ich rejim
```

---

## 🛡️ Error Handling

### Mumkin bo'lgan Xatolar va Yechimlar

| Xato | Sababi | Yechim |
|------|--------|--------|
| `ModuleNotFoundError: requests` | requests kutubxonasi o'rnatilmagan | `pip install requests` |
| `BUXDU API not available` | API ulanish xatosi | VPN/Tarmoq tekshirich |
| `Empty DataFrame` | API ma'lumot qaytarmadi | API statusini tekshirich |
| `File not found` | Excel fayl yo'q | Upload tugmasini foydalanish |

### Try-Except Himoyasi

Barcha API so'rovlari try-except blokida himoyalangan:
```python
try:
    api_data = api_client.get_all_data()
except Exception as e:
    print(f"API Error: {e}")
    # Fallback demo dataga
    df = create_demo_data()
```

---

## 📊 Keling Test Qilamiz!

### 1. File Rejimini Test Qilish
```bash
1. Dashboard ochish: http://localhost:5000
2. 📁 File radio tugmasini tanlash
3. "Ma'lumot Manbasini Yangilash" tugmasini bosish
4. Status: ✓ file - 16037 satir
```

### 2. API Rejimini Test Qilish
```bash
1. 🌐 BUXDU API radio tugmasini tanlash
2. "Ma'lumot Manbasini Yangilash" tugmasini bosish
3. API mavjud bo'lsa: Status: ✓ BUXDU API - XXXX satir
4. API mavjud bo'lmasa: Status: ✗ error
```

### 3. Birlashtirilgan Rejimini Test Qilish
```bash
1. 🔗 Birlashtirilgan radio tugmasini tanlash
2. "Ma'lumot Manbasini Yangilash" tugmasini bosish
3. Status: ✓ combined - 17500+ satir
4. File va API ma'lumotlarini ko'rish
```

---

## 🎯 Keyingi Qadamlar

### Ushbu Versiyada Taklif Etilgan Xususiyatlar:

- [ ] **Real-time Refresh**: 5 minutda avtomatik yangilash
- [ ] **Caching**: API ma'lumotlarini kesh qilish (5 min TTL)
- [ ] **Scheduled Sync**: O'tgan vaqtda avtomatik sync
- [ ] **Email Reports**: Email orqali hisobotlarni yuborish
- [ ] **Database Persistence**: SQLite/PostgreSQL saqlash
- [ ] **Authentication**: Login tizimi qo'shish
- [ ] **Notifications**: Push bildirishnomalar

---

## 📝 Kod Misollari

### Python da API Foydalanika

```python
from buxdu_api_client import BuxduAPIClient, DataNormalizer

# API clientini yaratish
client = BuxduAPIClient()

# API holati tekshirish
if client.check_api_health():
    # Barcha ma'lumotlarni olish
    api_data = client.get_all_data()
    
    # Log formatiga aylantirish
    df = DataNormalizer.combine_data_sources(api_data)
    
    # Tahlil qilish
    from analytics import LogAnalytics
    analytics = LogAnalytics(df)
    stats = analytics.get_stats()
```

### JavaScript da Frontend Foydalanika

```javascript
// Data source o'zgarish holati
document.querySelectorAll('input[name="dataSource"]')
    .forEach(radio => {
        radio.addEventListener('change', loadDataSource);
    });

// API health tekshirish
fetch('/api/buxdu/health')
    .then(r => r.json())
    .then(data => console.log('API Status:', data.api_available));

// Combined analysis qilish
fetch('/api/buxdu/combined-analysis', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'}
})
    .then(r => r.json())
    .then(data => console.log('Combined rows:', data.total_rows));
```

---

## 📚 Fayl Tuzilmasi

```
infografmaker.uz/
├── app.py                       # Asosiy Flask app (yangilangan)
├── buxdu_api_client.py         # NEW: BUXDU API integration
├── analytics.py                # Log analytics
├── ai_analyzer.py              # AI insights
├── action_profiler.py          # Action profiling
├── behavior_analyzer.py        # Behavioral analysis
├── export_manager.py           # Export functionality
├── charts.py                   # Chart generation
├── pdf_export.py               # PDF generation
├── templates/
│   └── index.html             # Frontend (yangilangan)
├── requirements.txt            # Dependencies
├── BUXDU_API_INTEGRATION.md   # NEW: This file
└── Log-22_09_2025_12_09_24.xlsx # Sample data
```

---

## 🚀 Boshlanish

### 1. Server Ishga Tushirish
```bash
cd d:\Xampp\htdocs\infografmaker.uz
python app.py
```

### 2. Dashboard Ochish
```
http://localhost:5000
```

### 3. Data Source Tanlash
- File, API yoki Birlashtirilgan rejimni tanlang
- "Ma'lumot Manbasini Yangilash" tugmasini bosing
- Tahlillar avtomatik yuklonadi

### 4. Eksport Qilish
- CSV, Excel, JSON formatlarida eksport
- PDF hisoboti yaratish

---

## 📞 Qo'llab-Quvvatlash

**Biron xato paydo bo'lsa:**
1. Browser konsolini ochish (F12 → Console)
2. Server logsini tekshirish
3. API health endpointini test qilish: `GET /api/buxdu/health`
4. Network tabl da so'rovlarni tekshirish

---

## ✨ Hammasini Bildi!

Endi sizda:
- ✅ File yuklovchi log analiz tizimi
- ✅ BUXDU API integratsiyasi
- ✅ Hybrid ma'lumot manbasi
- ✅ AI-powered insights
- ✅ Behavioral analysis
- ✅ Multi-format export
- ✅ Professional dashboard

**Foydalanish boshlang!** 🎉
