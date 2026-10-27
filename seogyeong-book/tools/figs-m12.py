"""figs-m12.py - 12장(기법 8, 다자료 교차검증) 새 그림과 새 사례 계산.
실행: python3 tools/figs-m12.py  (그림/ch12 에 컬러·흑백 PDF 생성)
이 파일의 계산 함수(격자, 풀링, 사례 1~8)는 원고의 새 사례 숫자의 근거이다. 모든 세계는 가상이며 서경의 결과가 아니다.
"""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
from figlib import *

FS = 8.5

# ======================================================================= 계산 틀
STEP = 0.5
XS = np.arange(0, 60 + 1e-9, STEP)
GX, GY = np.meshgrid(XS, XS)          # GY[i, j]=북, GX[i, j]=동
CELL = STEP * STEP                    # km^2
U_LO, U_HI, U_MID = 0.36, 0.48, 0.42  # km/리 (이 책의 연습용 가정)


def dist(c):
    return np.hypot(GX - c[0], GY - c[1])


def bearing(c):
    """c에서 각 칸을 본 방위각(북=0, 동=90, 시계 방향, 0~360)"""
    return (np.degrees(np.arctan2(GX - c[0], GY - c[1])) + 360) % 360


def ring(c, lo, hi):
    d = dist(c)
    return ((d >= lo) & (d <= hi)).astype(float)


def sector(c, brg, half):
    b = bearing(c)
    diff = np.abs((b - brg + 180) % 360 - 180)
    return (diff <= half).astype(float)


def soft_ring(c, mu, sd):
    return np.exp(-0.5 * ((dist(c) - mu) / sd) ** 2)


def norm(L):
    s = L.sum()
    return L / s if s > 0 else L


def area(mask):
    return float(mask.sum() * CELL)


def hpd_mask(p, level=0.95):
    flat = p.ravel()
    order = np.argsort(-flat)
    cs = np.cumsum(flat[order])
    k = int(np.searchsorted(cs, level * cs[-1]) + 1)
    m = np.zeros_like(flat, dtype=bool)
    m[order[:k]] = True
    return m.reshape(p.shape)


def hpd_area(p, level=0.95):
    return area(hpd_mask(p, level))


def centroid(p):
    s = p.sum()
    return (float((GX * p).sum() / s), float((GY * p).sum() / s))


def ovl(p, q):
    return float(np.minimum(norm(p), norm(q)).sum())


def bc(p, q):
    return float(np.sqrt(norm(p) * norm(q)).sum())


def hellinger(p, q):
    return float(math.sqrt(max(0.0, 1 - bc(p, q))))


def log_pool(ps, w=None):
    w = w or [1.0] * len(ps)
    out = np.ones_like(ps[0])
    for p, wk in zip(ps, w):
        out = out * np.power(norm(p), wk)
    return norm(out)


def lin_pool(ps, w=None):
    w = w or [1.0 / len(ps)] * len(ps)
    return norm(sum(wk * norm(p) for p, wk in zip(ps, w)))


def at(p, x, y):
    j = int(round(x / STEP)); i = int(round(y / STEP))
    return float(p[i, j])


def mass_near(p, c, r):
    return float(norm(p)[dist(c) <= r].sum())


def km2li(km, u=U_MID):
    return km / u


# ======================================================================= 사례 계산
def case_b1():
    """세 고을에서 잰 거리·방위가 일치할 때: 가상 세계, 참 위치 (30,30)"""
    T = (30.0, 30.0)
    refs = {"갑군": ((9.0, 30.0), 50, 90.0), "을진": ((33.0, 13.0), 40, 0.0), "병현": ((38.5, 38.5), 30, 225.0)}
    out = {"T": T}
    regs = {}
    for k, (c, li, brg) in refs.items():
        lo = li * 0.9 * U_LO; hi = li * 1.1 * U_HI
        reg = ring(c, lo, hi) * sector(c, brg, 22.5)
        regs[k] = reg
        d_true = math.hypot(T[0] - c[0], T[1] - c[1])
        out[k] = dict(lo=lo, hi=hi, area=area(reg > 0), d_true=d_true, li_true=d_true / U_MID,
                      brg_true=float((math.degrees(math.atan2(T[0] - c[0], T[1] - c[1])) + 360) % 360),
                      has_T=bool(at(reg, *T) > 0))
    ps = list(regs.values())
    prod = np.prod(ps, axis=0)
    out["prod_area"] = area(prod > 0)
    out["prod_has_T"] = bool(at(prod, *T) > 0)
    # 단위를 하나로 공유한 정확한 해: 칸마다 u 구간이 비지 않아야 함
    ulo = np.full(GX.shape, U_LO); uhi = np.full(GX.shape, U_HI)
    ok = np.ones(GX.shape, bool)
    for k, (c, li, brg) in refs.items():
        r = dist(c)
        ulo = np.maximum(ulo, r / (li * 1.1)); uhi = np.minimum(uhi, r / (li * 0.9))
        ok &= sector(c, brg, 22.5) > 0
    exact = ok & (ulo <= uhi)
    out["exact_area"] = area(exact)
    out["exact_has_T"] = bool(exact[int(T[1] / STEP), int(T[0] / STEP)])
    lin = lin_pool(ps)
    out["lin_area95"] = hpd_area(lin, 0.95)
    out["lin_max_share"] = float(lin.max() / lin.sum())
    # 겹친 개수 지도: 칸마다 몇 개 영역에 들어 있나
    cnt = sum((p > 0).astype(int) for p in ps)
    out["cnt_area"] = {n: area(cnt >= n) for n in (1, 2, 3)}
    out["prod_cent"] = centroid(prod)
    out["exact_cent"] = centroid(exact.astype(float))
    out["ulo_T"] = float(ulo[int(T[1] / STEP), int(T[0] / STEP)])
    out["uhi_T"] = float(uhi[int(T[1] / STEP), int(T[0] / STEP)])
    for k, (c, li, brg) in refs.items():
        r = math.hypot(T[0] - c[0], T[1] - c[1])
        out[k]["u_lo"] = r / (li * 1.1); out[k]["u_hi"] = r / (li * 0.9)
    out["regs"] = regs; out["prod"] = prod; out["exact"] = exact; out["refs"] = {k: v[0] for k, v in refs.items()}
    return out


def phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def case_b2(seed=7, n=200000):
    """옮겨 쓴 문헌: 가우스 1차원. 원본 X(σx), 필사본 Y·Z(X와 같은 숫자), 독립 W(σw)"""
    rng = np.random.default_rng(seed)
    sx, sw = 2.5, 3.0   # km
    out = dict(sx=sx, sw=sw)
    cov = {}
    for k in (1, 2, 3):
        cov[k] = 2 * phi(1.96 / math.sqrt(k)) - 1
    out["cov_copies"] = cov
    out["half_width_copies"] = {k: 1.96 * sx / math.sqrt(k) for k in (1, 2, 3)}
    # 원본 1 + 필사 2 + 독립 1: 가중 없음(4표) 대 가중(X·Y·Z 각 1/3, W 1)
    T = 0.0
    ex = rng.normal(0, sx, n); ew = rng.normal(0, sw, n)
    mu_x = T + ex; mu_w = T + ew
    res = {}
    for name, wx, ww in (("가중 없음", 3.0, 1.0), ("가중 있음", 1.0, 1.0)):
        prec = wx / sx ** 2 + ww / sw ** 2
        mu = (wx * mu_x / sx ** 2 + ww * mu_w / sw ** 2) / prec
        sd = math.sqrt(1 / prec)
        cover = float(np.mean(np.abs(mu - T) <= 1.96 * sd))
        res[name] = dict(sd=sd, half=1.96 * sd, cover=cover)
    out["mix"] = res
    # 원본이 틀렸을 때(원본 오차 +8 km): 중심이 어디로 끌리나
    for name, wx, ww in (("가중 없음", 3.0, 1.0), ("가중 있음", 1.0, 1.0)):
        prec = wx / sx ** 2 + ww / sw ** 2
        mu = (wx * 8.0 / sx ** 2 + ww * 0.0 / sw ** 2) / prec
        res[name]["bad_center"] = mu
    return out


