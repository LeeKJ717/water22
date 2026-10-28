"""figs-m14.py - 14장(기법 간 충돌 분석) 새 그림과 새 사례 계산.
실행: python3 tools/figs-m14.py          (그림/ch14 에 컬러·흑백 PDF 생성, 계산 숫자를 출력)
      python3 tools/figs-m14.py --calc   (그림 없이 계산 숫자만 출력)
모든 가상 세계는 서경의 결과가 아니다. 실제 사료 사례(평양부 기록)는 본문에 적힌 리 수와 방위만 쓰며 좌표를 쓰지 않는다.
"""
import sys, os, math, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Wedge, Circle
from figlib import *

FS = 8.5
STEP = 0.5
XS = np.arange(0, 60 + 1e-9, STEP)
GX, GY = np.meshgrid(XS, XS)
CELL = STEP * STEP
U_LO, U_HI, U_MID = 0.36, 0.48, 0.42


def dist(c):
    return np.hypot(GX - c[0], GY - c[1])


def bearing(c):
    return (np.degrees(np.arctan2(GX - c[0], GY - c[1])) + 360) % 360


def sector(c, brg, half=22.5):
    b = bearing(c)
    return (np.abs((b - brg + 180) % 360 - 180) <= half).astype(float)


def ring(c, lo, hi):
    d = dist(c)
    return ((d >= lo) & (d <= hi)).astype(float)


def norm(L):
    s = L.sum()
    return L / s if s > 0 else L


def area(m):
    return float((m > 0).sum() * CELL)


def centroid(m):
    s = m.sum()
    return (float((GX * m).sum() / s), float((GY * m).sum() / s)) if s > 0 else (float("nan"), float("nan"))


def ovl(p, q):
    return float(np.minimum(norm(p), norm(q)).sum())


def line_region(c, li, brg, u_lo=U_LO, u_hi=U_HI, tol=0.10, half=22.5):
    """리 서술을 고리와 부채꼴의 교집합으로: 거리 읽기 +-tol, 단위 구간 u_lo~u_hi, 방위 반폭 half"""
    return ring(c, li * (1 - tol) * u_lo, li * (1 + tol) * u_hi) * sector(c, brg, half)


def dempster_K(masks, r=0.9):
    """각 출처가 자기 영역에 r, 전체(모른다)에 1-r을 둘 때 모든 출처를 결합한 충돌량 K"""
    n = len(masks)
    K = 0.0
    for pick in itertools.product([0, 1], repeat=n):
        pr = 1.0
        inter = np.ones(GX.shape, bool)
        for k, a in enumerate(pick):
            pr *= r if a else (1 - r)
            if a:
                inter &= masks[k] > 0
        if inter.sum() == 0 and any(pick):
            K += pr
    return K


def pair_ovl(masks):
    n = len(masks)
    M = np.eye(n)
    for i in range(n):
        for j in range(n):
            if i != j:
                M[i, j] = ovl(masks[i], masks[j])
    return M


def prod_mask(masks):
    out = np.ones(GX.shape)
    for m in masks:
        out = out * (m > 0)
    return out


def loo_shift(masks, full_cent):
    """하나 빼기: k번째를 빼고 곱한 영역의 무게중심이 전체 곱 영역의 무게중심에서 움직인 거리(km); 전체가 비면 None"""
    res = []
    for k in range(len(masks)):
        rest = [m for i, m in enumerate(masks) if i != k]
        pm = prod_mask(rest)
        c = centroid(pm)
        res.append((area(pm), c))
    return res


T = (30.0, 30.0)
REFS = {"갑군": ((9.0, 30.0), 50, 90.0), "을진": ((33.0, 13.0), 40, 0.0), "병현": ((38.5, 38.5), 30, 225.0)}


def b1_masks(over=None):
    """12장 사례 B1과 같은 가상 세계의 세 줄. over={이름: dict(li=, brg=, ulo=, uhi=)} 로 입력을 바꾼다"""
    ms = {}
    for k, (c, li, brg) in REFS.items():
        o = (over or {}).get(k, {})
        ms[k] = line_region(c, o.get("li", li), o.get("brg", brg), o.get("ulo", U_LO), o.get("uhi", U_HI))
    return ms


def summarize(ms, label):
    names = list(ms)
    L = [ms[k] for k in names]
    pm = prod_mask(L)
    d = dict(label=label, areas={k: area(ms[k]) for k in names}, prod_area=area(pm), prod_cent=centroid(pm),
             K=dempster_K(L), pair={f"{names[i]}-{names[j]}": ovl(L[i], L[j]) for i in range(len(names)) for j in range(i + 1, len(names))},
             hasT=bool(pm[int(T[1] / STEP), int(T[0] / STEP)] > 0) if pm.sum() > 0 else False)
    loo = []
    for k in range(len(names)):
        rest = [L[i] for i in range(len(names)) if i != k]
        r = prod_mask(rest)
        loo.append((names[k], area(r), centroid(r)))
    d["loo"] = loo
    return d


# ===================================================================== 사례 계산
def case_v1():
    """단위 오류: 을진지 '四十里'를 40 km로 입력(리->km 환산 빠짐). 정상과 비교"""
    ok = b1_masks()
    bad_over = dict(을진=dict(li=40, ulo=1.0, uhi=1.0))   # 40 km 로 읽음: 단위 1 km/리
    bad = b1_masks(bad_over)
    return summarize(ok, "정상"), summarize(bad, "을진지 단위 오류")


def case_v2():
    """방위 뒤집힘: 병현지 '西南'을 '東南'(135도)으로 입력"""
    bad = b1_masks(dict(병현=dict(brg=135.0)))
    # 뒤집어 보기 시험: 각 줄의 동서를 뒤집어 곱한 영역이 생기는지
    flips = {}
    cur = {"갑군": REFS["갑군"][2], "을진": REFS["을진"][2], "병현": 135.0}
    for k in REFS:
        fb = (360 - cur[k]) % 360
        ms = b1_masks({"병현": dict(brg=135.0)})
        c, li, _ = REFS[k]
        ms[k] = line_region(c, li, fb)
        flips[k] = area(prod_mask(list(ms.values())))
    return summarize(bad, "병현지 동서 뒤집힘"), flips


