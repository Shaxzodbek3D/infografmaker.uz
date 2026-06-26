"""
Behavior Analyzer
Amallarning kombinatsiyalarini va workflow-larni analiz qilish
"""

import pandas as pd
from collections import defaultdict, Counter
from datetime import datetime, timedelta

class BehaviorAnalyzer:
    """Admin va IP larning behavioral patterns"""
    
    def __init__(self, df):
        self.df = df
        self.df['Yaratilgan'] = pd.to_datetime(self.df['Yaratilgan'], format='%d.%m.%Y %H:%M:%S', errors='coerce')
    
    def analyze_user_workflows(self):
        """Foydalanuvchi workflows (amallar ketma-ketligi) analiz qilish"""
        workflows = defaultdict(lambda: defaultdict(int))
        
        for admin in self.df['Admin nomi'].unique()[:50]:
            admin_logs = self.df[self.df['Admin nomi'] == admin].sort_values('Yaratilgan')
            
            # Ketma-ketlik yaratish
            actions = admin_logs['Amal'].tolist()
            for i in range(len(actions) - 1):
                workflow = f"{actions[i]} -> {actions[i+1]}"
                workflows[admin][workflow] += 1
        
        # Eng ko'p kelatgan workflows
        common_workflows = defaultdict(int)
        for admin_workflows in workflows.values():
            for workflow, count in admin_workflows.items():
                common_workflows[workflow] += count
        
        return sorted(common_workflows.items(), key=lambda x: x[1], reverse=True)[:20]
    
    def detect_activity_clusters(self):
        """Vaqt bo'yicha faollik klasterlarini aniqlash"""
        self.df['Hour'] = self.df['Yaratilgan'].dt.hour
        
        clusters = {}
        
        for admin in self.df['Admin nomi'].unique()[:30]:
            admin_logs = self.df[self.df['Admin nomi'] == admin]
            
            # Soatlar bo'yicha logarni grupp qilish
            hourly_activity = admin_logs.groupby('Hour').size()
            
            if len(hourly_activity) > 0:
                peak_hour = hourly_activity.idxmax()
                avg_per_hour = hourly_activity.mean()
                
                clusters[admin] = {
                    'peak_hour': int(peak_hour),
                    'peak_activity': int(hourly_activity[peak_hour]),
                    'average_per_hour': round(float(avg_per_hour), 2),
                    'active_hours_count': len(hourly_activity),
                    'pattern': self._describe_activity_pattern(hourly_activity)
                }
        
        return clusters
    
    def _describe_activity_pattern(self, hourly_activity):
        """Faollik patternini tavsiflab berish"""
        if len(hourly_activity) <= 4:
            return 'Concentrated - ma\'lum soatlarga to\'plandirilgan'
        elif len(hourly_activity) >= 20:
            return 'Distributed - butun kun faol'
        else:
            return 'Moderate - normal faollik'
    
    def find_data_movement_patterns(self):
        """Ma'lumotlar harakatini aniqlash (IMPORT/EXPORT patterns)"""
        patterns = []
        
        for admin in self.df['Admin nomi'].unique():
            admin_logs = self.df[self.df['Admin nomi'] == admin]
            
            imports = len(admin_logs[admin_logs['Amal'] == 'IMPORT'])
            exports = len(admin_logs[admin_logs['Amal'] == 'EXPORT'])
            downloads = len(admin_logs[admin_logs['Amal'] == 'DOWNLOAD'])
            uploads = len(admin_logs[admin_logs['Amal'] == 'UPLOAD'])
            
            total_data_ops = imports + exports + downloads + uploads
            
            # Agar hech bo'lmasa bitta data amali bo'lsa, ko'rsatamiz
            if total_data_ops > 0:
                patterns.append({
                    'admin': admin,
                    'imports': imports,
                    'exports': exports,
                    'downloads': downloads,
                    'uploads': uploads,
                    'total_data_operations': total_data_ops,
                    'risk_assessment': self._assess_data_movement_risk({
                        'imports': imports,
                        'exports': exports,
                        'downloads': downloads,
                        'uploads': uploads
                    })
                })
        
        return sorted(patterns, key=lambda x: x['total_data_operations'], reverse=True)[:20]
    
    def _assess_data_movement_risk(self, ops):
        """Ma'lumot harakatining xavfini baholash"""
        risk_score = 0
        risk_factors = []
        
        # Ko'p export
        if ops['exports'] > ops['imports'] + 5:
            risk_score += 40
            risk_factors.append("Ko'p ma'lumot eksport qilinmoqda")
        
        # Asimmetrik import/export
        if ops['exports'] > 0 and ops['imports'] == 0 and ops['exports'] > 5:
            risk_score += 30
            risk_factors.append("Faqat eksport qilinmoqda, import yo'q")
        
        # Bulk operations
        if ops['downloads'] + ops['uploads'] > 50:
            risk_score += 20
            risk_factors.append("Ko'p fayl harakati")
        
        return {
            'risk_score': min(risk_score, 100),
            'risk_level': 'high' if risk_score > 60 else 'medium' if risk_score > 30 else 'low',
            'factors': risk_factors
        }
    
    def identify_user_roles(self):
        """Foydalanuvchi rollarini avtomatik aniqlash"""
        user_roles = {}
        
        for admin in self.df['Admin nomi'].unique()[:50]:
            admin_logs = self.df[self.df['Admin nomi'] == admin]
            
            actions = admin_logs['Amal'].value_counts()
            action_types = set(actions.index)
            
            role = self._classify_user_role(action_types, admin_logs)
            
            user_roles[admin] = {
                'inferred_role': role['role'],
                'description': role['description'],
                'primary_actions': actions.head(3).to_dict(),
                'confidence': role['confidence']
            }
        
        return user_roles
    
    def _classify_user_role(self, actions, logs):
        """Foydalanuvchi rolini klassifikatsiya qilish"""
        
        # Super Admin - hammasini qila oladi
        if 'GRANT_PERMISSION' in actions and 'RESET_PASSWORD' in actions and 'BACKUP' in actions:
            return {
                'role': 'Super Admin',
                'description': 'Barcha huquqlar bilan - sistema boshqaruvi',
                'confidence': 'high'
            }
        
        # System Admin - tizim boshqaruvidan mas'ul
        elif 'BACKUP' in actions or 'RESTORE' in actions:
            return {
                'role': 'System Administrator',
                'description': 'Tizim va ma\'lumotlar boshqaruvi',
                'confidence': 'high'
            }
        
        # Data Manager - ma'lumot bilan ishlaydi
        elif len([a for a in actions if a in ['IMPORT', 'EXPORT', 'UPLOAD', 'DOWNLOAD']]) >= 2:
            return {
                'role': 'Data Manager',
                'description': 'Ma\'lumotlarni import/export qiladi',
                'confidence': 'medium'
            }
        
        # Content Editor - kontent o'zgartiradi
        elif 'UPDATE' in actions and 'CREATE' in actions:
            return {
                'role': 'Content Editor',
                'description': 'Ma\'lumot tahrirlash va yaratish',
                'confidence': 'medium'
            }
        
        # Viewer - faqat ko'radi
        elif 'VIEW' in actions and len(actions) <= 2:
            return {
                'role': 'Viewer/Analyst',
                'description': 'Faqat ma\'lumot ko\'rish va tahlil qilish',
                'confidence': 'medium'
            }
        
        # Approver - tasdiqlash/rad etish
        elif 'APPROVE' in actions or 'REJECT' in actions:
            return {
                'role': 'Approver',
                'description': 'Talab va o\'zgarishlarni tasdiqlash',
                'confidence': 'medium'
            }
        
        else:
            return {
                'role': 'General User',
                'description': 'Umumiy foydalanuvchi',
                'confidence': 'low'
            }
    
    def detect_privilege_escalation(self):
        """Huquqlarni o'stirish urinishlarini aniqlash"""
        escalations = []
        
        for admin in self.df['Admin nomi'].unique():
            admin_logs = self.df[self.df['Admin nomi'] == admin].sort_values('Yaratilgan')
            
            grants = admin_logs[admin_logs['Amal'] == 'GRANT_PERMISSION']
            
            if len(grants) > 0:
                # O'z huquqlarini o'stirish?
                suspicious = len(grants) > len(admin_logs) * 0.2  # 20%dan ko'p
                
                if suspicious:
                    escalations.append({
                        'admin': admin,
                        'grant_count': len(grants),
                        'total_actions': len(admin_logs),
                        'percentage': round((len(grants) / len(admin_logs)) * 100, 2),
                        'risk': 'high',
                        'description': f'{admin} {len(grants)} marta GRANT_PERMISSION amalini bajaradi'
                    })
        
        return escalations
    
    def analyze_time_zone_anomalies(self):
        """Vaqt zonasi anomalylarini aniqlash"""
        anomalies = []
        
        # Abnormal hours - 22:00 - 06:00
        abnormal_hours = list(range(22, 24)) + list(range(0, 6))
        
        for admin in self.df['Admin nomi'].unique()[:30]:
            admin_logs = self.df[self.df['Admin nomi'] == admin]
            admin_logs['Hour'] = admin_logs['Yaratilgan'].dt.hour
            
            abnormal_actions = len(admin_logs[admin_logs['Hour'].isin(abnormal_hours)])
            total_actions = len(admin_logs)
            
            if abnormal_actions > total_actions * 0.3:  # 30%dan ko'p
                anomalies.append({
                    'admin': admin,
                    'abnormal_hour_actions': abnormal_actions,
                    'total_actions': total_actions,
                    'percentage': round((abnormal_actions / total_actions) * 100, 2),
                    'risk': 'medium',
                    'description': f'{admin} {round((abnormal_actions / total_actions) * 100, 1)}% vaqti gece soatlarda faol'
                })
        
        return sorted(anomalies, key=lambda x: x['percentage'], reverse=True)
