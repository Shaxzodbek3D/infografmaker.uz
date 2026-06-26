"""
Advanced Export Module
Loglarni turli formatlarda eksport qilish
"""

import pandas as pd
import json
import os
from datetime import datetime
from io import BytesIO

class ExportManager:
    def __init__(self, df):
        """
        df: pandas DataFrame
        """
        self.df = df
        self.export_dir = 'exports'
        
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
    
    def export_to_csv(self, filters=None):
        """CSV formatga eksport"""
        try:
            filtered_df = self._apply_filters(filters)
            
            filename = f"{self.export_dir}/logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filtered_df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            return {
                'success': True,
                'filename': filename,
                'rows': len(filtered_df),
                'message': f'{len(filtered_df)} qatorni CSV-ga eksport qilindi'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def export_to_excel(self, filters=None):
        """Excel formatga eksport"""
        try:
            filtered_df = self._apply_filters(filters)
            
            filename = f"{self.export_dir}/logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, sheet_name='Logs', index=False)
                
                # Summary sheet
                summary_df = pd.DataFrame({
                    'Parametr': ['Jami qatorlar', 'Uniq Adminlar', 'Uniq IPs', 'Uniq Amallar'],
                    'Qiymat': [
                        len(filtered_df),
                        filtered_df['Admin nomi'].nunique(),
                        filtered_df['IP'].nunique(),
                        filtered_df['Amal'].nunique()
                    ]
                })
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            return {
                'success': True,
                'filename': filename,
                'rows': len(filtered_df),
                'message': f'{len(filtered_df)} qatorni Excel-ga eksport qilindi'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def export_to_json(self, filters=None):
        """JSON formatga eksport"""
        try:
            filtered_df = self._apply_filters(filters)
            
            data = {
                'export_date': datetime.now().isoformat(),
                'total_rows': len(filtered_df),
                'summary': {
                    'unique_admins': int(filtered_df['Admin nomi'].nunique()),
                    'unique_ips': int(filtered_df['IP'].nunique()),
                    'unique_actions': int(filtered_df['Amal'].nunique())
                },
                'logs': filtered_df.to_dict('records')
            }
            
            filename = f"{self.export_dir}/logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return {
                'success': True,
                'filename': filename,
                'rows': len(filtered_df),
                'message': f'{len(filtered_df)} qatorni JSON-ga eksport qilindi'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def export_analytics_report(self, analytics_data):
        """Tahlil natijalarini JSON-ga eksport"""
        try:
            report = {
                'report_date': datetime.now().isoformat(),
                'analytics': analytics_data
            }
            
            filename = f"{self.export_dir}/analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            return {
                'success': True,
                'filename': filename,
                'message': 'Analytics hisoboti eksport qilindi'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _apply_filters(self, filters):
        """Filtr qo'llash"""
        filtered_df = self.df.copy()
        
        if not filters:
            return filtered_df
        
        if filters.get('admin'):
            filtered_df = filtered_df[filtered_df['Admin nomi'].str.contains(filters['admin'], case=False, na=False)]
        
        if filters.get('ip'):
            filtered_df = filtered_df[filtered_df['IP'] == filters['ip']]
        
        if filters.get('action'):
            filtered_df = filtered_df[filtered_df['Amal'] == filters['action']]
        
        if filters.get('start_date'):
            start = pd.to_datetime(filters['start_date'])
            filtered_df = filtered_df[filtered_df['Yaratilgan'] >= start]
        
        if filters.get('end_date'):
            end = pd.to_datetime(filters['end_date'])
            filtered_df = filtered_df[filtered_df['Yaratilgan'] <= end]
        
        return filtered_df
    
    def get_export_history(self):
        """Eksport tarixi"""
        exports = []
        
        if os.path.exists(self.export_dir):
            for filename in os.listdir(self.export_dir):
                filepath = os.path.join(self.export_dir, filename)
                size = os.path.getsize(filepath)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                exports.append({
                    'filename': filename,
                    'size': size,
                    'created': mtime.isoformat(),
                    'type': filename.split('.')[-1].upper()
                })
        
        return sorted(exports, key=lambda x: x['created'], reverse=True)
