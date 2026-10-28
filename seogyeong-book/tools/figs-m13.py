"""figs-m13.py - 13장(8기법 결과 비교표) 새 그림과 새 사례 계산.
실행: python3 tools/figs-m13.py  (그림/ch13 에 컬러·흑백 PDF 생성, 숫자는 json 파일(인자로 경로 지정))
이 파일의 계산 함수는 원고의 새 숫자의 근거이다. 모든 세계는 가상이며 서경의 결과가 아니다.
눈 가린 검증 모의 실험의 약속: 가상 세계는 400 km x 400 km, 참 위치는 [60, 340] 구간에서 균등하게 뽑는다.
"""
import sys, os, math, json, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
from figlib import *

FS = 8.5
Z95 = 1.959964
R95 = math.sqrt(-2 * math.log(0.05))      # 2차원 정규의 95% 원 반경 / 표준편차 = 2.4477
HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.join(HERE, "..")


# ======================================================================= 공통 계산
def wilson(k, n, z=Z95):
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


def binom_pmf(n, p):
    return [math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]


def p_pass(n, p, thr):
    """k/n >= thr 일 확률(정확한 이항 합)"""
    kmin = math.ceil(thr * n - 1e-9)
    pm = binom_pmf(n, p)
    return sum(pm[kmin:])


def read_form():
    rows = list(csv.reader(open(os.path.join(BOOK, "표", "ch12-summary.csv"), encoding="utf-8")))[1:]
    out = []
    for r in rows:
        out.append(dict(name=r[0], x=float(r[1]), y=float(r[2]), dist=float(r[3]), area=float(r[4])))
    return out


FORM = read_form()
# 12장 가상 세계 8기법의 95% 영역 면적에서 정규 표준편차를 거꾸로 구한다: A = pi r^2, r = R95 * sigma
for f in FORM:
    f["r"] = math.sqrt(f["area"] / math.pi)
    f["sigma"] = f["r"] / R95

NAMES = [f["name"] for f in FORM]


# ======================================================================= 표본 모의 (사례 B2~B5, B8, B9, B11)
def sim_places(n, seed, lo=60.0, hi=340.0):
    rng = np.random.default_rng(seed)
    return rng.uniform(lo, hi, size=(n, 2))


def method_errors(n, seed, sig_mult=None, claim_mult=None):
    """8기법의 모의 중심 오차(2차원, km)와 주장 반경(km). T1~T3은 공통 오차를 나눠 가진다.
    sig_mult[k]: k번째 기법의 실제 오차 배율(없으면 1), claim_mult[k]: 주장 반경 배율(없으면 1)"""
    rng = np.random.default_rng(seed)
    sg = [f["sigma"] for f in FORM]
    sig_mult = sig_mult or {}
    claim_mult = claim_mult or {}
    common_sd = 6.0                               # T1~T3이 공유하는 오차(해석 분포 공유 가정 등)
    zc = rng.normal(0, common_sd, size=(n, 2))
    err = []
    for k in range(8):
        base = rng.normal(0, 1, size=(n, 2))
        m = sig_mult.get(k, 1.0)
        if k in (0, 1, 2):
            own = math.sqrt(max(sg[k] ** 2 - common_sd ** 2, 1.0))
            e = zc + base * own
        else:
            e = base * sg[k]
        if isinstance(m, np.ndarray):
            e = e * m[:, None]
        else:
            e = e * m
        err.append(e)
    # T8: T1~T3 중심의 평균(독립이라고 믿고 합친 것)
    e8 = (err[0] + err[1] + err[2]) / 3.0
    err[7] = e8
    claim_r = []
    for k in range(8):
        r = FORM[k]["r"] * claim_mult.get(k, 1.0)
        claim_r.append(r)
    # T8의 주장 반경은 12장 가상 세계 표의 값(304 km2)을 그대로 쓴다. 실제 오차는 T1~T3 중심의 평균이며 공통 오차가 남아 있다.
    return err, claim_r


def b2_blind_validation(n=40, seed=2026):
    mult = {4: 1.0}
    claim = {4: 0.8}                               # T5는 영역을 0.8배로 좁게 주장(과신)
    err, cr = method_errors(n, seed, claim_mult=claim)
    rows = []
    for k in range(8):
        d = np.hypot(err[k][:, 0], err[k][:, 1])
        hit = int((d <= cr[k]).sum())
        lo, hi = wilson(hit, n)
        med = float(np.median(d))
        area = math.pi * cr[k] ** 2
        # 브라이어 점수: 95% 영역이 맞는다는 예보 0.95에 대하여
        bs = float(np.mean((0.95 - (d <= cr[k]).astype(float)) ** 2))
        rows.append(dict(name=NAMES[k], hit=hit, n=n, rate=hit / n, lo=lo, hi=hi, med=med, area=area, bs=bs, r=cr[k]))
    return rows


def theory_cover(sig_true, r_claim):
    return 1 - math.exp(-r_claim ** 2 / (2 * sig_true ** 2))


