"""
NLP Log Analyzer — HEMIS tizimi log xabarlarini tahlil qilish
Imkoniyatlar:
  1. Keyword extraction (muhim so'zlarni ajratish)
  2. Error classification (xatoliklarni tasniflash)
  3. Log template extraction (shablon aniqlash)
  4. Sentiment/severity scoring (og'irlik darajasi)
  5. Action semantic grouping (amallarni semantik guruhlash)
"""

import pandas as pd
import numpy as np
import re
from collections import Counter, defaultdict
from datetime import datetime
import json


# ─────────────────────────────────────────────
# 1. KONSTANTALAR
# ─────────────────────────────────────────────

# Xatolik darajalarini aniqlash uchun kalit so'zlar
SEVERITY_KEYWORDS = {
    'critical': ['critical', 'fatal', 'crash', 'halt', 'xato', 'singan', 'down', 'failed', 'failure',
                 'exception', 'traceback', 'panic', 'abort', 'dead'],
    'error':    ['error', 'err', 'xato', 'noto\'g\'ri', 'invalid', 'denied', 'forbidden',
                 'unauthorized', '404', '500', '503', 'timeout', 'refused'],
    'warning':  ['warning', 'warn', 'deprecated', 'slow', 'retry', 'ogohlantirish',
                 'sekin', 'limit', 'threshold', 'high'],
    'info':     ['success', 'ok', 'login', 'logout', 'view', 'get', 'post', 'muvaffaqiyat',
                 'created', 'updated', 'deleted', 'kirdi', 'chiqdi'],
    'debug':    ['debug', 'trace', 'verbose', 'start', 'end', 'begin', 'init']
}

# Amallarni semantik kategoriyalarga guruhlash
ACTION_CATEGORIES = {
    'Kirish/Chiqish':   ['login', 'logout', 'auth', 'dashboard/login', 'dashboard/logout',
                         'dashboard/auth', 'dashboard/reset'],
    'O\'qish':          ['view', 'read', 'get', 'index', 'list', 'show', 'profile',
                         'dashboard/profile', 'dashboard/index'],
    'Yaratish':         ['create', 'add', 'new', 'insert', 'post', 'upload', 'submit'],
    'Tahrirlash':       ['edit', 'update', 'modify', 'change', 'patch', 'put'],
    'O\'chirish':       ['delete', 'remove', 'destroy', 'drop'],
    'Eksport/Import':   ['export', 'import', 'download', 'upload', 'transfer'],
    'Ta\'lim':          ['curriculum', 'schedule', 'subject', 'grade', 'credit',
                         'attendance', 'exam', 'student', 'teacher', 'education'],
    'Arxiv':            ['archive', 'diploma', 'transcript', 'employment'],
    'Tizim':            ['system', 'classifier', 'sync', 'oauth', 'settings'],
    'Boshqa':           []
}

# Stop so'zlar (filtrlash uchun)
STOP_WORDS = {
    'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or',
    'is', 'are', 'was', 'were', 'be', 'been', 'has', 'have', 'had',
    'do', 'does', 'did', 'will', 'would', 'can', 'could', 'may', 'might',
    'with', 'from', 'by', 'as', 'it', 'its', 'this', 'that', 'these', 'those',
    'null', 'none', 'true', 'false', '0', '1', '', '-', '/', '\\'
}


# ─────────────────────────────────────────────
# 2. ASOSIY NLP ANALYZER KLASSI
# ─────────────────────────────────────────────