def case_v3():
    """이름 충돌: 기준 지명 '서성' 후보 A, B. 사료: 송포는 서성 동쪽 20리. 둘째 줄: 송포는 합수 머리 남쪽 10리"""
    candA, candB = (15.0, 30.0), (40.0, 45.0)
    r1A = line_region(candA, 20, 90.0); r1B = line_region(candB, 20, 90.0)
    conf = (24.0, 36.0)    # 가상의 두 강의 합수
    r2 = line_region(conf, 15, 180.0)
    # 후보 기간 겹침(가상력)
    src = (120, 180)
    pA = (100, 200); pB = (170, 260)
    ovA = max(0, min(src[1], pA[1]) - max(src[0], pA[0])); ovB = max(0, min(src[1], pB[1]) - max(src[0], pB[0]))
    L = src[1] - src[0]
    prior = np.array([ovA / L, ovB / L]); prior_n = prior / prior.sum()
    like = np.array([area(r1A * r2) / area(r2), area(r1B * r2) / area(r2)])
    post = prior * like; post_n = post / post.sum() if post.sum() > 0 else post
    return dict(areaA=area(r1A), areaB=area(r1B), areaR2=area(r2), interA=area(r1A * r2), interB=area(r1B * r2),
                ovA=ovA, ovB=ovB, L=L, prior=prior, prior_n=prior_n, like=like, post_n=post_n, centA=centroid(r1A * r2),
                regs=(r1A, r1B, r2), cands=(candA, candB), conf=conf)


def case_v4():
    """시대마다 리가 다른데 한 시대의 단위만 가정: 갑군지·을진지(옛 시대, u=0.42), 병현지(뒤 시대, u=0.46)"""
    Tt = T
    A, B, C = REFS["갑군"][0], REFS["을진"][0], REFS["병현"][0]
    dA = math.hypot(Tt[0] - A[0], Tt[1] - A[1]); dB = math.hypot(Tt[0] - B[0], Tt[1] - B[1]); dC = math.hypot(Tt[0] - C[0], Tt[1] - C[1])
    liA, liB, liC = 50, 40, 25      # 서술(가상): 병현지는 西南 二十五里
    out = dict(dA=dA, dB=dB, dC=dC, trueli=(dA / 0.42, dB / 0.42, dC / 0.46))
    cases = {}
    for name, rng in [("옛 단위 0.36~0.40으로 모두", {"갑군": (0.36, 0.40), "을진": (0.36, 0.40), "병현": (0.36, 0.40)}),
                      ("0.36~0.48로 모두", {"갑군": (0.36, 0.48), "을진": (0.36, 0.48), "병현": (0.36, 0.48)}),
                      ("시대별(옛 0.40~0.44, 뒤 0.44~0.48)", {"갑군": (0.40, 0.44), "을진": (0.40, 0.44), "병현": (0.44, 0.48)})]:
        ms = {}
        for k, li, c, brg in [("갑군", liA, A, 90.0), ("을진", liB, B, 0.0), ("병현", liC, C, 225.0)]:
            ms[k] = line_region(c, li, brg, rng[k][0], rng[k][1])
        d = summarize(ms, name)
        cases[name] = d
    out["cases"] = cases
    return out


def case_v5():
    """모형의 한계: 사흘 길. 150 km 창. 거리·방위 두 줄은 T에서 만나고, 사흘 길 줄만 하루 길을 25 km로 가정해 어긋남"""
    # 별도 창(0~150) 계산은 해석식으로: 선분/원 관계로 풀기 위해 격자를 쓴다
    xs = np.arange(0, 150 + 1e-9, 0.5); gx, gy = np.meshgrid(xs, xs)
    cell = 0.25
    Tt = (75.0, 75.0)
    P = (75.0, 40.0)   # 사흘 길의 출발지(가상 '해진')
    def d(c): return np.hypot(gx - c[0], gy - c[1])
    def b(c): return (np.degrees(np.arctan2(gx - c[0], gy - c[1])) + 360) % 360
    def sec(c, brg, half=22.5): return (np.abs((b(c) - brg + 180) % 360 - 180) <= half)
    # 두 줄(단위를 0.42 km/리 한 값으로 고정, 거리 읽기 +-10%): 『갑지』 A2에서 동북쪽 135리, 『을지』 B2에서 서남쪽 125리
    A2, B2 = (30.0, 40.0), (110.0, 115.0)
    dA2 = math.hypot(Tt[0] - A2[0], Tt[1] - A2[1]); dB2 = math.hypot(Tt[0] - B2[0], Tt[1] - B2[1])
    bA2 = (math.degrees(math.atan2(Tt[0] - A2[0], Tt[1] - A2[1])) + 360) % 360
    bB2 = (math.degrees(math.atan2(Tt[0] - B2[0], Tt[1] - B2[1])) + 360) % 360
    ra = (d(A2) >= 135 * 0.42 * 0.9) & (d(A2) <= 135 * 0.42 * 1.1) & sec(A2, 45.0)
    rb = (d(B2) >= 125 * 0.42 * 0.9) & (d(B2) <= 125 * 0.42 * 1.1) & sec(B2, 225.0)
    others = ra & rb
    dP_true = math.hypot(Tt[0] - P[0], Tt[1] - P[1])   # 51 km
    out = dict(dA2=dA2, dB2=dB2, bA2=bA2, bB2=bB2, area_others=others.sum() * cell, dP_true=dP_true)
    # 사흘 길: 방위는 '북쪽'(0도)로 서술, 하루 길 구간 [lo,hi]
    def trav(lo, hi, days=3):
        return (d(P) >= days * lo) & (d(P) <= days * hi) & sec(P, 0.0)
    res = {}
    for name, lo, hi in [("평지 20~30", 20, 30), ("산길 포함 12~30", 12, 30), ("산길 12~20", 12, 20)]:
        r = trav(lo, hi)
        res[name] = dict(area=r.sum() * cell, inter=(r & others).sum() * cell, hasT=bool(r[int(Tt[1] / 0.5), int(Tt[0] / 0.5)]))
    out["res"] = res
    # 충돌이 사라지는 하루 길 하한: others 영역의 P에서 가장 가까운 점까지 거리 / 3
    dd = d(P)[others]
    out["dmin"] = float(dd.min()); out["dmax"] = float(dd.max())
    out["lo_thresh"] = float(dd.max() / 3)      # 하루 길 하한이 이 값 이하여야 사흘 길 띠가 두 줄 영역에 닿기 시작함
    out["lo_true"] = float(dP_true / 3)         # 참 위치까지 포함하려면 이 값 이하
    out["grid"] = (xs, others, P, Tt, A2, B2)
    return out


