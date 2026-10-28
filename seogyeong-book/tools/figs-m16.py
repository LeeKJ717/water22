"""figs-m16.py - 16장(한반도 서북부, 지역 가설 H0) 새 그림과 새 사례 계산.
실행: python3 tools/figs-m16.py          (그림/ch16 에 컬러·흑백 PDF 생성)
      python3 tools/figs-m16.py --calc   (본문에 쓴 숫자만 출력)
이 파일의 계산 함수는 원고의 새 숫자의 근거이다.
- 실제 지리 값(평양 중심점, 대성산, 안학궁, 성곽 길이)은 영문 위키백과 항목에서 확인한 값이다(원고와 참고문헌/ch16.txt 참조).
- 가상 세계의 값(고을 이름, 좌표, 리 수, 점수)은 모두 연습용으로 만든 것이며 서경의 결과가 아니다.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
from figlib import *

FS = 8.5
CH = "ch16"

# ======================================================================= 실제 지리 값 (위키백과에서 확인)
P_CITY = (39 + 1 / 60, 125 + 44 / 60 + 51 / 3600)            # 영문 위키백과 Pyongyang 상자 39°01′00″N 125°44′51″E
T_PEAK = (39.07389, 125.82833)                                # 영문 위키백과 Taesongsan 상자 39°4′26″N 125°49′42″E (39.07389, 125.82833)
A_PAL1 = (39.0618, 125.8340)                                  # Anhakkung 인용 좌표 39°03′42″N 125°50′02″E (39.0618N 125.8340E)
A_PAL2 = (39 + 3 / 60 + 44.3 / 3600, 125 + 50 / 60 + 2.4 / 3600)  # Anhakkung 상자 39°03'44.3"N 125°50'02.4"E


def hav(a, b):
    """두 점(위도, 경도) 사이 거리(km)와 a에서 본 b의 방위각(북 0, 동 90)"""
    R = 6371.0088
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = 2 * R * math.asin(math.sqrt(math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))
    y = math.sin(lo2 - lo1) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(lo2 - lo1)
    return d, (math.degrees(math.atan2(y, x)) + 360) % 360


def enu(a, b):
    """a를 원점으로 한 b의 동·북 거리(km), 작은 범위의 평면 근사"""
    d, br = hav(a, b)
    return d * math.sin(math.radians(br)), d * math.cos(math.radians(br))


def calc_geo():
    out = {}
    for n, a, b in [("P-T", P_CITY, T_PEAK), ("P-A1", P_CITY, A_PAL1), ("P-A2", P_CITY, A_PAL2), ("T-A1", T_PEAK, A_PAL1),
                    ("T-A2", T_PEAK, A_PAL2), ("A1-A2", A_PAL1, A_PAL2)]:
        out[n] = hav(a, b)
    out["P"] = P_CITY; out["A2"] = A_PAL2
    out["cos"] = math.cos(math.radians(P_CITY[0]))
    out["kmlon"] = 111.32 * out["cos"]
    out["li"] = {u: [10 * u, out["P-A2"][0] / u] for u in (0.3, 0.4, 0.5)}
    # 안학궁 제원 자체 점검 (위키백과: 둘레 2,488 m, 한 변 622 m, 면적 380,000 m2)
    out["anhak_perim_check"] = 4 * 622
    out["anhak_area_check"] = 622 ** 2
    out["anhak_area_diff"] = (622 ** 2 - 380000) / 380000
    # 대성산성 둘레 두 값 (7,218 m, 7,076 m)
    out["fort_diff_m"] = 7218 - 7076
    out["fort_diff_pct"] = (7218 - 7076) / 7076
    out["fort_circle_area_km2"] = (7218 / 1000) ** 2 / (4 * math.pi)
    out["fort_circle_area_km2_b"] = (7076 / 1000) ** 2 / (4 * math.pi)
    out["anhak_area_km2"] = 0.38
    out["anhak_over_inner"] = 38 / 130          # 38만 m2 / 내성 130만 m2... 아래에서 단위 확인
    out["anhak_vs_changan"] = 0.38 / 11.85
    out["anhak_circle_perim"] = 2 * math.sqrt(math.pi * 0.38)
    return out


# ======================================================================= 연대·기저율
def calc_time():
    e = {"427-586": 586 - 427, "586-1081": 1081 - 586, "1081-1128": 1128 - 1081, "1128-1135": 1135 - 1128, "1135-1145": 1145 - 1135,
         "343-1145": 1145 - 343, "427-668": 668 - 427, "1145-1811": 1811 - 1145, "1811-1814": 1814 - 1811,
         "kimbusik_age_1135": 1135 - 1075, "kimbusik_age_1145": 1145 - 1075, "hanchiyun_age": 1814 - 1765, "yundusu_age_1588": 1588 - 1533,
         "yundusu_age_1592": 1592 - 1533, "dasan_age_1811": 1811 - 1762, "popper": 1959 - 1934, "wason-popper": 1960 - 1934,
         "1128-1811": 1811 - 1128, "1811-1902": 1902 - 1811}
    return e


def calc_bayes():
    """위키백과 '기저율'의 예: 1%, 100%, 20% -> 사후 4.8%"""
    pr, tp, fp = 0.01, 1.0, 0.20
    post = pr * tp / (pr * tp + (1 - pr) * fp)
    # 이 책의 연습: 두 지역 가설의 사전 확률 비 3:1(가상)과 우도비 1/4(가상)
    prior_odds = 3.0; lr = 1 / 4
    post_odds = prior_odds * lr
    post_p = post_odds / (1 + post_odds)
    # 사전 확률 1%인 가설이 우도비 20을 받으면
    po = (0.01 / 0.99) * 20
    return dict(post=post, naive=0.8, post_odds=post_odds, post_p=post_p, small_prior_post=po / (1 + po), small_prior_odds=po)


# ======================================================================= 가상 세계: 지역 가설의 주변 우도
STEP = 0.5
XS = np.arange(0, 60 + 1e-9, STEP)
GX, GY = np.meshgrid(XS, XS)
CELL = STEP * STEP
U_TRUE = 0.42


def dist(c):
    return np.hypot(GX - c[0], GY - c[1])


def bearing(c):
    return (np.degrees(np.arctan2(GX - c[0], GY - c[1])) + 360) % 360


def sector(c, brg, sd=20.0):
    """방위 서술의 우도: 적힌 방위에서 벗어난 각도의 가우스형(표준편차 20도). 8방위로 적었으므로 22.5도 안쪽을 가장 높게 본다."""
    diff = np.abs((bearing(c) - brg + 180) % 360 - 180)
    return np.exp(-0.5 * (diff / sd) ** 2)


def soft_ring(c, mu, sd):
    return np.exp(-0.5 * ((dist(c) - mu) / sd) ** 2)


def nearest8(b):
    return int(round(b / 45.0)) % 8 * 45.0


def box_mask(x0, x1, y0, y1):
    return ((GX >= x0) & (GX <= x1) & (GY >= y0) & (GY <= y1))


def make_world(T, refs, rel_sd=0.25, sec_sd=25.0):
    """가상 세계: 참 위치 T. 갑에 대해서는 거리만(5리 단위로 어림), 을에 대해서는 방위만(8방위) 적혀 있다고 하자."""
    L = np.ones(GX.shape)
    rows = []
    for k, (c, kind) in refs.items():
        d = math.hypot(T[0] - c[0], T[1] - c[1])
        b = (math.degrees(math.atan2(T[0] - c[0], T[1] - c[1])) + 360) % 360
        if kind == "거리":
            li = max(5, int(round(d / U_TRUE / 5.0)) * 5)
            mu = li * U_TRUE
            L = L * soft_ring(c, mu, rel_sd * mu)
            rows.append((k, c, "거리", d, li, None))
        else:
            b8 = nearest8(b)
            L = L * sector(c, b8, sec_sd)
            rows.append((k, c, "방위", d, None, b8))
    return L, rows


def region_stats(L, R):
    m = R
    return float(L[m].mean()), float(L[m].sum() * CELL), float(m.sum() * CELL)


REFS = {"갑": ((30.0, 34.0), "거리"), "을": ((30.0, 4.0), "방위")}
R0 = (30.0, 55.0, 8.0, 33.0)     # 통설 지역(가상 H0): 동 30~55, 북 8~33  (625 km2)
R1 = (4.0, 29.0, 34.0, 59.0)     # 대안 지역(가상 H1): 동 4~29, 북 34~59  (625 km2)
WORLD = {"가": (40.0, 22.0), "나": (15.0, 46.0), "다": (32.0, 30.0)}


def calc_region(T, shift=0.0):
    L, rows = make_world(T, REFS)
    r0 = (R0[0] + shift, R0[1] + shift, R0[2], R0[3])
    m0 = box_mask(*r0); m1 = box_mask(*R1)
    a0, s0, ar0 = region_stats(L, m0)
    a1, s1, ar1 = region_stats(L, m1)
    bf = a0 / a1 if a1 > 0 else float("inf")
    return dict(rows=rows, mean0=a0, mean1=a1, bf=bf, area0=ar0, area1=ar1, post0=bf / (1 + bf), L=L)


def calc_region_all():
    out = {}
    for k, T in WORLD.items():
        out[k] = calc_region(T)
        out["shift" + k] = {s: calc_region(T, s)["bf"] for s in (-10, -5, 0, 2, 4, 6)}
    return out


# ======================================================================= 확증 편향 모의
def calc_halo(N=200000, seed=16):
    rng = np.random.default_rng(seed)
    res = {}
    for m, label in ((-0.4, "H1참"), (0.4, "H0참")):
        x = rng.normal(m, 1.0, size=(N, 8))
        xs = np.sort(x, axis=1)      # 오름차순
        full = (x.sum(axis=1) > 0).mean()
        r = {"all": float(full)}
        for drop in (1, 2, 3):
            kept = xs[:, drop:]       # 가장 불리한(작은) drop개를 버림
            r[f"drop{drop}"] = float((kept.sum(axis=1) > 0).mean())
        res[label] = r
    # 같은 사람이 H1에 유리한 것만 버리는 반대 편향도 대칭이므로 따로 계산하지 않음
    return res


# ======================================================================= 순환 증거
def phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def calc_circular(sigma=3.0):
    n = 5
    h_naive = 1.96 * sigma / math.sqrt(n)
    # 기록 5건 중 4건이 한 통설 목록을 베낀 것(오차가 같이 따라옴), 1건은 독립
    var = (4 ** 2 + 1 ** 2) / n ** 2 * sigma ** 2
    sd = math.sqrt(var)
    neff = sigma ** 2 / var
    cov = 2 * phi(h_naive / sd) - 1
    h_right = 1.96 * sd
    # 계통 수로 센 값: 2
    h_lineage = 1.96 * sigma / math.sqrt(2)
    return dict(h_naive=h_naive, sd=sd, neff=neff, cov=cov, h_right=h_right, h_lineage=h_lineage)


# ======================================================================= 지형 서술의 변별력(가상)
RIVER = np.array([[0, 46], [15, 41], [30, 33], [45, 22], [60, 18]], float)   # 가상 하천: H1과 H0을 모두 지난다
PEAKS = [(14.0, 53.0), (24.0, 51.0), (50.0, 36.0)]


def dist_to_polyline(pts):
    d = np.full(GX.shape, 1e9)
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        vx, vy = x1 - x0, y1 - y0
        t = np.clip(((GX - x0) * vx + (GY - y0) * vy) / (vx * vx + vy * vy), 0, 1)
        d = np.minimum(d, np.hypot(GX - (x0 + t * vx), GY - (y0 + t * vy)))
    return d


def calc_terrain():
    dr = dist_to_polyline(RIVER)
    dm = np.min([dist(p) for p in PEAKS], axis=0)
    weak = dr <= 3.0                       # '강에 임한다'
    strong = (dr <= 3.0) & (dm >= 5.0) & (dm <= 15.0)   # '강에 임하고 산에 의지한다'
    m0 = box_mask(*R0); m1 = box_mask(*R1)
    out = {}
    for k, m in (("weak", weak), ("strong", strong)):
        f0 = float((m & m0).sum() / m0.sum()); f1 = float((m & m1).sum() / m1.sum())
        out[k] = dict(f0=f0, f1=f1, a0=float((m & m0).sum() * CELL), a1=float((m & m1).sum() * CELL))
    out["dr"] = dr; out["dm"] = dm; out["weak"]["mask"] = weak; out["strong"]["mask"] = strong
    return out


# ======================================================================= 이동시간 서술 '사흘 길'(가상)
def calc_travel():
    out = {}
    v_lo, v_hi = 25.0, 35.0           # km/일 (가정)
    days = 3
    d_lo, d_hi = v_lo * days, v_hi * days
    c_lo, c_hi = 1.2, 1.4             # 직선거리 대비 굽음 계수(가정)
    r_lo, r_hi = d_lo / c_hi, d_hi / c_lo
    out.update(d_lo=d_lo, d_hi=d_hi, r_lo=r_lo, r_hi=r_hi, ring=math.pi * (r_hi ** 2 - r_lo ** 2))
    out["ring_ratio"] = r_hi / r_lo
    # 배: 대동강 하구에서 평양까지 109 km (위키백과)
    out["boat"] = {v: 109.0 / v for v in (20.0, 30.0, 40.0)}
    out["walk_109"] = {v: 109.0 / v for v in (25.0, 30.0, 35.0)}
    return out


# ======================================================================= 눈 가린 검증
def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def binom_tail(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def calc_blind():
    out = {}
    for k, n in ((17, 20), (51, 60), (9, 10)):
        lo, hi = wilson(k, n)
        out[(k, n)] = dict(p=k / n, se=math.sqrt(k / n * (1 - k / n) / n), lo=lo, hi=hi)
    chance = 40.0 / 625.0
    out["chance"] = chance
    out["tail17"] = binom_tail(17, 20, chance)
    out["tail17_half"] = binom_tail(17, 20, 0.5)
    out["tail17_08"] = binom_tail(17, 20, 0.8)
    # 표본 크기: 표준오차 0.05 이하가 되려면
    out["n_need"] = 0.85 * 0.15 / 0.05 ** 2
    return out


# ======================================================================= 네 예측의 우도비 곱
def calc_pred():
    cases = {"모두 조금씩 맞음": (2.0, 1.5, 1.5, 2.0), "하나가 크게 틀림": (3.0, 2.0, 1.5, 0.05), "모두 중립": (1.0, 1.0, 1.0, 1.0),
             "넷 다 강하게 맞음": (4.0, 3.0, 2.0, 5.0)}
    out = {}
    for k, v in cases.items():
        p = 1.0
        for x in v:
            p *= x
        out[k] = dict(lr=v, prod=p, post_even=p / (1 + p), post_3to1=3 * p / (1 + 3 * p))
    return out


# ======================================================================= 거리 환산 (식 1)
def calc_dist_interval():
    out = {}
    for n_lo, n_hi, u_lo, u_hi in ((10, 15, 0.3, 0.5), (10, 10, 0.3, 0.5), (10, 15, 0.36, 0.48)):
        out[(n_lo, n_hi, u_lo, u_hi)] = (n_lo * u_lo, n_hi * u_hi)
    cos = math.cos(math.radians(P_CITY[0]))
    out["cos"] = cos
    out["dlon_per_km"] = 1 / (111.32 * cos)
    out["dlat_per_km"] = 1 / 111.2
    for d in (3.0, 4.0, 5.0, 7.5):
        out[("dlon", d)] = d / (111.32 * cos)
        out[("dlat", d)] = d / 111.2
    # 각도 부채꼴: 8방위의 폭은 45도, 전체의 비율
    out["sector_frac"] = 45 / 360
    return out


# ======================================================================= 사례 묶음 A·B의 추가 계산
def river_y(x):
    return float(np.interp(x, RIVER[:, 0], RIVER[:, 1]))


def calc_b1():
    """가상: 정현(10,38)에서 동쪽으로 칠십 리, 강 북쪽 기슭. 서술을 하나씩 더하며 평균 우도비 H0:H1를 본다."""
    c = (10.0, 38.0)
    mu = 70 * U_TRUE
    ring = soft_ring(c, mu, 0.25 * mu)
    east = sector(c, 90.0, 25.0)
    ry = np.interp(GX, RIVER[:, 0], RIVER[:, 1])
    dr = dist_to_polyline(RIVER)
    north_bank = ((GY > ry) & (dr <= 6.0)).astype(float)
    m0 = box_mask(*R0); m1 = box_mask(*R1)
    out = {"mu": mu, "sd": 0.25 * mu}
    steps = [("거리", ring), ("거리+동쪽", ring * east), ("거리+동쪽+강 북쪽", ring * east * north_bank)]
    for name, L in steps:
        a0 = float(L[m0].mean()); a1 = float(L[m1].mean())
        out[name] = dict(a0=a0, a1=a1, bf=(a0 / a1 if a1 > 0 else float("inf")), s0=float(L[m0].sum() * CELL), s1=float(L[m1].sum() * CELL))
    return out


def calc_b2():
    """가상: 갑(30,34)에서 하루 길. 하루 25~35 km, 굽음 계수 1.2~1.4 -> 직선 반경 [25/1.4, 35/1.2]"""
    c = (30.0, 34.0)
    r_lo, r_hi = 25.0 / 1.4, 35.0 / 1.2
    d = dist(c)
    ring = ((d >= r_lo) & (d <= r_hi))
    m0 = box_mask(*R0); m1 = box_mask(*R1)
    f0 = float((ring & m0).sum() / m0.sum()); f1 = float((ring & m1).sum() / m1.sum())
    return dict(r_lo=r_lo, r_hi=r_hi, area=math.pi * (r_hi ** 2 - r_lo ** 2), f0=f0, f1=f1, ratio=(f0 / f1 if f1 > 0 else float("inf")),
                a0=float((ring & m0).sum() * CELL), a1=float((ring & m1).sum() * CELL))


def calc_b3():
    """가상: 같은 이름 신성이 H0 안 (45,20)과 H1 안 (12,48)에 있다. 갑(30,34)에서 '삼십 리'"""
    c = (30.0, 34.0)
    mu = 30 * U_TRUE
    sd = 0.25 * mu
    pts = {"신성 가(H0)": (45.0, 20.0), "신성 나(H1)": (12.0, 48.0)}
    out = {"mu": mu, "sd": sd}
    for k, (x, y) in pts.items():
        d = math.hypot(x - c[0], y - c[1])
        out[k] = dict(d=d, L=math.exp(-0.5 * ((d - mu) / sd) ** 2))
    a, b = out["신성 가(H0)"]["L"], out["신성 나(H1)"]["L"]
    out["ratio"] = a / b
    out["post_a"] = a / (a + b)
    return out


def calc_b4():
    """가상: 필사본 하나는 삼십 리, 다른 하나는 이십 리. 오류 확률 eps를 섞은 우도"""
    c = (30.0, 34.0)
    cand = {"H0 후보": (41.0, 25.0), "H1 후보": (24.0, 41.0)}
    out = {}
    for k, (x, y) in cand.items():
        d = math.hypot(x - c[0], y - c[1])
        r = {"d": d}
        for li in (30, 20):
            mu = li * U_TRUE
            r[li] = math.exp(-0.5 * ((d - mu) / (0.25 * mu)) ** 2)
        out[k] = r
    res = {}
    for eps in (0.0, 0.1, 0.2, 0.5):
        L0 = (1 - eps) * out["H0 후보"][30] + eps * out["H0 후보"][20]
        L1 = (1 - eps) * out["H1 후보"][30] + eps * out["H1 후보"][20]
        res[eps] = dict(L0=L0, L1=L1, ratio=L0 / L1)
    out["res"] = res
    return out


def calc_b7():
    """같은 넓이(625 km2)의 원과 상자로 H0, H1를 정의했을 때 세 세계의 평균 우도비"""
    r = math.sqrt(625.0 / math.pi)
    c0 = ((R0[0] + R0[1]) / 2, (R0[2] + R0[3]) / 2); c1 = ((R1[0] + R1[1]) / 2, (R1[2] + R1[3]) / 2)
    mc0 = dist(c0) <= r; mc1 = dist(c1) <= r
    out = {"r": r, "area0": float(mc0.sum() * CELL), "area1": float(mc1.sum() * CELL)}
    for k, T in WORLD.items():
        L, rows = make_world(T, REFS)
        bf_box = float(L[box_mask(*R0)].mean() / L[box_mask(*R1)].mean())
        bf_circ = float(L[mc0].mean() / L[mc1].mean())
        out[k] = dict(box=bf_box, circ=bf_circ)
    return out


def calc_a():
    out = {}
    # A3: 리+척 (1리=n척 가정)
    out["chek"] = {n: 4.0 / n for n in (1000, 1500, 1800, 2000)}
    # A4: 평원왕 28년(586) -> 83년 -> 보장왕 27년(668)
    out["pw"] = dict(a=586, b=668, diff=668 - 586, incl=668 - 586 + 1, recorded=83)
    # A5: 사경 거리 31, 42, 25, 31
    out["sagyeong"] = dict(EW=31 + 42, NS=25 + 31)
    # A5: 동남 30리쯤 -> 25~35리 x 0.3~0.5 km, 부채꼴 45도
    r_lo, r_hi = 25 * 0.3, 35 * 0.5
    out["sonbang"] = dict(r_lo=r_lo, r_hi=r_hi, area=(45 / 360) * math.pi * (r_hi ** 2 - r_lo ** 2), ring=math.pi * (r_hi ** 2 - r_lo ** 2))
    # A6: 강가 1 km 이내, 강 길이 L km
    out["gangga"] = {L: 2 * 1.0 * L for L in (20.0, 40.0)}
    # A7: 4088 보, 가상 측정 둘레 4.9 km
    out["bo"] = dict(bo=4088, meas=4.9, m_per_bo=4900 / 4088)
    return out


def calc_all():
    return dict(geo=calc_geo(), time=calc_time(), bayes=calc_bayes(), region=calc_region_all(), halo=calc_halo(), circ=calc_circular(),
                terrain=calc_terrain(), travel=calc_travel(), blind=calc_blind(), pred=calc_pred(), dist=calc_dist_interval())


def print_calc():
    C = calc_all()
    print("== b1", calc_b1())
    print("== b2", calc_b2())
    print("== b3", calc_b3())
    print("== b4", calc_b4())
    print("== b7", calc_b7())
    print("== a", calc_a())
    g = C["geo"]
    print("== geo")
    for k in ("P-T", "P-A1", "P-A2", "T-A1", "T-A2", "A1-A2"):
        print(k, "%.3f km  방위 %.1f" % g[k])
    print("cos", g["cos"], "km/lon deg", g["kmlon"])
    for u, v in g["li"].items():
        print("u", u, "10li", v[0], "P-A2 in li", round(v[1], 1))
    print("anhak perim", g["anhak_perim_check"], "area", g["anhak_area_check"], "diff", round(g["anhak_area_diff"] * 100, 2), "%")
    print("fort diff", g["fort_diff_m"], round(g["fort_diff_pct"] * 100, 2), "%", "circle area", round(g["fort_circle_area_km2"], 3), round(g["fort_circle_area_km2_b"], 3))
    print("anhak vs changan", round(g["anhak_vs_changan"] * 100, 2), "%", "anhak/inner", round(0.38 / 1.30, 3), "perim circle", round(g["anhak_circle_perim"], 3))
    print("== time", C["time"])
    print("== bayes", C["bayes"])
    r = C["region"]
    for k in ("가", "나", "다"):
        print("region", k, "bf %.4g mean0 %.4g mean1 %.4g post0 %.4f" % (r[k]["bf"], r[k]["mean0"], r[k]["mean1"], r[k]["post0"]))
        for row in r[k]["rows"]:
            print("   ", row)
        print("   shift", {s: round(v, 3) for s, v in r["shift" + k].items()})
    print("== halo", C["halo"])
    print("== circ", C["circ"])
    t = C["terrain"]
    print("== terrain", {k: {kk: round(vv, 4) for kk, vv in t[k].items() if kk != "mask"} for k in ("weak", "strong")})
    print("== travel", C["travel"])
    print("== blind", C["blind"])
    print("== pred", C["pred"])
    print("== dist", C["dist"])
    return C


# ======================================================================= 그림 도구
def box(ax, x, y, w, h, text, mode, fc=None, ls="-", fs=FS, bold=False, hatch=None):
    s = STY[mode]
    fc = fc or ("#ffffff" if mode == "bw" else "#fdf3e1")
    p = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=fc, ec=s["line"], lw=0.9, ls=ls,
                       hatch=hatch, zorder=3)
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, zorder=4, fontweight="bold" if bold else "normal",
            bbox=dict(fc="white", ec="none", pad=1.5) if hatch else None)


def arrow(ax, x1, y1, x2, y2, mode, ls="-", lw=1.1):
    s = STY[mode]
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=s["line"], lw=lw, ls=ls, shrinkA=0, shrinkB=0), zorder=2)


def colors(mode):
    if mode == "color":
        return dict(A="#1f6fb8", B="#2e7d32", C="#c0392b", D="#8e44ad")
    return dict(A="#000000", B="#444444", C="#777777", D="#222222")


# ======================================================================= 그림 1: 연대기 종합
def _ev(ax, y, yr, tx, dy, text, mk, col, mode, va=None):
    """연대 표시 한 점: (해 yr, 선 위 높이 y)에서 글 위치 (tx, y+dy)로 지시선을 긋는다"""
    ax.plot([yr, tx], [y, y + dy], color=col, lw=0.7, zorder=2)
    ax.plot(yr, y, mk, ms=5, color=col if mode == "color" else "white", mec=col, mew=1.0, zorder=4)
    va = va or ("bottom" if dy > 0 else "top")
    ax.text(tx, y + dy, text, ha="center", va=va, fontsize=FS, linespacing=1.05)


def fig_timeline(mode):
    """연대기 종합 그림. 두 단: 위는 427~1150년, 아래는 1500~2020년. 가로축은 해이다."""
    s = STY[mode]
    c = colors(mode)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(WIDTH, 6.6), gridspec_kw=dict(height_ratios=[2.5, 4.3]))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.995, bottom=0.005, hspace=0.03)
    for ax in (ax1, ax2):
        ax.axis("off")
    # ----- 위 단 (427~1150)
    ax1.set_xlim(250, 1260); ax1.set_ylim(-4.2, 7.6)
    yA, yB = 3.0, -1.5
    ax1.plot([400, 1240], [yA, yA], color=c["A"], lw=2.0, ls="-")
    ax1.plot([400, 1240], [yB, yB], color=c["B"], lw=2.0, ls="--")
    ax1.text(256, yA - 0.4, "평양과 서경의 지명·사건", fontsize=FS, fontweight="bold", color=c["A"], ha="left", va="top")
    ax1.text(256, yB + 0.4, "사료의 편찬", fontsize=FS, fontweight="bold", color=c["B"], ha="left", va="bottom")
    for yr in (400, 600, 800, 1000, 1200):
        for y in (yA, yB):
            ax1.plot([yr, yr], [y - 0.12, y + 0.12], color=s["line"], lw=0.8)
        ax1.text(yr, 0.7, str(yr), ha="center", va="center", fontsize=FS, color=s["gray"])
    _ev(ax1, yA, 427, 470, 0.7, "427\n평양 천도", "o", c["A"], mode)
    _ev(ax1, yA, 586, 610, 2.4, "586\n장안성 이거", "o", c["A"], mode)
    _ev(ax1, yA, 1081, 1010, 0.7, "1081\n문종 35년 기사", "o", c["A"], mode)
    _ev(ax1, yA, 1128, 1090, 2.4, "1128\n묘청 서경천도론", "o", c["A"], mode)
    _ev(ax1, yA, 1135, 1195, 0.7, "1135\n묘청의 난", "o", c["A"], mode)
    _ev(ax1, yB, 1145, 1100, -0.7, "1145 삼국사기\n(1146년 설도 있음)", "s", c["B"], mode)
    ax1.text(256, -3.6, "343년 고국원왕 기사는 1145년 편찬본에 \"지금의 서경\"으로 실렸다", fontsize=FS, ha="left", va="center")
    # ----- 아래 단 (1500~2020)
    ax2.set_xlim(1470, 2075); ax2.set_ylim(-6.8, 10.6)
    yB2, yC2, yD2 = 7.5, 2.5, -3.0
    for y, col, ls in ((yB2, c["B"], "--"), (yC2, c["C"], "-."), (yD2, c["D"], ":")):
        ax2.plot([1500, 2060], [y, y], color=col, lw=2.0, ls=ls)
        for yr in range(1500, 2001, 100):
            ax2.plot([yr, yr], [y - 0.12, y + 0.12], color=s["line"], lw=0.8)
    ax2.text(1476, yB2 - 0.4, "사료와 연구", fontsize=FS, fontweight="bold", color=c["B"], ha="left", va="top")
    ax2.text(1476, yC2 + 0.4, "현대의 연구(연구서 재인용)", fontsize=FS, fontweight="bold", color=c["C"], ha="left", va="bottom")
    ax2.text(1476, yD2 + 0.4, "검증의 방법", fontsize=FS, fontweight="bold", color=c["D"], ha="left", va="bottom")
    for yr in range(1500, 2001, 100):
        ax2.text(yr, -6.3, str(yr), ha="center", va="center", fontsize=FS, color=s["gray"])
    _ev(ax2, yB2, 1588, 1595, 0.7, "1588~92\n윤두수와 평양", "s", c["B"], mode)
    _ev(ax2, yB2, 1811, 1740, 0.7, "1811\n아방강역고", "s", c["B"], mode)
    _ev(ax2, yB2, 1814, 1865, 0.7, "1814\n한치윤 사망", "s", c["B"], mode)
    _ev(ax2, yB2, 1902, 1965, 0.7, "1902경\n세키노", "s", c["B"], mode)
    _ev(ax2, yC2, 2004, 1978, -0.7, "2004\n다나카", "^", c["C"], mode)
    _ev(ax2, yC2, 2007, 2018, 0.7, "2007\n임기환", "^", c["C"], mode)
    _ev(ax2, yC2, 2020, 2046, -0.7, "2020\n기경량", "^", c["C"], mode)
    _ev(ax2, yD2, 1934, 1895, 0.7, "1934\n포퍼 독일어판", "D", c["D"], mode)
    _ev(ax2, yD2, 1959, 1995, 0.7, "1959\n영어판", "D", c["D"], mode)
    _ev(ax2, yD2, 1960, 2035, -0.7, "1960 웨이슨\n2-4-6 실험", "D", c["D"], mode)
    return save(fig, CH, "fig16-a-timeline", mode)


# ======================================================================= 그림 2: 실제 점 세 개와 10리의 눈금
def fig_scale(mode):
    """현대 평양 중심점, 대성산 정상, 안학궁 위치와, 중심점 둘레의 가정한 10리 원(3, 4, 5 km)"""
    from matplotlib.lines import Line2D
    s = STY[mode]
    c = colors(mode)
    fig, ax = plt.subplots(figsize=(WIDTH, 4.3))
    fig.subplots_adjust(left=0.10, right=0.97, top=0.97, bottom=0.12)
    ax.set_aspect("equal")
    pts = {"평양 중심점": P_CITY, "대성산 정상": T_PEAK, "안학궁": A_PAL2}
    xy = {k: enu(P_CITY, v) for k, v in pts.items()}
    hs = []
    for r, ls, lab in ((3.0, ":", "10리 = 3 km (1리 0.3 km 가정)"), (4.0, "--", "10리 = 4 km (1리 0.4 km 가정)"), (5.0, "-.", "10리 = 5 km (1리 0.5 km 가정)")):
        ax.add_patch(Circle((0, 0), r, fill=False, ls=ls, ec=c["B"], lw=1.3, zorder=2))
        hs.append(Line2D([0], [0], color=c["B"], ls=ls, lw=1.3, label=lab))
    mk = {"평양 중심점": ("o", c["A"]), "대성산 정상": ("^", c["C"]), "안학궁": ("s", c["D"])}
    off = {"평양 중심점": (-0.9, -0.95), "대성산 정상": (0.35, 0.15), "안학궁": (0.35, -1.0)}
    for k, (x, y) in xy.items():
        m, col = mk[k]
        ax.plot(x, y, m, ms=7, color=col if mode == "color" else "white", mec=col, mew=1.2, zorder=5)
        ax.annotate(k, (x, y), xytext=(x + off[k][0], y + off[k][1]), fontsize=FS, zorder=6, ha="left")
    (x0, y0), (x1, y1) = xy["평양 중심점"], xy["안학궁"]
    ax.plot([x0, x1], [y0, y1], color=s["line"], lw=0.8, zorder=3)
    ax.text((x0 + x1) / 2 - 0.2, (y0 + y1) / 2 + 0.2, "%.1f km" % hav(P_CITY, A_PAL2)[0], fontsize=FS, ha="right", va="bottom")
    (x0, y0), (x1, y1) = xy["안학궁"], xy["대성산 정상"]
    ax.plot([x0, x1], [y0, y1], color=s["line"], lw=0.8, zorder=3)
    ax.text(x0 - 0.2, (y0 + y1) / 2, "%.1f km" % hav(A_PAL2, T_PEAK)[0], fontsize=FS, ha="right", va="center")
    ax.set_xlim(-6, 11.5); ax.set_ylim(-6.0, 7.6)
    ax.set_xlabel("평양 중심점에서 동쪽으로 (km)"); ax.set_ylabel("북쪽으로 (km)")
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    ax.legend(handles=hs, loc="lower right", fontsize=8.5, frameon=True, framealpha=0.95)
    return save(fig, CH, "fig16-b-scale", mode)


# ======================================================================= 그림 3: 지역 가설의 주변 우도
def _panel(ax, mode, title, res, T, refs=True):
    s = STY[mode]
    L = res["L"]
    ax.set_xlim(0, 60); ax.set_ylim(0, 60); ax.set_aspect("equal")
    ax.imshow(np.where(L > 1e-3, L / L.max(), np.nan), origin="lower", extent=(0, 60, 0, 60), cmap=s["cmap"], vmin=0, vmax=1, alpha=0.9, zorder=1)
    for r, ls, lab in ((R0, "-", "H0"), (R1, "--", "H1")):
        ax.add_patch(Rectangle((r[0], r[2]), r[1] - r[0], r[3] - r[2], fill=False, ec=s["line"], lw=1.3, ls=ls, zorder=4))
        ax.text(r[0] + 1.0, r[3] - 1.0, lab, fontsize=FS, fontweight="bold", ha="left", va="top", zorder=6, bbox=dict(fc="white", ec="none", pad=0.6))
    if refs:
        for k, (c, _kind) in REFS.items():
            ax.plot(*c, "^", ms=5, color=s["ref"], mfc=s["ref"] if mode == "color" else "white", mew=0.8, zorder=5)
            ax.annotate(k, c, xytext=(3, 3), textcoords="offset points", fontsize=FS, zorder=6)
    ax.plot(*T, "*", ms=10, color=s["truth"], mec="black", mew=0.5, zorder=7)
    ax.set_title(title, loc="left", fontsize=9)
    ax.set_xticks(range(0, 61, 20)); ax.set_yticks(range(0, 61, 20))
    ax.set_xlabel("동 (km)"); ax.set_ylabel("북 (km)")


def fig_region(mode, C):
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 3.0), constrained_layout=True)
    rin, rout = C["region"]["가"], C["region"]["나"]
    _panel(axs[0], mode, "세계 가: 참 위치가 H0 안", rin, WORLD["가"])
    _panel(axs[1], mode, "세계 나: 참 위치가 H1 안", rout, WORLD["나"])
    axs[0].text(30, -13, "평균 우도비 H0:H1 = %s" % fmt_bf(rin["bf"]), fontsize=FS, ha="center", va="top", clip_on=False)
    axs[1].text(30, -13, "평균 우도비 H0:H1 = %s" % fmt_bf(rout["bf"]), fontsize=FS, ha="center", va="top", clip_on=False)
    return save(fig, CH, "fig16-c-region-bf", mode)


def fmt_bf(x):
    if x >= 100:
        return "%d" % round(x)
    if x >= 10:
        return "%.0f" % x
    if x >= 0.1:
        return "%.2f" % x
    return "%.4f" % x


# ======================================================================= 그림 4: 경계를 옮기면
def fig_shift(mode, C):
    s = STY[mode]
    c = colors(mode)
    fig, ax = plt.subplots(figsize=(WIDTH, 2.9))
    fig.subplots_adjust(left=0.12, right=0.97, top=0.93, bottom=0.17)
    xs = [-10, -5, 0, 2, 4, 6]
    y_in = [C["region"]["shift가"][x] for x in xs]
    y_edge = [C["region"]["shift다"][x] for x in xs]
    ax.plot(xs, y_in, "o-", color=c["A"], lw=1.6, label="세계 가 (참 위치가 H0 안쪽)", ms=5)
    ax.plot(xs, y_edge, "s--", color=c["C"], lw=1.6, label="세계 다 (참 위치가 H0 서쪽 변에서 2 km)", ms=5, mfc="white")
    ax.set_yscale("log")
    ax.axhline(1.0, color=s["gray"], lw=0.8, ls=":")
    ax.text(6.0, 1.0, "우도비 1(차이 없음)", fontsize=FS, ha="right", va="bottom", color=s["gray"])
    ax.set_xlabel("H0 경계 상자를 동쪽으로 옮긴 거리 (km, 음수는 서쪽)")
    ax.set_ylabel("평균 우도비 H0:H1 (로그 눈금)")
    ax.legend(loc="lower left", frameon=True, framealpha=0.95)
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    return save(fig, CH, "fig16-d-boundary", mode)


# ======================================================================= 그림 5: 확증 편향 모의
def fig_halo(mode, C):
    s = STY[mode]
    c = colors(mode)
    h = C["halo"]["H1참"]
    fig, ax = plt.subplots(figsize=(WIDTH, 3.0))
    fig.subplots_adjust(left=0.12, right=0.97, top=0.93, bottom=0.22)
    labs = ["증거 8개\n모두 사용", "불리한 것\n1개 버림", "불리한 것\n2개 버림", "불리한 것\n3개 버림"]
    vals = [h["all"], h["drop1"], h["drop2"], h["drop3"]]
    hatches = ["", "//", "xx", "\\\\"]
    cols = [c["A"], c["C"], c["C"], c["C"]] if mode == "color" else ["#ffffff", "#dddddd", "#bbbbbb", "#999999"]
    bars = ax.bar(range(4), vals, color=cols, edgecolor="black", lw=0.8)
    for b, hch in zip(bars, hatches):
        b.set_hatch(hch)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.012, "%.1f%%" % (100 * v), ha="center", va="bottom", fontsize=FS)
    ax.set_xticks(range(4)); ax.set_xticklabels(labs)
    ax.set_ylabel("H0이 맞다고 결론낸 비율")
    ax.set_ylim(0, 0.78)
    ax.grid(axis="y", color=s["grid"], lw=0.3, ls=":")
    return save(fig, CH, "fig16-e-halo", mode)


# ======================================================================= 그림 6: 눈 가린 검증의 신뢰구간
def fig_blind(mode, C):
    s = STY[mode]
    c = colors(mode)
    b = C["blind"]
    fig, ax = plt.subplots(figsize=(WIDTH, 2.7))
    fig.subplots_adjust(left=0.20, right=0.97, top=0.93, bottom=0.22)
    rows = [((9, 10), "10개 중 9개"), ((17, 20), "20개 중 17개"), ((51, 60), "60개 중 51개")]
    for i, (key, lab) in enumerate(rows):
        r = b[key]
        ax.plot([r["lo"], r["hi"]], [i, i], "-", color=c["A"], lw=2.2)
        ax.plot(r["p"], i, "o", color=c["A"] if mode == "color" else "white", mec=c["A"], mew=1.2, ms=6, zorder=4)
        ax.text(r["hi"] + 0.01, i, "%.2f~%.2f" % (r["lo"], r["hi"]), fontsize=FS, va="center", ha="left")
    ax.axvline(b["chance"], color=c["C"], lw=1.2, ls="--")
    ax.text(b["chance"] + 0.01, 2.45, "우연히 찍어 맞출 비율 %.2f" % b["chance"], fontsize=FS, color=c["C"], ha="left", va="center")
    ax.set_yticks(range(3)); ax.set_yticklabels([r[1] for r in rows])
    ax.set_xlim(0, 1.18); ax.set_ylim(-0.5, 2.8)
    ax.set_xlabel("적중 비율 (점은 관측값, 선은 윌슨 95% 구간)")
    ax.grid(axis="x", color=s["grid"], lw=0.3, ls=":")
    return save(fig, CH, "fig16-f-blind", mode)


# ======================================================================= 그림 7: 예측 네 개의 우도비 곱
def fig_pred(mode, C):
    s = STY[mode]
    c = colors(mode)
    p = C["pred"]
    names = ["모두\n조금씩 맞음", "넷 다\n강하게 맞음", "하나가\n크게 틀림"]
    keys = ["모두 조금씩 맞음", "넷 다 강하게 맞음", "하나가 크게 틀림"]
    fig, ax = plt.subplots(figsize=(WIDTH, 3.5))
    fig.subplots_adjust(left=0.12, right=0.97, top=0.95, bottom=0.34)
    x = np.arange(len(keys)); w = 0.18
    labels = ["예측 1 거리·방위", "예측 2 지형", "예측 3 이동시간", "예측 4 이름·시기"]
    cols = [c["A"], c["B"], c["D"], c["C"]] if mode == "color" else ["#ffffff", "#cccccc", "#888888", "#333333"]
    hs = ["", "//", "..", "xx"]
    for j in range(4):
        vals = [p[k]["lr"][j] for k in keys]
        bars = ax.bar(x + (j - 1.5) * w, vals, w, color=cols[j], edgecolor="black", lw=0.7, label=labels[j], hatch=hs[j])
    ax.set_yscale("log")
    ax.axhline(1.0, color=s["gray"], lw=0.9, ls=":")
    for i, k in enumerate(keys):
        ax.text(i, 8.5, "곱 = %.2f" % p[k]["prod"], ha="center", fontsize=FS, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(names)
    ax.set_ylim(0.03, 14)
    ax.set_ylabel("우도비 (로그 눈금)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), frameon=False, fontsize=8.5, ncol=2)
    ax.grid(axis="y", color=s["grid"], lw=0.3, ls=":")
    return save(fig, CH, "fig16-g-pred", mode)


# ======================================================================= 그림 8: 지형 서술의 변별력
def fig_terrain(mode, C):
    s = STY[mode]
    c = colors(mode)
    t = C["terrain"]
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 3.0), constrained_layout=True)
    for ax, key, title in ((axs[0], "weak", "서술 하나: 강에 임한다"), (axs[1], "strong", "서술 둘: 강에 임하고 산 가까이")):
        ax.set_xlim(0, 60); ax.set_ylim(0, 60); ax.set_aspect("equal")
        m = t[key]["mask"].astype(float)
        ax.imshow(np.where(m > 0, 1.0, np.nan), origin="lower", extent=(0, 60, 0, 60), cmap=s["cmap"], vmin=0, vmax=1.3, zorder=1)
        ax.plot(RIVER[:, 0], RIVER[:, 1], color=s["river"], ls=s["river_ls"], lw=1.2, zorder=3)
        for p in PEAKS:
            ax.plot(*p, "^", ms=6, color=s["ref"], mfc=s["ref"] if mode == "color" else "white", zorder=5)
        for r, ls, lab in ((R0, "-", "H0"), (R1, "--", "H1")):
            ax.add_patch(Rectangle((r[0], r[2]), r[1] - r[0], r[3] - r[2], fill=False, ec=s["line"], lw=1.3, ls=ls, zorder=4))
            ax.text(r[0] + 1.0, r[3] - 1.0, lab, fontsize=FS, fontweight="bold", ha="left", va="top", zorder=6, bbox=dict(fc="white", ec="none", pad=0.6))
        ax.set_title(title, loc="left", fontsize=8.5)
        ax.set_xticks(range(0, 61, 20)); ax.set_yticks(range(0, 61, 20))
        ax.set_xlabel("동 (km)")
        if ax is axs[0]:
            ax.set_ylabel("북 (km)")
        ax.text(30, -14, "H0 안 %.0f%%, H1 안 %.0f%%" % (100 * t[key]["f0"], 100 * t[key]["f1"]), fontsize=FS, ha="center", va="top", clip_on=False)
    return save(fig, CH, "fig16-h-terrain", mode)


def figures(C):
    out = []
    for mode in ("color", "bw"):
        out.append(fig_timeline(mode))
        out.append(fig_scale(mode))
        out.append(fig_region(mode, C))
        out.append(fig_shift(mode, C))
        out.append(fig_halo(mode, C))
        out.append(fig_blind(mode, C))
        out.append(fig_pred(mode, C))
        out.append(fig_terrain(mode, C))
    return out


if __name__ == "__main__":
    C = print_calc() if "--calc" in sys.argv else calc_all()
    if "--calc" not in sys.argv:
        for p in figures(C):
            print(p)