def b3_leak(n=40, seed=303):
    """T3 베이즈: 정직한 오차 대 좌표가 새어 들어간 오차(참 위치 쪽으로 70% 당겨짐)"""
    rng = np.random.default_rng(seed)
    sg = FORM[2]["sigma"]
    r = FORM[2]["r"]
    e = rng.normal(0, sg, size=(n, 2))
    d_h = np.hypot(e[:, 0], e[:, 1])
    e_l = e * 0.3
    d_l = np.hypot(e_l[:, 0], e_l[:, 1])
    out = dict(sigma=sg, r=r,
               honest_hit=int((d_h <= r).sum()), leak_hit=int((d_l <= r).sum()), n=n,
               honest_med=float(np.median(d_h)), leak_med=float(np.median(d_l)),
               leak_wilson=wilson(int((d_l <= r).sum()), n), honest_wilson=wilson(int((d_h <= r).sum()), n))
    return out


def b4_strata(seed=404):
    """T3(거리 서술형)를 문형별로: 거리형 24, 일정형 8, 이웃형 8. 일정형은 하루 길이의 불확실성이 더해져 오차가 1.8배."""
    rng = np.random.default_rng(seed)
    sg = FORM[2]["sigma"]; r = FORM[2]["r"]
    strata = [("거리형", 24, 1.0), ("일정형", 8, 1.8), ("이웃형", 8, 1.0)]
    out = []
    tot_k = 0; tot_n = 0
    for nm, n, m in strata:
        e = rng.normal(0, sg * m, size=(n, 2))
        d = np.hypot(e[:, 0], e[:, 1])
        k = int((d <= r).sum())
        lo, hi = wilson(k, n)
        out.append(dict(name=nm, n=n, k=k, rate=k / n, lo=lo, hi=hi, mult=m, theory=theory_cover(sg * m, r)))
        tot_k += k; tot_n += n
    lo, hi = wilson(tot_k, tot_n)
    out.append(dict(name="전체", n=tot_n, k=tot_k, rate=tot_k / tot_n, lo=lo, hi=hi, mult=None, theory=None))
    return out


def b5_terrain(seed=505):
    """T4 최소비용: 지형이 평지면 오차 1.0배, 해안 1.3배, 산지 1.6배. 표본을 어떻게 고르느냐에 따른 판정."""
    rng = np.random.default_rng(seed)
    sg = FORM[3]["sigma"]; r = FORM[3]["r"]
    terr = [("평지", 1.0), ("해안", 1.3), ("산지", 1.6)]
    pools = {}
    for nm, m in terr:
        e = rng.normal(0, sg * m, size=(400, 2))
        pools[nm] = np.hypot(e[:, 0], e[:, 1]) <= r
    def pick(plan):
        k = 0; n = 0
        for nm, cnt in plan.items():
            k += int(pools[nm][:cnt].sum()); n += cnt
        lo, hi = wilson(k, n)
        return dict(k=k, n=n, rate=k / n, lo=lo, hi=hi)
    plans = {"평지만 40": {"평지": 40}, "평지 20, 해안 10, 산지 10": {"평지": 20, "해안": 10, "산지": 10},
             "평지 14, 해안 13, 산지 13": {"평지": 14, "해안": 13, "산지": 13}}
    res = {k: pick(v) for k, v in plans.items()}
    theory = {nm: theory_cover(sg * m, r) for nm, m in terr}
    # 큰 표본(각 지형 400)으로 본 실제 적중률
    big = {nm: float(pools[nm].mean()) for nm, _ in terr}
    return dict(plans=res, theory=theory, big=big)


def b6_info():
    """12장 가상 세계 8기법의 영역이 400 km 정사각형(160,000 km2)에서 차지하는 비율과 정보량(비트)"""
    tot = 400.0 * 400.0
    out = []
    for f in FORM:
        out.append(dict(name=f["name"], area=f["area"], frac=f["area"] / tot, bits=math.log2(tot / f["area"])))
    return out


def b7_reading():
    """12장 가상 세계 표: 중심 사이 거리와 면적을 같게 하는 원의 반지름. 원이 겹치는가"""
    n = len(FORM)
    D = np.zeros((n, n)); ov = np.zeros((n, n), dtype=bool)
    for i in range(n):
        for j in range(n):
            D[i, j] = math.hypot(FORM[i]["x"] - FORM[j]["x"], FORM[i]["y"] - FORM[j]["y"])
            ov[i, j] = D[i, j] <= FORM[i]["r"] + FORM[j]["r"]
    # 한 영역이 다른 영역의 중심을 담는가
    contain = [[D[i, j] <= FORM[i]["r"] for j in range(n)] for i in range(n)]
    return dict(D=D.tolist(), ov=ov.tolist(), r=[f["r"] for f in FORM], contain=contain,
                maxd=float(D.max()), pairs_total=n * (n - 1) // 2,
                pairs_overlap=int(sum(ov[i, j] for i in range(n) for j in range(i + 1, n))))


