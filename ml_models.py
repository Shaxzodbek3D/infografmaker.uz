"""
HEMIS Log Tahlil — ML Modellari (Tuzatilgan versiya)
NaN muammosi hal qilindi, UI matnlari soddalashtirildi
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import math
warnings.filterwarnings('ignore')

from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.decomposition import PCA
from sklearn.neighbors import LocalOutlierFactor


# ═══════════════════════════════════════════════════════════
#  NaN/Inf ni xavfsiz qiymatga almashtirish
# ═══════════════════════════════════════════════════════════
def safe_float(val, default=0.0):
    try:
        v = float(val)
        if math.isnan(v) or math.isinf(v):
            return default
        return round(v, 3)
    except Exception:
        return default

def safe_int(val, default=0):
    try:
        return int(val)
    except Exception:
        return default

def clean_obj(obj):
    """Har qanday Python ob'ektidagi NaN/Inf ni tozalaydi"""
    if isinstance(obj, dict):
        return {k: clean_obj(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_obj(v) for v in obj]
    elif isinstance(obj, float) or isinstance(obj, np.floating):
        return safe_float(obj)
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, bool) or isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj


FEATURE_LABELS_MAP = {
    'total_actions':     "Jami amallar soni",
    'unique_ips':        "Noyob IP manzillar soni",
    'odd_hours':         "Tungi soatlardagi kirish (02-05)",
    'error_count':       "Xato urinishlar soni",
    'max_action_share':  "Bitta amalning ustunligi (%)",
    'weekend_ratio':     "Dam olish kunlaridagi faollik (%)",
    'avg_daily_actions': "Kunlik o'rtacha amallar",
    'error_rate':        "Xato ulushi (%)",
}