def case_v6(seed=20261028, n=40000):
    """사후 분할의 위험. 한 곳을 가리키는 증거 8개(점 추정, 오차 sigma=3 km). 사전에 정한 4:4 분할과 결과를 보고 고른 분할의 평균 사이 거리"""
    rng = np.random.default_rng(seed)
    sig = 3.0
    m = 8
    splits = [s for s in itertools.product([0, 1], repeat=m) if 2 <= sum(s) <= m - 2 and s[0] == 0]
    S = np.array(splits, dtype=float)       # 분할 수 x 8, 1이면 B군 (s[0]=0 이므로 거울 중복 제거)
    nb = S.sum(1); na = m - nb
    fixed = np.array([0, 0, 0, 0, 1, 1, 1, 1], dtype=float)
    fixed_d = []; best_d = []; best_d44 = []
    idx44 = np.where(nb == 4)[0]
    for _ in range(n):
        X = rng.normal(0, sig, size=(m, 2))
        mb = (S @ X) / nb[:, None]; ma = ((1 - S) @ X) / na[:, None]
        dd = np.hypot(*(mb - ma).T)
        best_d.append(dd.max()); best_d44.append(dd[idx44].max())
        mbf = (fixed @ X) / 4; maf = ((1 - fixed) @ X) / 4
        fixed_d.append(float(np.hypot(*(mbf - maf))))
    fixed_d = np.array(fixed_d); best_d = np.array(best_d); best_d44 = np.array(best_d44)
    sd_d = sig * math.sqrt(1 / 4 + 1 / 4)
    return dict(n=n, nsplit=len(splits), n44=len(idx44), fixed_mean=float(fixed_d.mean()), fixed_p95=float(np.percentile(fixed_d, 95)),
                best_mean=float(best_d.mean()), best_p95=float(np.percentile(best_d, 95)), best44_mean=float(best_d44.mean()),
                best44_p95=float(np.percentile(best_d44, 95)),
                ray_p95=sd_d * math.sqrt(-2 * math.log(0.05)), ray_mean=sd_d * math.sqrt(math.pi / 2),
                frac_fixed_over5=float((fixed_d > 5.0).mean()), frac_best_over5=float((best_d > 5.0).mean()),
                fixed_d=fixed_d, best_d=best_d)


def case_v6b():
    """참된 이질성: 전기 증거 4줄은 (20,20) 부근, 후기 4줄은 (40,42) 부근을 가리킴. 가상 점 추정과 Cochran Q"""
    pts_a = np.array([(19.0, 21.5), (21.5, 18.5), (20.5, 22.0), (18.0, 19.0)])
    pts_b = np.array([(41.0, 43.5), (38.5, 40.5), (40.5, 41.0), (42.0, 42.5)])
    sig = 3.0
    allp = np.vstack([pts_a, pts_b])
    def Q(P):
        mu = P.mean(0)
        return float(((P - mu) ** 2).sum() / sig ** 2)   # 2차원: 자유도 2(n-1)
    out = dict(ma=pts_a.mean(0), mb=pts_b.mean(0), dist=float(np.hypot(*(pts_a.mean(0) - pts_b.mean(0)))),
               Q_all=Q(allp), df_all=2 * (len(allp) - 1), Q_a=Q(pts_a), Q_b=Q(pts_b), df_a=2 * 3, df_b=2 * 3)
    out["I2"] = max(0.0, (out["Q_all"] - out["df_all"]) / out["Q_all"])
    return out


def case_v7():
    """원인이 겹칠 때: 다섯 줄. 정상 세 줄 + 정포(을진지 단위 오류가 아니라 정포지) + 서성 후보 문제"""
    A, B, C = REFS["갑군"][0], REFS["을진"][0], REFS["병현"][0]
    D = (52.0, 30.0); E1 = (20.0, 52.0)       # 넷째 기준: 무진 (정현에서 서쪽 20리 부근 가정), 다섯째 후보
    # 넷째 줄: 『정포지』 丁縣在茂津西二十里 (무진 기준 서쪽 20리)
    # 다섯째 줄: 『서성지』 丁縣在西城南四十里. 서성 후보 가는 두 곳
    rows = {}
    base = b1_masks()
    l4 = line_region(D, 50, 270.0)   # 무진은 (52,30). 丁縣在茂津西五十里
    # 단위 오류 판: 50 km로 읽음
    l4_bad = line_region(D, 50, 270.0, 1.0, 1.0)
    # 다섯째: 丁縣在西城南四十里. 서성 후보 둘
    S_A = (30.0, 47.0); S_B = (8.0, 52.0)
    l5A = line_region(S_A, 40, 180.0); l5B = line_region(S_B, 40, 180.0)
    steps = []
    def row(label, ms):
        names = list(ms); L = [ms[k] for k in names]
        pm = prod_mask(L)
        steps.append(dict(label=label, n=len(L), K=dempster_K(L), prod_area=area(pm), cent=centroid(pm),
                          minovl=min(ovl(L[i], L[j]) for i in range(len(L)) for j in range(i + 1, len(L)))))
    ms0 = dict(base); ms0["무진"] = l4_bad; ms0["서성B"] = l5B
    row("0 입력 그대로(무진 단위 오류, 서성 후보 B)", ms0)
    ms1 = dict(base); ms1["무진"] = l4; ms1["서성B"] = l5B
    row("1 무진 단위 오류를 고침", ms1)
    ms2 = dict(base); ms2["무진"] = l4; ms2["서성A"] = l5A
    row("2 서성 후보를 A로 바꿈", ms2)
    ms3 = dict(base); ms3["무진"] = l4
    row("3 서성 줄을 빼고 보고", ms3)
    return steps, dict(l4=l4, l4_bad=l4_bad, l5A=l5A, l5B=l5B, base=base, pts=dict(D=D, SA=S_A, SB=S_B))


