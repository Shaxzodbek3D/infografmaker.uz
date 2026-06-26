"""
AI Log Analysis Engine
Loglarni tahlil qilish va smart insights generatsiya qilish
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter
import json

class AILogAnalyzer:
    def __init__(self, df):
        """
        df: pandas DataFrame
        """
        self.df = df
        self.prepare_data()
    
    def prepare_data(self):
        """Ma'lumotlarni tayyorlash"""
        self.df['Yaratilgan'] = pd.to_datetime(self.df['Yaratilgan'], format='%d.%m.%Y %H:%M:%S', errors='coerce')
        self.df['Soat'] = self.df['Yaratilgan'].dt.hour
        self.df['Kun'] = self.df['Yaratilgan'].dt.date
        self.df['Hafta_kuni'] = self.df['Yaratilgan'].dt.day_name()
    
    def analyze_log_patterns(self):
        """Log patternlarini tahlil qilish"""
        patterns = {}
        
        # 1. Admin faollik patternlari
        admin_stats = {}
        top_admins = (
            self.df['Admin nomi']
            .dropna()
            .value_counts()
            .head(50)
            .index
            .tolist()
        )

        for admin in top_admins:
            admin_df = self.df[self.df['Admin nomi'] == admin]
            days_count = admin_df['Kun'].dropna().nunique()
            days_count = int(days_count) if days_count > 0 else 1
            
            admin_stats[admin] = {
                'total_actions': len(admin_df),
                'unique_ips': admin_df['IP'].nunique(),
                'most_frequent_hour': int(admin_df['Soat'].mode()[0]) if len(admin_df['Soat'].mode()) > 0 else 0,
                'most_frequent_action': admin_df['Amal'].mode()[0] if len(admin_df['Amal'].mode()) > 0 else 'N/A',
                'active_days': days_count,
                'avg_daily_actions': round(len(admin_df) / days_count, 2)
            }
        
        patterns['admin_patterns'] = admin_stats
        
        # 2. Vaqt patternlari
        hourly_distribution = self.df.groupby('Soat').size()
        peak_hour = hourly_distribution.idxmax()
        quiet_hours = hourly_distribution[hourly_distribution < hourly_distribution.mean()].index.tolist()
        
        patterns['time_patterns'] = {
            'peak_hour': int(peak_hour),
            'peak_hour_count': int(hourly_distribution[peak_hour]),
            'quiet_hours': [int(h) for h in quiet_hours],
            'average_per_hour': round(float(hourly_distribution.mean()), 2)
        }
        
        # 3. Amal patternlari
        action_patterns = {}
        for action in self.df['Amal'].unique():
            action_df = self.df[self.df['Amal'] == action]
            action_patterns[action] = {
                'frequency': len(action_df),
                'unique_admins': action_df['Admin nomi'].nunique(),
                'percentage': round((len(action_df) / len(self.df)) * 100, 2)
            }
        
        patterns['action_patterns'] = action_patterns
        
        # 4. IP patternlari
        ip_patterns = {}
        for ip in self.df['IP'].value_counts().head(10).index:
            ip_df = self.df[self.df['IP'] == ip]
            ip_patterns[ip] = {
                'requests': len(ip_df),
                'unique_admins': ip_df['Admin nomi'].nunique(),
                'actions': ip_df['Amal'].unique().tolist()[:5]
            }
        
        patterns['ip_patterns'] = ip_patterns
        
        return patterns
    
    def generate_smart_insights(self):
        """Smart insights generatsiya qilish"""
        insights = []
        patterns = self.analyze_log_patterns()
        
        # 1. Eng faol adminlar
        admin_patterns = patterns['admin_patterns']
        top_admins = sorted(admin_patterns.items(), key=lambda x: x[1]['total_actions'], reverse=True)[:3]
        
        for admin, stats in top_admins:
            insights.append({
                'type': 'top_user',
                'severity': 'info',
                'title': f"Eng Faol Admin: {admin.title()}",
                'description': f"{stats['total_actions']} ta amal qildi, {stats['unique_ips']} ta turli IPdan kiripti",
                'recommendation': f"Ko'p faollikka e'tibor bering, xavf yoki spam bo'lmaganligini tekshiring",
                'data': stats
            })
        
        # 2. Notekis faollik vaqtlar
        time_patterns = patterns['time_patterns']
        if len(time_patterns['quiet_hours']) > 0:
            insights.append({
                'type': 'unusual_timing',
                'severity': 'info',
                'title': f"Soat {time_patterns['peak_hour']}da Peak Faollik",
                'description': f"Bu soatda {time_patterns['peak_hour_count']} ta amal. Normal: {time_patterns['average_per_hour']:.0f}",
                'recommendation': "Peak vaqtlarda tizim yukiga e'tibor bering",
                'data': time_patterns
            })
        
        # 3. Eng ko'p kelatgan amallar
        action_patterns = patterns['action_patterns']
        top_actions = sorted(action_patterns.items(), key=lambda x: x[1]['frequency'], reverse=True)[:3]
        
        for action, stats in top_actions:
            if stats['percentage'] > 30:
                insights.append({
                    'type': 'dominant_action',
                    'severity': 'warning',
                    'title': f"Yuqori {action} Faolligi",
                    'description': f"{stats['percentage']}% loglar bu amalga tegishli",
                    'recommendation': f"{action} amalini optimallashtirish, audit qilish kerak",
                    'action': action,
                    'data': stats
                })
        
        # 4. Potensial xavf signallari
        admin_stats = list(admin_patterns.values())
        avg_actions = np.mean([a['total_actions'] for a in admin_stats])
        std_actions = np.std([a['total_actions'] for a in admin_stats])
        
        for admin, stats in admin_patterns.items():
            if stats['total_actions'] > avg_actions + (2 * std_actions):
                insights.append({
                    'type': 'anomaly_detected',
                    'severity': 'high',
                    'title': f"Anomaliya: {admin.title()}",
                    'description': f"{stats['total_actions']} amallar (o'rtacha: {avg_actions:.0f})",
                    'recommendation': "Bu admin faolligini qat'iy tekshiring",
                    'data': stats
                })
        
        return insights
    
    def get_actionable_recommendations(self):
        """Harakati amalga oshirish uchun tavsiyalar"""
        recommendations = []
        insights = self.generate_smart_insights()
        
        for insight in insights:
            if insight['type'] == 'anomaly_detected':
                admin_name = insight['title'].split(':')[1].strip() if ':' in insight['title'] else insight['title']
                recommendations.append({
                    'priority': 'high',
                    'title': f"Ma'lumot xavfsizligi auditi: {admin_name}",
                    'category': 'Security Audit',
                    'impact': 'high',
                    'urgency': '24 soat ichida',
                    'reason': insight['description'],
                    'evidence': {
                        'metric': 'Anomaliya faolligi',
                        'value': insight['description']
                    },
                    'steps': [
                        "Adminning barcha log entrylarini to'liq ko'ring",
                        "IP manzillar va sessiyalarni solishtiring",
                        "Oxirgi 24 soatdagi o'zgarishlarni tekshiring",
                        "Kerak bo'lsa, parolni darhol yangilang"
                    ],
                    'verification': "Audit natijasida xavf belgisi topilmasa, statusni 'yopildi' deb belgilang"
                })
            
            elif insight['type'] == 'unusual_timing':
                recommendations.append({
                    'priority': 'medium',
                    'title': "Peak vaqtlar uchun monitoring siyosati",
                    'category': 'Performance',
                    'impact': 'medium',
                    'urgency': '1 hafta ichida',
                    'reason': insight['description'],
                    'evidence': {
                        'metric': 'Peak soat yuklanishi',
                        'value': insight['description']
                    },
                    'steps': [
                        "Server resurslarini soatlik kuzatish",
                        "Peak soatlarda balanslashni tekshirish",
                        "Sekin so'rovlarni optimallashtirish"
                    ],
                    'verification': "Peak soatlarda response vaqti me'yorda ekanligi tasdiqlansin"
                })
            
            elif insight['type'] == 'dominant_action':
                recommendations.append({
                    'priority': 'medium',
                    'title': f"Optimallashtirish: {insight['title']}",
                    'category': 'Optimization',
                    'impact': 'medium',
                    'urgency': '2 hafta ichida',
                    'reason': f"Tizim yuk 30% dan yuqori",
                    'evidence': {
                        'metric': 'Dominant amal ulushi',
                        'value': insight['description']
                    },
                    'steps': [
                        "DB querylarni optimallashtirish",
                        "Indekslarni tahlil qilish",
                        "Bulk operatsiyalarni kamaytirish"
                    ],
                    'verification': "Amal ulushi kamaygani monitoring grafiklarda ko'rinsin"
                })
        
        return sorted(recommendations, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x['priority'], 3))
    
    def get_comparison_analysis(self):
        """Kunlar/haftalalar bo'yicha taqqoslash"""
        comparison = {}
        
        # Kunlari bo'yicha taqqoslash
        daily_stats = self.df.groupby('Kun').size()
        
        if len(daily_stats) > 1:
            latest_day = daily_stats.iloc[-1]
            prev_day = daily_stats.iloc[-2] if len(daily_stats) > 1 else daily_stats.iloc[-1]
            
            percent_change = round(((latest_day - prev_day) / prev_day * 100), 2) if prev_day > 0 else 0
            
            comparison['daily_comparison'] = {
                'latest_day_logs': int(latest_day),
                'previous_day_logs': int(prev_day),
                'percent_change': percent_change,
                'trend': 'yuqorish' if percent_change > 0 else 'pasayish'
            }
        
        # Hafta kunlari bo'yicha
        weekly_stats = self.df.groupby('Hafta_kuni').size()
        comparison['weekly_pattern'] = {
            k: int(v) for k, v in weekly_stats.items()
        }
        
        return comparison
    
    def predict_issues(self):
        """Potensial muammolarni oldindan aytish"""
        predictions = []
        
        # 1. Spam/Brute force hujum
        failed_logins = self.df[self.df['Xabar'].str.contains('error|failed|invalid', case=False, na=False)]
        if len(failed_logins) > len(self.df) * 0.1:  # 10%dan yuqori
            predictions.append({
                'risk': 'brute_force_attack',
                'confidence': 'high',
                'message': f"{len(failed_logins)} ta noto'g'ri login urinishi aniqlandi",
                'suggested_action': "Brute force zashtitasini yoqing"
            })
        
        # 2. Data leakage risk
        admin_ip_combos = self.df.groupby('Admin nomi')['IP'].nunique()
        suspicious_admins = admin_ip_combos[admin_ip_combos > 10]
        
        if len(suspicious_admins) > 0:
            predictions.append({
                'risk': 'data_leakage',
                'confidence': 'medium',
                'message': f"{len(suspicious_admins)} ta admin ko'p IPlardan foydalanmoqda",
                'suggested_action': "VPN/Proxy huquqlarini tekshiring"
            })
        
        # 3. Resource exhaustion
        hourly_logs = self.df.groupby('Soat').size()
        if hourly_logs.max() > hourly_logs.mean() * 3:
            predictions.append({
                'risk': 'ddos_risk',
                'confidence': 'medium',
                'message': f"Soat {hourly_logs.idxmax()}-da {hourly_logs.max()} ta loglar",
                'suggested_action': "Rate limiting va CDN qo'shish"
            })
        
        return predictions