def case_b3():
    """필사 한 글자가 틀린 경우. 세 줄 모두 거리+방위, 참 (30,30), 병현 줄이 '삼십 리'→'이십 리'"""
    T = (30.0, 30.0)
    lines = {"갑군": ((9.0, 30.0), 50, 90.0), "을진": ((33.0, 13.0), 40, 0.0), "병현": ((38.5, 38.5), 30, 225.0)}
    def post(c, li, brg):
        mu = li * U_MID; sd = 0.12 * mu
        return norm(soft_ring(c, mu, sd) * sector(c, brg, 22.5) + 1e-6 * sector(c, brg, 22.5))
    good = {k: post(*v) for k, v in lines.items()}
    bad = dict(good); bad["병현"] = post(lines["병현"][0], 20, 225.0)
    out = {"T": T}
    for tag, P in (("good", good), ("bad", bad)):
        ks = list(P)
        M = {(a, b): ovl(P[a], P[b]) for a in ks for b in ks}
        pool = log_pool([P[k] for k in ks])
        loo = {}
        for k in ks:
            rest = [P[j] for j in ks if j != k]
            loo[k] = dict(cent=centroid(log_pool(rest)), ovl_all=ovl(log_pool(rest), pool), area=hpd_area(log_pool(rest)))
        Mx = {f"{a}-{b}": M[(a, b)] for i, a in enumerate(ks) for b in ks[i + 1:]}
        out[tag] = dict(M=M, Mx=Mx, pool_cent=centroid(pool), pool_area=hpd_area(pool), loo=loo,
                        has_T=bool(hpd_mask(pool)[int(T[1] / STEP), int(T[0] / STEP)]),
                        cent={k: centroid(P[k]) for k in ks}, area={k: hpd_area(P[k]) for k in ks})
        out[tag]["shift"] = {k: math.hypot(loo[k]["cent"][0] - out[tag]["pool_cent"][0], loo[k]["cent"][1] - out[tag]["pool_cent"][1]) for k in ks}
        out[tag]["cent_vs_T"] = math.hypot(out[tag]["pool_cent"][0] - T[0], out[tag]["pool_cent"][1] - T[1])
        out[tag]["lin_cent"] = centroid(lin_pool([P[k] for k in ks]))
        out[tag]["lin_cent_vs_T"] = math.hypot(out[tag]["lin_cent"][0] - T[0], out[tag]["lin_cent"][1] - T[1])
        out[tag]["P"] = P; out[tag]["pool"] = pool
    out["lines"] = lines
    return out


def blob(c, sd):
    return norm(np.exp(-0.5 * (dist(c) / sd) ** 2))


def case_b4():
    """동명이지: 이름이 같은 두 후보 P1(18,40), P2(44,22). 갑군(9,30)에서 '동쪽 팔십 리'"""
    P1 = (18.0, 40.0); P2 = (44.0, 22.0); gap = (9.0, 30.0)
    A = norm(blob(P1, 2.5) + blob(P2, 2.5))
    # 갑군 줄: 거리 80리 ±10%, 단위 정규 근사, 동쪽 반폭 22.5도
    mu = 80 * U_MID; sd = 0.12 * mu
    B = norm((soft_ring(gap, mu, sd) + 1e-6) * sector(gap, 90.0, 22.5))
    out = dict(P1=P1, P2=P2, gap=gap)
    for nm, p in (("A", A), ("B", B), ("log", log_pool([A, B])), ("lin", lin_pool([A, B]))):
        out[nm] = dict(m1=mass_near(p, P1, 6), m2=mass_near(p, P2, 6), area95=hpd_area(p))
    d1 = math.hypot(P1[0] - gap[0], P1[1] - gap[1]); d2 = math.hypot(P2[0] - gap[0], P2[1] - gap[1])
    out["d1"] = d1; out["d2"] = d2
    out["li1"] = d1 / U_MID; out["li2"] = d2 / U_MID
    out["brg1"] = float((math.degrees(math.atan2(P1[0] - gap[0], P1[1] - gap[1])) + 360) % 360)
    out["brg2"] = float((math.degrees(math.atan2(P2[0] - gap[0], P2[1] - gap[1])) + 360) % 360)
    # B가 틀려서(참은 P1) 같은 줄이 P2를 가리킬 때: 이름 쪽 A의 신뢰가 반반이어도 결과는 P2 쪽 100%
    out["A_p"], out["B_p"], out["log_p"], out["lin_p"] = A, B, log_pool([A, B]), lin_pool([A, B])
    return out


def case_b5(N=500, seed=11):
    """공통 가정 오류: 참 단위가 가정(0.36~0.48)과 다를 때. 거리 줄 3개(단위 공유) 대 거리 3 + 방위 3.
    각 줄의 거리 어림 폭: 단위 가정 구간의 상대 표준편차 0.083(=0.035/0.42)과 5리 단위 반올림 오차(표준편차 5/sqrt(12)리)"""
    rng = np.random.default_rng(seed)
    refs = [(9.0, 30.0), (33.0, 13.0), (38.5, 38.5)]
    names8 = np.arange(0, 360, 45.0)
    res = {}
    for key in ("range", 0.36, 0.42, 0.48, 0.54, 0.60):
        cov_d = cov_db = 0; alarm = 0; area_d = []; area_db = []
        for s in range(N):
            u_true = rng.uniform(0.36, 0.48) if key == "range" else key
            tx, ty = rng.uniform(18, 42, 2)
            Ds = []; Bs = []
            for c in refs:
                r = math.hypot(tx - c[0], ty - c[1])
                li = max(round(r / u_true / 5) * 5, 5)
                mu = li * U_MID; sd = math.sqrt((0.083 * mu) ** 2 + (5 / math.sqrt(12) * U_MID) ** 2)
                Ds.append(norm(soft_ring(c, mu, sd)))
                brg = (math.degrees(math.atan2(tx - c[0], ty - c[1])) + 360) % 360
                b8 = names8[int(np.argmin(np.abs((names8 - brg + 180) % 360 - 180)))]
                Bs.append(norm(sector(c, b8, 22.5) + 0.01))
            pd = log_pool(Ds)
            pdb = log_pool(Ds + Bs)
            i, j = int(round(ty / STEP)), int(round(tx / STEP))
            hd = hpd_mask(pd); hdb = hpd_mask(pdb)
            cov_d += bool(hd[i, j]); cov_db += bool(hdb[i, j])
            area_d.append(area(hd)); area_db.append(area(hdb))
            pb = log_pool(Bs)
            alarm += int(ovl(pd, pb) < 0.05)
        res[key] = dict(cov_d=cov_d / N, cov_db=cov_db / N, alarm=alarm / N,
                        med_area_d=float(np.median(area_d)), med_area_db=float(np.median(area_db)))
    nm = {"range": "r", 0.36: "u36", 0.42: "u42", 0.48: "u48", 0.54: "u54", 0.60: "u60"}
    return dict(N=N, res=res, t={nm[k]: v for k, v in res.items()})


def case_b6():
    """종류가 다른 증거 세 줄을 하나씩 겹치기: 참 (36.5, 29.4)"""
    T = (36.5, 29.4)
    gap = (8.0, 30.0)
    river = np.array([(5, 8), (20, 18), (33, 27), (39, 31), (48, 40), (58, 52)], float)
    M = (37.0, 37.0)
    # L1 하루 길: 하루 20~35 km (이 책의 가정)
    L1 = ring(gap, 20, 35)
    # L2 강가: 강에서 1.5 km 이내
    dmin = np.full(GX.shape, 1e9)
    for a, b in zip(river[:-1], river[1:]):
        ab = b - a; t = ((GX - a[0]) * ab[0] + (GY - a[1]) * ab[1]) / (ab @ ab); t = np.clip(t, 0, 1)
        px = a[0] + t * ab[0]; py = a[1] + t * ab[1]
        dmin = np.minimum(dmin, np.hypot(GX - px, GY - py))
    L2 = (dmin <= 1.5).astype(float)
    # L3 산 남쪽 기슭: 정상에서 2~9 km, 남쪽 (180 도) 반폭 45
    L3 = ring(M, 2, 9) * sector(M, 180.0, 45.0)
    Ls = {"하루 길": L1, "강가": L2, "산 남쪽 기슭": L3}
    out = dict(T=T, river=river, M=M, gap=gap, win=area(np.ones(GX.shape) > 0))
    out["area"] = {k: area(v > 0) for k, v in Ls.items()}
    out["has_T"] = {k: bool(at(v, *T) > 0) for k, v in Ls.items()}
    import itertools
    def inter(ks):
        p = np.ones(GX.shape)
        for k in ks: p = p * Ls[k]
        return p
    names = list(Ls)
    out["pair"] = {" + ".join(ks): area(inter(ks) > 0) for ks in itertools.combinations(names, 2)}
    out["all"] = area(inter(names) > 0)
    out["loo"] = {k: area(inter([j for j in names if j != k]) > 0) for k in names}
    out["order"] = {}
    for perm in itertools.permutations(names):
        out["order"][" > ".join(perm)] = [area(inter(perm[:i + 1]) > 0) for i in range(3)]
    out["Ls"] = Ls; out["inter"] = inter(names)
    return out


def case_b7():
    """겨우 닿는 두 영역: K는 0이지만 겹침 비율은 아주 작다"""
    A = (dist((20, 30)) <= 6).astype(float)
    B = (dist((31.5, 30)) <= 6).astype(float)
    inter = A * B
    out = dict(areaA=area(A > 0), areaB=area(B > 0), inter=area(inter > 0), ovl=ovl(A, B),
               frac_small=area(inter > 0) / min(area(A > 0), area(B > 0)))
    r = 0.9
    out["K_touch"] = 0.0
    far = (dist((34.0, 30)) <= 6).astype(float)
    out["inter_far"] = area(A * far > 0)
    out["K_far"] = r * r
    out["post_touch"] = (0.9 * 0.9 + 0.9 * 0.1 + 0.1 * 0.9, 0.1 * 0.1)
    out["A"] = A; out["B"] = B; out["far"] = far
    return out


def case_b8():
    """반례: 서로 다른 대상 (E1 좌궁 우궁 연습값)과 증거 하나뿐일 때"""
    lo, hi = 10 * U_LO, 15 * U_HI
    out = dict(lo=lo, hi=hi)
    xs = np.arange(-12, 12.001, 0.1)
    east = ((xs >= lo) & (xs <= hi)).astype(float)
    west = ((xs <= -lo) & (xs >= -hi)).astype(float)
    out["ovl_ew"] = float(np.minimum(east / east.sum(), west / west.sum()).sum())
    out["inter_ew"] = float((east * west).sum() * 0.1)
    out["w_len"] = hi - lo
    return out


