"""
BUXDU API Integration Module
BUXDU Student Management System API dan ma'lumot olish va analiz qilish
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

class BuxduAPIClient:
    """BUXDU API bilan ishlaydigan client"""
    
    def __init__(self, base_url="https://student.buxdu.uz"):
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/rest"
        self.session = requests.Session()
        self.token = None
        self.last_request_time = 0
        self.rate_limit_delay = 0.1  # Requests orasidagi kechikish
    
    def _rate_limit(self):
        """Rate limiting - API overload qo'riqlanmoq uchun"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def get_students(self, limit: int = 100) -> Optional[pd.DataFrame]:
        """Talabalarnigeta ma'lumotlarini olish"""
        try:
            self._rate_limit()
            url = f"{self.api_endpoint}/students"
            response = self.session.get(url, params={'limit': limit}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict) and 'data' in data:
                    return pd.DataFrame(data['data'])
                return None
            return None
        except Exception as e:
            print(f"Error fetching students: {e}")
            return None
    
    def get_courses(self, limit: int = 100) -> Optional[pd.DataFrame]:
        """Kurslar ma'lumotlari"""
        try:
            self._rate_limit()
            url = f"{self.api_endpoint}/courses"
            response = self.session.get(url, params={'limit': limit}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict) and 'data' in data:
                    return pd.DataFrame(data['data'])
                return None
            return None
        except Exception as e:
            print(f"Error fetching courses: {e}")
            return None
    
    def get_enrollments(self, limit: int = 100) -> Optional[pd.DataFrame]:
        """Talabalarning kursga yozilishi"""
        try:
            self._rate_limit()
            url = f"{self.api_endpoint}/enrollments"
            response = self.session.get(url, params={'limit': limit}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict) and 'data' in data:
                    return pd.DataFrame(data['data'])
                return None
            return None
        except Exception as e:
            print(f"Error fetching enrollments: {e}")
            return None
    
    def get_attendance(self, student_id: Optional[str] = None, limit: int = 100) -> Optional[pd.DataFrame]:
        """Davomatni olish"""
        try:
            self._rate_limit()
            url = f"{self.api_endpoint}/attendance"
            params = {'limit': limit}
            if student_id:
                params['student_id'] = student_id
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict) and 'data' in data:
                    return pd.DataFrame(data['data'])
                return None
            return None
        except Exception as e:
            print(f"Error fetching attendance: {e}")
            return None
    
    def get_grades(self, limit: int = 100) -> Optional[pd.DataFrame]:
        """Baholar ma'lumotlari"""
        try:
            self._rate_limit()
            url = f"{self.api_endpoint}/grades"
            response = self.session.get(url, params={'limit': limit}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict) and 'data' in data:
                    return pd.DataFrame(data['data'])
                return None
            return None
        except Exception as e:
            print(f"Error fetching grades: {e}")
            return None
    
    def get_user_activities(self, user_id: Optional[str] = None, limit: int = 100) -> Optional[pd.DataFrame]:
        """Foydalanuvchi aktivligi"""
        try:
            self._rate_limit()
            url = f"{self.api_endpoint}/activities"
            params = {'limit': limit}
            if user_id:
                params['user_id'] = user_id
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict) and 'data' in data:
                    return pd.DataFrame(data['data'])
                return None
            return None
        except Exception as e:
            print(f"Error fetching activities: {e}")
            return None
    
    def get_all_data(self) -> Dict[str, pd.DataFrame]:
        """Barcha ma'lumotlarni bir vaqtda olish"""
        data = {}
        
        print("Fetching students...")
        students = self.get_students(limit=500)
        if students is not None:
            data['students'] = students
            print(f"  -> {len(students)} talaba")
        
        print("Fetching courses...")
        courses = self.get_courses(limit=500)
        if courses is not None:
            data['courses'] = courses
            print(f"  -> {len(courses)} kurs")
        
        print("Fetching enrollments...")
        enrollments = self.get_enrollments(limit=1000)
        if enrollments is not None:
            data['enrollments'] = enrollments
            print(f"  -> {len(enrollments)} yozilish")
        
        print("Fetching attendance...")
        attendance = self.get_attendance(limit=1000)
        if attendance is not None:
            data['attendance'] = attendance
            print(f"  -> {len(attendance)} davomat")
        
        print("Fetching grades...")
        grades = self.get_grades(limit=1000)
        if grades is not None:
            data['grades'] = grades
            print(f"  -> {len(grades)} baho")
        
        print("Fetching activities...")
        activities = self.get_user_activities(limit=1000)
        if activities is not None:
            data['activities'] = activities
            print(f"  -> {len(activities)} aktivlik")
        
        return data
    
    def check_api_health(self) -> bool:
        """API holati tekshirish"""
        try:
            self._rate_limit()
            url = f"{self.api_endpoint}/health"
            response = self.session.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False

