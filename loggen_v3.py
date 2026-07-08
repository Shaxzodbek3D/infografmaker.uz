"""
Parametric mathematical model of information-system logs (v3).
No empirical calibration: all parameters are literature-motivated and
exposed as model knobs.

Model:
  Activity:  N_u ~ round( LogNormal(mu, sigma) )        w.p. 1-pi
             N_u ~ round( 10 + 15 * Pareto(alpha) )     w.p. pi   (heavy tail)
  Timestamps: NHPP with diurnal intensity
             lambda(h) = b + A1*exp(-(h-m1)^2/2s1^2) + A2*exp(-(h-m2)^2/2s2^2)
             (bimodal working-day profile)
  Actions:   Zipf-like categorical over K types
  Population: (1-rho) light "student" users + rho "staff" users with
             elevated activity and administrative action mix.
Anomalies: six mechanism-typed scenarios (extreme-value / structural)
with severity in {0.5 easy, 1.0 medium, 2.0 hard (subtle)}.
"""
import random
import numpy as np
import pandas as pd

K_ACTIONS = 30
ACTIONS = [f"act_{i:02d}" for i in range(K_ACTIONS)]
ADMIN_ACTIONS = ACTIONS[20:]                      # last 10 types = administrative
STUDENT_ACTIONS = ACTIONS[:20]

def zipf_p(items, s=1.6):
    r = np.arange(1, len(items) + 1, dtype=float)
    p = r ** (-s); return p / p.sum()
SA_P = zipf_p(STUDENT_ACTIONS)
AA_P = zipf_p(ADMIN_ACTIONS, 1.2)

def diurnal_p(b=0.2, A1=1.0, m1=11, s1=2.0, A2=0.7, m2=20, s2=2.5):
    h = np.arange(24)
    lam = b + A1*np.exp(-(h-m1)**2/(2*s1**2)) + A2*np.exp(-(h-m2)**2/(2*s2**2))
    return lam / lam.sum()
HOUR_P = diurnal_p()
HOURS = np.arange(24)

def rand_ip(rng):
    return ".".join(str(rng.integers(1, 255)) for _ in range(4))

def sample_times(rng, n, days, hour_p=HOUR_P):
    day = rng.integers(0, days, n)
    hour = rng.choice(HOURS, n, p=hour_p)
    sec = rng.integers(0, 3600, n)
    base = pd.Timestamp("2026-05-01")
    return [base + pd.Timedelta(days=int(d), hours=int(h), seconds=int(s))
            for d, h, s in zip(day, hour, sec)]

def sample_activity(rng, n, mu=0.26, sigma=0.52, pi=0.01, alpha=1.5):
    x = rng.lognormal(mean=mu, sigma=sigma, size=n)
    tail = rng.random(n) < pi
    x[tail] = 10 + 15 * rng.pareto(alpha, tail.sum())
    return np.clip(np.round(x), 1, None).astype(int)

def student(rng, uid, days, tail):
    n = int(sample_activity(rng, 1, sigma=tail["sigma"], pi=tail["pi"],
                            alpha=tail["alpha"])[0])
    ips = [rand_ip(rng) for _ in range(1 + (rng.random() < 0.15))]
    acts = rng.choice(STUDENT_ACTIONS, n, p=SA_P)
    return [(uid, t, random.choice(ips), a, rng.random() < 0.97)
            for t, a in zip(sample_times(rng, n, days), acts)]

def staff(rng, uid, days):
    n = int(rng.lognormal(np.log(25), 0.6))
    ips = [rand_ip(rng) for _ in range(rng.integers(1, 5))]
    mix = rng.random(n) < 0.6
    acts = np.where(mix, rng.choice(ADMIN_ACTIONS, n, p=AA_P),
                    rng.choice(STUDENT_ACTIONS, n, p=SA_P))
    return [(uid, t, random.choice(ips), a, rng.random() < 0.96)
            for t, a in zip(sample_times(rng, n, days), acts)]