def case_v8():
    """이상치 규칙: 일곱 문헌이 같은 두 지점 사이 거리를 리로 적은 값. 가상"""
    from math import erf, sqrt
    def pz(z): return 0.5 * (1 + erf(z / sqrt(2)))
    def inv_two_tail(p):
        lo, hi = 0.0, 10.0
        for _ in range(100):
            mid = (lo + hi) / 2
            if 2 * (1 - pz(mid)) > p: lo = mid
            else: hi = mid
        return (lo + hi) / 2
    out = {}
    for name, v in [("(가) 20이 한 개", [40, 40, 42, 45, 40, 43, 20]), ("(나) 20이 두 개", [40, 40, 42, 45, 20, 43, 20])]:
        v = np.array(v, float); n = len(v)
        mu = v.mean(); sd = v.std(ddof=1); zc = inv_two_tail(1 / (2 * n))
        z = np.abs(v - mu) / sd
        q1, q3 = np.percentile(v, [25, 75]); iqr = q3 - q1
        lo_f, hi_f = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        med = np.median(v); mad = np.median(np.abs(v - med)); rz = 0.6745 * (v - med) / mad if mad > 0 else None
        out[name] = dict(v=v.tolist(), n=n, mu=mu, sd=sd, zc=zc, zmax=float(z.max()), flagged_chauv=[float(x) for x in v[z > zc]],
                         q1=q1, q3=q3, iqr=iqr, lo_f=lo_f, hi_f=hi_f, flagged_tukey=[float(x) for x in v[(v < lo_f) | (v > hi_f)]],
                         med=med, mad=mad, flagged_mad=[float(x) for x in v[np.abs(rz) > 3.5]] if rz is not None else None,
                         rz=[float(x) for x in rz], mu_wo=float(np.mean([x for x in v if x != 20])))
    return out


def case_r3():
    """실제 사료 RE11·RE12(세종실록 지리지 평양부): 동명왕묘 '府巽方三十里許, 中和境' 과 사경 '南距中和二十五里'. 리 수와 방위만 쓴다"""
    south_border = 25.0
    d0 = 30.0
    out = {}
    th = math.radians(135)
    out["strict_south"] = d0 * -math.cos(th); out["strict_east"] = d0 * math.sin(th)
    out["short"] = south_border - out["strict_south"]; out["short_frac"] = out["short"] / south_border
    # 허용 폭: 거리 +-10 %, 방위 반폭 22.5 도
    lo = 0.9 * d0 * -math.cos(math.radians(157.5)) * 0 + 0.9 * d0 * -math.cos(math.radians(112.5))
    hi = 1.1 * d0 * -math.cos(math.radians(157.5))
    out["tol_lo"] = lo; out["tol_hi"] = hi
    # 거리 30 리 그대로일 때 25 리를 넘기 위한 최소 방위각
    out["theta_min"] = math.degrees(math.acos(-south_border / d0))
    # 방위 135도 그대로일 때 필요한 거리
    out["d_needed"] = south_border / -math.cos(th)
    out["d_needed_ratio"] = out["d_needed"] / d0
    out["mid_range_30"] = (d0 * -math.cos(math.radians(112.5)), d0 * -math.cos(math.radians(157.5)))
    return out


def case_r2():
    """실제 사료 E6(대성산 동북쪽), E9(구룡산 위), RE14(이명). 산을 반경 r의 원으로 둔 가상 비율 계산"""
    out = {}
    r = 3.0; far = 12.0
    sec = 45.0 / 360.0
    a_sector = sec * math.pi * far ** 2
    a_inside = sec * math.pi * r ** 2
    a_outside = sec * math.pi * (far ** 2 - r ** 2)
    out.update(r=r, far=far, a_sector=a_sector, a_inside=a_inside, a_outside=a_outside, frac_inside=a_inside / a_sector,
               disk=math.pi * r ** 2)
    # 산 반경 r이 커질수록 "산 위"와 "동북쪽 부채꼴"의 겹침 비율
    out["by_r"] = {rr: (sec * math.pi * rr ** 2) / a_sector for rr in (1.0, 3.0, 6.0, 9.0, 12.0)}
    return out


def eq_numbers():
    """수식 절의 숫자"""
    out = {}
    x = np.array([39.0, 41.0, 40.0, 38.0, 52.0, 53.0]); s = np.array([2.0] * 6)   # 1차원 점 추정(가상), 오차 2 km
    w = 1 / s ** 2; xw = (w * x).sum() / w.sum(); Q = float((w * (x - xw) ** 2).sum()); df = len(x) - 1
    out["xw"] = float(xw); out["Q"] = Q; out["df"] = df; out["I2"] = max(0.0, (Q - df) / Q)
    xa, xb = x[:4], x[4:]
    out["Qa"] = float((w[:4] * (xa - xa.mean()) ** 2).sum()); out["Qb"] = float((w[4:] * (xb - xb.mean()) ** 2).sum())
    out["Qwithin"] = out["Qa"] + out["Qb"]; out["Qbetween"] = Q - out["Qwithin"]
    out["meana"] = float(xa.mean()); out["meanb"] = float(xb.mean())
    # 하나 빼기 이동 (1차원)
    out["loo"] = {i: float(np.delete(x, i).mean() - x.mean()) for i in range(len(x))}
    out["mean"] = float(x.mean())
    return out