def b7b_shift(shift=60.0):
    """T5의 중심만 동쪽으로 shift km 옮긴 가상 변형: 같은 표에서 읽기가 어떻게 달라지는가"""
    F = FORM
    n = 8
    xs = [f["x"] for f in F]; ys = [f["y"] for f in F]
    xs[4] += shift
    res = {}
    for j in range(n):
        if j == 4:
            continue
        d = math.hypot(xs[4] - xs[j], ys[4] - ys[j])
        res[F[j]["name"][:2]] = dict(d=d, rsum=F[4]["r"] + F[j]["r"], overlap=d <= F[4]["r"] + F[j]["r"])
    # 원래 표: 참값에서 중심까지의 거리 / 반경
    ratio = [dict(name=f["name"], dist=f["dist"], r=f["r"], ratio=f["dist"] / f["r"]) for f in F]
    return dict(shift=shift, pairs=res, ratio=ratio, x5=xs[4], y5=ys[4])


def b8_recal(n_cal=40, n_test=40, reps=2000, seed=808):
    """T8(독립이라고 믿고 합친 영역)이 눈 가린 검증에서 모자랄 때, 보정 배율을 정하고 새 지명으로 다시 시험한다."""
    rng = np.random.default_rng(seed)
    out_ks = []; out_cov = []; out_cov_raw = []
    # 이론: 실제 오차 sd 대 주장 반경
    for _ in range(reps):
        err, cr = method_errors(n_cal + n_test, int(rng.integers(1, 10 ** 9)), claim_mult={4: 0.8})
        d = np.hypot(err[7][:, 0], err[7][:, 1]) / cr[7]
        cal = d[:n_cal]; tst = d[n_cal:]
        k = float(np.quantile(cal, 0.95))
        k = max(k, 1.0) if False else k
        out_ks.append(k)
        out_cov.append(float((tst <= k).mean()))
        out_cov_raw.append(float((tst <= 1.0).mean()))
    return dict(k_mean=float(np.mean(out_ks)), k_sd=float(np.std(out_ks)), k_min=float(np.min(out_ks)), k_max=float(np.max(out_ks)),
                cov_mean=float(np.mean(out_cov)), cov_sd=float(np.std(out_cov)),
                raw_mean=float(np.mean(out_cov_raw)), area_mult=float(np.mean(np.array(out_ks) ** 2)),
                frac_below90=float(np.mean(np.array(out_cov) < 0.90)))


def b9_unblinded(n=40, reps=500, seed=909, m=6):
    """분석자가 참 위치를 알고 6개 설정 중 가장 가까운 것을 고르면(눈 가림이 깨지면) 적중률과 오차가 얼마나 부풀까"""
    rng = np.random.default_rng(seed)
    sig = FORM[2]["sigma"]; r = FORM[2]["r"]
    blind_hit = []; open_hit = []; blind_med = []; open_med = []
    for _ in range(reps):
        a = rng.normal(0, sig / math.sqrt(2), size=(n, 1, 2))
        b = rng.normal(0, sig / math.sqrt(2), size=(n, m, 2))
        e = a + b                                     # 각 설정의 오차, 설정 사이 상관 0.5
        d = np.hypot(e[..., 0], e[..., 1])            # n x m
        d0 = d[:, 0]
        dmin = d.min(axis=1)
        blind_hit.append((d0 <= r).mean()); open_hit.append((dmin <= r).mean())
        blind_med.append(np.median(d0)); open_med.append(np.median(dmin))
    return dict(blind_hit=float(np.mean(blind_hit)), open_hit=float(np.mean(open_hit)),
                blind_med=float(np.mean(blind_med)), open_med=float(np.mean(open_med)), r=r, sigma=sig, m=m,
                coverage_theory=theory_cover(sig, r))


def b1_forking(reps=20000, seed=101, m=6, off=12.0):
    """기대 위치 E가 참 위치에서 off km 떨어져 있다. 6개 설정의 95% 영역(반지름 r) 중 하나라도 E를 담을 확률 등"""
    rng = np.random.default_rng(seed)
    sig = FORM[2]["sigma"]; r = FORM[2]["r"]
    E = np.array([off, 0.0])
    a = rng.normal(0, sig / math.sqrt(2), size=(reps, 1, 2))
    b = rng.normal(0, sig / math.sqrt(2), size=(reps, m, 2))
    c = a + b                                          # 중심의 참 위치에서의 오차
    dE = np.hypot(c[..., 0] - E[0], c[..., 1] - E[1])
    dT = np.hypot(c[..., 0], c[..., 1])
    inE = dE <= r; inT = dT <= r
    one_inE = inE[:, 0].mean()
    any_inE = inE.any(axis=1).mean()
    pre_miss_E_any_hit = ((~inE[:, 0]) & inE[:, 1:].any(axis=1)).mean()
    cond = pre_miss_E_any_hit / (1 - one_inE)
    # 한 세계의 예: 사전 등록 설정은 E를 담지 못하고 다른 설정 중 일부가 E를 담는 첫 번째 시드
    ex = None
    for s in range(1, 400):
        rr = np.random.default_rng(s)
        aa = rr.normal(0, sig / math.sqrt(2), size=(1, 2)); bb = rr.normal(0, sig / math.sqrt(2), size=(m, 2))
        cc = aa + bb
        tE = np.hypot(cc[:, 0] - E[0], cc[:, 1] - E[1]) <= r
        tT = np.hypot(cc[:, 0], cc[:, 1]) <= r
        if (not tE[0]) and tT[0] and tE[1:].sum() >= 2:
            ex = dict(seed=s, centers=cc.tolist(), inE=tE.tolist(), inT=tT.tolist(),
                      dT=np.hypot(cc[:, 0], cc[:, 1]).tolist(), dE=np.hypot(cc[:, 0] - E[0], cc[:, 1] - E[1]).tolist())
            break
    return dict(one_inE=float(one_inE), any_inE=float(any_inE), cond=float(cond), r=r, sigma=sig, off=off, m=m,
                one_inT=float(inT[:, 0].mean()), any_inT=float(inT.any(axis=1).mean()), example=ex)