def anomaly(rng, uid, sc, days, sev, tail):
    sub = sev / 2.0
    ev = []
    if sc == "S1_account_takeover":
        ev += student(rng, uid, days, tail)
        night = np.zeros(24); night[2:6] = 1; night /= night.sum()
        n = max(4, int(rng.integers(15, 30) * (1 - 0.7*sub)))
        ev += [(uid, t, rand_ip(rng), random.choice(STUDENT_ACTIONS), True)
               for t in sample_times(rng, n, days, night)]
    elif sc == "S2_bruteforce":
        n = max(8, int(rng.integers(25, 80) * (1 - 0.7*sub)))
        start = sample_times(rng, 1, days)[0]; ip = rand_ip(rng)
        gap = int(5 + 60*sub)
        ev += [(uid, start + pd.Timedelta(seconds=i*rng.integers(2, gap)),
                ip, ACTIONS[0], rng.random() < 0.08) for i in range(n)]
    elif sc == "S3_scraping":
        n = max(10, int(rng.integers(60, 200) * (1 - 0.75*sub)))
        act = random.choice(STUDENT_ACTIONS[1:6])
        start = sample_times(rng, 1, days)[0]
        ev += [(uid, start + pd.Timedelta(seconds=i*rng.integers(2, 15)),
                rand_ip(rng) if rng.random() < .1 else "10.0.0.9", act, True)
               for i in range(n)]
    elif sc == "S4_ip_hopping":
        n = max(5, int(rng.integers(8, 25) * (1 - 0.5*sub)))
        ts = sorted(sample_times(rng, n, days))
        ev += [(uid, t, rand_ip(rng), ACTIONS[0], True) for t in ts]
    elif sc == "S5_privilege_misuse":
        ev += student(rng, uid, days, tail)
        n = max(3, int(rng.integers(5, 12) * (1 - 0.5*sub)))
        ev += [(uid, t, rand_ip(rng), random.choice(ADMIN_ACTIONS), True)
               for t in sample_times(rng, n, days)]
    elif sc == "S6_stealth_temporal":
        n = int(rng.integers(6, 16))
        flat = np.ones(24)/24
        ip = rand_ip(rng)
        ev += [(uid, t, ip, random.choice(STUDENT_ACTIONS), True)
               for t in sample_times(rng, n, days, flat)]
    return ev

SCEN = ("S1_account_takeover", "S2_bruteforce", "S3_scraping",
        "S4_ip_hopping", "S5_privilege_misuse", "S6_stealth_temporal")

def generate(n_users=5000, days=30, contamination=0.03, staff_share=0.05,
             seed=42, sigma=0.52, pi=0.01, alpha=1.5):
    rng = np.random.default_rng(seed); random.seed(seed)
    tail = {"sigma": sigma, "pi": pi, "alpha": alpha}
    n_anom = int(n_users * contamination)
    n_norm = n_users - n_anom
    n_staff = int(n_norm * staff_share)
    rows, labels = [], {}
    for i in range(n_norm - n_staff):
        uid = f"U{i:05d}"; labels[uid] = "normal"
        rows += student(rng, uid, days, tail)
    for i in range(n_staff):
        uid = f"W{i:05d}"; labels[uid] = "normal"
        rows += staff(rng, uid, days)
    sevs = [0.5, 1.0, 2.0]
    for j in range(n_anom):
        uid = f"A{j:05d}"
        sc = SCEN[j % len(SCEN)]
        sev = sevs[(j // len(SCEN)) % 3]
        labels[uid] = f"{sc}|sev={sev}"
        rows += anomaly(rng, uid, sc, days, sev, tail)
    log = pd.DataFrame(rows, columns=["user_id","timestamp","ip","action","success"])
    log = log.sort_values("timestamp").reset_index(drop=True)
    lab = pd.DataFrame(labels.items(), columns=["user_id","label"])
    return log, lab

if __name__ == "__main__":
    for sigma, pi, alpha in [(0.35,0.0,1.5),(0.5,0.005,1.8),(0.52,0.01,1.5),
                              (0.7,0.02,1.2),(0.9,0.03,1.0)]:
        log, lab = generate(seed=1, sigma=sigma, pi=pi, alpha=alpha)
        ua = log[log.user_id.str.startswith(('U','W'))].groupby('user_id').size()
        print(f"sigma={sigma} pi={pi} alpha={alpha}: skew={ua.skew():6.2f} "
              f"p95={ua.quantile(.95):.0f} max={ua.max()}")