def eq_more():
    """수식 절과 연습 문제의 숫자"""
    out = {}
    # 식 2 이상치: 쇼브네
    def pz(z): return 0.5 * (1 + math.erf(z / math.sqrt(2)))
    def zc(n):
        lo, hi = 0.0, 10.0
        for _ in range(100):
            mid = (lo + hi) / 2
            if 2 * (1 - pz(mid)) > 1 / (2 * n): lo = mid
            else: hi = mid
        return (lo + hi) / 2
    out["zc"] = {n: zc(n) for n in (5, 7, 10, 20, 50)}
    v = np.array([38, 40, 40, 41, 42, 44, 70.0]); mu = v.mean(); sd = v.std(ddof=1)
    out["p2"] = dict(mu=mu, sd=sd, z=float(abs(70 - mu) / sd), zc=zc(7), mu_wo=float(v[:-1].mean()), sd_wo=float(v[:-1].std(ddof=1)),
                     z_wo=float(abs(70 - v[:-1].mean()) / v[:-1].std(ddof=1)))
    v2 = np.array([38, 40, 40, 41, 42, 44, 50.0]); out["p2b"] = dict(mu=v2.mean(), sd=v2.std(ddof=1), z=float(abs(50 - v2.mean()) / v2.std(ddof=1)))
    # 식 3 편향 바닥
    out["floor"] = {n: math.sqrt(2.5 ** 2 / n + 3.0 ** 2) for n in (1, 4, 9, 25, 100, 10000)}
    out["floor_ind"] = {n: 2.5 / math.sqrt(n) for n in (1, 4, 9, 25, 100)}
    out["floor_p5"] = {n: math.sqrt(2.0 ** 2 / n + 1.5 ** 2) for n in (1, 4, 16, 100)}
    # 식 4 분할
    out["splits"] = {m: 2 ** (m - 1) - 1 - m for m in (4, 6, 8, 10, 12)}
    sd_d = {(a, b): 3.0 * math.sqrt(1 / a + 1 / b) for a, b in ((4, 4), (3, 3), (2, 6), (5, 5))}
    out["sd_d"] = sd_d; out["lim95"] = {k: v * math.sqrt(-2 * math.log(0.05)) for k, v in sd_d.items()}
    # 연습 7: 이름 충돌
    out["p7"] = dict(ovA=30, ovB=20, pa=30 / 50, pb=20 / 50, post=(0.6 * 3) / (0.6 * 3 + 0.4 * 1))
    # 연습 1
    out["p1"] = dict(lo=50 * 0.9 * 0.36, hi=50 * 1.1 * 0.48, bad_lo=50 * 0.9, bad_hi=50 * 1.1, ratio=45 / 26.4)
    # 연습 6
    out["p6"] = dict(d3=(3 * 20, 3 * 30), d25=(2.5 * 20, 2.5 * 30), d35=(3.5 * 20, 3.5 * 30))
    # 연습 3 Q
    x = np.array([55.0, 52.0, 58.0, 54.0, 71.0]); sg = np.array([3.0, 3.0, 3.0, 3.0, 3.0]); w = 1 / sg ** 2
    xw = (w * x).sum() / w.sum(); Q = float((w * (x - xw) ** 2).sum()); out["p3"] = dict(xw=float(xw), Q=Q, df=4, I2=max(0, (Q - 4) / Q))
    x4 = x[:4]; Q4 = float((w[:4] * (x4 - x4.mean()) ** 2).sum()); out["p3b"] = dict(mean=float(x4.mean()), Q=Q4, df=3, I2=max(0, (Q4 - 3) / Q4))
    return out


def phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


# ===================================================================== 그림 도구
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


def _panel(ax, mode, title, regs, T=None, fills=None, refs=None):
    s = STY[mode]
    ax.set_xlim(0, 60); ax.set_ylim(0, 60); ax.set_aspect("equal")
    ax.set_xticks(range(0, 61, 20)); ax.set_yticks(range(0, 61, 20))
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    ax.set_title(title, fontsize=FS, loc="left")
    ax.tick_params(labelsize=FS)
    hat = ["//", "\\\\", ".."]
    colc = ["#1f6fb8", "#2e7d32", "#c0392b"]
    for i, (k, m) in enumerate(regs.items()):
        col = colc[i % 3] if mode == "color" else "#444444"
        kw = dict(hatches=[hat[i % 3]]) if mode == "bw" else {}
        if (m > 0).any():
            ax.contourf(GX, GY, (m > 0).astype(float), levels=[0.5, 1.5], colors=[col], alpha=0.30 if mode == "color" else 0.12, **kw)
        if (m > 0).any():
            ax.contour(GX, GY, (m > 0).astype(float), levels=[0.5], colors=[col if mode == "color" else "#000000"], linewidths=0.9,
                       linestyles=["-", "--", ":"][i % 3])
    if refs:
        for k, (x, y) in refs.items():
            ax.plot(x, y, "^", color=s["ref"], ms=5, mfc=s["ref"] if mode == "color" else "white", mew=0.8, zorder=5)
            ax.annotate(k, (x, y), xytext=(3, 3), textcoords="offset points", fontsize=FS)
    if T is not None:
        ax.plot(*T, "*", color=s["truth"], ms=9, mec="black", mew=0.5, zorder=7)