def binom_major(p, n):
    """n명(홀수)이 독립으로 각자 p의 확률로 옳을 때 다수결이 옳을 확률"""
    from math import comb
    k0 = n // 2 + 1
    return sum(comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(k0, n + 1))


def kl_bits(p, q):
    p = np.asarray(p, float); q = np.asarray(q, float)
    if np.any((q == 0) & (p > 0)):
        return float("inf")
    m = p > 0
    return float((p[m] * np.log2(p[m] / q[m])).sum())


def extras():
    """본문 개념·수식·사례 A의 작은 계산. 모두 손으로 따라 할 수 있는 숫자이다."""
    X = {}
    X["galton_pct"] = 11 / 1197 * 100
    X["galton_kg"] = 1197 * 0.45359237
    X["cj"] = {"p60": {n: binom_major(0.6, n) for n in (1, 3, 11, 101)}, "p40": {n: binom_major(0.4, n) for n in (1, 3, 11, 101)}}
    # 비유 2: 반 투표
    a = np.array([0.50, 0.20, 0.20, 0.10]); b = np.array([0.05, 0.40, 0.45, 0.10])
    pr = a * b
    X["vote"] = dict(sum=float(pr.sum()), prod=list(pr / pr.sum()), lin=list((a + b) / 2), prod_raw=list(pr))
    # 비유 3: 같은 글을 세 부 베낌
    sx = 2.5
    X["copy"] = dict(sd3=sx / math.sqrt(3), half3=1.96 * sx / math.sqrt(3), half1=1.96 * sx,
                     cov3=2 * phi(1.96 / math.sqrt(3)) - 1, cov1=2 * phi(1.96) - 1,
                     cov2=2 * phi(1.96 / math.sqrt(2)) - 1, cov4=2 * phi(1.96 / 2) - 1, cov6=2 * phi(1.96 / math.sqrt(6)) - 1)
    X["tri"] = dict(r10=1 / math.sin(math.radians(10)), r30=1 / math.sin(math.radians(30)))
    # 개념 1
    n = len(XS) ** 2
    X["grid"] = dict(n=n, area=n * CELL, c169=int(169 / CELL), p169=169 / CELL / n)
    # 개념 2
    p = np.array([0.30, 0.22, 0.15, 0.10, 0.07, 0.05, 0.04, 0.03, 0.025, 0.015])
    cs = np.cumsum(p)
    X["hpd"] = dict(c7=float(cs[6]), c8=float(cs[7]), sum=float(p.sum()))
    # 개념 3
    X["neff"] = dict(n=3 * (1 / 3) + 1 + 1)
    # 개념 4
    g = np.array([0.7, 0.2, 0.1]); h = np.array([0.5, 0.4, 0.1])
    pp = g * h
    X["prod3"] = dict(sum=float(pp.sum()), p=list(pp / pp.sum()))
    # 개념 6
    X["expo"] = dict(r2=8 ** 0.5, r3=8 ** (1 / 3))
    # 개념 7
    p4 = np.array([0.1, 0.6, 0.2, 0.1]); q4 = np.array([0.2, 0.5, 0.1, 0.2]); q0 = np.array([0.5, 0.0, 0.3, 0.2])
    bcv = float(np.sqrt(p4 * q4).sum())
    X["dist"] = dict(ovl=float(np.minimum(p4, q4).sum()), bc=bcv, h=math.sqrt(1 - bcv), kl_pq=kl_bits(p4, q4), kl_qp=kl_bits(q4, p4),
                     kl_p_q0=kl_bits(p4, q0), kl_q0p=kl_bits(q0, p4), ovl0=float(np.minimum(p4, q0).sum()))
    # 개념 8
    e = np.array([20.0, 21.0, 28.0]); m = e.mean()
    loo = [float(np.delete(e, i).mean()) for i in range(3)]
    X["loo"] = dict(mean=float(m), m1=loo[0], m2=loo[1], m3=loo[2], s1=abs(loo[0] - m), s2=abs(loo[1] - m), s3=abs(loo[2] - m))
    # 개념 9
    X["k"] = dict(r90=0.9 * 0.9, r70=0.7 * 0.7, r50=0.5 * 0.5)
    # 개념 10
    X["unit"] = dict(k36=50 * 0.36, k42=50 * 0.42, k48=50 * 0.48, k54=50 * 0.54, w=50 * 0.48 - 50 * 0.36, w2=50 * 0.54 - 50 * 0.36)
    # 개념 11
    se = math.sqrt(0.95 * 0.05 / 150)
    X["se"] = dict(se95=se, lo=0.95 - 1.96 * se, hi=0.95 + 1.96 * se)
    # 사례 A1: 증거표
    import csv
    rows = list(csv.DictReader(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "evidence-seogyeong-v1.csv"), encoding="utf-8-sig")))
    lay = {}
    for r in rows:
        k = r["layer"][:2]
        lay[k] = lay.get(k, 0) + 1
    via = {}
    for r in rows:
        k = "3" if "고구려통사 3" in r["quoted_via"] else ("5" if "고구려통사 5" in r["quoted_via"] else "직접")
        via[k] = via.get(k, 0) + 1
    w_a = [1, 1, 1, 1, 1]
    w_b = [1 / 2, 1 / 2, 1 / 3, 1 / 3, 1 / 3]
    w_c = [1, 1, 1, 1 / 2, 1 / 2]
    X["a1"] = dict(n=len(rows), lay=lay, via=via, s1=sum(w_a), s2=sum(w_b), s3=sum(w_c),
                   w1=1 / math.sqrt(sum(w_a)), w2=1 / math.sqrt(sum(w_b)), w3=1 / math.sqrt(sum(w_c)),
                   ratio=math.sqrt(sum(w_a)) / math.sqrt(sum(w_b)))
    # 사례 A2: 연도
    X["a2"] = dict(d1=586 - 343, d2=1081 - 586, d3=1081 - 343)
    # 사례 A3: 60갑자
    stems = "甲乙丙丁戊己庚辛壬癸"; branches = "子丑寅卯辰巳午未申酉戌亥"
    def gz(i):
        return stems[(i - 1) % 10] + branches[(i - 1) % 12]
    idx = {gz(i): i for i in range(1, 61)}
    X["a3"] = dict(gichuk=idx["己丑"], giyu=idx["己酉"], diff=idx["己酉"] - idx["己丑"], diff2=60 - (idx["己酉"] - idx["己丑"]),
                   d_lo=29 + 29 + 7, d_hi=30 + 30 + 7, chk=gz(26) + gz(46))
    # 사례 A4: 면적
    ar = {"북성": 25, "내성": 130, "중성": 300, "외성": 730}
    tot = sum(ar.values())
    A_km2 = tot / 100.0   # 만 m^2 -> km^2
    P = 23.0
    side_disc = (P / 2) ** 2 - 4 * A_km2
    X["a4"] = dict(tot=tot, km2=A_km2, pct={k: v / tot * 100 for k, v in ar.items()},
                   iso=4 * math.pi * A_km2 / P ** 2, circ=2 * math.sqrt(math.pi * A_km2),
                   rect_a=((P / 2) + math.sqrt(side_disc)) / 2, rect_b=((P / 2) - math.sqrt(side_disc)) / 2,
                   years=593 - 552, years_incl=593 - 552 + 1, ratio=P / (2 * math.sqrt(math.pi * A_km2)))
    # 사례 A5
    X["a5"] = dict(lo=10 * U_LO, hi=15 * U_HI, pairs=[(5.0, 5.2, True), (4.0, 7.0, True), (8.0, 5.0, False)])
    X["a5"]["K90"] = 0.9 * 0.9
    # 장 끝 수식 풀이 (그림 fig12-b-pool-bars와 같은 칸 네 개 예)
    p1 = np.array([0.1, 0.6, 0.2, 0.1]); p2 = np.array([0.2, 0.5, 0.1, 0.2]); p3 = np.array([0.5, 0.0, 0.3, 0.2])
    def pool(a, b, wa, wb):
        v = a ** wa * b ** wb
        return v, float(v.sum()), v / v.sum()
    e1 = {}
    for nm, (a, b, wa, wb) in dict(p11=(p1, p2, 1, 1), ph=(p1, p2, .5, .5), p13=(p1, p3, 1, 1)).items():
        v, z, post = pool(a, b, wa, wb)
        e1[nm] = dict(v=list(v), Z=z, post=list(post), root=list(a ** wa), root2=list(b ** wb))
    e1["avg12"] = list((p1 + p2) / 2); e1["avg13"] = list((p1 + p3) / 2)
    e1["p1"] = list(p1); e1["p2"] = list(p2); e1["p3"] = list(p3)
    e1["ent11"] = float(-(np.array(e1["p11"]["post"]) * np.log2(np.array(e1["p11"]["post"]))).sum())
    e1["enth"] = float(-(np.array(e1["ph"]["post"]) * np.log2(np.array(e1["ph"]["post"]))).sum())
    X["eq1"] = e1
    sig = 2.5
    X["eq2"] = dict(sig=sig, n_a=3.0, n_b=1.0, s_a=sig / math.sqrt(3.0), s_b=sig / math.sqrt(1.0), h_a=1.96 * sig / math.sqrt(3.0), h_b=1.96 * sig,
                    c_a=2 * phi(1.96 / math.sqrt(3.0)) - 1, c_b=2 * phi(1.96) - 1)
    bc12 = float(np.sqrt(p1 * p2).sum()); bc13 = float(np.sqrt(p1 * p3).sum())
    X["eq3"] = dict(ovl12=float(np.minimum(p1, p2).sum()), bc12=bc12, h12=math.sqrt(1 - bc12),
                    ovl13=float(np.minimum(p1, p3).sum()), bc13=bc13, h13=math.sqrt(1 - bc13),
                    sq12=list(np.sqrt(p1 * p2)), sq13=list(np.sqrt(p1 * p3)), mn12=list(np.minimum(p1, p2)), mn13=list(np.minimum(p1, p3)))
    X["eq4"] = dict(n=150, se95=math.sqrt(0.95 * 0.05 / 150), p_obs=136 / 150, se_obs=math.sqrt((136 / 150) * (1 - 136 / 150) / 150),
                    n_need=0.95 * 0.05 / 0.01 ** 2, se500=math.sqrt(0.5 * 0.5 / 500), n100=math.sqrt(0.9 * 0.1 / 100))
    # 연습 문제
    var_w = (1 + 1) / 4.0   # 두 줄기 평균
    var_u = (3 ** 2 + 2 ** 2) / 25.0
    X["q1"] = dict(n_eff_w=2.0, sd_unw=1 / math.sqrt(5.0), sd_w=1 / math.sqrt(2.0), cov_unw=2 * phi(1.96 * math.sqrt((1 / 5.0) / var_u)) - 1,
                   cov_w=2 * phi(1.96 * math.sqrt((1 / 2.0) / var_w)) - 1, var_u=var_u, var_w=var_w)
    u = np.array([0.4, 0.3, 0.2, 0.1, 0.0, 0.0]); v = np.array([0.1, 0.4, 0.3, 0.2, 0.0, 0.0]); w = np.array([0.0, 0.2, 0.3, 0.3, 0.2, 0.0])
    pu = u * v; pq = u * v * w
    X["q2"] = dict(prod_uv=list(pu / pu.sum()), sum_uv=float(pu.sum()), prod_uvw_sum=float(pq.sum()), lin_uv=list((u + v) / 2),
                   ovl_uv=float(np.minimum(u, v).sum()), ovl_uw=float(np.minimum(u, w).sum()), ovl_vw=float(np.minimum(v, w).sum()))
    X["eq4"]["lo_obs"] = X["eq4"]["p_obs"] - 1.96 * X["eq4"]["se_obs"]; X["eq4"]["hi_obs"] = X["eq4"]["p_obs"] + 1.96 * X["eq4"]["se_obs"]
    X["eq4"]["sq"] = 0.95 * 0.05
    X["q2"]["post_uvw"] = list((pq / pq.sum()))
    X["q1"]["hw_unw"] = 1.96 / math.sqrt(5.0); X["q1"]["hw_w"] = 1.96 / math.sqrt(2.0)
    X["q1"]["sd_true_u"] = math.sqrt(var_u); X["q1"]["z_unw"] = X["q1"]["hw_unw"] / X["q1"]["sd_true_u"]
    X["v1"] = dict(neff=0.5 + 0.5 + 1 + 1 + 1)
    X["q3"] = dict(k1=0.8 * 0.6, k2=0.9 * 0.9, k3=0.5 * 0.9)
    X["q4"] = dict(n_need=0.9 * 0.1 / 0.02 ** 2, se100=math.sqrt(0.9 * 0.1 / 100), se300=math.sqrt(0.9 * 0.1 / 300))
    X["q5"] = dict(gh=idx["己亥"], gy=idx["己酉"], d=idx["己酉"] - idx["己亥"], d2=60 - (idx["己酉"] - idx["己亥"]))
    return X