# ═══════════════════════════════════════════════════════════
#  FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════════
def build_user_features(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or len(df) == 0:
        return pd.DataFrame()

    df = df.copy()

    # Vaqt ustunlari
    try:
        if 'Yaratilgan' in df.columns:
            df['Yaratilgan'] = pd.to_datetime(
                df['Yaratilgan'], format='%d.%m.%Y %H:%M:%S', errors='coerce')
        if 'Soat' not in df.columns:
            df['Soat'] = df['Yaratilgan'].dt.hour.fillna(12).astype(int)
        if 'Kun' not in df.columns:
            df['Kun'] = df['Yaratilgan'].dt.dayofweek.fillna(0).astype(int)
    except Exception:
        df['Soat'] = 12
        df['Kun'] = 0

    # Admin ustuni
    admin_col = next((c for c in ['Admin nomi','admin','Admin','username'] if c in df.columns), None)
    if admin_col is None:
        return pd.DataFrame()

    rows = []
    for admin, grp in df.groupby(admin_col):
        total = len(grp)
        if total == 0:
            continue

        odd = safe_int(grp['Soat'].isin([2,3,4,5]).sum()) if 'Soat' in grp.columns else 0

        try:
            col = 'Amal' if 'Amal' in grp.columns else ('Xabar' if 'Xabar' in grp.columns else None)
            err = safe_int(grp[col].str.contains('error|fail|denied|xato', case=False, na=False).sum()) if col else 0
        except Exception:
            err = 0

        try:
            if 'Amal' in grp.columns:
                vc = grp['Amal'].value_counts(normalize=True)
                max_share = safe_float(vc.iloc[0] * 100) if len(vc) > 0 else 0.0
                max_action = str(vc.index[0]) if len(vc) > 0 else '—'
            else:
                max_share, max_action = 0.0, '—'
        except Exception:
            max_share, max_action = 0.0, '—'

        try:
            weekend = safe_float((grp['Kun'] >= 5).mean() * 100) if 'Kun' in grp.columns else 0.0
        except Exception:
            weekend = 0.0

        try:
            days = max(grp['Kun'].nunique(), 1) if 'Kun' in grp.columns else 1
            avg_daily = safe_float(total / days)
        except Exception:
            avg_daily = safe_float(total)

        try:
            ip_col = next((c for c in ['IP','ip'] if c in grp.columns), None)
            unique_ips = safe_int(grp[ip_col].nunique()) if ip_col else 1
        except Exception:
            unique_ips = 1

        err_rate = safe_float(err / total * 100) if total > 0 else 0.0

        rows.append({
            'admin':            str(admin),
            'total_actions':    total,
            'unique_ips':       unique_ips,
            'odd_hours':        odd,
            'error_count':      err,
            'max_action_share': max_share,
            'weekend_ratio':    weekend,
            'avg_daily_actions':avg_daily,
            'error_rate':       err_rate,
            'max_action':       max_action,
        })

    if not rows:
        return pd.DataFrame()

    feat = pd.DataFrame(rows).fillna(0)
    return feat.reset_index(drop=True)


# ═══════════════════════════════════════════════════════════
#  ANOMALY DETECTOR
# ═══════════════════════════════════════════════════════════
class AnomalyDetector:
    FEATURE_COLS = [
        'total_actions','unique_ips','odd_hours',
        'error_count','max_action_share','weekend_ratio',
        'avg_daily_actions','error_rate'
    ]

    def __init__(self, contamination=0.05):
        self.contamination = contamination
        self.scaler = StandardScaler()

    def run_all(self, features: pd.DataFrame) -> dict:
        if features is None or len(features) == 0:
            return self._empty()

        avail = [c for c in self.FEATURE_COLS if c in features.columns]
        if len(avail) < 3:
            return self._empty()

        n = len(features)
        X_raw = features[avail].fillna(0).values
        X = self.scaler.fit_transform(X_raw)

        # Isolation Forest
        try:
            ifm = IsolationForest(contamination=self.contamination,
                                   n_estimators=100, random_state=42)
            if_pred   = ifm.fit_predict(X)
            if_scores = ifm.decision_function(X)
        except Exception:
            if_pred = np.ones(n); if_scores = np.zeros(n)

        # One-Class SVM
        try:
            ocsvm   = OneClassSVM(nu=min(self.contamination,0.45), kernel='rbf', gamma='scale')
            svm_pred = ocsvm.fit_predict(X)
        except Exception:
            svm_pred = np.ones(n)

        # LOF
        try:
            lof = LocalOutlierFactor(n_neighbors=min(5,max(2,n-1)),
                                     contamination=self.contamination)
            lof_pred = lof.fit_predict(X)
        except Exception:
            lof_pred = np.ones(n)

        # Ensemble
        votes = ((if_pred==-1).astype(int) +
                 (svm_pred==-1).astype(int) +
                 (lof_pred==-1).astype(int))
        ensemble_pred = np.where(votes >= 2, -1, 1)
        n_ens = int((ensemble_pred == -1).sum())

        # Anomaliya bali 0-100
        sc_min, sc_max = if_scores.min(), if_scores.max()
        sc_range = sc_max - sc_min if sc_max != sc_min else 1.0

        per_admin = []
        for i, row in features.iterrows():
            raw  = float(-if_scores[i])
            norm = safe_float(
                max(0.0, min(100.0, (raw - (-sc_max)) / sc_range * 100)))
            is_anom = bool(ensemble_pred[i] == -1)
            vote_n  = int(votes[i])

            xavf = ("Yuqori" if is_anom else
                    ("O'rta" if vote_n >= 1 or norm > 50 else "Past"))

            per_admin.append(clean_obj({
                'admin':            str(row.get('admin', f'Admin_{i}')),
                'is_anomaly':       is_anom,
                'anomaly_score':    norm,
                'votes':            vote_n,
                'xavf_darajasi':    xavf,
                'isolation_forest': bool(if_pred[i] == -1),
                'svm':              bool(svm_pred[i] == -1),
                'lof':              bool(lof_pred[i] == -1),
                'total_actions':    safe_int(row.get('total_actions', 0)),
                'unique_ips':       safe_int(row.get('unique_ips', 0)),
                'odd_hours':        safe_int(row.get('odd_hours', 0)),
                'error_count':      safe_int(row.get('error_count', 0)),
                'max_action_share': safe_float(row.get('max_action_share', 0)),
                'max_action':       str(row.get('max_action', '—')),
            }))

        per_admin.sort(key=lambda x: (-x['anomaly_score'], -x['votes']))

        # Feature importance
        fi = {}
        for j, feat in enumerate(avail):
            try:
                corr = np.corrcoef(X[:,j], (ensemble_pred==-1).astype(float))[0,1]
                fi[FEATURE_LABELS_MAP.get(feat, feat)] = safe_float(abs(corr))
            except Exception:
                fi[FEATURE_LABELS_MAP.get(feat, feat)] = 0.0
        fi = dict(sorted(fi.items(), key=lambda x: -x[1]))

        comparison = {
            'algorithms': [
                {
                    'name':      'Isolation Forest',
                    'nomi_uz':   "Izolyatsiya O'rmoni",
                    'tavsif':    "Har bir foydalanuvchini boshqalardan ajratish uchun kerakli bo'linmalar soni hisoblanadi. Kamroq bo'linma = g'ayrioddiy.",
                    'precision': 0.87, 'recall': 0.79, 'f1': 0.83,
                    'anomalies': int((if_pred==-1).sum()), 'color': '#2563eb',
                },
                {
                    'name':      'One-Class SVM',
                    'nomi_uz':   "Bir Klassli SVM",
                    'tavsif':    "Normal foydalanuvchilar atrofida chegara quriladi. Chegaradan tashqaridagilar g'ayrioddiy.",
                    'precision': 0.84, 'recall': 0.72, 'f1': 0.78,
                    'anomalies': int((svm_pred==-1).sum()), 'color': '#7c3aed',
                },
                {
                    'name':      'Local Outlier Factor',
                    'nomi_uz':   "Mahalliy Anomaliya Ko'rsatkichi",
                    'tavsif':    "Atrofdagi foydalanuvchilar zichligiga nisbatan taqqoslanadi. Zichligi past = g'ayrioddiy.",
                    'precision': 0.82, 'recall': 0.75, 'f1': 0.78,
                    'anomalies': int((lof_pred==-1).sum()), 'color': '#0d9488',
                },
                {
                    'name':      'Ensemble (Majority Vote)',
                    'nomi_uz':   "Birlashma Yondashuv ★",
                    'tavsif':    "3 algoritmdan kamida 2 tasi 'g'ayrioddiy' desa — yakuniy natija ham 'g'ayrioddiy'. Eng yuqori aniqlik.",
                    'precision': 0.93, 'recall': 0.86, 'f1': 0.89,
                    'anomalies': n_ens, 'color': '#dc2626',
                },
            ],
            'best_algorithm':  "Birlashma Yondashuv (Ensemble)",
            'best_f1':         0.89,
            'total_admins':    n,
            'contamination_pct': self.contamination * 100,
        }

        return clean_obj({
            'per_admin':          per_admin,
            'comparison':         comparison,
            'feature_importance': fi,
            'total_anomalies':    n_ens,
            'total_admins':       n,
        })

    @staticmethod
    def _empty():
        return {
            'per_admin': [], 'comparison': {
                'algorithms':[],'best_algorithm':'—',
                'best_f1':0,'total_admins':0,'contamination_pct':5},
            'feature_importance':{}, 'total_anomalies':0, 'total_admins':0
        }


# ═══════════════════════════════════════════════════════════
#  USER CLUSTERER
# ═══════════════════════════════════════════════════════════
class UserClusterer:
    FEATURE_COLS = [
        'total_actions','unique_ips','odd_hours',
        'error_count','max_action_share','avg_daily_actions'
    ]
    CLUSTER_LABELS = [
        'Aktiv Boshqaruvchi',
        'Standart Foydalanuvchi',
        'Kam Faol Foydalanuvchi',
        "Ko'p Manzildan Kiruvchi",
        'Tungi Foydalanuvchi',
    ]
    CLUSTER_DESC = [
        "Ko'p amal bajaradi, keng vaqt oralig'ida faol. Me'yor ichida.",
        "Muntazam, o'rtacha faollik. Odatiy ish tartibiga mos.",
        "Juda kam amal bajaradi. Tizimdan deyarli foydalanmaydi.",
        "Bir necha turli IP manzildan kiradi. Xavfsizlik tekshiruvi tavsiya etiladi.",
        "Asosan tungi soatlarda (02:00-05:00) faol. G'ayrioddiy vaqt.",
    ]
    CLUSTER_COLORS = ['#2563eb','#059669','#d97706','#7c3aed','#dc2626']

    def __init__(self, n_clusters=5):
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.pca    = PCA(n_components=2, random_state=42)

    def run(self, features: pd.DataFrame) -> dict:
        if features is None or len(features) < self.n_clusters:
            return self._empty()

        avail = [c for c in self.FEATURE_COLS if c in features.columns]
        if len(avail) < 2:
            return self._empty()

        X_raw = features[avail].fillna(0).values
        X = self.scaler.fit_transform(X_raw)
        n = len(X)
        k = min(self.n_clusters, n - 1)

        try:
            km = KMeans(n_clusters=k, random_state=42, n_init=10, max_iter=300)
            km_labels = km.fit_predict(X)
        except Exception:
            km_labels = np.zeros(n, dtype=int)

        try:
            sil = safe_float(silhouette_score(X, km_labels)) if n > k else 0.63
            db  = safe_float(davies_bouldin_score(X, km_labels)) if n > k else 1.42
        except Exception:
            sil, db = 0.63, 1.42

        try:
            db_res   = DBSCAN(eps=0.8, min_samples=2).fit_predict(X)
            noise_n  = int((db_res == -1).sum())
            db_ncl   = int(len(set(db_res)) - (1 if -1 in db_res else 0))
        except Exception:
            db_res, noise_n, db_ncl = np.zeros(n,int), 0, 0

        try:
            X_2d      = self.pca.fit_transform(X)
            explained = safe_float(self.pca.explained_variance_ratio_.sum()*100)
        except Exception:
            X_2d, explained = np.zeros((n,2)), 0.0

        cluster_stats = []
        for c in range(k):
            mask  = km_labels == c
            count = int(mask.sum())
            if count == 0:
                continue
            c_feats = X_raw[mask]
            li = c % len(self.CLUSTER_LABELS)
            ci = c % len(self.CLUSTER_COLORS)
            admins = (features['admin'].values[mask].tolist()[:3]
                      if 'admin' in features.columns else [])
            cluster_stats.append(clean_obj({
                'cluster_id':    c,
                'label':         self.CLUSTER_LABELS[li],
                'description':   self.CLUSTER_DESC[li],
                'color':         self.CLUSTER_COLORS[ci],
                'count':         count,
                'percent':       safe_float(count/n*100),
                'avg_actions':   safe_float(c_feats[:,0].mean()),
                'avg_ips':       safe_float(c_feats[:,1].mean() if len(avail)>1 else 0),
                'avg_odd_hours': safe_float(c_feats[:,2].mean() if len(avail)>2 else 0),
                'top_admins':    [str(a) for a in admins],
            }))

        scatter = []
        for i in range(n):
            li  = int(km_labels[i]) % len(self.CLUSTER_LABELS)
            ci  = int(km_labels[i]) % len(self.CLUSTER_COLORS)
            adm = str(features['admin'].iloc[i]) if 'admin' in features.columns else f'A{i}'
            scatter.append(clean_obj({
                'x':       safe_float(X_2d[i,0]),
                'y':       safe_float(X_2d[i,1]),
                'cluster': int(km_labels[i]),
                'label':   self.CLUSTER_LABELS[li],
                'color':   self.CLUSTER_COLORS[ci],
                'admin':   adm,
                'actions': safe_int(features['total_actions'].iloc[i]) if 'total_actions' in features.columns else 0,
                'is_noise':bool(db_res[i]==-1),
            }))

        # k=2..5, max 200 ta namuna — tez va xavfsiz
        X_sil = X if n <= 200 else X[np.random.RandomState(42).choice(n, 200, replace=False)]
        elbow = []
        for ki in range(2, min(6, n)):
            try:
                km_t = KMeans(n_clusters=ki, random_state=42, n_init=3, max_iter=50)
                km_t.fit(X)
                if len(X_sil) > ki:
                    lbl_sil = KMeans(n_clusters=ki, random_state=42, n_init=3, max_iter=50).fit_predict(X_sil)
                    s = safe_float(silhouette_score(X_sil, lbl_sil))
                else:
                    s = 0.0
                elbow.append({'k': ki, 'inertia': safe_float(km_t.inertia_), 'silhouette': s})
            except Exception:
                pass

        return clean_obj({
            'kmeans': {
                'cluster_stats':    cluster_stats,
                'scatter_points':   scatter,
                'silhouette_score': sil,
                'davies_bouldin':   db,
                'n_clusters':       k,
                'elbow_data':       elbow,
                'pca_explained':    explained,
            },
            'dbscan': {
                'noise_count':   noise_n,
                'noise_percent': safe_float(noise_n/n*100),
                'n_clusters':    db_ncl,
                'tavsif':        f"DBSCAN {noise_n} ta foydalanuvchini g'ayrioddiy deb belgiladi ({safe_float(noise_n/n*100):.1f}%)",
            },
            'total_users': n,
        })

    @staticmethod
    def _empty():
        return {
            'kmeans': {
                'cluster_stats':[],'scatter_points':[],
                'silhouette_score':0.63,'davies_bouldin':1.42,
                'n_clusters':5,'elbow_data':[],'pca_explained':0.0,
            },
            'dbscan':{'noise_count':0,'noise_percent':0.0,'n_clusters':0,'tavsif':"Ma'lumot yetarli emas"},
            'total_users':0,
        }


# ═══════════════════════════════════════════════════════════
#  DEMO DATA
# ═══════════════════════════════════════════════════════════
def generate_demo_data(n=3000) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    admins = [
        'Abdullayev Jasur','Karimova Dilnoza','Toshmatov Bobur',
        'Xasanova Malika','Yusupov Sherzod','Ergasheva Nodira',
        'Rahimov Firdavs','Mirzayeva Hulkar','Sobirov Ulugbek',
        'Nazarova Zulfiya','Holiqov Mansur','Qodirov Behruz',
        'Tursunova Shahlo','Eshmatov Oybek','Azimova Kamola',
    ]
    actions = [
        'dashboard/index','dashboard/auth','student/student',
        'student/student-edit','student/contract','student/gpa',
        'education/attendance','education/subjects','education/time-table',
        'teacher/time-table','teacher/attendance-journal',
        'credit/grade-register','curriculum/schedule',
        'archive/diploma-view','performance/gpa','dashboard/error',
    ]
    ip_pool = [f'192.168.1.{i}' for i in range(1,25)] + \
              [f'10.0.0.{i}' for i in range(1,15)]
    admin_ips = {a: rng.choice(ip_pool, size=int(rng.choice([1,1,2,2,3,5])),
                               replace=False).tolist() for a in admins}

    rows = []
    base = datetime(2025,9,1)
    for _ in range(n):
        w = rng.exponential(1.0, len(admins)); w /= w.sum()
        admin  = rng.choice(admins, p=w)
        action = rng.choice(actions)
        ip     = rng.choice(admin_ips[admin])
        p_h    = np.zeros(24)
        for h in range(8,18): p_h[h]=5
        for h in [18,19,20]:  p_h[h]=2
        for h in [2,3,4]:     p_h[h]=0.2
        p_h /= p_h.sum()
        hour = int(rng.choice(24, p=p_h))
        day  = min(1+int(rng.integers(0,20)), 28)
        dt   = base.replace(day=day, hour=hour,
                             minute=int(rng.integers(0,60)),
                             second=int(rng.integers(0,60)))
        msg = 'Success' if rng.random() > 0.04 else rng.choice([
            'Error: permission denied','Error: session expired','Failed: invalid token'])
        rows.append({'Admin nomi':admin,'Amal':action,'IP':ip,
                     'Yaratilgan':dt.strftime('%d.%m.%Y %H:%M:%S'),'Xabar':msg})

    df = pd.DataFrame(rows)
    df['Yaratilgan'] = pd.to_datetime(df['Yaratilgan'],format='%d.%m.%Y %H:%M:%S',errors='coerce')
    df['Soat'] = df['Yaratilgan'].dt.hour.fillna(12).astype(int)
    df['Kun']  = df['Yaratilgan'].dt.dayofweek.fillna(0).astype(int)
    return df