# ===================================================================== 그림
def fig_timeline(mode):
    s = STY[mode]
    cA = "#1f6fb8" if mode == "color" else "#000000"
    cB = "#2e7d32" if mode == "color" else "#444444"
    cC = "#c0392b" if mode == "color" else "#777777"
    fig, ax = plt.subplots(figsize=(WIDTH, 4.8))
    fig.subplots_adjust(left=0.03, right=0.97, top=0.98, bottom=0.03)
    ax.set_xlim(1790, 2025); ax.set_ylim(-5.4, 6.2); ax.axis("off")
    ys = {"A": 3.2, "B": 0.0, "C": -3.2}
    cols = {"A": cA, "B": cB, "C": cC}
    mk = {"A": "o", "B": "s", "C": "D"}
    lab = {"A": "오차와 이상치", "B": "이질성과 전체론", "C": "사료 비판"}
    for k, y in ys.items():
        ax.plot([1800, 2018], [y, y], color=cols[k], lw=2.0, ls={"A": "-", "B": "--", "C": "-."}[k], zorder=2)
        ax.text(1792, y + 0.35, lab[k], fontsize=FS, fontweight="bold", color=cols[k], ha="left", va="bottom")
    for yr in (1800, 1850, 1900, 1950, 2000):
        for y in ys.values():
            ax.plot([yr, yr], [y - 0.1, y + 0.1], color=s["line"], lw=0.8, zorder=3)
        for yy in (1.6, -1.6):
            ax.text(yr, yy, str(yr), ha="center", va="center", fontsize=FS, color=s["gray"], bbox=dict(fc="white", ec="none", pad=0.8))
    items = [
        ("A", 1809, 1830, 1, "가우스\n1809"), ("A", 1852, 1865, 2, "B. 피어스\n1852"), ("A", 1863, 1890, 1, "쇼브네\n1863"),
        ("A", 1977, 1975, 1, "튜키\n1977"), ("A", 1994, 2003, 2, "NIST\n1994"),
        ("B", 1906, 1900, -1, "뒤엠\n1906"), ("B", 1954, 1950, -1, "코크란\n1954"), ("B", 2003, 2005, -1, "I²\n2003"),
        ("C", 1824, 1845, -1, "랑케\n1824"), ("C", 1949, 1949, -1, "블로크\n1949"),
    ]
    for k, yr, tx, lv, t in items:
        y = ys[k]; sign = 1 if lv > 0 else -1
        ty = y + sign * (0.75 + (abs(lv) - 1) * 1.15)
        ax.plot([yr, tx], [y, ty], color=cols[k], lw=0.7, zorder=2)
        ax.plot(yr, y, mk[k], ms=5, color=cols[k] if mode == "color" else "white", mec=cols[k], mew=1.0, zorder=4)
        ax.text(tx, ty, t, ha="center", va="bottom" if sign > 0 else "top", fontsize=FS, linespacing=1.05)
    ax.text(2022, -5.3, "이 책의 충돌 분석은\n세 줄이 만나는 자리", ha="right", va="bottom", fontsize=FS, linespacing=1.05)
    return save(fig, "ch14", "fig14-a-timeline", mode)


def fig_flow(mode):
    s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 5.0))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.99, bottom=0.01)
    ax.set_xlim(0, 10); ax.set_ylim(0, 12); ax.axis("off")
    steps = [("1 경보의 위치", "K, 부딪침 행렬,\n하나 빼기"), ("2 입력 점검", "verified, 단위,\n방위, 중복"), ("3 공유 가정 바꾸기", "단위, 시대, 계통을\n하나씩 바꿈"),
             ("4 증거 분할", "사전에 정한 기준으로\n둘로 나눔"), ("5 기록", "run 표와 보고 서식")]
    ys = [10.7, 8.5, 6.3, 4.1, 1.9]
    for (t, d), y in zip(steps, ys):
        box(ax, 2.6, y, 4.6, 1.5, f"{t}\n{d}", mode, bold=False)
    for i in range(4):
        arrow(ax, 2.6, ys[i] - 0.78, 2.6, ys[i + 1] + 0.78, mode)
    # 오른쪽: 단계에서 나오는 원인
    side = [("원인 3 공유 가정\n(모두 모여 있음)", 10.7), ("원인 1 입력 오류\n(한 줄을 빼면 사라짐)", 8.5), ("원인 3 공유 가정\n(가정을 바꾸면 사라짐)", 6.3),
            ("원인 5 이질성\n(두 덩어리)", 4.1), ("원인 2·4는 2~4단계\n어디서든 나옴", 1.9)]
    for t, y in side:
        box(ax, 7.8, y, 3.9, 1.3, t, mode, ls="--", fc="#ffffff" if mode == "bw" else "#e8f0f8")
        arrow(ax, 5.0, y, 5.85, y, mode, ls="--")
    ax.text(0.15, 0.25, "고친 뒤에는 처음(1단계)부터 다시 계산한다. 제외한 증거는 제외 전후 결과를 함께 적는다.", fontsize=FS, va="bottom", ha="left")
    return save(fig, "ch14", "fig14-b-flow", mode)


def fig_v12(mode, V1, V2):
    ok, bad1 = V1; bad2, flips = V2
    fig, axs = plt.subplots(1, 3, figsize=(WIDTH, 2.35), constrained_layout=True)
    refs = {k: v[0] for k, v in REFS.items()}
    _panel(axs[0], mode, "(가) 바른 입력", b1_masks(), T, refs=None)
    _panel(axs[1], mode, "(나) 단위 오류", b1_masks(dict(을진=dict(li=40, ulo=1.0, uhi=1.0))), T)
    _panel(axs[2], mode, "(다) 방위 뒤집힘", b1_masks(dict(병현=dict(brg=135.0))), T)
    for ax in axs:
        for k, (c, li, brg) in REFS.items():
            ax.plot(*c, "^", color="black", ms=4, mfc="black" if mode == "color" else "white", mew=0.7, zorder=6)
    axs[0].annotate("갑", REFS["갑군"][0], xytext=(3, 3), textcoords="offset points", fontsize=FS)
    axs[0].annotate("을", REFS["을진"][0], xytext=(3, -10), textcoords="offset points", fontsize=FS)
    axs[0].annotate("병", REFS["병현"][0], xytext=(3, 3), textcoords="offset points", fontsize=FS)
    return save(fig, "ch14", "fig14-c-input-errors", mode)