def extras2(b3, b6, b8):
    """사례 B3, B6, B8에서 본문에 쓴 보조 숫자"""
    Y = {}
    T = b3["T"]
    for tag in ("good", "bad"):
        P = b3[tag]["P"]; ks = list(P)
        masks = {k: hpd_mask(P[k], 0.95) for k in ks}
        Y[tag + "_inter"] = {f"{a}-{b}": area(masks[a] & masks[b]) for i, a in enumerate(ks) for b in ks[i + 1:]}
        Y[tag + "_loo_err"] = {k: math.hypot(b3[tag]["loo"][k]["cent"][0] - T[0], b3[tag]["loo"][k]["cent"][1] - T[1]) for k in ks}
    # B6: 하루 길을 '이틀 길'(40~70 km)로 잘못 썼을 때
    gap = b6["gap"]
    L1x = ring(gap, 40, 70)
    L2 = b6["Ls"]["강가"]; L3 = b6["Ls"]["산 남쪽 기슭"]
    Y["b6_wrong_all"] = area(L1x * L2 * L3 > 0)
    Y["b6_wrong_pair"] = area(L1x * L2 > 0)
    Y["b6_wrong_ring"] = area(L1x > 0)
    Y["b6_frac"] = {k: v / b6["win"] for k, v in b6["area"].items()}
    Y["b6_frac_all"] = b6["all"] / b6["win"]
    # B8: 방위 줄만 셋(삼각측량)과 거의 나란한 방위 줄 셋
    refs = {"갑군": ((9.0, 30.0), 90.0), "을진": ((33.0, 13.0), 0.0), "병현": ((38.5, 38.5), 225.0)}
    S = {k: sector(c, brg, 22.5) for k, (c, brg) in refs.items()}
    Y["b8_sec"] = {k: area(v > 0) for k, v in S.items()}
    ks = list(S)
    Y["b8_pair"] = {f"{a}-{b}": area(S[a] * S[b] > 0) for i, a in enumerate(ks) for b in ks[i + 1:]}
    Y["b8_sec_all"] = area(np.prod(list(S.values()), axis=0) > 0)
    Y["b8_win"] = area(np.ones(GX.shape) > 0)
    par = [sector(c, 90.0, 22.5) for c in ((9.0, 20.0), (9.0, 30.0), (9.0, 40.0))]
    Y["b8_par_single"] = [area(v > 0) for v in par]
    Y["b8_par_all"] = area(np.prod(par, axis=0) > 0)
    return Y


def gauss2(c, sd):
    return np.exp(-0.5 * (dist(c) ** 2) / sd ** 2)


R95_2D = math.sqrt(5.991464547)   # 2차원 등방 정규의 95% 반경 / sd


def bc_gauss2(m1, s1, m2, s2):
    """2차원 등방 정규 둘의 바타차리야 계수(닫힌 식)"""
    d2 = (m1[0] - m2[0]) ** 2 + (m1[1] - m2[1]) ** 2
    return (2 * s1 * s2 / (s1 ** 2 + s2 ** 2)) * math.exp(-d2 / (4 * (s1 ** 2 + s2 ** 2)))


def case_b9():
    """결과가 '중심과 95% 반경'만 남았을 때: 2차원 정규 어림으로 겹침을 재고 합친다"""
    reps = {"갑법": ((30.8, 29.6), 6.0), "을법": ((28.9, 31.2), 9.0), "병법": ((36.5, 26.0), 7.0)}
    out = dict(reps={k: dict(c=v[0], r=v[1], sd=v[1] / R95_2D) for k, v in reps.items()})
    ks = list(reps)
    G = {k: norm(gauss2(reps[k][0], reps[k][1] / R95_2D)) for k in ks}
    out["pair"] = {}
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            ca, ra = reps[a]; cb, rb = reps[b]
            sa, sb = ra / R95_2D, rb / R95_2D
            dd = math.hypot(ca[0] - cb[0], ca[1] - cb[1])
            bcc = bc_gauss2(ca, sa, cb, sb)
            out["pair"][f"{a}-{b}"] = dict(d=dd, rsum=ra + rb, bc_closed=bcc, bc_grid=bc(G[a], G[b]), h=math.sqrt(max(0, 1 - bcc)),
                                          ovl=ovl(G[a], G[b]))
    def pool_gauss(sel, w=None):
        w = w or [1.0] * len(sel)
        prec = [wk / (reps[k][1] / R95_2D) ** 2 for k, wk in zip(sel, w)]
        P = sum(prec)
        cx = sum(pr * reps[k][0][0] for pr, k in zip(prec, sel)) / P
        cy = sum(pr * reps[k][0][1] for pr, k in zip(prec, sel)) / P
        sd = math.sqrt(1 / P)
        return dict(c=(cx, cy), sd=sd, r95=sd * R95_2D)
    out["all"] = pool_gauss(ks)
    out["loo"] = {k: pool_gauss([x for x in ks if x != k]) for k in ks}
    for k in ks:
        d = out["loo"][k]["c"]; a = out["all"]["c"]
        out["loo"][k]["shift"] = math.hypot(d[0] - a[0], d[1] - a[1])
    # 격자로 확인: 세 정규의 곱
    gp = log_pool([G[k] for k in ks])
    cg = centroid(gp)
    out["grid_check"] = dict(c=cg, dx=abs(cg[0] - out["all"]["c"][0]), dy=abs(cg[1] - out["all"]["c"][1]), r95=math.sqrt(hpd_area(gp, 0.95) / math.pi))
    # 세 보고가 독립이 아니고 갑법과 을법이 같은 증거를 쓴 경우(지수 1/2)
    out["w_half"] = pool_gauss(ks, [0.5, 0.5, 1.0])
    out["prec"] = {k: 1 / (reps[k][1] / R95_2D) ** 2 for k in ks}
    out["prec_sum"] = sum(out["prec"].values())
    pa = out["pair"]["갑법-을법"]
    s1, s2 = reps["갑법"][1] / R95_2D, reps["을법"][1] / R95_2D
    out["ab"] = dict(s1=s1, s2=s2, num=2 * s1 * s2, den=s1 ** 2 + s2 ** 2, f1=2 * s1 * s2 / (s1 ** 2 + s2 ** 2), d2=pa["d"] ** 2,
                     ex=pa["d"] ** 2 / (4 * (s1 ** 2 + s2 ** 2)), f2=math.exp(-pa["d"] ** 2 / (4 * (s1 ** 2 + s2 ** 2))))
    # 병법이 가장 멀다: 병법 중심이 나머지 둘의 곱에서 몇 sd 떨어졌나
    two = pool_gauss(["갑법", "을법"])
    cb, rb = reps["병법"]
    sdt = math.sqrt(two["sd"] ** 2 + (rb / R95_2D) ** 2)
    dd = math.hypot(cb[0] - two["c"][0], cb[1] - two["c"][1])
    out["bing_vs_two"] = dict(d=dd, sd=sdt, z=dd / sdt, two_c=two["c"], two_r95=two["r95"])
    out["R95"] = R95_2D
    out["G"] = G; out["gp"] = gp
    return out