class DataNormalizer:
    """Turli manbalardan olingan ma'lumotlarni normallashtirish"""
    
    @staticmethod
    def normalize_activities(df: pd.DataFrame) -> pd.DataFrame:
        """Activities ma'lumotlarini log formatiga o'girish"""
        normalized = df.copy()
        
        # Zarur ustunlar
        if 'user_id' in normalized.columns:
            normalized['Admin nomi'] = normalized.get('user_name', normalized['user_id'])
        
        if 'timestamp' in normalized.columns or 'created_at' in normalized.columns:
            time_col = 'timestamp' if 'timestamp' in normalized.columns else 'created_at'
            normalized['Yaratilgan'] = pd.to_datetime(normalized[time_col])
        
        if 'action' in normalized.columns:
            normalized['Amal'] = normalized['action'].str.upper()
        else:
            normalized['Amal'] = 'ACTIVITY'
        
        if 'ip_address' in normalized.columns:
            normalized['IP'] = normalized['ip_address']
        else:
            normalized['IP'] = '127.0.0.1'
        
        if 'description' in normalized.columns:
            normalized['Xabar'] = normalized['description']
        else:
            normalized['Xabar'] = ''
        
        # Kerakli ustunlarni saqlash
        required_cols = ['Admin nomi', 'Yaratilgan', 'Amal', 'IP', 'Xabar']
        for col in required_cols:
            if col not in normalized.columns:
                normalized[col] = ''
        
        return normalized[required_cols]
    
    @staticmethod
    def create_synthetic_logs_from_enrollments(enrollments: pd.DataFrame, students: pd.DataFrame) -> pd.DataFrame:
        """Yozilish ma'lumotlaridan synthetic loglar yaratish"""
        logs = []
        
        for idx, enrollment in enrollments.iterrows():
            student_id = enrollment.get('student_id', '')
            course_id = enrollment.get('course_id', '')
            status = enrollment.get('status', 'ACTIVE')
            created_at = enrollment.get('created_at', datetime.now())
            
            # Student nomi topish
            student_name = students[students['id'] == student_id]['name'].values
            student_name = student_name[0] if len(student_name) > 0 else student_id
            
            logs.append({
                'Admin nomi': student_name,
                'Yaratilgan': created_at,
                'Amal': 'ENROLL',
                'IP': '10.0.0.1',
                'Xabar': f'Course {course_id} ga yozildi - Status: {status}',
                'So\'rov': f'{{"course_id": "{course_id}"}}',
                'Post': '{}'
            })
        
        return pd.DataFrame(logs)
    
    @staticmethod
    def combine_data_sources(api_data: Dict[str, pd.DataFrame], file_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Turli manbalardan olingan ma'lumotlarni birgalikda ishlatish"""
        dfs = []
        
        # File data'ni qo'shish (agar bor bo'lsa)
        if file_data is not None:
            dfs.append(file_data)
        
        # API activities
        if 'activities' in api_data:
            normalized = DataNormalizer.normalize_activities(api_data['activities'])
            dfs.append(normalized)
        
        # Synthetic logs from enrollments
        if 'enrollments' in api_data and 'students' in api_data:
            synthetic = DataNormalizer.create_synthetic_logs_from_enrollments(
                api_data['enrollments'],
                api_data['students']
            )
            dfs.append(synthetic)
        
        # Barchasini birlashtiramiz
        if dfs:
            combined = pd.concat(dfs, ignore_index=True)
            return combined
        
        return pd.DataFrame()