def b10_power():
    ns = [10, 20, 30, 50, 100]
    ps = [0.95, 0.90, 0.85, 0.80, 0.70]
    tab = {n: {p: p_pass(n, p, 0.90) for p in ps} for n in ns}
    # 합격 규칙 2: 윌슨 하한이 0.80 이상
    def pass_wilson(n, p, low=0.80):
        pm = binom_pmf(n, p)
        return sum(pm[k] for k in range(n + 1) if wilson(k, n)[0] >= low)
    tab2 = {n: {p: pass_wilson(n, p) for p in ps} for n in ns}
    # 적중률 0.95를 관측했을 때 윌슨 하한이 0.85 이상이 되는 최소 n
    nmin = None
    for n in range(10, 400):
        k = round(0.95 * n)
        if wilson(k, n)[0] >= 0.85:
            nmin = (n, k); break
    # 구간 폭이 0.2 이하가 되는 최소 n(관측 0.9)
    wmin = None
    for n in range(10, 400):
        k = round(0.9 * n)
        lo, hi = wilson(k, n)
        if hi - lo <= 0.20:
            wmin = (n, k, lo, hi); break
    return dict(ns=ns, ps=ps, rule1=tab, rule2=tab2, nmin=nmin, wmin=wmin)


def b11_denominator(seed=1111):
    """분모가 다른 비교: 기법 A는 40곳 모두 계산, 기법 B는 단서가 쉬운 25곳만 계산. 어려운 15곳에서는 A의 오차가 1.7배."""
    rng = np.random.default_rng(seed)
    sg = FORM[2]["sigma"]; r = FORM[2]["r"]
    easy, hard = 25, 15
    eA = np.concatenate([rng.normal(0, sg, size=(easy, 2)), rng.normal(0, sg * 1.7, size=(hard, 2))])
    dA = np.hypot(eA[:, 0], eA[:, 1])
    eB = rng.normal(0, sg * 1.15, size=(easy, 2))     # B는 쉬운 곳에서 A보다 조금 덜 정확
    dB = np.hypot(eB[:, 0], eB[:, 1])
    kA40 = int((dA <= r).sum()); kA25 = int((dA[:easy] <= r).sum()); kB25 = int((dB <= r).sum())
    return dict(kA40=kA40, nA40=40, kA25=kA25, kB25=kB25, nB=25,
                wA40=wilson(kA40, 40), wA25=wilson(kA25, 25), wB25=wilson(kB25, 25), r=r, sigma=sg)


def extra_numbers():
    """사례 B12~B16, 이론 1~4, 수식과 연습 문제에 쓴 값. 모두 닫힌 식으로 계산한다."""
    from math import comb, sqrt, log, log2, exp, pi, ceil

    def wl(k, n, z=1.96):
        p = k / n
        c = (p + z * z / (2 * n)) / (1 + z * z / n)
        h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        return c - h, c + h

    def pm(n, k, p):
        return comb(n, k) * p ** k * (1 - p) ** (n - k)

    def pass1(n, p):
        t = ceil(0.9 * n - 1e-9)
        return sum(pm(n, k, p) for k in range(t, n + 1))

    def pass2(n, p):
        return sum(pm(n, k, p) for k in range(n + 1) if wl(k, n)[0] >= 0.8)

    o = {}
    o["b12"] = {"stable": wl(27, 28), "renamed": wl(8, 12), "total": wl(35, 40)}
    r1 = 2.4477 * 5.0
    o["b13"] = {k: {"indep_cov": 1 - exp(-2.9957 / k), "shared_cov": 1 - exp(-2.9957 / k ** 2),
                    "r_indep": r1 * sqrt(k), "r_shared": r1 * k,
                    "bits_indep": log2(160000 / (pi * (r1 * sqrt(k)) ** 2)),
                    "bits_shared": log2(160000 / (pi * (r1 * k) ** 2))} for k in range(1, 5)}
    o["b14"] = {a: (a / 360 * pi * 50 ** 2, log2(160000 / (a / 360 * pi * 50 ** 2))) for a in (45, 90, 180)}
    th = pi / 4
    o["b15"] = {"R1": th / 2 * (14.4 ** 2 - 10.8 ** 2), "R2": th / 2 * (6.24 ** 2 - 4.68 ** 2)}
    q50, q20 = pass1(50, 0.8), pass1(20, 0.8)
    o["b16"] = {"q50": q50, "q20": q20,
                "t50": {t: 1 - (1 - q50) ** t for t in (1, 3, 5, 10, 20)},
                "t20": {t: 1 - (1 - q20) ** t for t in (1, 3, 5, 10, 20)},
                "need_half50": ceil(log(0.5) / log(1 - q50)), "need_90_50": ceil(log(0.1) / log(1 - q50)),
                "q_for_t": {t: 1 - 0.95 ** (1 / t) for t in (3, 5, 10)}}
    o["rule2"] = {n: (pass2(n, 0.95), pass2(n, 0.8)) for n in range(40, 70)}
    o["brier_prop"] = {f: 0.95 * (1 - f) ** 2 + 0.05 * f ** 2 for f in (0.8, 0.9, 0.95, 0.99, 1.0)}
    o["pairs"] = {"any_false": 1 - 0.95 ** 28, "per_pair": 0.05 / 28, "any_false_adj": 1 - (1 - 0.05 / 28) ** 28}
    o["design_effect"] = {rho: 50 / (1 + 3 * rho) for rho in (0, 0.2, 0.5, 1.0)}
    o["ex"] = {"wilson_18_20": wl(18, 20), "wilson_36_40": wl(36, 40), "wilson_45_50": wl(45, 50),
               "wilson_20_25": wl(20, 25), "wilson_22_25": wl(22, 25),
               "pass_n10_p9": pass1(10, 0.9), "pass_n20_p9": pass1(20, 0.9),
               "pass_n30_p95": pass1(30, 0.95), "pass_n30_p8": pass1(30, 0.8),
               "brier_30_of_40": (30 * 0.0025 + 10 * 0.9025) / 40,
               "honest_le30_of40": sum(pm(40, k, 0.95) for k in range(31)),
               "c90": sqrt(2 * log(10)) / 2.4477}
    return o