def case_b10():
    """거울상 두 해: 두 읍에서 각각 같은 거리, 세 번째 증거가 하나를 고른다"""
    A, B = (15.0, 20.0), (35.0, 20.0)
    li, u = 40, U_MID
    mu = li * u                       # 16.8 km
    sd = 1.4
    ra, rb = soft_ring(A, mu, sd), soft_ring(B, mu, sd)
    two = norm(ra * rb)
    h = math.sqrt(mu ** 2 - 10.0 ** 2)
    N = (25.0, 20.0 + h); S = (25.0, 20.0 - h)
    C = (45.0, 33.0)
    third = sector(C, 270.0, 22.5)
    third_wrong = sector(C, 90.0, 22.5)
    withC = norm(ra * rb * third)
    out = dict(mu=mu, sd=sd, h=h, N=N, S=S, C=C, d_AB=20.0)
    out["mass_N_two"] = mass_near(two, N, 3.0); out["mass_S_two"] = mass_near(two, S, 3.0)
    out["area_two"] = hpd_area(two, 0.95)
    out["mass_N_C"] = mass_near(withC, N, 3.0); out["mass_S_C"] = mass_near(withC, S, 3.0)
    out["area_C"] = hpd_area(withC, 0.95)
    out["third_has_N"] = bool(at(third, *N) > 0); out["third_has_S"] = bool(at(third, *S) > 0)
    out["brg_N"] = float((math.degrees(math.atan2(N[0] - C[0], N[1] - C[1])) + 360) % 360)
    out["brg_S"] = float((math.degrees(math.atan2(S[0] - C[0], S[1] - C[1])) + 360) % 360)
    out["dC_N"] = math.hypot(N[0] - C[0], N[1] - C[1]); out["dC_S"] = math.hypot(S[0] - C[0], S[1] - C[1])
    wrongP = ra * rb * third_wrong
    out["wrong_sum"] = float(wrongP.sum()); out["two_sum"] = float((ra * rb).sum())
    out["wrong_ratio"] = out["wrong_sum"] / out["two_sum"]
    out["ovl_two_third"] = ovl(two, norm(third))
    out["ovl_two_wrong"] = ovl(two, norm(third_wrong))
    out["cent_N"] = centroid(withC)
    out["two"] = two; out["withC"] = withC; out["ra"] = ra; out["rb"] = rb; out["third"] = third; out["A"] = A; out["B"] = B
    return out


def extras3():
    """장 앞의 개념(개념 13~15)과 연습 문제 7~10, 실수 사례집에 쓴 숫자"""
    Z = {}
    p1 = np.array([0.1, 0.6, 0.2, 0.1]); p2 = np.array([0.2, 0.5, 0.1, 0.2]); p3 = np.array([0.5, 0.0, 0.3, 0.2])
    # 개념 13: 바닥값(ε 오염)
    eps = {}
    for e in (0.0, 0.01, 0.05, 0.10, 0.20):
        q = (1 - e) * p3 + e / 4
        v = p1 * q
        eps[f"e{int(round(e * 100)):02d}"] = dict(q=list(q), v=list(v), Zs=float(v.sum()), post=list(v / v.sum()))
    Z["eps"] = eps
    # 개념 14: 곱의 합 Z와 일치 지수 Q=N*Z
    N = 4
    Z["q"] = dict(z12=float((p1 * p2).sum()), z13=float((p1 * p3).sum()), z23=float((p2 * p3).sum()), N=N)
    for k in ("12", "13", "23"):
        Z["q"]["q" + k] = N * Z["q"]["z" + k]
    # 개념 15: 지수 훑기
    sweep = []
    for w in (1.0, 0.75, 0.5, 0.25, 0.0):
        v = (p1 ** w) * (p2 ** w); post = v / v.sum()
        ent = float(-(post * np.log2(post)).sum())
        sweep.append(dict(w=w, post=list(post), mx=float(post.max()), ent=ent))
    Z["sweep"] = sweep
    Z["q"]["q12_2x"] = 2 * Z["q"]["q12"]
    k50 = math.sqrt(2 * math.log(2))
    Z["r50"] = dict(k50=k50, k95=R95_2D, ratio=R95_2D / k50, sd_as95=6.0 / R95_2D, sd_as50=6.0 / k50)
    # 실수 사례: 분기(m개의 자유로운 선택)
    Z["fork"] = {str(m): 1 - 0.95 ** m for m in (1, 3, 6, 8, 10, 13, 14)}
    Z["mhalf"] = math.log(0.5) / math.log(0.95)
    # 문제 7: 바닥값 0.1
    Z["p7"] = eps["e10"]
    # 문제 8: 일치 지수(칸 여섯)
    u = np.array([0.4, 0.3, 0.2, 0.1, 0, 0]); v = np.array([0.1, 0.4, 0.3, 0.2, 0, 0]); w = np.array([0, 0.2, 0.3, 0.3, 0.2, 0])
    Z["p8"] = dict(zuv=float((u * v).sum()), zuw=float((u * w).sum()), zvw=float((v * w).sum()))
    for k in ("uv", "uw", "vw"):
        Z["p8"]["q" + k] = 6 * Z["p8"]["z" + k]
    # 문제 10: 같은 sd의 2차원 정규 둘
    s = 2.0; d = 4.0
    bcv = math.exp(-d ** 2 / (4 * (s ** 2 + s ** 2)))
    Z["p10"] = dict(bc=bcv, h=math.sqrt(1 - bcv), sd=s, d=d, r95=s * R95_2D, rsum=2 * s * R95_2D)
    return Z


def case_b11(b3):
    """의심스러운 줄의 지수를 1에서 0까지 낮추는 '하나 빼기의 연속판'(사례 B3의 틀린 필사 세계)"""
    T = b3["T"]; P = b3["bad"]["P"]; ks = list(P)
    out = {"rows": {}}
    for w in (1.0, 0.75, 0.5, 0.25, 0.0):
        pool = log_pool([P[k] for k in ks], [1.0, 1.0, w])
        c = centroid(pool); m = hpd_mask(pool)
        out["rows"][f"w{int(w * 100):03d}"] = dict(w=w, err=math.hypot(c[0] - T[0], c[1] - T[1]), area=hpd_area(pool),
                                                  has_T=bool(m[int(T[1] / STEP), int(T[0] / STEP)]), cent=c)
    # 다른 두 줄 가운데 하나를 같은 방식으로 낮췄을 때(대조): 갑군 줄
    pool = log_pool([P[k] for k in ks], [0.5, 1.0, 1.0])
    c = centroid(pool)
    out["gap_half"] = dict(err=math.hypot(c[0] - T[0], c[1] - T[1]), area=hpd_area(pool))
    pool = log_pool([P[k] for k in ks], [1.0, 0.5, 1.0])
    c = centroid(pool)
    out["eul_half"] = dict(err=math.hypot(c[0] - T[0], c[1] - T[1]), area=hpd_area(pool))
    # 참 위치를 모를 때 볼 수 있는 값: 줄마다 지수를 ½로 낮췄을 때 합의 중심이 움직인 거리
    full = centroid(log_pool([P[k] for k in ks]))
    out["r_area"] = out["rows"]["w000"]["area"] / out["rows"]["w100"]["area"]
    out["shift_half"] = {}
    for i, k in enumerate(ks):
        w = [1.0, 1.0, 1.0]; w[i] = 0.5
        c = centroid(log_pool([P[j] for j in ks], w))
        out["shift_half"][k] = math.hypot(c[0] - full[0], c[1] - full[1])
    return out


def all_cases():
    return dict(b1=case_b1(), b2=case_b2(), b3=case_b3(), b4=case_b4(), b5=case_b5(), b6=case_b6(), b7=case_b7(), b8=case_b8(), b9=case_b9(), b10=case_b10())