class NLPLogAnalyzer:
    """HEMIS log ma'lumotlarini NLP usullari bilan tahlil qilish"""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._prepare()

    # ── Tayyorlash ──────────────────────────────
    def _prepare(self):
        """Ma'lumotlarni NLP tahlili uchun tayyorlash"""
        # Vaqt ustunini parse qilish
        self.df['Yaratilgan'] = pd.to_datetime(
            self.df.get('Yaratilgan', pd.Series(dtype='object')),
            format='%d.%m.%Y %H:%M:%S', errors='coerce'
        )
        self.df['Soat'] = self.df['Yaratilgan'].dt.hour
        self.df['Kun']  = self.df['Yaratilgan'].dt.date

        # Xabar ustunini normallashtirish
        msg_col = next((c for c in self.df.columns if c in ['Xabar', 'Message', 'message']), None)
        if msg_col:
            self.df['_msg'] = self.df[msg_col].fillna('').astype(str).str.lower().str.strip()
        else:
            self.df['_msg'] = ''

        # Amal ustunini normallashtirish
        act_col = next((c for c in self.df.columns if c in ['Amal', 'Action', 'action']), None)
        if act_col:
            self.df['_act'] = self.df[act_col].fillna('').astype(str).str.lower().str.strip()
        else:
            self.df['_act'] = ''

    # ── Yordamchi funksiyalar ───────────────────
    @staticmethod
    def _tokenize(text: str) -> list:
        """Matnni tokenlarga ajratish"""
        text = re.sub(r'[^\w\s]', ' ', str(text).lower())
        tokens = text.split()
        return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]

    @staticmethod
    def _get_severity(text: str) -> str:
        """Xabarning og'irlik darajasini aniqlash"""
        text_lower = str(text).lower()
        for level in ['critical', 'error', 'warning', 'info', 'debug']:
            if any(kw in text_lower for kw in SEVERITY_KEYWORDS[level]):
                return level
        return 'info'

    @staticmethod
    def _categorize_action(action: str) -> str:
        """Amalni semantik kategoriyaga joylashtirish"""
        action_lower = str(action).lower()
        for category, keywords in ACTION_CATEGORIES.items():
            if any(kw in action_lower for kw in keywords):
                return category
        return 'Boshqa'

    @staticmethod
    def _extract_log_template(message: str) -> str:
        """Log xabaridan shablon ajratish (raqam/ID larni <NUM> bilan almashtirish)"""
        msg = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '<IP>', str(message))
        msg = re.sub(r'\b[0-9a-f]{8,}\b', '<ID>', msg)
        msg = re.sub(r'\b\d+\b', '<NUM>', msg)
        msg = re.sub(r'\s+', ' ', msg).strip()
        return msg

    # ── 1. Keyword Extraction ────────────────────
    def extract_keywords(self, top_n: int = 30) -> list:
        """
        Log xabarlaridan eng muhim kalit so'zlarni ajratish.
        TF (term frequency) asosida.
        """
        all_tokens = []
        for msg in self.df['_msg']:
            all_tokens.extend(self._tokenize(msg))

        # Amal nomlaridan ham token olish
        for act in self.df['_act']:
            all_tokens.extend(self._tokenize(act.replace('/', ' ').replace('-', ' ')))

        freq = Counter(all_tokens)

        # Natijani formatlash
        result = []
        total = sum(freq.values()) or 1
        for word, count in freq.most_common(top_n):
            result.append({
                'keyword': word,
                'frequency': count,
                'percentage': round(count / total * 100, 2),
                'category': self._detect_keyword_category(word)
            })
        return result

    def _detect_keyword_category(self, word: str) -> str:
        """Kalit so'zning kategoriyasini aniqlash"""
        for level, kws in SEVERITY_KEYWORDS.items():
            if word in kws:
                return f'severity:{level}'
        for cat, kws in ACTION_CATEGORIES.items():
            if word in kws:
                return f'action:{cat}'
        return 'general'

    # ── 2. Error Classification ──────────────────
    def classify_errors(self) -> dict:
        """
        Log xabarlarini xatolik darajalariga ko'ra tasniflash.
        """
        self.df['severity'] = self.df['_msg'].apply(self._get_severity)

        # Umumiy taqsimot
        dist = self.df['severity'].value_counts().to_dict()

        # Har bir daraja uchun namuna xabarlar
        samples = {}
        for level in ['critical', 'error', 'warning', 'info', 'debug']:
            subset = self.df[self.df['severity'] == level]
            if len(subset) > 0:
                msgs = subset['_msg'].dropna().unique()[:5].tolist()
                samples[level] = msgs

        # Vaqt bo'yicha xatoliklar
        error_df = self.df[self.df['severity'].isin(['critical', 'error'])]
        hourly_errors = {}
        if 'Soat' in error_df.columns:
            hourly_errors = error_df.groupby('Soat').size().to_dict()
            hourly_errors = {int(k): int(v) for k, v in hourly_errors.items()}

        # Eng ko'p xatolik chiqargan adminlar
        admin_col = next((c for c in self.df.columns if c in ['Admin nomi', 'Admin']), None)
        top_error_admins = []
        if admin_col:
            err_admins = (
                error_df[admin_col]
                .value_counts()
                .head(10)
                .reset_index()
            )
            err_admins.columns = ['admin', 'error_count']
            top_error_admins = err_admins.to_dict('records')

        return {
            'distribution': {k: int(v) for k, v in dist.items()},
            'samples': samples,
            'hourly_errors': hourly_errors,
            'top_error_admins': top_error_admins,
            'total_errors': int(error_df.shape[0]),
            'error_rate': round(error_df.shape[0] / max(len(self.df), 1) * 100, 2)
        }

    # ── 3. Log Template Extraction ───────────────
    def extract_templates(self, top_n: int = 20) -> list:
        """
        O'xshash log xabarlarini umumiy shablonlarga guruhlash (Drain-lite).
        """
        templates = Counter()
        for msg in self.df['_msg']:
            tmpl = self._extract_log_template(msg)
            if tmpl:
                templates[tmpl] += 1

        result = []
        for tmpl, count in templates.most_common(top_n):
            result.append({
                'template': tmpl,
                'count': count,
                'percentage': round(count / max(len(self.df), 1) * 100, 2),
                'severity': self._get_severity(tmpl)
            })
        return result

    # ── 4. Action Semantic Grouping ──────────────
    def group_actions_semantically(self) -> dict:
        """
        Amallarni semantik kategoriyalarga guruhlash va statistika.
        """
        self.df['action_category'] = self.df['_act'].apply(self._categorize_action)

        # Kategoriyalar bo'yicha statistika
        cat_stats = {}
        for cat in ACTION_CATEGORIES.keys():
            subset = self.df[self.df['action_category'] == cat]
            if len(subset) == 0:
                continue

            admin_col = next((c for c in self.df.columns if c in ['Admin nomi', 'Admin']), None)
            top_actions = subset['_act'].value_counts().head(5).to_dict()

            cat_stats[cat] = {
                'count': int(len(subset)),
                'percentage': round(len(subset) / max(len(self.df), 1) * 100, 2),
                'top_actions': {k: int(v) for k, v in top_actions.items()},
                'unique_admins': int(subset[admin_col].nunique()) if admin_col else 0,
                'peak_hour': int(subset['Soat'].mode()[0]) if 'Soat' in subset.columns and len(subset) > 0 else 0
            }

        return cat_stats

    # ── 5. N-gram Tahlili ────────────────────────
    def extract_ngrams(self, n: int = 2, top_n: int = 20) -> list:
        """
        Eng ko'p uchraydigan n-gramlarni ajratish (bigram/trigram).
        """
        ngrams = Counter()
        for msg in self.df['_msg']:
            tokens = self._tokenize(msg)
            for i in range(len(tokens) - n + 1):
                gram = ' '.join(tokens[i:i+n])
                ngrams[gram] += 1

        result = []
        for gram, count in ngrams.most_common(top_n):
            result.append({
                'ngram': gram,
                'n': n,
                'count': count,
                'percentage': round(count / max(len(self.df), 1) * 100, 2)
            })
        return result

    # ── 6. Umumiy NLP Hisobot ────────────────────
    def generate_nlp_report(self) -> dict:
        """
        Barcha NLP tahlillarini bitta hisobotga jamlash.
        """
        print("[NLP] Kalit so'zlar ajratilmoqda...")
        keywords = self.extract_keywords(top_n=30)

        print("[NLP] Xatoliklar tasniflanmoqda...")
        errors = self.classify_errors()

        print("[NLP] Shablon ajratilmoqda...")
        templates = self.extract_templates(top_n=15)

        print("[NLP] Amallar guruhlash...")
        action_groups = self.group_actions_semantically()

        print("[NLP] N-gramlar hisoblanyapdi...")
        bigrams  = self.extract_ngrams(n=2, top_n=15)
        trigrams = self.extract_ngrams(n=3, top_n=10)

        # Umumiy ko'rsatkichlar
        total = len(self.df)
        admin_col = next((c for c in self.df.columns if c in ['Admin nomi', 'Admin']), None)

        summary = {
            'total_logs':       total,
            'unique_admins':    int(self.df[admin_col].nunique()) if admin_col else 0,
            'unique_actions':   int(self.df['_act'].nunique()),
            'unique_templates': len(templates),
            'error_rate_pct':   errors['error_rate'],
            'top_keywords':     [k['keyword'] for k in keywords[:10]],
            'dominant_category': max(action_groups, key=lambda x: action_groups[x]['count'])
                                 if action_groups else 'N/A'
        }

        return {
            'summary':       summary,
            'keywords':      keywords,
            'error_analysis': errors,
            'templates':     templates,
            'action_groups': action_groups,
            'bigrams':       bigrams,
            'trigrams':      trigrams,
            'generated_at':  datetime.now().isoformat()
        }