def toy_numbers():
    out = {}
    out["wilson_table"] = [(n, k, k / n, *wilson(k, n)) for n, k in [(5, 4), (10, 9), (20, 18), (50, 45), (100, 90), (30, 27), (40, 38), (40, 40), (25, 25), (60, 54)]]
    out["fork_q"] = {m: 1 - (1 - 0.3) ** m for m in (1, 2, 3, 6, 10)}
    out["b1"] = b1_forking()
    out["b2"] = b2_blind_validation()
    out["b3"] = b3_leak()
    out["b4"] = b4_strata()
    out["b5"] = b5_terrain()
    out["b6"] = b6_info()
    out["b7"] = b7_reading()
    out["b7b"] = b7b_shift()
    out["b8"] = b8_recal()
    out["b9"] = b9_unblinded()
    out["b10"] = b10_power()
    out["b11"] = b11_denominator()
    out["extra"] = extra_numbers()
    return out


# ======================================================================= 그림 공통
def box(ax, x, y, w, h, text, mode, fc=None, ls="-", fs=FS, bold=False, hatch=None):
    s = STY[mode]
    fc = fc or ("#ffffff" if mode == "bw" else "#fdf3e1")
    p = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=fc, ec=s["line"],
                       lw=0.9, ls=ls, hatch=hatch, zorder=3)
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, zorder=4, fontweight="bold" if bold else "normal",
            bbox=dict(fc="white", ec="none", pad=1.5) if hatch else None, linespacing=1.1)


def arrow(ax, x1, y1, x2, y2, mode, ls="-", lw=1.1):
    s = STY[mode]
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=s["line"], lw=lw, ls=ls,
                                                                 shrinkA=0, shrinkB=0), zorder=2)