# ======================================================================= 그림
def box(ax, x, y, w, h, text, mode, fc=None, ls="-", fs=FS, bold=False, hatch=None):
    s = STY[mode]
    fc = fc or ("#ffffff" if mode == "bw" else "#fdf3e1")
    p = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=fc, ec=s["line"],
                       lw=0.9, ls=ls, hatch=hatch, zorder=3)
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, zorder=4, fontweight="bold" if bold else "normal",
            bbox=dict(fc="white", ec="none", pad=1.5) if hatch else None)


def arrow(ax, x1, y1, x2, y2, mode, ls="-", lw=1.1):
    s = STY[mode]
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=s["line"], lw=lw, ls=ls,
                                                                 shrinkA=0, shrinkB=0), zorder=2)


def fig_timeline(mode):
    """연대기 종합 그림: 가로 시간축 1780~2020, 세 줄(합치기와 증거 이론 / 측정과 검증 / 역사 방법)"""
    s = STY[mode]
    cA = "#1f6fb8" if mode == "color" else "#000000"
    cB = "#2e7d32" if mode == "color" else "#444444"
    cC = "#c0392b" if mode == "color" else "#777777"
    fig, ax = plt.subplots(figsize=(WIDTH, 4.6))
    fig.subplots_adjust(left=0.03, right=0.97, top=0.98, bottom=0.03)
    ax.set_xlim(1770, 2040); ax.set_ylim(-5.0, 6.0); ax.axis("off")
    ys = {"A": 3.0, "B": 0.0, "C": -3.0}
    cols = {"A": cA, "B": cB, "C": cC}
    mk = {"A": "o", "B": "s", "C": "D"}
    lab = {"A": "합치기와 증거 이론", "B": "측정과 검증", "C": "역사 방법"}
    for k, y in ys.items():
        ax.plot([1780, 2030], [y, y], color=cols[k], lw=2.0, ls={"A": "-", "B": "--", "C": "-."}[k], zorder=2)
        ax.text(1772, y + 0.3, lab[k], fontsize=FS, fontweight="bold", color=cols[k], ha="left", va="bottom")
    for yr in range(1800, 2021, 50):
        for y in ys.values():
            ax.plot([yr, yr], [y - 0.1, y + 0.1], color=s["line"], lw=0.8, zorder=3)
        for yy in (1.5, -1.5):
            ax.text(yr, yy, str(yr), ha="center", va="center", fontsize=FS, color=s["gray"], bbox=dict(fc="white", ec="none", pad=0.8))
    # (줄, 해, 글자 가운데 x, 높이 단계(+위 -아래), 글자)
    items = [
        ("A", 1785, 1805, 1, "콩도르세\n1785"), ("A", 1951, 1930, 1, "쿨백·라이블러\n1951"), ("A", 1967, 1960, 2, "뎀프스터\n1967"),
        ("A", 1976, 1990, 1, "셰이퍼\n1976"), ("A", 1986, 2008, 2, "게네스트·지덱,\n자데 1986"), ("A", 2002, 2024, 1, "힌턴\n2002"),
        ("B", 1907, 1893, -1, "갈턴\n1907"), ("B", 1909, 1935, -1, "헬링거\n1909"), ("B", 1959, 1975, -1, "캠벨·피스크\n1959"),
        ("C", 1925, 1925, -1, "왕국유\n1925"),
    ]
    for k, yr, tx, lv, t in items:
        y = ys[k]
        sign = 1 if lv > 0 else -1
        ty = y + sign * (0.7 + (abs(lv) - 1) * 1.1)
        ax.plot([yr, tx], [y, ty], color=cols[k], lw=0.7, zorder=2)
        ax.plot(yr, y, mk[k], ms=5, color=cols[k] if mode == "color" else "white", mec=cols[k], mew=1.0, zorder=4)
        ax.text(tx, ty, t, ha="center", va="bottom" if sign > 0 else "top", fontsize=FS, linespacing=1.05)
    ax.text(2035, -4.6, "이 책의 8기법은\n이 세 줄 위에 놓인다", ha="right", va="bottom", fontsize=FS, linespacing=1.05)
    return save(fig, "ch12", "fig12-a-timeline", mode)


def fig_pool_bars(mode):
    """로그 풀링과 선형 풀링: 칸 네 개 예. 본문 수식 풀이의 숫자"""
    s = STY[mode]
    p1 = np.array([0.1, 0.6, 0.2, 0.1]); p2 = np.array([0.2, 0.5, 0.1, 0.2]); p3 = np.array([0.5, 0.0, 0.3, 0.2])
    def lg(a, b, wa=1, wb=1):
        v = a ** wa * b ** wb; return v / v.sum()
    rows = [("기법 1", p1), ("기법 2", p2), ("곱, 지수 1·1", lg(p1, p2)), ("곱, 지수 ½·½", lg(p1, p2, .5, .5)),
            ("평균", (p1 + p2) / 2), ("기법 1과 3의 곱", lg(p1, p3)), ("기법 1과 3의 평균", (p1 + p3) / 2)]
    fig, axs = plt.subplots(2, 4, figsize=(WIDTH, 3.6), sharey=True, constrained_layout=True)
    axs = axs.ravel()
    hat = ["", "", "//", "xx", "..", "//", ".."]
    for ax, (t, v), h in zip(axs, rows, hat):
        ax.bar(range(1, 5), v, color=("#7fb3d5" if mode == "color" else "#d0d0d0"), ec=s["line"], lw=0.7, hatch=h)
        for i, x in enumerate(v):
            ax.text(i + 1, x + 0.02, f"{x:.2f}".lstrip("0") if x else "0", ha="center", va="bottom", fontsize=FS)
        ax.set_title(t, fontsize=FS); ax.set_xticks(range(1, 5)); ax.set_ylim(0, 0.95)
        ax.tick_params(labelsize=FS)
    axs[0].set_ylabel("확률"); axs[4].set_ylabel("확률")
    axs[7].axis("off")
    axs[7].text(0.0, 0.5, "칸 1~4의 확률.\n기법 3은 칸 2에\n확률 0을 준다.", fontsize=FS, va="center", ha="left", transform=axs[7].transAxes)
    return save(fig, "ch12", "fig12-b-pool-bars", mode)


def fig_lineage(mode):
    """증거표 13줄이 읽힌 경로와 층. 읽은 경로는 둘이다"""
    s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 4.2))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    ax.set_xlim(0, 10); ax.set_ylim(0, 8.6); ax.axis("off")
    # 왼쪽 큰 상자: 고구려통사 3
    ax.add_patch(FancyBboxPatch((0.15, 2.7), 2.5, 5.6, boxstyle="round,pad=0.02,rounding_size=0.15", fc="none", ec=s["line"], lw=1.2, ls="-", zorder=1))
    ax.text(1.4, 8.0, "고구려통사 3 (3줄)", ha="center", va="center", fontsize=FS, fontweight="bold")
    for i, (e, t, h) in enumerate([("E1", "1층 거리", None), ("E3", "1층 방위", None), ("E2", "3층 해석", "//")]):
        box(ax, 1.4, 6.9 - i * 1.35, 1.9, 0.9, f"{e}\n{t}", mode, hatch=h)
    # 오른쪽 큰 상자: 고구려통사 5
    ax.add_patch(FancyBboxPatch((2.95, 2.7), 6.9, 5.6, boxstyle="round,pad=0.02,rounding_size=0.15", fc="none", ec=s["line"], lw=1.2, ls="-", zorder=1))
    ax.text(6.4, 8.0, "고구려통사 5 (9줄)", ha="center", va="center", fontsize=FS, fontweight="bold")
    cols = [("조선 문헌", 3.95, [("E6", "1층 방위"), ("E9", "1층 위치")]),
            ("연구자 서술", 6.4, [("E4", "2층 위치"), ("E5", "2층 크기"), ("E7", "2층 크기")]),
            ("각자성석", 8.85, [("E8", "2층 새김글"), ("E10", "2층 새김글"), ("E11", "2층 새김글"), ("E12", "2층 새김글")])]
    for hd, x, grp in cols:
        ax.text(x, 7.45, hd, ha="center", va="center", fontsize=FS, color=s["gray"])
        for i, (e, t) in enumerate(grp):
            box(ax, x, 6.6 - i * 0.95, 2.05, 0.75, f"{e} {t}", mode)
    # 아래: 직접 확인 한 줄과 설명
    box(ax, 1.4, 1.95, 1.9, 0.9, "G1 현대 좌표\n(직접 확인)", mode, ls="--")
    ax.text(5.9, 1.95, "읽은 경로는 연구서 2권, 직접 확인 1줄.\n같은 연구서를 거친 줄끼리는\n서로 독립이라고 말할 수 없다.", ha="center", va="center", fontsize=FS, linespacing=1.15)
    ax.text(5.0, 0.55, "E6와 E9의 원사료 계통(해동역사가 신증동국여지승람을 옮겼는가)은 원문 대조 필요", ha="center", va="center", fontsize=FS - 0.0)
    return save(fig, "ch12", "fig12-c-lineage", mode)