def fig_ladder(mode, steps):
    s = STY[mode]
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 2.7), constrained_layout=True)
    xl = ["0", "1", "2", "3"]
    Ks = [st["K"] for st in steps]
    colr = ["#c0392b", "#e08e0b", "#2e7d32", "#1f6fb8"] if mode == "color" else ["#555555"] * 4
    hat = ["", "//", "xx", ".."]
    axs[0].bar(range(4), Ks, color=colr if mode == "color" else "#d0d0d0", ec=s["line"], lw=0.7, hatch=None)
    for i, b in enumerate(axs[0].patches):
        if mode == "bw":
            b.set_hatch(hat[i])
    for i, v in enumerate(Ks):
        axs[0].text(i, v + 0.02, f"{v:.2f}", ha="center", va="bottom", fontsize=FS)
    axs[0].set_xticks(range(4)); axs[0].set_xticklabels(xl, fontsize=FS); axs[0].set_ylim(0, 1.18)
    axs[0].set_ylabel("충돌량 K"); axs[0].set_xlabel("조치 단계"); axs[0].set_title("(가) 충돌량", fontsize=FS, loc="left")
    ar = [st["prod_area"] for st in steps]
    axs[1].bar(range(4), ar, color=colr if mode == "color" else "#d0d0d0", ec=s["line"], lw=0.7)
    for i, b in enumerate(axs[1].patches):
        if mode == "bw":
            b.set_hatch(hat[i])
    for i, v in enumerate(ar):
        axs[1].text(i, v + max(ar) * 0.02, f"{v:.1f}", ha="center", va="bottom", fontsize=FS)
    axs[1].set_xticks(range(4)); axs[1].set_xticklabels(xl, fontsize=FS); axs[1].set_ylim(0, max(ar) * 1.18 + 1)
    axs[1].set_ylabel("곱한 영역 (km²)"); axs[1].set_xlabel("조치 단계"); axs[1].set_title("(나) 곱한 영역의 넓이", fontsize=FS, loc="left")
    return save(fig, "ch14", "fig14-d-ladder", mode)


def fig_posthoc(mode, V6):
    s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 2.7), constrained_layout=True)
    bins = np.arange(0, 16.01, 0.5)
    ax.hist(V6["fixed_d"], bins=bins, density=True, histtype="stepfilled", color="#7fb3d5" if mode == "color" else "#e0e0e0", ec=s["line"], lw=0.7, hatch=".." if mode == "bw" else None, label="사전에 정한 분할")
    ax.hist(V6["best_d"], bins=bins, density=True, histtype="step", color="#c0392b" if mode == "color" else "#000000", lw=1.5, ls="--", label="결과를 보고 고른 분할")
    ax.axvline(5.0, color=s["gray"], lw=0.9, ls=":")
    ax.text(5.2, 0.015, "5 km", fontsize=FS, va="bottom")
    ax.set_xlabel("두 덩어리 평균 사이의 거리 (km)"); ax.set_ylabel("밀도")
    ax.set_xlim(0, 16)
    ax.legend(loc="upper right", fontsize=FS, frameon=False)
    return save(fig, "ch14", "fig14-e-posthoc", mode)


def fig_r3(mode, R3):
    """실제 사료 RE11·RE12의 숫자만으로 그린 도식(좌표 없음): 府를 원점, 남쪽 경계 25리, 巽方 30리"""
    s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 3.3))
    fig.subplots_adjust(left=0.10, right=0.97, top=0.93, bottom=0.14)
    ax.set_xlim(-8, 40); ax.set_ylim(-36, 6); ax.set_aspect("equal")
    ax.set_xlabel("동쪽으로 (리)"); ax.set_ylabel("북(+)·남(-)으로 (리)")
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    ax.axhline(-25, color=("#c0392b" if mode == "color" else "#000000"), lw=1.3, ls="--")
    ax.text(-7.5, -24.0, "남쪽 경계 25리 (사경)", ha="left", va="bottom", fontsize=FS)
    ax.plot(0, 0, "^", color="black", ms=6, mfc="black" if mode == "color" else "white", mew=0.8, zorder=6)
    ax.annotate("府", (0, 0), xytext=(4, 3), textcoords="offset points", fontsize=FS)
    # 방위 부채꼴(손방 = 동남, 반폭 22.5도): 거리 27~33리
    for lo, hi, a in [(27, 33, 0.35)]:
        w = Wedge((0, 0), hi, -90 + 22.5 * 0 - 22.5 + 0, -90 + 22.5 + 0, width=hi - lo)
    # 방위각(북=0 시계) 112.5~157.5 -> 수학각(동=0 반시계) = 90 - 방위각 : -22.5 ~ -67.5
    w = Wedge((0, 0), 33, -67.5, -22.5, width=6, fc="#f0b45a" if mode == "color" else "#d0d0d0", ec=s["line"], lw=0.8, hatch="//" if mode == "bw" else None, zorder=3)
    ax.add_patch(w)
    # 정확한 손방 30리 점
    px, py = 30 * math.sin(math.radians(135)), -30 * -math.cos(math.radians(135))
    px = 30 * math.sin(math.radians(135)); py = 30 * math.cos(math.radians(135))
    ax.plot(px, py, "o", color="#c0392b" if mode == "color" else "black", ms=6, zorder=7)
    ax.annotate("손방 정확히 30리\n(남쪽으로 21.2리)", (px, py), xytext=(-7.5, -14), textcoords="data", fontsize=FS, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=s["line"], lw=0.6))
    th = R3["theta_min"]
    qx = 30 * math.sin(math.radians(th)); qy = 30 * math.cos(math.radians(th))
    ax.plot(qx, qy, "s", color="#1f6fb8" if mode == "color" else "white", mec="black", ms=6, zorder=7)
    ax.annotate(f"방위 {th:.1f}도, 30리면\n경계(25리)에 닿음", (qx, qy), xytext=(1, -33), textcoords="data", fontsize=FS, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=s["line"], lw=0.6))
    ax.text(-7.5, 3.5, "띠: 손방 ±22.5도, 27~33리", fontsize=FS, ha="left", va="center")
    return save(fig, "ch14", "fig14-f-pyeongyang-border", mode)