def fig_timeline(mode):
    """연대기 종합 그림: 가로 시간축 1780~2030, 세 줄(눈 가림과 대조 실험 / 가설 비교·사전 등록·재현성 / 비교 대회와 점수)"""
    s = STY[mode]
    cA = "#1f6fb8" if mode == "color" else "#000000"
    cB = "#c0392b" if mode == "color" else "#555555"
    cC = "#2e7d32" if mode == "color" else "#888888"
    fig, ax = plt.subplots(figsize=(WIDTH, 5.9))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.995, bottom=0.01)
    ax.set_xlim(1755, 2055); ax.set_ylim(-9.6, 7.6); ax.axis("off")
    ys = {"A": 5.4, "B": 0.4, "C": -4.6}
    cols = {"A": cA, "B": cB, "C": cC}
    mk = {"A": "o", "B": "s", "C": "D"}
    lab = {"A": "눈 가림과 대조 실험", "B": "가설 비교, 사전 등록, 재현성", "C": "비교 대회와 점수"}
    ls = {"A": "-", "B": "--", "C": "-."}
    for yr in range(1800, 2021, 50):
        ax.plot([yr, yr], [-8.2, 7.0], color=s["grid"], lw=0.5, ls=":", zorder=0)
        ax.text(yr, -8.5, str(yr), ha="center", va="center", fontsize=FS, color=s["gray"], bbox=dict(fc="white", ec="none", pad=0.8))
    for k, y in ys.items():
        ax.plot([1775, 2040], [y, y], color=cols[k], lw=2.0, ls=ls[k], zorder=2)
        ax.text(1757, y + 0.45, lab[k], fontsize=FS, fontweight="bold", color=cols[k], ha="left", va="bottom",
                bbox=dict(fc="white", ec="none", pad=1.0), zorder=5)
    # (줄, 해, 글자 가운데 x, 높이 단계(+위 -아래), 글자)
    items = [
        ("A", 1784, 1822, 1, "프랭클린 위원회\n1784"), ("A", 1907, 1880, 1, "리버스·웨버\n1907"), ("A", 1935, 1936, 1, "피셔 책\n1935"),
        ("A", 1948, 1985, -1, "스트렙토마이신\n시험 1948"), ("A", 1963, 2008, 1, "로젠탈·포드\n1963"),
        ("B", 1890, 1890, -1, "챔벌린\n1890"), ("B", 1979, 1938, -1, "로젠탈 파일\n서랍 1979"), ("B", 2005, 1992, 1, "ICMJE 등록\n2005"),
        ("B", 2005.5, 1993, -1, "이오아니디스\n2005"), ("B", 2011, 2033, 1, "시먼스 외\n2011"), ("B", 2015, 2032, -1, "재현성 계획\n2015"),
        ("C", 1927, 1918, -1, "윌슨 구간\n1927"), ("C", 1950, 1958, -1, "브라이어\n1950"), ("C", 1982, 1972, 1, "M 대회\n1982"),
        ("C", 1994, 2000, -1, "CASP\n1994"), ("C", 2018, 2030, -1, "M4\n2018"),
    ]
    for k, yr, tx, lv, t in items:
        y = ys[k]
        sign = 1 if lv > 0 else -1
        ty = y + sign * (0.9 + (abs(lv) - 1) * 1.7)
        ax.plot([yr, tx], [y, ty], color=cols[k], lw=0.7, zorder=2)
        ax.plot(yr, y, mk[k], ms=5, color=cols[k] if mode == "color" else "white", mec=cols[k], mew=1.0, zorder=4)
        ax.text(tx, ty, t, ha="center", va="bottom" if sign > 0 else "top", fontsize=FS, linespacing=1.05,
                bbox=dict(fc="white", ec="none", pad=0.6), zorder=5)
    ax.text(2052, -7.4, "이 책의 비교표는 세 줄이 만나는 곳", ha="right", va="center", fontsize=FS)
    return save(fig, "ch13", "fig13-a-timeline", mode)


def fig_flow(mode):
    """사전 등록 - 눈 가린 검증 - 판정 - 서경 계산 - 비교표 - 충돌 분석의 순서와 되돌아가는 길"""
    s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 3.9))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    ax.set_xlim(0, 10); ax.set_ylim(0, 8.2); ax.axis("off")
    xs = [1.7, 5.0, 8.3]
    w, h = 3.0, 1.35
    top, bot = 6.0, 2.9
    box(ax, xs[0], top, w, h, "1 사전 등록\n증거, 격자, 기준", mode)
    box(ax, xs[1], top, w, h, "2 눈 가린 검증\n좌표 가린 지명", mode)
    box(ax, xs[2], top, w, h, "3 판정 규칙\n적중률, 윌슨 구간", mode)
    box(ax, xs[2], bot, w, h, "4 서경 계산\n등록한 입력 그대로", mode)
    box(ax, xs[1], bot, w, h, "5 비교표\n미산출, 적중률 괄호", mode)
    box(ax, xs[0], bot, w, h, "6 충돌 분석\n14장, 15장", mode)
    arrow(ax, xs[0] + w / 2, top, xs[1] - w / 2, top, mode)
    arrow(ax, xs[1] + w / 2, top, xs[2] - w / 2, top, mode)
    arrow(ax, xs[2], top - h / 2, xs[2], bot + h / 2, mode)
    arrow(ax, xs[2] - w / 2, bot, xs[1] + w / 2, bot, mode)
    arrow(ax, xs[1] - w / 2, bot, xs[0] + w / 2, bot, mode)
    ax.annotate("", xy=(xs[0], top + h / 2), xytext=(xs[2], top + h / 2),
                arrowprops=dict(arrowstyle="-|>", color=s["line"], lw=1.0, ls="--", connectionstyle="arc3,rad=0.22", shrinkA=0, shrinkB=0), zorder=1)
    ax.text(5.0, 7.75, "불합격: 입력과 모형을 고치고 새 기록을 만든다(옛 기록은 남긴다)", ha="center", va="center", fontsize=FS)
    ax.text(5.0, 1.15, "서경 계산(4)은 판정(3) 뒤에 한다. 순서를 바꾸면 결과를 보고 기준을 고치게 된다.", ha="center", va="center", fontsize=FS)
    ax.text(5.0, 0.35, "실선은 정해진 순서, 점선은 되돌아가는 길이다.", ha="center", va="center", fontsize=FS)
    return save(fig, "ch13", "fig13-b-flow", mode)