def _panel(ax, mode, title, regs=None, post=None, refs=None, T=None, cmap=None, fill=None, ext=(0, 60, 0, 60)):
    s = STY[mode]
    ax.set_xlim(0, 60); ax.set_ylim(0, 60); ax.set_aspect("equal")
    ax.set_xticks(range(0, 61, 20)); ax.set_yticks(range(0, 61, 20))
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    ax.set_title(title, fontsize=FS, loc="left")
    ax.tick_params(labelsize=FS)


def fig_b1(mode, B1):
    s = STY[mode]
    fig = plt.figure(figsize=(WIDTH, 3.2), constrained_layout=True)
    gs = fig.add_gridspec(2, 3)
    ax0 = fig.add_subplot(gs[:, 0:2]); ax1 = fig.add_subplot(gs[0, 2]); ax2 = fig.add_subplot(gs[1, 2])
    fills = {"color": ["#f0b45a", "#7fb3d5", "#a5d6a7"], "bw": ["#d0d0d0", "#b0b0b0", "#e8e8e8"]}[mode]
    hat = [None, "//", ".."]
    ax = ax0; _panel(ax, mode, "(가) 세 줄이 허용하는 영역")
    for (k, reg), f, h in zip(B1["regs"].items(), fills, hat):
        ax.contourf(GX, GY, reg, levels=[0.5, 1.5], colors=[f], alpha=0.55 if mode == "color" else 0.6, hatches=[h])
        ax.contour(GX, GY, reg, levels=[0.5], colors=[s["line"]], linewidths=0.6)
    for k, c in B1["refs"].items():
        ax.plot(*c, "^", color=s["ref"], ms=5, mfc=s["ref"] if mode == "color" else "white")
        ax.annotate(k, c, xytext=(3, 3), textcoords="offset points", fontsize=FS)
    ax.plot(*B1["T"], "*", color=s["truth"], ms=9, mec="black", mew=0.5)
    ax = ax1; _panel(ax, mode, "(나) 곱한 영역")
    ax.contourf(GX, GY, B1["prod"], levels=[0.5, 1.5], colors=[fills[0]], alpha=0.8)
    ax.contour(GX, GY, B1["prod"], levels=[0.5], colors=[s["line"]], linewidths=0.8)
    ax.contour(GX, GY, B1["exact"].astype(float), levels=[0.5], colors=[s["line"]], linewidths=1.0, linestyles=["--"])
    ax.plot(*B1["T"], "*", color=s["truth"], ms=8, mec="black", mew=0.5)
    ax.set_xlim(22, 38); ax.set_ylim(22, 38); ax.set_xticks([25, 35]); ax.set_yticks([25, 35])
    ax = ax2; _panel(ax, mode, "(다) 겹친 개수")
    cnt = sum((p > 0).astype(int) for p in B1["regs"].values())
    ax.contourf(GX, GY, cnt, levels=[0.5, 1.5, 2.5, 3.5], colors=(["#fdf0d5", "#f0b45a", "#c0392b"] if mode == "color" else ["#eeeeee", "#aaaaaa", "#333333"]))
    ax.plot(*B1["T"], "*", color="white" if mode == "bw" else s["truth"], ms=8, mec="black", mew=0.5)
    ax.set_xlim(22, 38); ax.set_ylim(22, 38); ax.set_xticks([25, 35]); ax.set_yticks([25, 35])
    return save(fig, "ch12", "fig12-d-three-towns", mode)


def fig_b2(mode, B2):
    s = STY[mode]
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 2.7), constrained_layout=True)
    ax = axs[0]
    ks = [1, 2, 3, 4, 6]
    cov = [2 * phi(1.96 / math.sqrt(k)) - 1 for k in ks]
    ax.plot(ks, cov, "o-", color=("#c0392b" if mode == "color" else "#000000"), lw=1.2, ms=5, mfc="white" if mode == "bw" else None)
    ax.axhline(0.95, color=s["line"], lw=0.8, ls="--")
    ax.text(6.0, 0.965, "명목 0.95", ha="right", va="bottom", fontsize=FS)
    for k, c in zip(ks, cov):
        ax.text(k + (0.25 if k == 1 else 0), c - 0.03, f"{c:.3f}", ha="center", va="top", fontsize=FS)
    ax.set_xlabel("같은 숫자를 옮긴 문헌의 수"); ax.set_ylabel("95% 구간의 적중 비율")
    ax.set_ylim(0.4, 1.02); ax.set_xticks(ks)
    ax.set_title("(가) 가중 없이 센 경우", fontsize=FS, loc="left")
    ax = axs[1]
    names = ["가중 없음", "가중 있음"]
    cv = [B2["mix"][n]["cover"] for n in names]
    bars = ax.bar(names, cv, color=["#e0e0e0", "#7fb3d5"] if mode == "color" else ["#ffffff", "#bbbbbb"], ec=s["line"], hatch=None)
    bars[0].set_hatch("//")
    ax.axhline(0.95, color=s["line"], lw=0.8, ls="--")
    for b, c in zip(bars, cv):
        ax.text(b.get_x() + b.get_width() / 2, c + 0.01, f"{c:.3f}", ha="center", va="bottom", fontsize=FS)
    ax.set_ylim(0.5, 1.05); ax.set_ylabel("95% 구간의 적중 비율")
    ax.set_title("(나) 필사본 둘과 독립 하나", fontsize=FS, loc="left")
    return save(fig, "ch12", "fig12-e-copies", mode)


def fig_b3(mode, B3):
    s = STY[mode]
    fig, axs = plt.subplots(1, 3, figsize=(WIDTH, 2.6), constrained_layout=True)
    ks = list(B3["lines"])
    cols = {"color": ["#f0b45a", "#7fb3d5", "#a5d6a7"], "bw": ["#cfcfcf", "#9a9a9a", "#e9e9e9"]}[mode]
    for ax, tag, ttl in ((axs[0], "good", "(가) 필사가 맞을 때"), (axs[1], "bad", "(나) 병현 줄이 틀릴 때")):
        _panel(ax, mode, ttl)
        for k, c in zip(ks, cols):
            m = hpd_mask(B3[tag]["P"][k], 0.95)
            ax.contour(GX, GY, m.astype(float), levels=[0.5], colors=[s["line"]], linewidths=0.9,
                       linestyles=[{"갑군": "-", "을진": "--", "병현": ":"}[k]])
        pm = hpd_mask(B3[tag]["pool"], 0.95)
        ax.contourf(GX, GY, pm.astype(float), levels=[0.5, 1.5], colors=[("#c0392b" if mode == "color" else "#444444")], alpha=0.7)
        ax.plot(*B3["T"], "*", color="white" if mode == "bw" else s["truth"], ms=9, mec="black", mew=0.5, zorder=6)
        ax.set_xlim(10, 50); ax.set_ylim(10, 50); ax.set_xticks(range(10, 51, 20)); ax.set_yticks(range(10, 51, 20))
    ax = axs[2]
    x = np.arange(3); w = 0.38
    g = [B3["good"]["shift"][k] for k in ks]; b = [B3["bad"]["shift"][k] for k in ks]
    ax.bar(x - w / 2, g, w, color=("#bdbdbd"), ec=s["line"], label="맞을 때")
    bb = ax.bar(x + w / 2, b, w, color=("#c0392b" if mode == "color" else "#444444"), ec=s["line"], label="틀릴 때")
    for r in bb: r.set_hatch("//") if mode == "bw" else None
    ax.set_xticks(x); ax.set_xticklabels(ks, fontsize=FS)
    ax.set_ylabel("빼면 중심이 움직인 거리 (km)")
    ax.set_title("(다) 하나 빼기", fontsize=FS, loc="left")
    ax.legend(fontsize=FS, loc="upper left", frameon=False)
    return save(fig, "ch12", "fig12-f-copy-error", mode)


def fig_b4(mode, B4):
    s = STY[mode]
    fig, axs = plt.subplots(1, 4, figsize=(WIDTH, 1.75), constrained_layout=True)
    items = [("이름 줄(A)", B4["A_p"]), ("갑군 줄(B)", B4["B_p"]), ("곱", B4["log_p"]), ("평균", B4["lin_p"])]
    for ax, (t, p) in zip(axs, items):
        ax.set_xlim(0, 60); ax.set_ylim(0, 60); ax.set_aspect("equal")
        ax.imshow(p / p.max(), origin="lower", extent=(0, 60, 0, 60), cmap=("YlOrBr" if mode == "color" else "Greys"), vmin=0, vmax=1)
        ax.plot(*B4["P1"], "o", mfc="none", mec=s["line"], ms=5); ax.plot(*B4["P2"], "o", mfc="none", mec=s["line"], ms=5)
        ax.text(B4["P1"][0] + 2, B4["P1"][1] + 2, "①", fontsize=FS); ax.text(B4["P2"][0] + 2, B4["P2"][1] + 2, "②", fontsize=FS)
        ax.set_title(t, fontsize=FS, loc="left"); ax.set_xticks([0, 30, 60]); ax.set_yticks([0, 30, 60]); ax.tick_params(labelsize=FS)
    return save(fig, "ch12", "fig12-g-homonym", mode)