def fig_outlier(mode, V8):
    s = STY[mode]
    fig, axs = plt.subplots(2, 1, figsize=(WIDTH, 3.2), sharex=True, constrained_layout=True)
    for ax, (name, d) in zip(axs, V8.items()):
        v = np.array(d["v"])
        ax.axvspan(d["lo_f"], d["hi_f"], color="#cfe3f3" if mode == "color" else "#e8e8e8", alpha=0.9, lw=0)
        ax.axvline(d["mu"] + d["zc"] * d["sd"], color=s["truth"], lw=1.0, ls="--")
        ax.axvline(d["mu"] - d["zc"] * d["sd"], color=s["truth"], lw=1.0, ls="--")
        jit = np.linspace(-0.12, 0.12, len(v)) * (np.arange(len(v)) % 2 * 2 - 1)
        ax.plot(v, jit, "o", color="#222222" if mode == "color" else "black", ms=5, mfc="white", mew=1.0)
        ax.set_ylim(-0.6, 0.6); ax.set_yticks([])
        ax.set_title(name, fontsize=FS, loc="left")
        ax.set_xlim(10, 60)
    axs[1].set_xlabel("적은 거리 (리)")
    return save(fig, "ch14", "fig14-g-outlier-rules", mode)


def fig_sweep(mode, V5):
    s = STY[mode]
    xs, others, P, Tt, A2, B2 = V5["grid"]
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 2.8), constrained_layout=True)
    ax = axs[0]
    ax.set_xlim(0, 150); ax.set_ylim(0, 150); ax.set_aspect("equal"); ax.grid(color=s["grid"], lw=0.3, ls=":")
    ax.set_xticks(range(0, 151, 50)); ax.set_yticks(range(0, 151, 50)); ax.tick_params(labelsize=FS)
    ax.set_title("(가) 세 줄의 영역", fontsize=FS, loc="left")
    gx, gy = np.meshgrid(xs, xs)
    kw = dict(hatches=["//"]) if mode == "bw" else {}
    ax.contourf(gx, gy, others.astype(float), levels=[0.5, 1.5], colors=["#2e7d32" if mode == "color" else "#999999"], alpha=0.5 if mode == "color" else 0.35, **kw)
    ax.plot(*P, "^", color="black", ms=5, mfc="black" if mode == "color" else "white")
    ax.annotate("해진", P, xytext=(4, -4), textcoords="offset points", fontsize=FS, va="top")
    # 사흘 길 구간: 평지 가정 60~90 km 와 산길 포함 하루 길의 띠
    th = np.linspace(-22.5, 22.5, 60) * math.pi / 180
    for lo, hi, ls, lb in [(60, 90, "-", "하루 20~30 km"), (36, 90, ":", "하루 12~30 km")]:
        ax.plot(P[0] + hi * np.sin(th), P[1] + hi * np.cos(th), color="#c0392b" if mode == "color" else "black", ls=ls, lw=1.0)
        ax.plot(P[0] + lo * np.sin(th), P[1] + lo * np.cos(th), color="#c0392b" if mode == "color" else "black", ls=ls, lw=1.0)
    ax.plot(*Tt, "*", color=s["truth"], ms=9, mec="black", mew=0.5, zorder=7)
    ax = axs[1]
    lo_list = np.arange(10, 31, 1.0)
    # 하한을 바꿀 때 사흘 길 띠(3*lo ~ 3*30 km)와 두 줄 영역이 겹치는 넓이
    d = np.hypot(gx - P[0], gy - P[1]); b = (np.degrees(np.arctan2(gx - P[0], gy - P[1])) + 360) % 360
    secm = (np.abs((b - 0 + 180) % 360 - 180) <= 22.5)
    inter = []
    for lo in lo_list:
        r = (d >= 3 * lo) & (d <= 3 * 30) & secm
        inter.append((r & others).sum() * 0.25)
    ax.plot(lo_list, inter, "-o", color="#c0392b" if mode == "color" else "black", ms=3.5)
    ax.axvline(V5["lo_thresh"], color=s["gray"], lw=0.9, ls=":")
    ax.text(V5["lo_thresh"] + 0.4, max(inter) * 0.55, f"{V5['lo_thresh']:.1f}", fontsize=FS)
    ax.set_xlabel("하루 길 하한 (km)"); ax.set_ylabel("겹친 넓이 (km²)"); ax.set_title("(나) 하한을 낮추면", fontsize=FS, loc="left")
    return save(fig, "ch14", "fig14-h-travel-days", mode)


def figures(cases):
    out = []
    for mode in ("color", "bw"):
        out.append(fig_timeline(mode))
        out.append(fig_flow(mode))
        out.append(fig_v12(mode, cases["v1"], cases["v2"]))
        out.append(fig_ladder(mode, cases["v7"][0]))
        out.append(fig_posthoc(mode, cases["v6"]))
        out.append(fig_r3(mode, cases["r3"]))
        out.append(fig_outlier(mode, cases["v8"]))
        out.append(fig_sweep(mode, cases["v5"]))
    return out


def all_cases():
    return dict(v1=case_v1(), v2=case_v2(), v3=case_v3(), v4=case_v4(), v5=case_v5(), v6=case_v6(), v6b=case_v6b(), v7=case_v7(),
                v8=case_v8(), r2=case_r2(), r3=case_r3(), eq=eq_numbers(), more=eq_more())


if __name__ == "__main__":
    C = all_cases()
    import pprint
    for k, v in C.items():
        if k in ("v6",):
            print(k, {a: b for a, b in v.items() if a not in ("fixed_d", "best_d")})
        elif k == "v7":
            for st in v[0]: print("v7", st)
        elif k == "v3":
            print(k, {a: b for a, b in v.items() if a not in ("regs",)})
        elif k == "v5":
            print(k, {a: b for a, b in v.items() if a != "grid"})
        else:
            pprint.pprint({k: v}, width=140)
    if "--calc" not in sys.argv:
        for p in figures(C):
            print("saved", p)
