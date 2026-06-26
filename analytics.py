"""
Log Tahlil Moduli
Hemis loglarini tahlil qilish va statistika chiqarish
"""

import pandas as pd
from datetime import datetime
import json

class LogAnalytics:
    def __init__(self, df):
        """
        df: pandas DataFrame (Excel fayldan yuklangan)
        """
        self.df = df
        self.prepare_data()
    
    def prepare_data(self):
        """Ma'lumotlarni tayyorlash"""
        try:
            # Yaratilgan vaqtni datetime ga o'tkazish
            self.df['Yaratilgan'] = pd.to_datetime(self.df['Yaratilgan'], format='%d.%m.%Y %H:%M:%S', errors='coerce')
            self.df['Soat'] = self.df['Yaratilgan'].dt.hour
            self.df['Kun'] = self.df['Yaratilgan'].dt.date
        except Exception as e:
            print(f"Data preparation error: {e}")
    
    def get_admin_activity(self):
        """Har bir admin nomi qancha logga ega"""
        activity = self.df['Admin nomi'].value_counts().head(20)
        return {
            'labels': activity.index.tolist(),
            'data': activity.values.tolist(),
            'total': len(activity)
        }
    
    def get_action_distribution(self):
        """Amal turlarining tarqatilishi"""
        distribution = self.df['Amal'].value_counts()
        return {
            'labels': distribution.index.tolist(),
            'data': distribution.values.tolist(),
            'percentage': (distribution.values / len(self.df) * 100).round(2).tolist()
        }
    
    def get_ip_analysis(self):
        """IP manzilarning tahlili"""
        ips = self.df['IP'].value_counts().head(15)
        return {
            'labels': ips.index.tolist(),
            'data': ips.values.tolist(),
            'total_unique': self.df['IP'].nunique()
        }
    
    def get_timeline(self):
        """Vaqt bo'yicha loglar soni"""
        timeline = self.df.groupby(self.df['Yaratilgan'].dt.date).size()
        return {
            'labels': [str(d) for d in timeline.index],
            'data': timeline.values.tolist()
        }
    
    def get_hourly_distribution(self):
        """Soatlar bo'yicha tarqatilishi"""
        hourly = self.df.groupby('Soat').size()
        return {
            'labels': [f"{h}:00" for h in hourly.index],
            'data': hourly.values.tolist()
        }
    
    def get_admin_by_ip(self):
        """Har bir admin qaysi IPdan login qilgan"""
        result = self.df.groupby(['Admin nomi', 'IP']).size().reset_index(name='count')
        return result.to_dict('records')
    
    def get_error_logs(self):
        """Xato loglarini topish"""
        errors = self.df[self.df['Xabar'].str.contains('error|Error|ERROR', na=False)]
        return {
            'count': len(errors),
            'data': errors[['Admin nomi', 'IP', 'Amal', 'Xabar']].head(50).to_dict('records')
        }
    
    def get_summary(self):
        """Umumiy xulosasi"""
        return {
            'total_logs': len(self.df),
            'unique_admins': self.df['Admin nomi'].nunique(),
            'unique_ips': self.df['IP'].nunique(),
            'unique_actions': self.df['Amal'].nunique(),
            'date_range': {
                'start': str(self.df['Yaratilgan'].min()),
                'end': str(self.df['Yaratilgan'].max())
            }
        }
    
    def detect_anomalies(self):
        """Notekis faollikni aniqlash"""
        anomalies = []
        
        # 1. Noto'g'ri parol urinishlari (failed login)
        failed_logins = self.df[self.df['Xabar'].str.contains('error|failed|invalid', case=False, na=False)]
        if len(failed_logins) > 0:
            anomalies.append({
                'type': 'Failed Logins',
                'count': len(failed_logins),
                'severity': 'high' if len(failed_logins) > 100 else 'medium',
                'description': f'{len(failed_logins)} ta noto\'g\'ri login urinishi aniqlandi'
            })
        
        # 2. Ko'p IP dan bir adminning logini
        admin_ip_pairs = self.df.groupby('Admin nomi')['IP'].nunique()
        multi_ip_admins = admin_ip_pairs[admin_ip_pairs > 5]
        
        for admin in multi_ip_admins.index[:5]:
            anomalies.append({
                'type': 'Multi-IP Access',
                'admin': admin,
                'ip_count': int(multi_ip_admins[admin]),
                'severity': 'medium',
                'description': f'{admin} {int(multi_ip_admins[admin])} ta turli IPdan kiripti'
            })
        
        # 3. Odd vaqtlarda faollik (2:00 - 5:00 AM)
        odd_hours = self.df[self.df['Soat'].isin([2, 3, 4, 5])]
        if len(odd_hours) > 50:
            anomalies.append({
                'type': 'Suspicious Hours',
                'count': len(odd_hours),
                'severity': 'medium',
                'description': f'{len(odd_hours)} ta log gecaning 2-5 soatlari o\'rtasida aniqlandi'
            })
        
        # 4. Massive bulk actions
        action_counts = self.df.groupby('Amal').size().sort_values(ascending=False)
        top_action = action_counts.iloc[0]
        if top_action > len(self.df) * 0.5:
            anomalies.append({
                'type': 'Bulk Actions',
                'action': action_counts.index[0],
                'percentage': round((top_action / len(self.df)) * 100, 2),
                'severity': 'low',
                'description': f'{round((top_action / len(self.df)) * 100, 2)}% loglar bitta amalga tegishli'
            })
        
        return {
            'total_anomalies': len(anomalies),
            'anomalies': anomalies
        }
    
    def get_admin_risk_score(self):
        """Har bir admin uchun risk balini hisoblash (0-100)"""
        admin_stats = []

        # Eng ko'p amallar bajargan adminlar bo'yicha hisoblaymiz
        top_admins = (
            self.df['Admin nomi']
            .dropna()
            .value_counts()
            .head(20)
            .index
            .tolist()
        )

        for admin in top_admins:
            admin_logs = self.df[self.df['Admin nomi'] == admin]
            
            # Risk fakterlari
            risk = 0
            
            # Failed logins
            failed = len(admin_logs[admin_logs['Xabar'].str.contains('error|failed|invalid', case=False, na=False)])
            failed_points = min(failed * 2, 30)
            risk += failed_points
            
            # Ko'p IP
            ip_count = admin_logs['IP'].nunique()
            ip_points = min(max(ip_count - 1, 0) * 5, 25)
            risk += ip_points
            
            # Odd hours
            odd_hour_logs = admin_logs[admin_logs['Soat'].isin([2, 3, 4, 5])]
            odd_hours_count = len(odd_hour_logs)
            odd_hours_points = min(odd_hours_count * 0.5, 20)
            risk += odd_hours_points
            
            # Large batch operations
            action_counts = admin_logs.groupby('Amal').size()
            bulk_points = 0
            max_action = None
            max_action_count = 0
            max_action_share = 0.0
            if len(action_counts) > 0 and len(admin_logs) > 0:
                max_action = action_counts.idxmax()
                max_action_count = int(action_counts.max())
                max_action_share = (max_action_count / len(admin_logs)) * 100
                if max_action_share > 70:
                    bulk_points = 15
                    risk += bulk_points

            risk_score_raw = min(risk, 100)
            
            admin_stats.append({
                'admin': admin,
                'risk_score': int(risk_score_raw),
                'risk_score_raw': round(risk_score_raw, 1),
                'failed_points': round(failed_points, 1),
                'ip_points': round(ip_points, 1),
                'odd_hours_points': round(odd_hours_points, 1),
                'bulk_points': bulk_points,
                'odd_hours_count': odd_hours_count,
                'max_action': max_action,
                'max_action_count': max_action_count,
                'max_action_share': round(max_action_share, 1),
                'total_actions': len(admin_logs),
                'unique_ips': ip_count,
                'failed_attempts': failed
            })
        
        return sorted(admin_stats, key=lambda x: x['risk_score'], reverse=True)
    
    def get_time_distribution(self):
        """Vaqt bo'yicha admin faolligi (admin, soat -> count)"""
        time_data = self.df.groupby(['Admin nomi', 'Soat']).size().reset_index(name='count')
        return time_data.to_dict('records')