def fig_b5(mode, B5):
    s = STY[mode]
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 2.7), constrained_layout=True)
    us = [u for u in B5["res"] if u != "range"]
    ax = axs[0]
    ax.plot(us, [B5["res"][u]["cov_d"] for u in us], "o-", color=("#c0392b" if mode == "color" else "#000000"), lw=1.2, ms=5, label="거리 줄 셋")
    ax.plot(us, [B5["res"][u]["cov_db"] for u in us], "s--", color=("#1f6fb8" if mode == "color" else "#555555"), lw=1.2, ms=5, mfc="white", label="거리 셋 + 방위 셋")
    ax.axhline(0.95, color=s["line"], lw=0.8, ls=":")
    ax.axvspan(0.36, 0.48, color="#dddddd", alpha=0.6, lw=0)
    ax.text(0.42, 0.05, "가정한\n범위", ha="center", va="bottom", fontsize=FS)
    ax.set_xlabel("참 단위 (km/리)"); ax.set_ylabel("95% 영역의 적중 비율")
    ax.set_ylim(0, 1.05); ax.legend(fontsize=FS, loc="lower left", bbox_to_anchor=(0.0, 0.2), frameon=False)
    ax.set_title("(가) 적중 비율", fontsize=FS, loc="left")
    ax = axs[1]
    ax.bar(range(len(us)), [B5["res"][u]["alarm"] for u in us], color=("#bbbbbb"), ec=s["line"], hatch="//")
    ax.set_xticks(range(len(us))); ax.set_xticklabels([f"{u:.2f}" for u in us], fontsize=FS)
    ax.set_xlabel("참 단위 (km/리)"); ax.set_ylabel("경보가 울린 비율")
    ax.set_ylim(0, 1.05)
    ax.set_title("(나) 경보 비율", fontsize=FS, loc="left")
    return save(fig, "ch12", "fig12-h-shared-unit", mode)


def fig_b6(mode, B6):
    s = STY[mode]
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 2.7), constrained_layout=True)
    ax = axs[0]; _panel(ax, mode, "(가) 세 줄의 영역")
    cols = {"color": ["#f0b45a", "#7fb3d5", "#a5d6a7"], "bw": ["#d8d8d8", "#aaaaaa", "#eeeeee"]}[mode]
    for (k, L), c, h in zip(B6["Ls"].items(), cols, [None, None, "//"]):
        ax.contourf(GX, GY, L, levels=[0.5, 1.5], colors=[c], alpha=0.6, hatches=[h])
        ax.contour(GX, GY, L, levels=[0.5], colors=[s["line"]], linewidths=0.5)
    ax.plot(B6["river"][:, 0], B6["river"][:, 1], color=s["river"], ls=s["river_ls"], lw=1.2)
    ax.plot(*B6["T"], "*", color=s["truth"], ms=9, mec="black", mew=0.5, zorder=6)
    ax.plot(*B6["gap"], "^", color=s["ref"], ms=5, mfc=s["ref"] if mode == "color" else "white"); ax.annotate("갑군", B6["gap"], xytext=(3, 3), textcoords="offset points", fontsize=FS)
    ax.plot(*B6["M"], "^", color=s["ref"], ms=5, mfc=s["ref"] if mode == "color" else "white"); ax.annotate("산", B6["M"], xytext=(3, 3), textcoords="offset points", fontsize=FS)
    ax = axs[1]
    labs = ["하루 길", "+ 강가", "+ 기슭"]
    seq = B6["order"]["하루 길 > 강가 > 산 남쪽 기슭"]
    seq2 = B6["order"]["산 남쪽 기슭 > 강가 > 하루 길"]
    ax.plot([0, 1, 2], seq, "o-", color=("#1f6fb8" if mode == "color" else "#000000"), lw=1.2, ms=5, label="하루 길부터")
    ax.plot([0, 1, 2], seq2, "s--", color=("#c0392b" if mode == "color" else "#555555"), lw=1.2, ms=5, mfc="white", label="기슭부터")
    ax.set_yscale("log")
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["첫 줄", "둘째 줄", "셋째 줄"], fontsize=FS)
    ax.set_ylabel("남은 영역의 넓이 (km²)")
    ax.legend(fontsize=FS, frameon=False, loc="upper right")
    ax.set_title("(나) 겹칠수록 줄어든다", fontsize=FS, loc="left")
    return save(fig, "ch12", "fig12-i-three-kinds", mode)


def fig_b9(mode, B9):
    s = STY[mode]
    fig = plt.figure(figsize=(WIDTH, 2.7), constrained_layout=True)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 1])
    ax = fig.add_subplot(gs[0]); ax2 = fig.add_subplot(gs[1])
    ax.set_xlim(18, 46); ax.set_ylim(14, 42); ax.set_aspect("equal")
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    ax.set_xticks(range(20, 46, 10)); ax.set_yticks(range(15, 41, 10)); ax.tick_params(labelsize=FS)
    ax.set_title("(가) 세 보고와 합친 영역", fontsize=FS, loc="left")
    styles = {"갑법": ("-", "#1f77b4"), "을법": ("--", "#d62728"), "병법": (":", "#2ca02c")}
    th = np.linspace(0, 2 * np.pi, 200)
    for k, v in B9["reps"].items():
        ls, col = styles[k]
        col = col if mode == "color" else s["line"]
        ax.plot(v["c"][0] + v["r"] * np.cos(th), v["c"][1] + v["r"] * np.sin(th), ls=ls, color=col, lw=1.3)
        ax.plot(*v["c"], "o", color=col, ms=3)
    a = B9["all"]
    ax.plot(a["c"][0] + a["r95"] * np.cos(th), a["c"][1] + a["r95"] * np.sin(th), "-", color=s["line"], lw=2.4)
    ax.plot(*a["c"], "*", color=s["line"], ms=8)
    ax.text(21.0, 38.5, "갑 실선\n을 파선\n병 점선\n굵은 선 합침", fontsize=FS, va="top",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=s["gray"], lw=0.5))
    names = [k.replace("법", "") for k in B9["pair"]]
    labs = [k.replace("법", "") for k in B9["pair"]]
    ys = [B9["pair"][k]["bc_closed"] for k in B9["pair"]]
    hat = ["//", "..", "xx"]
    bars = ax2.bar(range(3), ys, color=("#7fb3d5" if mode == "color" else "#d0d0d0"), ec=s["line"], lw=0.7)
    for b_, h_ in zip(bars, hat):
        b_.set_hatch(h_)
    for i, y in enumerate(ys):
        ax2.text(i, y + 0.02, f"{y:.2f}", ha="center", va="bottom", fontsize=FS)
    ax2.set_xticks(range(3)); ax2.set_xticklabels([l.replace("-", "·") for l in labs], fontsize=FS)
    ax2.set_ylim(0, 1.05); ax2.tick_params(labelsize=FS)
    ax2.set_title("(나) 쌍의 겹침(BC)", fontsize=FS, loc="left")
    return save(fig, "ch12", "fig12-j-gauss-reports", mode)


def fig_b10(mode, B10):
    s = STY[mode]
    fig, axs = plt.subplots(1, 3, figsize=(WIDTH, 2.0), constrained_layout=True)
    cm = "YlOrBr" if mode == "color" else "Greys"
    items = [("(가) 두 읍의 거리", B10["two"]), ("(나) 세 번째 줄(현의 서쪽)", B10["third"]), ("(다) 셋을 곱함", B10["withC"])]
    for ax, (t, p) in zip(axs, items):
        ax.set_xlim(5, 55); ax.set_ylim(0, 50); ax.set_aspect("equal")
        sc = 0.35 if t.startswith("(나)") else 1.0
        ax.imshow(p / p.max() * sc, origin="lower", extent=(-0.25, 60.25, -0.25, 60.25), cmap=cm, vmin=0, vmax=1)
        th = np.linspace(0, 2 * np.pi, 200)
        for cc in (B10["A"], B10["B"]):
            ax.plot(cc[0] + B10["mu"] * np.cos(th), cc[1] + B10["mu"] * np.sin(th), ls=":", color=s["gray"], lw=0.8)
        ax.set_xlim(5, 55); ax.set_ylim(0, 50)
        for (x, y), nm in ((B10["A"], "갑"), (B10["B"], "을"), (B10["C"], "병")):
            ax.plot(x, y, "^", mfc="white", mec=s["line"], ms=5)
            ax.text(x + 1.2, y + 1.5, nm, fontsize=FS)
        for pt, nm in ((B10["N"], "①"), (B10["S"], "②")):
            ax.plot(*pt, "o", mfc="none", mec=s["line"], ms=7)
            ax.text(pt[0] + 2, pt[1] - 1.5, nm, fontsize=FS)
        ax.set_title(t, fontsize=FS, loc="left"); ax.set_xticks([10, 30, 50]); ax.set_yticks([0, 25, 50]); ax.tick_params(labelsize=FS)
    return save(fig, "ch12", "fig12-k-mirror", mode)


def figures(cases):
    out = []
    for mode in ("color", "bw"):
        out.append(fig_timeline(mode))
        out.append(fig_pool_bars(mode))
        out.append(fig_lineage(mode))
        out.append(fig_b1(mode, cases["b1"]))
        out.append(fig_b2(mode, cases["b2"]))
        out.append(fig_b3(mode, cases["b3"]))
        out.append(fig_b4(mode, cases["b4"]))
        out.append(fig_b5(mode, cases["b5"]))
        out.append(fig_b6(mode, cases["b6"]))
        out.append(fig_b9(mode, cases["b9"]))
        out.append(fig_b10(mode, cases["b10"]))
    return out


if __name__ == "__main__":
    C = all_cases()
    for p in figures(C):
        print(p)