def fig_wilson(mode, B2):
    """가상 눈 가린 검증(40곳)의 8기법 적중률과 95% 윌슨 구간"""
    s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 3.9))
    fig.subplots_adjust(left=0.30, right=0.96, top=0.93, bottom=0.14)
    lab = ["T1 제약·구간", "T2 기하 보간", "T3 베이즈", "T4 최소비용", "T5 그래프", "T6 지명 정합", "T7 언어학", "T8 교차검증"]
    for i, r in enumerate(B2):
        y = len(B2) - 1 - i
        col = s["gray"] if mode == "bw" else ("#c0392b" if r["lo"] > 0.0 and r["hi"] < 0.95 else "#1f6fb8")
        ax.plot([r["lo"], r["hi"]], [y, y], color=col, lw=2.0, solid_capstyle="butt")
        ax.plot(r["rate"], y, "o" if r["hi"] >= 0.95 else "s", ms=5.5, color=col if mode == "color" else ("black" if r["hi"] >= 0.95 else "white"), mec="black", mew=0.8)
        ax.text(1.005, y, f"{r['hit']}/{r['n']}", va="center", ha="left", fontsize=FS)
    ax.axvline(0.95, color=s["line"], lw=1.0, ls="--")
    ax.text(0.95, len(B2) - 0.35, "명목 0.95", ha="center", va="bottom", fontsize=FS, bbox=dict(fc="white", ec="none", pad=0.5))
    ax.set_yticks(range(len(B2))); ax.set_yticklabels(lab[::-1], fontsize=FS)
    ax.set_xlim(0.45, 1.09); ax.set_ylim(-0.7, len(B2) + 0.15)
    ax.set_xticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_xlabel("95% 영역이 참 위치를 담은 비율(막대는 윌슨 95% 구간)")
    ax.grid(axis="x", color=s["grid"], lw=0.3, ls=":")
    return save(fig, "ch13", "fig13-c-wilson", mode)


def fig_forking(mode, B1):
    """가능한 설정의 수 m과 '기대와 맞는 설정이 하나라도 있을' 확률: 1-(1-q)^m"""
    s = STY[mode]
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 3.0), constrained_layout=True, gridspec_kw=dict(width_ratios=[1.0, 1.0]))
    ax = axs[0]
    ms = np.arange(1, 11)
    for q, ls, mk in ((0.1, ":", "^"), (0.3, "-", "o"), (0.5, "--", "s")):
        ax.plot(ms, 1 - (1 - q) ** ms, ls=ls, marker=mk, ms=4, color="#1f6fb8" if mode == "color" else "black", label=f"q={q}")
    ax.set_xlabel("고를 수 있는 설정의 수 m"); ax.set_ylabel("하나라도 맞는 확률")
    ax.set_xticks([1, 2, 4, 6, 8, 10]); ax.set_ylim(0, 1.02); ax.legend(loc="lower right", fontsize=FS)
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    ax.set_title("(가) 산식 1-(1-q)^m", fontsize=FS, loc="left")
    ax = axs[1]
    labs = ["사전 등록\n설정 1개", "6개 중\n하나라도"]
    vals = [B1["one_inE"], B1["any_inE"]]
    ax.bar([0], vals[:1], color=("#f0b45a" if mode == "color" else "#d0d0d0"), ec=s["line"], lw=0.8, width=0.55)
    ax.bar([1], vals[1:], color=("#f0b45a" if mode == "color" else "#d0d0d0"), ec=s["line"], lw=0.8, hatch="//", width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.02, f"{v:.2f}", ha="center", va="bottom", fontsize=FS)
    ax.set_xticks([0, 1]); ax.set_xticklabels(labs, fontsize=FS); ax.set_ylim(0, 1.0)
    ax.set_ylabel("영역이 기대 위치 E를 담을 확률")
    ax.set_title("(나) 가상 세계 모의(2만 번)", fontsize=FS, loc="left")
    ax.grid(axis="y", color=s["grid"], lw=0.3, ls=":")
    return save(fig, "ch13", "fig13-d-forking", mode)


def fig_reading(mode):
    """12장 가상 세계 8기법 표를 지도에 얹기: 중심(점)과 면적이 같은 원. 읽는 법 연습. 서경의 결과가 아니다."""
    s = STY[mode]
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 3.5), constrained_layout=True, gridspec_kw=dict(width_ratios=[1.35, 1.0]))
    colors = ["#1f6fb8", "#2e7d32", "#c0392b", "#8e44ad", "#d68910", "#117a65", "#566573", "#000000"]
    ls_cycle = ["-", "--", "-.", ":", "-", "--", "-.", ":"]
    ang = {0: 75, 1: 140, 2: 205, 4: 20, 5: 255, 7: 320}
    for ax, (xl, yl, ttl, sel) in zip(axs, [((178, 304), (130, 238), "(가) 확대: 영역이 작은 기법", [0, 1, 2, 4, 5, 7]),
                                           ((0, 400), (0, 400), "(나) 400 km 정사각형 전체", list(range(8)))]):
        ax.set_xlim(*xl); ax.set_ylim(*yl); ax.set_aspect("equal")
        ax.set_title(ttl, fontsize=FS, loc="left")
        ax.grid(color=s["grid"], lw=0.3, ls=":")
        for i in sel:
            f = FORM[i]
            col = colors[i] if mode == "color" else "black"
            lw = 1.8 if i == 7 else 1.0
            ax.add_patch(Circle((f["x"], f["y"]), f["r"], fill=False, ec=col, lw=lw, ls=ls_cycle[i], zorder=3))
            ax.plot(f["x"], f["y"], marker="o" if i < 4 else "s", ms=3.0, color=col, zorder=4)
            if ax is axs[0]:
                a = math.radians(ang[i]); rr = f["r"] + 1.0
                ax.text(f["x"] + rr * math.cos(a), f["y"] + rr * math.sin(a), f"T{i + 1}", fontsize=FS, ha="center", va="center",
                        color=col if mode == "color" else "black", bbox=dict(fc="white", ec="none", pad=0.4), zorder=6)
        if ax is axs[1]:
            for i in (3, 6):
                f = FORM[i]
                ang2 = {3: 60, 6: 300}[i]; a = math.radians(ang2)
                ax.text(f["x"] + (f["r"] + 14) * math.cos(a), f["y"] + (f["r"] + 14) * math.sin(a), f"T{i + 1}", fontsize=FS, ha="center", va="center",
                        bbox=dict(fc="white", ec="none", pad=0.4), zorder=6)
            ax.set_xticks(range(0, 401, 100)); ax.set_yticks(range(0, 401, 100))
            ax.add_patch(plt.Rectangle((178, 130), 126, 108, fill=False, ec=s["gray"], lw=0.8, ls=":"))
        ax.tick_params(labelsize=FS)
        ax.set_xlabel("동 (km)", fontsize=FS)
    axs[0].set_ylabel("북 (km)", fontsize=FS)
    return save(fig, "ch13", "fig13-e-reading", mode)


