"""
README - HEMIS Log Tahlili va Infografika Tizimi

Ishga tushirish:
1. Paketlarni o'rnatish:
   pip install -r requirements.txt

2. Flask dasturini ishga tushirish:
   python app.py

3. Veb-saytga kirish:
   http://localhost:5000

API Endpoints:
- GET /api/stats - Asosiy statistika
- GET /api/admin-activity - Admin faolligi
- GET /api/action-distribution - Amal tarqatilishi
- GET /api/ip-analysis - IP tahlili
- GET /api/timeline - Vaqt bo'yicha grafik
- GET /api/export-pdf - PDF ga eksport
- POST /api/search - Loglarni izlash

Struktura:
- app.py: Flask asosiy dastur
- analytics.py: Ma'lumot tahlil moduli
- charts.py: Chartlar yaratish
- pdf_export.py: PDF eksport
- templates/index.html: Frontend
- Log-22_09_2025_12_09_24.xlsx: Manba ma'lumotlar
"""

print(__doc__)
