"""
Action Profiler va Semantic Analyzer
Har bir admin/IP uchun detailed action profile va behavior analysis
"""

import pandas as pd
from collections import defaultdict, Counter
import re

class ActionProfiler:
    """Adminlar va IPlar uchun detailed behavioral profiles"""
    
    def __init__(self, df):
        self.df = df
        self.action_descriptions = self._init_action_descriptions()
    
    def _init_action_descriptions(self):
        """Amallarni odam tushunadigan tilga tarjima qilish"""
        return {
            # Common CRUD Operations
            'CREATE': {
                'uz': 'Yangi ma\'lumot qo\'shish',
                'description': 'Tizimga yangi foydalanuvchi, kurs, yoki ma\'lumot yaratildi',
                'severity': 'low',
                'category': 'Data Management'
            },
            'READ': {
                'uz': 'Ma\'lumotni o\'qish',
                'description': 'Tizimdan ma\'lumotni ko\'rish yoki yuklab olish',
                'severity': 'low',
                'category': 'Data Access'
            },
            'UPDATE': {
                'uz': 'Ma\'lumotni tahrirlash',
                'description': 'Mavjud ma\'lumotlar o\'zgartirildi yoki yangilandi',
                'severity': 'medium',
                'category': 'Data Management'
            },
            'DELETE': {
                'uz': 'Ma\'lumotni o\'chirish',
                'description': 'Ma\'lumotlar tizimdan o\'chirildi',
                'severity': 'high',
                'category': 'Data Management'
            },
            'LOGIN': {
                'uz': 'Tizimga kirish',
                'description': 'Admin tizimga kiripti va session yaratildi',
                'severity': 'low',
                'category': 'Authentication'
            },
            'LOGOUT': {
                'uz': 'Tizimdan chiqish',
                'description': 'Admin tizimdan chiqib sessionni tugatdi',
                'severity': 'low',
                'category': 'Authentication'
            },
            'EXPORT': {
                'uz': 'Ma\'lumotni eksport qilish',
                'description': 'Ma\'lumotlar CSV, Excel yoki boshqa formatda yuklab olindi',
                'severity': 'medium',
                'category': 'Data Export'
            },
            'IMPORT': {
                'uz': 'Ma\'lumotni import qilish',
                'description': 'Tashqi fayldan ma\'lumotlar tizimga kiritildi',
                'severity': 'high',
                'category': 'Data Import'
            },
            'APPROVE': {
                'uz': 'Ma\'lumotni tasdiqlash',
                'description': 'Talab yoki o\'zgarish tasdiqlandi va tashrif bopti',
                'severity': 'medium',
                'category': 'Approval'
            },
            'REJECT': {
                'uz': 'Taqdimotni rad etish',
                'description': 'Talab yoki o\'zgarish rad etildi',
                'severity': 'medium',
                'category': 'Approval'
            },
            'VIEW': {
                'uz': 'Sahifani ko\'rish',
                'description': 'Admin ma\'lum bir sahifani yoki modulni ko\'rdi',
                'severity': 'low',
                'category': 'Navigation'
            },
            'DOWNLOAD': {
                'uz': 'Faylni yuklab olish',
                'description': 'FayL yoki dokumentlar yuklab olindi',
                'severity': 'medium',
                'category': 'File Management'
            },
            'UPLOAD': {
                'uz': 'Fayl yuklash',
                'description': 'FayL yoki dokumentlar tizimga yuklandi',
                'severity': 'medium',
                'category': 'File Management'
            },
            'CHANGE_PASSWORD': {
                'uz': 'Parolni o\'zgartirish',
                'description': 'Admin parolini o\'zgartirdi',
                'severity': 'low',
                'category': 'Security'
            },
            'RESET_PASSWORD': {
                'uz': 'Parolni qayta o\'rnatish',
                'description': 'Admin parolini administrator qayta o\'rnatti',
                'severity': 'high',
                'category': 'Security'
            },
            'GRANT_PERMISSION': {
                'uz': 'Huquq berish',
                'description': 'Adminning huquqlari yoki rolli o\'zgartirildi',
                'severity': 'high',
                'category': 'Access Control'
            },
            'REVOKE_PERMISSION': {
                'uz': 'Huquqni olib tashlash',
                'description': 'Adminning huquqlari yoki rolli olib tashlandi',
                'severity': 'high',
                'category': 'Access Control'
            },
            'SEARCH': {
                'uz': 'Izlash',
                'description': 'Ma\'lumotlar ichida qidirish amalga oshirildi',
                'severity': 'low',
                'category': 'Navigation'
            },
            'FILTER': {
                'uz': 'Filtrlash',
                'description': 'Ma\'lumotlarni shartlari bo\'yicha filtrlash amalga oshirildi',
                'severity': 'low',
                'category': 'Navigation'
            },
            'REPORT': {
                'uz': 'Hisoboti yaratish',
                'description': 'Ma\'lumotlar asosida hisoboti yaratildi',
                'severity': 'medium',
                'category': 'Reporting'
            },
            'BACKUP': {
                'uz': 'Zaxira nusxa olish',
                'description': 'Ma\'lumotlar zaxira nusxasi yaratildi',
                'severity': 'high',
                'category': 'System Maintenance'
            },
            'RESTORE': {
                'uz': 'Zaxiradan qaytarish',
                'description': 'Ma\'lumotlar zaxira nusxadan qaytarildi',
                'severity': 'high',
                'category': 'System Maintenance'
            }
        }
    
    def get_action_explanation(self, action):
        """Amalning tafsilot tavsifini olish"""
        if action in self.action_descriptions:
            return self.action_descriptions[action]
        
        # Agar action topilmasa, unga algoritmik tarjima
        return {
            'uz': action.replace('_', ' ').lower(),
            'description': f'{action} amali bajarildi',
            'severity': 'medium',
            'category': 'Other'
        }
    
    def create_admin_profile(self, admin_name):
        """Har bir admin uchun detailed profile yaratish"""
        admin_logs = self.df[self.df['Admin nomi'] == admin_name]
        
        if len(admin_logs) == 0:
            return None
        
        # Amallar statistikasi
        action_counts = admin_logs['Amal'].value_counts().to_dict()
        
        profile = {
            'admin': admin_name,
            'total_actions': len(admin_logs),
            'unique_ips': admin_logs['IP'].nunique(),
            'ips': admin_logs['IP'].unique().tolist(),
            'action_summary': {},
            'risk_indicators': [],
            'behavioral_pattern': '',
            'typical_hours': [],
            'most_common_actions': []
        }
        
        # Har bir amal uchun tavsif
        for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            explanation = self.get_action_explanation(action)
            profile['action_summary'][action] = {
                'count': count,
                'percentage': round((count / len(admin_logs)) * 100, 2),
                'description': explanation['uz'],
                'category': explanation['category'],
                'severity': explanation['severity']
            }
            profile['most_common_actions'].append({
                'action': action,
                'count': count,
                'description_uz': explanation['uz']
            })
        
        # Soat bo'yicha pattern
        admin_logs['Soat'] = pd.to_datetime(admin_logs['Yaratilgan'], format='%d.%m.%Y %H:%M:%S', errors='coerce').dt.hour
        hourly = admin_logs['Soat'].value_counts().sort_index()
        profile['typical_hours'] = hourly.index.tolist()
        
        # Behavioral pattern ta'rifi
        if len(admin_logs) > 100:
            profile['behavioral_pattern'] = 'Ko\'p faol admin - o\'z ishiga mas\'ul'
        elif admin_logs['Amal'].nunique() > 5:
            profile['behavioral_pattern'] = 'Turli amallarni bajaradi - universal admin'
        else:
            profile['behavioral_pattern'] = 'Maxsus amallarni bajaradi'
        
        return profile
    
    def create_ip_profile(self, ip_address):
        """IP manzil uchun profile"""
        ip_logs = self.df[self.df['IP'] == ip_address]
        
        if len(ip_logs) == 0:
            return None
        
        profile = {
            'ip': ip_address,
            'total_requests': len(ip_logs),
            'unique_admins': ip_logs['Admin nomi'].nunique(),
            'admins': ip_logs['Admin nomi'].unique().tolist(),
            'actions': ip_logs['Amal'].value_counts().to_dict(),
            'risk_level': self._calculate_ip_risk(ip_logs),
            'access_pattern': ''
        }
        
        # Access pattern ta'rifi
        if profile['unique_admins'] == 1:
            profile['access_pattern'] = 'Single user - bitta admin faqat shu IPdan kiradi'
        elif profile['unique_admins'] > 10:
            profile['access_pattern'] = 'Multi-user shared - ko\'p adminlar shu IPdan kiradi'
        else:
            profile['access_pattern'] = 'Limited multi-user - ozgina adminlar shu IPdan kiradi'
        
        return profile
    
    def _calculate_ip_risk(self, ip_logs):
        """IP uchun risk level"""
        risk = 0
        
        if ip_logs['Admin nomi'].nunique() > 10:
            risk += 30
        
        failed_logins = len(ip_logs[ip_logs['Xabar'].str.contains('error|failed', case=False, na=False)])
        if failed_logins > 50:
            risk += 40
        
        bulk_actions = len(ip_logs[ip_logs['Amal'].isin(['EXPORT', 'IMPORT', 'BACKUP'])])
        if bulk_actions > len(ip_logs) * 0.5:
            risk += 20
        
        return min(risk, 100)
    
    def analyze_action_sequences(self, admin_name, limit=20):
        """Amallarning ketma-ketligini analiz qilish"""
        admin_logs = self.df[self.df['Admin nomi'] == admin_name].sort_values('Yaratilgan')
        
        sequences = []
        for i in range(min(limit, len(admin_logs))):
            log = admin_logs.iloc[i]
            action_info = self.get_action_explanation(log['Amal'])
            
            sequences.append({
                'timestamp': log['Yaratilgan'],
                'action': log['Amal'],
                'action_uz': action_info['uz'],
                'ip': log['IP'],
                'description': action_info['description']
            })
        
        return sequences
    
    def detect_suspicious_action_sequences(self):
        """Suspekt amal ketma-ketligini aniqlash"""
        suspicious_patterns = []
        
        for admin in self.df['Admin nomi'].unique()[:30]:
            admin_logs = self.df[self.df['Admin nomi'] == admin].sort_values('Yaratilgan')
            
            # Pattern 1: DELETE dan keyin EXPORT (backup o'chirish va ma'lumot olib ketish)
            if len(admin_logs) > 1:
                for i in range(len(admin_logs) - 1):
                    if admin_logs.iloc[i]['Amal'] == 'DELETE' and admin_logs.iloc[i+1]['Amal'] == 'EXPORT':
                        suspicious_patterns.append({
                            'pattern': 'DELETE -> EXPORT',
                            'admin': admin,
                            'risk': 'high',
                            'description': f'{admin} ma\'lumotni o\'chib, so\'ngra eksport qildi - data theft xavfi',
                            'timestamps': [admin_logs.iloc[i]['Yaratilgan'], admin_logs.iloc[i+1]['Yaratilgan']]
                        })
            
            # Pattern 2: Ko'p IMPORT operatsiyalari
            import_count = len(admin_logs[admin_logs['Amal'] == 'IMPORT'])
            if import_count > 10:
                suspicious_patterns.append({
                    'pattern': 'Multiple IMPORT',
                    'admin': admin,
                    'risk': 'medium',
                    'description': f'{admin} {import_count} marta bulk import qildi - tizim overload',
                    'count': import_count
                })
            
            # Pattern 3: Grant permission + Massive data access
            grants = len(admin_logs[admin_logs['Amal'] == 'GRANT_PERMISSION'])
            if grants > 0:
                exports = len(admin_logs[admin_logs['Amal'] == 'EXPORT'])
                if exports > 20:
                    suspicious_patterns.append({
                        'pattern': 'GRANT -> EXPORT',
                        'admin': admin,
                        'risk': 'high',
                        'description': f'{admin} huquq olgandan keyin {exports} marta ma\'lumot eksport qildi',
                        'grant_count': grants,
                        'export_count': exports
                    })
        
        return suspicious_patterns