# ─────────────────────────────────────────────
# 3. FLASK ENDPOINT UCHUN WRAPPER
# ─────────────────────────────────────────────

def run_nlp_analysis(df: pd.DataFrame) -> dict:
    """
    app.py dan chaqiriladigan asosiy funksiya.
    """
    try:
        analyzer = NLPLogAnalyzer(df)
        report = analyzer.generate_nlp_report()
        return {'success': True, 'data': report}
    except Exception as e:
        import traceback
        return {'success': False, 'error': str(e), 'trace': traceback.format_exc()}


# ─────────────────────────────────────────────
# 4. TEST (to'g'ridan-to'g'ri ishga tushirish)
# ─────────────────────────────────────────────
if __name__ == '__main__':
    # Demo ma'lumotlar bilan test
    import random
    random.seed(42)

    actions = [
        'dashboard/login', 'dashboard/profile', 'student/student',
        'curriculum/schedule-view', 'archive/diploma-view',
        'credit/grade-add', 'student/student-edit', 'dashboard/logout',
        'education/attendance', 'teacher/time-table', 'system/classifier'
    ]
    messages = [
        'Login muvaffaqiyatli', 'Error: connection timeout',
        'Student record updated', 'Invalid token', 'Schedule created',
        'Warning: slow query detected', 'Grade added successfully',
        'Fatal: database connection failed', 'View profile', 'Logout ok'
    ]
    admins = ['Ali Karimov', 'Zulfiya Rahimova', 'Bobur Toshmatov',
              'Nilufar Yusupova', 'Jasur Mirzayev']

    rows = []
    for i in range(500):
        dt = f"{random.randint(1,30):02d}.09.2025 {random.randint(8,22):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"
        rows.append({
            'ID': i,
            'Admin nomi': random.choice(admins),
            'Yaratilgan': dt,
            'IP': f"192.168.{random.randint(1,5)}.{random.randint(1,50)}",
            'Amal': random.choice(actions),
            'Xabar': random.choice(messages),
            "So'rov": '{}',
            'Post': '{}'
        })

    demo_df = pd.DataFrame(rows)
    result = run_nlp_analysis(demo_df)

    if result['success']:
        d = result['data']
        print("\n=== NLP TAHLIL NATIJASI ===")
        print(f"Jami loglar    : {d['summary']['total_logs']}")
        print(f"Error ulushi   : {d['summary']['error_rate_pct']}%")
        print(f"Top kalit so'z : {d['summary']['top_keywords'][:5]}")
        print(f"Dominant guruh : {d['summary']['dominant_category']}")
        print(f"\nXatoliklar taqsimoti: {d['error_analysis']['distribution']}")
        print(f"\nTop shablonlar:")
        for t in d['templates'][:3]:
            print(f"  [{t['count']}x] {t['template'][:60]}")
        print(f"\nAmal guruhlari:")
        for cat, stats in d['action_groups'].items():
            print(f"  {cat}: {stats['count']} ta ({stats['percentage']}%)")
    else:
        print("XATO:", result['error'])