def fig_power(mode, P):
    """검증 지명 수 n에 따라 '적중률 0.90 이상이면 합격' 규칙이 정직한 도구와 어긋난 도구를 가려내는 정도(n은 10의 배수)"""
    s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 3.1))
    fig.subplots_adjust(left=0.12, right=0.97, top=0.95, bottom=0.17)
    ns = np.arange(10, 121, 10)
    for p, ls, mk in ((0.95, "-", "o"), (0.85, "--", "s"), (0.80, "-.", "^"), (0.70, ":", "D")):
        ys = [p_pass(int(n), p, 0.90) for n in ns]
        col = ("#1f6fb8" if p == 0.95 else "#c0392b") if mode == "color" else "black"
        ax.plot(ns, ys, ls=ls, marker=mk, ms=4, color=col, lw=1.4, label=f"참 적중률 {p:.2f}")
    ax.set_xlabel("검증 지명 수 n (규칙: 적중 k가 0.9n 이상이면 합격)"); ax.set_ylabel("합격할 확률")
    ax.set_xticks(range(10, 121, 10)); ax.set_ylim(0, 1.02); ax.grid(color=s["grid"], lw=0.3, ls=":")
    ax.legend(fontsize=FS, loc="center right", bbox_to_anchor=(1.0, 0.55))
    return save(fig, "ch13", "fig13-f-power", mode)


def fig_denominator(mode, D):
    """분모가 다른 비교: 기법 A는 40곳, 기법 B는 25곳. 같은 25곳으로 맞추어 비교"""
    s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 2.9))
    fig.subplots_adjust(left=0.30, right=0.95, top=0.93, bottom=0.18)
    rows = [("A, 40곳 전체", D["kA40"], 40, D["wA40"]), ("A, 쉬운 25곳", D["kA25"], 25, D["wA25"]), ("B, 쉬운 25곳", D["kB25"], 25, D["wB25"])]
    for i, (t, k, n, w) in enumerate(rows):
        y = 2 - i
        col = ["#1f6fb8", "#2e7d32", "#c0392b"][i] if mode == "color" else "black"
        ax.plot([w[0], w[1]], [y, y], color=col, lw=2.0, ls=["-", "--", "-."][i])
        ax.plot(k / n, y, ["o", "s", "D"][i], ms=5.5, color=col if mode == "color" else ["black", "white", "gray"][i], mec="black")
        ax.text(1.004, y, f"{k}/{n}", va="center", ha="left", fontsize=FS)
    ax.set_yticks([2, 1, 0]); ax.set_yticklabels([r[0] for r in rows], fontsize=FS)
    ax.set_xlim(0.5, 1.07); ax.set_ylim(-0.6, 2.6)
    ax.axvline(0.95, color=s["line"], lw=1.0, ls="--")
    ax.set_xlabel("적중률(막대는 윌슨 95% 구간)")
    ax.grid(axis="x", color=s["grid"], lw=0.3, ls=":")
    return save(fig, "ch13", "fig13-g-denominator", mode)


def figures(N):
    out = []
    for mode in ("color", "bw"):
        out.append(fig_timeline(mode))
        out.append(fig_flow(mode))
        out.append(fig_wilson(mode, N["b2"]))
        out.append(fig_forking(mode, N["b1"]))
        out.append(fig_reading(mode))
        out.append(fig_power(mode, N["b10"]))
        out.append(fig_denominator(mode, N["b11"]))
    return out


if __name__ == "__main__":
    N = toy_numbers()
    p = sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/-home-claude/b023554a-572d-59d4-839e-2e82c2b24103/scratchpad/ch13-numbers.json"
    json.dump(N, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    for pth in figures(N):
        print(pth)
