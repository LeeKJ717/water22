"""figs-m19.py - 19장(만주) 새 그림과 새 사례 계산.
실행: python3 tools/figs-m19.py          (그림/ch19 에 컬러·흑백 PDF 생성, 계산값 출력)
      python3 tools/figs-m19.py --calc   (계산값만 출력)
이 파일의 계산 함수는 원고의 새 숫자의 근거이다.
실제 좌표는 위키백과 상자의 값(원고 참고문헌 참조)이고, 가상 세계의 숫자는 서경의 결과가 아니다.
"""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from figlib import *

FS = 8.5
R_EARTH = 6371.0088


# ======================================================================= 실제 좌표와 거리
def dms(d, m=0, s=0):
    return d + m / 60 + s / 3600


PLACES = {   # (북위, 동경) 위키백과 상자(원고 참고문헌)의 값
    "평양": (dms(39, 1, 0), dms(125, 44, 51)),
    "임강": (dms(41, 49), dms(126, 55)),
    "대동": (dms(40, 5, 49), dms(113, 22, 1)),
    "천지남": (dms(41, 58, 8), dms(128, 4, 24)),     # 압록강 발원(상자)
    "압록하구": (dms(39, 52), dms(124, 19)),          # 압록강 하구(상자)
}


def hav(a, b):
    la1, lo1 = map(math.radians, a)
    la2, lo2 = map(math.radians, b)
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R_EARTH * math.asin(math.sqrt(h))


FR = {"서북": (124.0, 128.6, 37.4, 41.6), "요하": (119.5, 125.5, 39.4, 43.6),
      "산동": (114.5, 122.9, 34.2, 38.9), "만주": (121.0, 132.0, 41.0, 47.0)}   # 4부 지역 지도의 틀(regionmapsv1.py)


def rect_area(l1, l2, p1, p2):
    return R_EARTH ** 2 * math.radians(l2 - l1) * (math.sin(math.radians(p2)) - math.sin(math.radians(p1)))


def real_calc(verbose=True):
    out = {}
    D = {}
    for k, (a, b) in {"평양-임강": ("평양", "임강"), "평양-대동": ("평양", "대동"), "임강-대동": ("임강", "대동"),
                     "임강-하구": ("임강", "압록하구"), "발원-하구": ("천지남", "압록하구"), "평양-하구": ("평양", "압록하구"),
                     "발원-임강": ("천지남", "임강")}.items():
        D[k] = hav(PLACES[a], PLACES[b])
    out["dist"] = D
    out["sinuosity"] = {"790": 790 / D["발원-하구"], "795": 795 / D["발원-하구"]}
    li830 = {u: 830 * u for u in (0.36, 0.42, 0.48)}
    out["li830"] = li830
    out["need_sin"] = {u: li830[u] / D["임강-하구"] for u in li830}
    A = {k: rect_area(*v) for k, v in FR.items()}
    out["area"] = A
    out["rel_ml"] = {k: A["서북"] / A[k] for k in A}          # 서북=1로 놓은 주변 우도의 상대값(증거 영역이 같을 때)
    l1, l2, p1, p2 = FR["만주"]
    lm, pm = (l1 + l2) / 2, (p1 + p2) / 2
    out["quad"] = [rect_area(l1, lm, p1, pm), rect_area(lm, l2, p1, pm), rect_area(l1, lm, pm, p2), rect_area(lm, l2, pm, p2)]
    # 서북 창과 만주 창의 겹침: 위도 41.0~41.6, 경도 124.0~128.6
    out["overlap_NW_M"] = rect_area(124.0, 128.6, 41.0, 41.6)
    out["in_window"] = {n: {k: (v[2] <= PLACES[n][0] <= v[3] and v[0] <= PLACES[n][1] <= v[1]) for k, v in FR.items()} for n in ("평양", "임강", "대동")}
    out["lat_margin_LJ_NW"] = PLACES["임강"][0] - FR["서북"][3]
    import datetime as dt
    out["ice"] = {"짧게": (dt.date(2002, 3, 1) - dt.date(2001, 11, 20)).days, "길게": (dt.date(2002, 3, 31) - dt.date(2001, 11, 30)).days}
    out["kuju"] = {"11월 1일": (dt.date(1019, 3, 10) - dt.date(1018, 11, 1)).days, "12월 31일": (dt.date(1019, 3, 10) - dt.date(1018, 12, 31)).days}
    if verbose:
        print("== 실제 좌표 계산")
        for k, v in PLACES.items():
            print(" ", k, round(v[0], 4), round(v[1], 4))
        for k, v in D.items():
            print(" 거리", k, round(v, 1), "km")
        print(" 꼬불꼬불 정도(압록강 길이/발원-하구 직선)", {k: round(v, 3) for k, v in out["sinuosity"].items()})
        print(" 830리", {k: round(v, 1) for k, v in li830.items()}, "필요한 굽이 지수", {k: round(v, 3) for k, v in out["need_sin"].items()})
        print(" 창 면적", {k: round(v) for k, v in A.items()})
        print(" 서북=1 상대 우도", {k: round(v, 3) for k, v in out["rel_ml"].items()})
        print(" 만주 1/4 면적", [round(q) for q in out["quad"]], "합", round(sum(out["quad"])), "만주 면적/1/4", [round(A['만주'] / q, 3) for q in out["quad"]])
        print(" 서북-만주 창 겹침 면적", round(out["overlap_NW_M"]), "만주 대비", round(out["overlap_NW_M"] / A["만주"], 4), "서북 대비", round(out["overlap_NW_M"] / A["서북"], 4))
        print(" 점이 든 창", out["in_window"], "임강 위도가 서북 창 위끝보다", round(out["lat_margin_LJ_NW"], 3), "도 위")
        print(" 결빙 일수", out["ice"], {k: round(v / 365, 3) for k, v in out["ice"].items()}, "구주까지", out["kuju"])
    return out


# ======================================================================= 가상 세계: 강 건너 사흘 길
XMAX, YMAX = 200, 160
STEP = 1.0
XS = np.arange(0, XMAX + 1e-9, STEP)
YS = np.arange(0, YMAX + 1e-9, STEP)
GX, GY = np.meshgrid(XS, YS)
CELL = STEP * STEP
S0 = (60.0, 25.0)      # 가상 읍
RIVER_Y = 60.0         # 가상 강(동서로 곧은 선)
L_LO, L_HI = 90.7, 151.1   # 사흘 길의 평지 환산(8장 단위 환산표)


def dist_to(c):
    return np.hypot(GX - c[0], GY - c[1])


def bearing_from(c):
    return (np.degrees(np.arctan2(GX - c[0], GY - c[1])) + 360) % 360


def sector_mask(c, brg, half):
    b = bearing_from(c)
    return np.abs((b - brg + 180) % 360 - 180) <= half


def ford_cases(fords, lo=L_LO, hi=L_HI, brg=45.0, half=22.5):
    north = GY > RIVER_Y
    sec = sector_mask(S0, brg, half) & north
    win = dist_to(S0)
    summer = np.full(GX.shape, np.inf)
    for f in fords:
        summer = np.minimum(summer, math.hypot(S0[0] - f[0], S0[1] - f[1]) + dist_to(f))
    m_w = sec & (win >= lo) & (win <= hi)
    m_s = sec & (summer >= lo) & (summer <= hi)
    return m_s, m_w, summer, win


def area_of(m):
    return float(m.sum() * CELL)


def case_ice(verbose=True):
    fords = [(30.0, RIVER_Y), (170.0, RIVER_Y)]
    m_s, m_w, summer, win = ford_cases(fords)
    u = m_s | m_w
    both = m_s & m_w
    res = {"summer": area_of(m_s), "winter": area_of(m_w), "union": area_of(u), "both": area_of(both)}
    # 나루가 하나일 때, 나루의 위치(동서)에 따른 변화
    by_n = {}
    for xf in range(20, 181, 10):
        a_s, a_w, _, _ = ford_cases([(float(xf), RIVER_Y)])
        by_n[xf] = (area_of(a_s), area_of(a_w), area_of(a_s | a_w), area_of(a_s & a_w))
    res["by_n"] = by_n
    # 두 예시 점: 여름 길에서만 맞는 점 Ta, 겨울 길에서만 맞는 점 Tb
    ex = {}
    for nm, T in (("Ta", (120.0, 88.0)), ("Tb", (135.0, 100.0))):
        st = math.hypot(T[0] - S0[0], T[1] - S0[1])
        via = {f: math.hypot(S0[0] - f[0], S0[1] - f[1]) + math.hypot(f[0] - T[0], f[1] - T[1]) for f in fords}
        ex[nm] = {"T": T, "straight": st, "via": via, "best": min(via.values()),
                  "bearing": (math.degrees(math.atan2(T[0] - S0[0], T[1] - S0[1])) + 360) % 360}
    res["ex"] = ex
    if verbose:
        print("== 가상 사례: 강 건너 사흘 길")
        print(" 면적", {k: round(v, 1) for k, v in res.items() if k in ("summer", "winter", "union", "both")})
        print(" 합집합/겨울", round(res["union"] / res["winter"], 3), "합집합/여름", round(res["union"] / res["summer"], 3), "겹침/합집합", round(res["both"] / res["union"], 3))
        for n, v in by_n.items():
            print("  나루 x=", n, [round(x, 1) for x in v], "합/겨울", round(v[2] / v[1], 3), "여름/겨울", round(v[0] / v[1], 3))
        for nm, e in ex.items():
            print(" 예시", nm, e["T"], "직선", round(e["straight"], 2), "나루 경유", {k: round(v, 2) for k, v in e["via"].items()}, "최소", round(e["best"], 2), "방위", round(e["bearing"], 1))
    return res, (fords, m_s, m_w)


# ======================================================================= 가상 사례: 지역 크기
def case_region_size(real, verbose=True):
    A = real["area"]
    L0E = 400.0   # 가상 증거 영역 400 km^2
    ml = {k: L0E / A[k] for k in A}
    # 사전 확률과 사후 확률(증거 영역이 어느 창에든 들어간다고 가정하지 않고, 서북 창 안이라고 가정)
    prior = {k: 0.25 for k in A}
    # 증거 영역이 서북 창 안에 있고 다른 창에는 없다: 다른 창의 주변 우도는 증거 영역 일부만 포함
    res = {"ml_in_all": ml}
    # 증거 영역이 두 창의 겹침에 있다고 하자 (서북+만주)
    ml2 = {"서북": L0E / A["서북"], "만주": L0E / A["만주"]}
    z = ml2["서북"] * 0.5 + ml2["만주"] * 0.5
    res["post_overlap"] = {k: ml2[k] * 0.5 / z for k in ml2}
    res["ratio_overlap"] = ml2["서북"] / ml2["만주"]
    # 하위 구역 분할: 증거가 북동 1/4 안에 있다고 하자
    q = real["quad"]
    sub_ml = [L0E / qq for qq in q]
    res["quad_ml"] = sub_ml
    res["whole_ml"] = L0E / A["만주"]
    # 분할 전체 가설의 주변 우도 = 하위 구역 우도의 사전 가중 평균 (사전 1/4씩 아님; 면적 비례 사전)
    w = [qq / A["만주"] for qq in q]
    res["quad_prior_area"] = w
    # 증거가 하위 구역 하나(북서 1/4: index 2)에만 있다
    # 하위 구역 가설의 주변 우도: 증거 영역이 그 구역 안이면 L0E/q, 아니면 0
    res["whole_from_sub"] = sum(wi * (L0E / qq if i == 2 else 0.0) for i, (wi, qq) in enumerate(zip(w, q)))
    if verbose:
        print("== 가상 사례: 지역 크기 효과 (증거 영역 400 km^2)")
        print(" 주변 우도(상대) ∝ 400/면적", {k: f"{v:.3e}" for k, v in ml.items()})
        print(" 창 면적비 만주/서북", round(A["만주"] / A["서북"], 3), "서북 우도/만주 우도", round(res["ratio_overlap"], 3))
        print(" 겹침에 증거: 사후(무차별 사전 2가설)", {k: round(v, 4) for k, v in res["post_overlap"].items()})
        print(" 하위 구역 우도 400/면적", [f"{v:.3e}" for v in sub_ml], "전체", f"{res['whole_ml']:.3e}", "하위/전체", [round(v / res['whole_ml'], 3) for v in sub_ml])
        print(" 면적비례 사전으로 하위를 합치면(증거가 구역 3에만)", f"{res['whole_from_sub']:.3e}", "==전체", abs(res['whole_from_sub'] - res['whole_ml']) < 1e-12)
    return res


# ======================================================================= 가상 사례: 같은 이름의 세 층
def case_layers(verbose=True):
    # 세 시대의 가상 '신주(新州)': 시대별 위치와 시대별 기준 지명
    sites = {"갑": (40.0, 40.0), "을": (95.0, 95.0), "병": (150.0, 40.0)}
    refs = {"갑": (10.0, 70.0), "을": (60.0, 130.0), "병": (185.0, 80.0)}
    u_lo, u_hi = 0.36, 0.48
    res = {}
    regions = {}
    for k in sites:
        d = math.hypot(sites[k][0] - refs[k][0], sites[k][1] - refs[k][1])
        li = round(d / 0.42 / 10) * 10          # 십 리 단위로 어림
        lo, hi = li * 0.9 * u_lo, li * 1.1 * u_hi
        m = (dist_to(refs[k]) >= lo) & (dist_to(refs[k]) <= hi)
        regions[k] = m
        res[k] = {"d": d, "li": li, "lo": lo, "hi": hi, "area": area_of(m), "has": bool(m[int(sites[k][1] / STEP), int(sites[k][0] / STEP)])}
    inter = regions["갑"] & regions["을"] & regions["병"]
    pair = {"갑을": area_of(regions["갑"] & regions["을"]), "을병": area_of(regions["을"] & regions["병"]), "갑병": area_of(regions["갑"] & regions["병"])}
    res["inter"] = area_of(inter)
    res["pair"] = pair
    res["union"] = area_of(regions["갑"] | regions["을"] | regions["병"])
    res["sum"] = sum(res[k]["area"] for k in sites)
    if verbose:
        print("== 가상 사례: 같은 이름의 세 층")
        for k in sites:
            print(" ", k, {kk: (round(v, 2) if isinstance(v, float) else v) for kk, v in res[k].items()})
        print(" 세 영역의 교집합", res["inter"], "쌍", pair, "합집합", res["union"], "세 면적 합", round(res["sum"], 1))
    return res, (sites, refs, regions)


# ======================================================================= 가상 사례: 지형 서술
def case_terrain(verbose=True):
    xr = XS
    yr = 60 + 8 * np.sin(2 * np.pi * xr / 80)          # 가상 강
    ym = 80 + 10 * np.sin(2 * np.pi * xr / 120 + 1.0)   # 가상 능선
    # 칸에서 강까지의 수직 거리 근사: 같은 x에서의 차이(강이 완만하므로 근사)
    dr = np.abs(GY - yr[None, :])
    near_river = dr <= 3.0
    foot = (GY <= ym[None, :]) & (GY >= ym[None, :] - 8.0)       # 능선 남쪽 8 km 띠
    both = near_river & foot
    res = {"river": area_of(near_river), "foot": area_of(foot), "both": area_of(both), "total": XMAX * YMAX * 1.0}
    # 강의 옛 물길이 2 km 북쪽이었다면
    dr2 = np.abs(GY - (yr[None, :] + 2.0))
    both2 = (dr2 <= 3.0) & foot
    res["both_shift"] = area_of(both2)
    # 두 서술을 모두 만족하는 칸이 서로 이어진 조각 수
    from scipy import ndimage
    lab, n = ndimage.label(both)
    res["pieces"] = int(n)
    res["piece_sizes"] = sorted([int((lab == i).sum()) for i in range(1, n + 1)], reverse=True)
    if verbose:
        print("== 가상 사례: 지형 서술")
        print(" ", {k: (round(v, 1) if isinstance(v, float) else v) for k, v in res.items()})
    return res, (yr, ym, near_river, foot, both)


# ======================================================================= 가상 사례: 배로 닷새
def case_boat(verbose=True):
    xs = np.linspace(0, 500, 5001)
    ys = 60 + 8 * np.sin(2 * np.pi * xs / 90)
    seg = np.hypot(np.diff(xs), np.diff(ys))
    arc = np.concatenate([[0], np.cumsum(seg)])
    L = arc[-1]
    x0 = 200.0
    i0 = int(np.argmin(np.abs(xs - x0)))
    VD, VU = 40.0, 20.0     # 가정: 하루 길 (하류, 상류) km/일
    days_lo, days_hi = 4.0, 6.0
    d_dn = (days_lo * VD, days_hi * VD)
    d_up = (days_lo * VU, days_hi * VU)

    def pos_at(s):
        j = int(np.argmin(np.abs(arc - (arc[i0] + s))))
        return float(xs[j]), float(ys[j])
    res = {"length": float(L), "wiggle": float(L / 500.0), "down": d_dn, "up": d_up}
    res["down_x"] = (pos_at(d_dn[0])[0], pos_at(d_dn[1])[0])
    res["up_x"] = (pos_at(-d_up[1])[0], pos_at(-d_up[0])[0])
    res["straight_down"] = (res["down_x"][0] - x0, res["down_x"][1] - x0)
    res["straight_up"] = (x0 - res["up_x"][1], x0 - res["up_x"][0])
    if verbose:
        print("== 가상 사례: 배로 닷새")
        print(" 강 길이/직선 500 km", round(res["wiggle"], 4), "길이", round(res["length"], 1))
        print(" 하류 물길", d_dn, "동쪽 x", [round(v, 1) for v in res["down_x"]], "직선", [round(v, 1) for v in res["straight_down"]])
        print(" 상류 물길", d_up, "서쪽 x", [round(v, 1) for v in res["up_x"]], "직선", [round(v, 1) for v in res["straight_up"]])
    return res


# ======================================================================= 윌슨 구간, 판정표 계산
def wilson(k, n, z=1.96):
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


def case_wilson(verbose=True):
    rows = []
    for k, n in [(3, 4), (6, 8), (15, 20), (60, 80)]:
        lo, hi = wilson(k, n)
        rows.append((k, n, k / n, lo, hi, hi - lo))
    if verbose:
        print("== 윌슨 구간 (적중률 0.75)")
        for r in rows:
            print("  k=%d n=%d p=%.2f [%.3f, %.3f] 폭 %.3f" % r)
        for k, n in [(4, 5), (3, 4), (0, 4), (4, 4)]:
            print("  ", k, n, [round(v, 3) for v in wilson(k, n)])
    return rows


def case_posterior(real, verbose=True):
    L = {"H0": 8.0e-4, "H1": 1.0e-4, "H2": 0.5e-4, "H3": 0.5e-4}
    pri_u = {k: 0.25 for k in L}
    pri_c = {"H0": 0.70, "H1": 0.10, "H2": 0.10, "H3": 0.10}

    def post(Lm, pri):
        z = sum(Lm[k] * pri[k] for k in Lm)
        return {k: Lm[k] * pri[k] / z for k in Lm}
    out = {}
    # 시나리오 1: 증거가 없다 (모두 같은 우도)
    Leq = {k: 1.0 for k in L}
    out["none_u"] = post(Leq, pri_u)
    out["none_c"] = post(Leq, pri_c)
    # 시나리오 2: 만주만 증거 없음을 0으로 잘못 넣었다
    Lbad = dict(L)
    Lbad["H3"] = 0.0
    out["bad_u"] = post(Lbad, pri_u)
    # 시나리오 3: 같은 증거 영역이 서북 창과 만주 창 밖 어디에도 없다 → 모두 0 → 계산 불가
    # 시나리오 4: 증거 영역이 겹침 띠에 있을 때 면적 효과만으로 생기는 비
    A = real["area"]
    Lov = {"H0": 400.0 / A["서북"], "H3": 400.0 / A["만주"]}
    z = Lov["H0"] * 0.5 + Lov["H3"] * 0.5
    out["ov"] = {k: Lov[k] * 0.5 / z for k in Lov}
    # 창을 20% 넓혔을 때 (면적 1.2배는 아니고 변 1.2배 → 면적 1.44배): 만주 창 가설 우도는 1/1.44
    out["scale"] = {"변": 1.2, "면적": 1.2 ** 2, "우도비": 1 / 1.2 ** 2}
    if verbose:
        print("== 사후 확률 시나리오")
        for k, v in out.items():
            print(" ", k, {kk: round(vv, 4) for kk, vv in v.items()} if isinstance(v, dict) else v)
    return out


def all_calc(verbose=True):
    real = real_calc(verbose)
    ice, _ = case_ice(verbose)
    reg = case_region_size(real, verbose)
    lay, _ = case_layers(verbose)
    ter, _ = case_terrain(verbose)
    boat = case_boat(verbose)
    wil = case_wilson(verbose)
    post = case_posterior(real, verbose)
    rings = case_rings(verbose)
    return dict(rings=rings, real=real, ice=ice, reg=reg, lay=lay, ter=ter, boat=boat, wil=wil, post=post)




# ======================================================================= 가상 사례: 서술이 늘면 영역이 줄어든다
def case_rings(verbose=True):
    """가상 읍 하나(참 위치 (100, 80))와 서로 다른 기준 지명 셋에서 잰 거리 서술. 방위는 없다."""
    from scipy import ndimage
    site = (100.0, 80.0)
    refs = [(60.0, 40.0), (150.0, 30.0), (120.0, 140.0)]
    u_lo, u_hi = 0.36, 0.48
    masks, info = [], []
    for r in refs:
        d = math.hypot(site[0] - r[0], site[1] - r[1])
        li = round(d / 0.42 / 10) * 10
        lo, hi = li * 0.9 * u_lo, li * 1.1 * u_hi
        m = (dist_to(r) >= lo) & (dist_to(r) <= hi)
        masks.append(m)
        info.append({"d": d, "li": li, "lo": lo, "hi": hi, "area": area_of(m)})
    cum = masks[0].copy()
    seq = [area_of(cum)]
    pieces = [int(ndimage.label(cum)[1])]
    for m in masks[1:]:
        cum = cum & m
        seq.append(area_of(cum))
        pieces.append(int(ndimage.label(cum)[1]))
    holds = bool(cum[int(site[1] / STEP), int(site[0] / STEP)])
    res = {"info": info, "seq": seq, "pieces": pieces, "holds": holds, "total": XMAX * YMAX * 1.0}
    if verbose:
        print("== 가상 사례: 서술이 늘면 영역이 줄어든다")
        for i in info:
            print("  ", {k: round(v, 2) for k, v in i.items()})
        print("  누적 교집합 넓이", seq, "조각 수", pieces, "참 위치 포함", holds)
        print("  전체 대비", [round(v / res["total"], 4) for v in seq], "첫 영역 대비", [round(v / seq[0], 4) for v in seq])
    return res


# ======================================================================= 장 끝 식과 연습 문제의 숫자
def flat_dist(a, b):
    """평면 근사: 위도 1도 111.2 km, 경도 1도 111.32*cos(평균 위도) km"""
    dphi = b[0] - a[0]
    dlam = b[1] - a[1]
    mid = (a[0] + b[0]) / 2
    dy = 111.2 * dphi
    dx = 111.32 * math.cos(math.radians(mid)) * dlam
    return dphi, dlam, mid, math.cos(math.radians(mid)), dx, dy, math.hypot(dx, dy)


def formula_calc(real, verbose=True):
    out = {}
    out["flat_PL"] = flat_dist(PLACES["평양"], PLACES["임강"])
    out["flat_PM"] = flat_dist(PLACES["평양"], PLACES["압록하구"])
    out["flat_LM"] = flat_dist(PLACES["임강"], PLACES["압록하구"])
    d = real["dist"]["임강-하구"]
    out["s830"] = {u: 830 * u / d for u in (0.36, 0.42, 0.48)}
    out["li830_pm10"] = (747 * 0.36, 913 * 0.48, 747 * 0.36 / d, 913 * 0.48 / d)
    out["li_of_308"] = {u: d / u for u in (0.36, 0.42, 0.48)}
    out["li250"] = {u: 250 * u for u in (0.36, 0.42, 0.48)}
    out["li250_pm10"] = (225 * 0.36, 275 * 0.48)
    A = real["area"]
    ov_rm = rect_area(121.0, 125.5, 41.0, 43.6)
    out["ov_RM"] = ov_rm
    out["ratio_MR"] = A["만주"] / A["요하"]
    out["post_RM"] = (A["만주"] / (A["만주"] + A["요하"]), A["요하"] / (A["만주"] + A["요하"]))   # 우도 비 1/A 이므로 요하 쪽 몫 = A_M/(A_M+A_R)
    out["ov_RM_share"] = (ov_rm / A["요하"], ov_rm / A["만주"])
    out["wil"] = {kn: wilson(*kn) for kn in [(4, 5), (3, 4), (16, 20), (45, 50), (9, 10)]}
    pri = (0.4, 0.2, 0.2, 0.2)
    Lb = (1, 1, 1, 0)
    z = sum(a * b for a, b in zip(pri, Lb))
    out["bad_post"] = [a * b / z for a, b in zip(pri, Lb)]
    out["quad_in"] = real["quad"]
    out["ice_pct"] = {"110일": 110 / 365, "100건중": (28, 33)}
    # 식 1의 숫자
    out["m_NW"] = 400 / A["서북"]
    out["m_M"] = 400 / A["만주"]
    # 이 장의 개괄 숫자: 만주 창이 서북 창의 몇 배
    out["MN"] = A["만주"] / A["서북"]
    if verbose:
        print("== 식과 연습 문제의 숫자")
        for k in ("flat_PL", "flat_PM", "flat_LM"):
            print(" ", k, [round(v, 4) for v in out[k]])
        print("  굽이 지수 830리", {k: round(v, 4) for k, v in out["s830"].items()}, "±10%", [round(v, 3) for v in out["li830_pm10"]])
        print("  308 km 는 몇 리", {k: round(v, 1) for k, v in out["li_of_308"].items()})
        print("  250리", {k: round(v, 1) for k, v in out["li250"].items()}, "±10%", [round(v, 1) for v in out["li250_pm10"]])
        print("  요하-만주 창 겹침", round(out["ov_RM"]), "요하 대비", round(out["ov_RM_share"][0], 4), "만주 대비", round(out["ov_RM_share"][1], 4), "면적비 만주/요하", round(out["ratio_MR"], 4))
        print("  요하/만주 사후(무차별 2가설, 증거가 겹침에)", [round(v, 4) for v in out["post_RM"]])
        print("  윌슨", {k: [round(x, 3) for x in v] for k, v in out["wil"].items()})
        print("  잘못 0 넣은 사후", [round(v, 4) for v in out["bad_post"]])
        print("  식1 m", out["m_NW"], out["m_M"], out["MN"])
    return out



# ======================================================================= 창 안의 하천 비율(Natural Earth 1:10m 중심선)
def river_share(buf=3.0, verbose=True):
    """각 창 안의 Natural Earth 하천 중심선 길이와, 중심선에서 buf km 이내인 땅의 비율. 중소 하천이 빠져 있어 하한값이다."""
    from shapely.geometry import shape, box as sbox
    from shapely.ops import unary_union
    import shapely
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "geo", "ne_10m_rivers_lake_centerlines.geojson")
    geoms = [shape(f["geometry"]) for f in json.load(open(p, encoding="utf-8"))["features"]]
    out = {}
    for k, (l1, l2, p1, p2) in FR.items():
        bb = sbox(l1, p1, l2, p2)
        lat0 = (p1 + p2) / 2
        sx, sy = 111.32 * math.cos(math.radians(lat0)), 111.2
        lines = []
        for g in geoms:
            if g.intersects(bb):
                c = g.intersection(bb)
                if not c.is_empty:
                    lines.append(shapely.transform(c, lambda a: a * np.array([sx, sy])))
        u = unary_union([l.buffer(buf) for l in lines])
        win = shapely.transform(bb, lambda a: a * np.array([sx, sy]))
        out[k] = {"n": len(lines), "length": sum(l.length for l in lines), "frac": u.intersection(win).area / win.area}
    if verbose:
        print("== 창 안의 Natural Earth 하천 (중심선 %.0f km 이내)" % buf)
        for k, v in out.items():
            print(" ", k, v["n"], "개", round(v["length"]), "km", round(v["frac"] * 100, 2), "%")
    return out


# ======================================================================= 그림 공통
def colors(mode):
    if mode == "color":
        return dict(a="#1f6fb8", b="#c0392b", c="#2e7d32", d="#f0b45a", e="#7a4fa3", g="#777777", ink="#222222", pale="#dfe9f3", pale2="#f6e3c0")
    return dict(a="#000000", b="#000000", c="#000000", d="#bdbdbd", e="#555555", g="#777777", ink="#000000", pale="#e6e6e6", pale2="#d0d0d0")


def ensure_dir():
    os.makedirs(os.path.join(ROOT, "ch19"), exist_ok=True)


# ----------------------------------------------------------------------- 그림 a: 연대기
def xmap(y):
    return (y - 650) / (2025 - 650)


def fig_timeline(mode):
    C = colors(mode)
    # (이름, 종류, 시작, 끝, 라벨, 보조 마름모 연도들)
    rows = [
        ("H", "땅과 이름(사료와 사건)"),
        ("발해", "bar", 698, 926, "698~926", []),
        ("호경(고려 서경)", "bar", 998, 1062, "998~1062", []),
        ("거란군 압록강 도하", "pt", 1018, None, "1018", []),
        ("요 서경(대동)", "pt", 1044, None, "1044", []),
        ("동북 9성", "pt", 1107, None, "1107", []),
        ("묘청의 난", "pt", 1135, None, "1135", []),
        ("서경의 동녕부", "bar", 1269, 1290, "1269~1290", []),
        ("H", "학자와 저작"),
        ("정약용", "bar", 1762, 1836, "1762~1836", []),
        ("한치윤", "bar", 1765, 1814, "1765~1814", [(1823, "1823 해동역사 완성")]),
        ("시라토리 구라키치", "bar", 1865, 1942, "1865~1942", []),
        ("이나바 이와키치", "bar", 1876, 1940, "1876~1940", []),
        ("신채호", "bar", 1880, 1936, "1880~1936", [(1908, "1908 독사신론"), (1931, "1931 조선상고사")]),
        ("담기양", "bar", 1911, 1992, "1911~1992", [(1982, "1982~88 역사지도집")]),
        ("H", "기후와 땅속 자료"),
        ("중세 온난기(약)", "bar", 950, 1250, "950~1250", []),
        ("축가정", "bar", 1890, 1974, "1890~1974", [(1972, "1972 논문")]),
        ("하남둔 조사", "pt", 2005, None, "2005", []),
    ]
    n = len(rows)
    fig, ax = new(mode, 6.0)
    face = {"A": C["a"], "B": C["d"], "C": C["c"]}
    if mode == "bw":
        face = {"A": "#7a7a7a", "B": "#d0d0d0", "C": "#ffffff"}
    grp = "A"
    labels = []
    for i, r in enumerate(rows):
        y = n - 1 - i
        if r[0] == "H":
            ax.text(0.0, y, r[1], fontsize=FS, weight="bold", va="center", ha="left")
            grp = {"땅과 이름(사료와 사건)": "A", "학자와 저작": "B", "기후와 땅속 자료": "C"}[r[1]]
            labels.append("")
            ax.axhline(y + 0.5, color=C["g"], lw=0.5, ls=":") if i > 0 else None
            continue
        nm, kind, y0, y1, lab, mk = r
        labels.append(nm)
        if kind == "bar":
            x0, x1 = xmap(y0), xmap(y1)
            ax.barh(y, x1 - x0, left=x0, height=0.55, color=face[grp], edgecolor=C["ink"], lw=0.7, hatch=("///" if (mode == "bw" and grp == "B") else ("..." if (mode == "bw" and grp == "C") else None)))
            xl = x0
        else:
            xl = xmap(y0)
            ax.plot(xl, y, "o", color=C["b"] if mode == "color" else "white", mec=C["ink"], ms=6.5, zorder=5)
        for yy, txt in mk:
            ax.plot(xmap(yy), y, "D", color=C["b"] if mode == "color" else "white", mec=C["ink"], ms=5.5, zorder=5)
        txt = lab + ("  " + "  ".join("◆" + t for _, t in mk) if mk else "")
        if kind == "bar" and xl < 0.1:
            ax.text(xmap(y1) + 0.012, y, txt, va="center", ha="left", fontsize=FS)
        else:
            ax.text(xl - 0.012, y, txt, va="center", ha="right", fontsize=FS)
    ax.set_yticks(range(n))
    ax.set_yticklabels(labels[::-1])
    ticks = [700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000]
    ax.set_xticks([xmap(t) for t in ticks])
    ax.set_xticklabels([str(t) if t % 200 == 0 or t in (1100, 1300, 1500, 1700, 1900) else "" for t in ticks][:0] or [str(t) for t in ticks], fontsize=7.5 if False else FS, rotation=90)
    ax.set_xlim(-0.01, 1.01)
    ax.set_ylim(-0.7, n - 0.3)
    ax.grid(axis="x", color=C["g"], lw=0.3, ls=":")
    ax.set_xlabel("연도")
    return fig


# ----------------------------------------------------------------------- 그림 b: 지역 창의 크기
def fig_windows(mode, real):
    C = colors(mode)
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 2.9), constrained_layout=True, gridspec_kw={"width_ratios": [1.15, 1.0]})
    ax = axs[0]
    names = {"서북": "서북", "요하": "요하", "산동": "산동", "만주": "만주"}
    ls_ = {"서북": "-", "요하": "--", "산동": "-.", "만주": ":"}
    cols = {"서북": C["a"], "요하": C["c"], "산동": C["e"], "만주": C["b"]}
    for k, (a, b, c, d) in FR.items():
        ax.add_patch(Rectangle((a, c), b - a, d - c, fill=(k == "만주"), fc=C["pale2"] if k == "만주" else "none", alpha=0.6 if k == "만주" else 1,
                               ec=cols[k] if mode == "color" else "black", lw=1.4, ls=ls_[k]))
    ax.text(121.2, 46.4, "만주", fontsize=FS, weight="bold", va="center")
    ax.text(124.15, 37.8, "서북", fontsize=FS, weight="bold", va="center")
    ax.text(119.7, 43.1, "요하", fontsize=FS, weight="bold", va="center")
    ax.text(114.7, 34.6, "산동", fontsize=FS, weight="bold", va="center")
    for nm, mk in (("평양", "o"), ("임강", "s"), ("대동", "^")):
        la, lo = PLACES[nm]
        ax.plot(lo, la, mk, color="black", mfc="white" if nm != "임강" else "black", ms=5.5, zorder=6)
    ax.annotate("임강", (PLACES["임강"][1], PLACES["임강"][0]), xytext=(4, 4), textcoords="offset points", fontsize=FS)
    ax.annotate("평양", (PLACES["평양"][1], PLACES["평양"][0]), xytext=(5, -4), textcoords="offset points", fontsize=FS)
    ax.annotate("대동", (PLACES["대동"][1], PLACES["대동"][0]), xytext=(-2, 5), textcoords="offset points", fontsize=FS)
    ax.set_xlim(112, 133)
    ax.set_ylim(33.2, 47.8)
    ax.set_aspect(1 / math.cos(math.radians(40.5)))
    ax.set_xlabel("동경 (도)")
    ax.set_ylabel("북위 (도)")
    ax.grid(color=C["grid"] if False else "#aaaaaa", lw=0.3, ls=":")
    ax.set_title("(가) 네 창의 위치", loc="left", fontsize=9)
    ax = axs[1]
    ks = ["서북", "요하", "산동", "만주"]
    A = [real["area"][k] / 1e4 for k in ks]
    rel = [real["rel_ml"][k] for k in ks]
    y = np.arange(len(ks))[::-1]
    ax.barh(y, rel, color=[cols[k] if mode == "color" else "#bdbdbd" for k in ks], edgecolor="black", lw=0.7,
            hatch=None if mode == "color" else None)
    for yi, r, a_, k in zip(y, rel, A, ks):
        ax.text(r + 0.02, yi, f"{r:.2f}  ({a_:.1f}만 km²)", va="center", fontsize=FS)
    ax.set_yticks(y)
    ax.set_yticklabels(ks)
    ax.set_xlim(0, 1.95)
    ax.set_xlabel("주변 우도의 상대값(서북=1)")
    ax.set_title("(나) 같은 증거라면", loc="left", fontsize=9)
    return fig


# ----------------------------------------------------------------------- 그림 c: 서경이라는 이름의 세 곳
_LAND = None


def land_polys(box_):
    global _LAND
    from shapely.geometry import shape, box as sbox
    if _LAND is None:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "geo", "ne_10m_land.geojson")
        _LAND = [shape(f["geometry"]) for f in json.load(open(p, encoding="utf-8"))["features"]]
    bb = sbox(*box_)
    out = []
    for g in _LAND:
        if g.intersects(bb):
            out.append(g.intersection(bb))
    return out


def rivers_lines(box_, names):
    from shapely.geometry import shape, box as sbox
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "geo", "ne_10m_rivers_lake_centerlines.geojson")
    bb = sbox(*box_)
    res = []
    for f in json.load(open(p, encoding="utf-8"))["features"]:
        nm = {k.lower(): v for k, v in f["properties"].items()}.get("name")
        if nm in names:
            g = shape(f["geometry"]).intersection(bb)
            if not g.is_empty:
                res.append(g)
    return res


def fig_xijing(mode, real):
    C = colors(mode)
    x0, x1, y0, y1 = 111.0, 133.0, 35.5, 47.8
    fig, ax = plt.subplots(figsize=(WIDTH, 4.1), constrained_layout=True)
    for g in land_polys((x0, y0, x1, y1)):
        for q in ([g] if g.geom_type == "Polygon" else list(g.geoms)):
            if q.geom_type == "Polygon":
                ax.fill(*q.exterior.xy, fc="#f4efe2" if mode == "color" else "#f2f2f2", ec="#8a8a8a", lw=0.5)
    for g in rivers_lines((x0, y0, x1, y1), {"Yalu", "Songhua", "Liao", "Tumen", "Nen", "Di’er Songhua", "Huang"}):
        for l in ([g] if g.geom_type == "LineString" else list(g.geoms)):
            if l.geom_type == "LineString":
                ax.plot(*l.xy, color=C["a"] if mode == "color" else "black", lw=0.8, ls="-" if mode == "color" else "-.")
    for k, (a, b, c, d) in FR.items():
        if k in ("서북", "만주"):
            ax.add_patch(Rectangle((a, c), b - a, d - c, fill=False, ec=C["b"] if mode == "color" else "black", lw=1.1, ls="-" if k == "만주" else "--"))
    ax.text(121.2, 46.55, "만주 창", fontsize=FS, weight="bold", va="center")
    ax.text(124.1, 37.7, "서북 창", fontsize=FS, weight="bold", va="center")
    pts = [("평양", "o", "고려 서경(통설)"), ("임강", "s", "발해 서경(통설)"), ("대동", "^", "요·금 서경")]
    for nm, mk, lab in pts:
        la, lo = PLACES[nm]
        ax.plot(lo, la, mk, color=C["b"] if mode == "color" else "black", mfc=C["b"] if mode == "color" else ("white" if nm != "임강" else "black"), mec="black", ms=7, zorder=7)
    la, lo = PLACES["평양"]
    ax.annotate("평양: 고려 서경", (lo, la), xytext=(8, -14), textcoords="offset points", fontsize=FS, zorder=8)
    la, lo = PLACES["임강"]
    ax.annotate("임강: 발해 서경(통설)", (lo, la), xytext=(6, 6), textcoords="offset points", fontsize=FS, zorder=8)
    la, lo = PLACES["대동"]
    ax.annotate("대동: 요·금 서경", (lo, la), xytext=(-8, 8), textcoords="offset points", fontsize=FS, zorder=8)
    D = real["dist"]
    for a, b, key, off in (("평양", "임강", "평양-임강", (-3, 0.35)), ("평양", "대동", "평양-대동", (0, -0.9)), ("임강", "대동", "임강-대동", (0, 0.45))):
        (la1, lo1), (la2, lo2) = PLACES[a], PLACES[b]
        ax.plot([lo1, lo2], [la1, la2], color="black", lw=0.8, ls=":", zorder=4)
        mx, my = (lo1 + lo2) / 2 + off[0], (la1 + la2) / 2 + off[1]
        ax.text(mx, my, f"{D[key]:,.0f} km", fontsize=FS, ha="center", va="center", bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.5), zorder=8)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect(1 / math.cos(math.radians(41.5)))
    ax.set_xlabel("동경 (도)")
    ax.set_ylabel("북위 (도)")
    ax.grid(color="#aaaaaa", lw=0.3, ls=":")
    return fig


# ----------------------------------------------------------------------- 그림 d: 계절이 길을 바꾼다
def fig_ice(mode, ice, extra):
    C = colors(mode)
    fords, m_s, m_w = extra
    fig, axs = plt.subplots(2, 2, figsize=(WIDTH, 4.7), constrained_layout=True)
    panels = [("(가) 여름: 나루로만 건넌다", m_s, "summer"), ("(나) 겨울: 얼음 위로 곧장", m_w, "winter"), ("(다) 계절을 모르면: 합집합", m_s | m_w, "union")]
    for ax, (ttl, m, key) in zip(axs.ravel()[:3], panels):
        ax.imshow(np.where(m, 1.0, np.nan), extent=(0, XMAX, 0, YMAX), origin="lower", cmap="Oranges" if mode == "color" else "Greys", vmin=0, vmax=1.6, alpha=0.9, aspect="equal", interpolation="nearest")
        if key == "union":
            both = m_s & m_w
            ax.imshow(np.where(both, 1.0, np.nan), extent=(0, XMAX, 0, YMAX), origin="lower", cmap="Blues" if mode == "color" else "Greys", vmin=0, vmax=2.6, alpha=0.9, aspect="equal", interpolation="nearest")
        ax.axhline(RIVER_Y, color=C["a"] if mode == "color" else "black", lw=1.6, ls="-" if mode == "color" else "-.")
        for f in fords:
            ax.plot(*f, "s", color="white", mec="black", ms=5, zorder=6)
        ax.plot(*S0, "^", color="black", ms=6, zorder=7)
        ax.text(S0[0] + 5, S0[1] + 1, "읍", fontsize=FS, va="bottom")
        if key != "winter":
            for f in fords:
                ax.text(f[0], f[1] + 4, "나루", fontsize=FS, ha="center", va="bottom")
        ax.set_xlim(0, XMAX)
        ax.set_ylim(0, YMAX)
        ax.set_title(ttl, loc="left", fontsize=9)
        ax.set_xticks(range(0, XMAX + 1, 50))
        ax.set_yticks(range(0, YMAX + 1, 40))
        ax.grid(color="#aaaaaa", lw=0.3, ls=":")
        if key == "summer":
            ax.set_ylabel("북 (km)")
        if key in ("union",):
            ax.set_xlabel("동 (km)")
            ax.set_ylabel("북 (km)")
        if key == "winter":
            pass
    ax = axs[1, 1]
    labs = ["여름", "겨울", "합집합", "겹침"]
    vals = [ice["summer"], ice["winter"], ice["union"], ice["both"]]
    fcs = [C["d"], C["a"], C["g"], C["c"]] if mode == "color" else ["#d0d0d0", "#7a7a7a", "#ffffff", "#333333"]
    ax.bar(range(4), vals, color=fcs, edgecolor="black", lw=0.7, hatch=None if mode == "color" else ["", "", "///", "xx"][0])
    if mode == "bw":
        for r, h in zip(ax.patches, ["", "...", "///", "xx"]):
            r.set_hatch(h)
    for i, v in enumerate(vals):
        ax.text(i, v + 120, f"{v:,.0f}", ha="center", fontsize=FS)
    ax.set_xticks(range(4))
    ax.set_xticklabels(labs)
    ax.set_ylim(0, 9200)
    ax.set_ylabel("넓이 (km²)")
    ax.set_title("(라) 후보 영역의 넓이", loc="left", fontsize=9)
    return fig


# ----------------------------------------------------------------------- 그림 e: 이름의 시기층
def fig_layers(mode):
    C = colors(mode)
    fig, ax = new(mode, 3.3)
    rows = [
        ("발해 5경 시기", 698, 926, "bar", "698~926"),
        ("요 서경(대동)", 1044, None, "arrow", "1044 서경이 됨, 끝은 미확인"),
        ("금 상경 회령부", 1138, 1173, "two", "1138 상경, 1173 다시 상경"),
        ("고려 서경=호경", 998, 1062, "bar", "998~1062"),
        ("고려 분사 강화", 1116, None, "mark", "1116"),
        ("서경의 동녕부", 1269, 1290, "bar", "1269~1290"),
    ]
    n = len(rows)
    xs = lambda y: (y - 650) / (1400 - 650)
    for i, (nm, y0, y1, kind, lab) in enumerate(rows):
        y = n - 1 - i
        if kind == "bar":
            ax.barh(y, xs(y1) - xs(y0), left=xs(y0), height=0.5, color=C["a"] if mode == "color" else "#7a7a7a", edgecolor="black", lw=0.7)
        elif kind == "two":
            ax.plot([xs(y0), xs(y1)], [y, y], color="black", lw=1.0, ls=":")
            ax.plot(xs(y0), y, "o", color="white", mec="black", ms=6.5, zorder=6)
            ax.plot(xs(y1), y, "s", color="white", mec="black", ms=6, zorder=6)
        elif kind == "arrow":
            ax.annotate("", xy=(1.0, y), xytext=(xs(y0), y), arrowprops=dict(arrowstyle="->", lw=1.3, color="black"))
            ax.plot(xs(y0), y, "o", color="white", mec="black", ms=6.5, zorder=6)
        else:
            ax.plot(xs(y0), y, "o", color=C["b"] if mode == "color" else "white", mec="black", ms=6.5, zorder=6)
        if kind == "bar" and y0 < 1000:
            ax.text(xs(y1) + 0.012, y, lab, ha="left", va="center", fontsize=FS)
        elif kind == "bar" and y0 < 1100:
            ax.text(xs(y1) + 0.012, y, lab, ha="left", va="center", fontsize=FS)
        else:
            ax.text(xs(y0) - 0.014, y, lab, ha="right", va="center", fontsize=FS)
    ax.set_yticks(range(n))
    ax.set_yticklabels([r[0] for r in rows][::-1])
    ticks = [700, 800, 900, 1000, 1100, 1200, 1300, 1400]
    ax.set_xticks([xs(t) for t in ticks])
    ax.set_xticklabels([str(t) for t in ticks])
    ax.set_xlim(0, 1.02)
    ax.set_ylim(-0.7, n - 0.3)
    ax.grid(axis="x", color="#aaaaaa", lw=0.3, ls=":")
    ax.set_xlabel("연도 (출처에 연도가 적힌 것만)")
    return fig


# ----------------------------------------------------------------------- 그림 f: 윌슨 구간
def fig_wilson(mode, rows):
    C = colors(mode)
    fig, ax = new(mode, 2.6)
    for i, (k, n, p, lo, hi, w) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.plot([lo, hi], [y, y], color="black", lw=2.2 if mode == "bw" else 2.4, solid_capstyle="butt", zorder=3)
        ax.plot([p], [y], "o", color=C["b"] if mode == "color" else "white", mec="black", ms=6.5, zorder=4)
        ax.text(hi + 0.02, y, f"{lo:.2f}~{hi:.2f}", va="center", fontsize=FS)
    ax.axvline(0.95, color=C["b"] if mode == "color" else "black", lw=1.0, ls="--")
    ax.text(0.95, len(rows) - 0.35, "명목 0.95", ha="right", va="bottom", fontsize=FS)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f"{k}/{n}" for (k, n, *_r) in rows][::-1])
    ax.set_xlim(0.2, 1.22)
    ax.set_ylim(-0.6, len(rows) - 0.1)
    ax.set_xlabel("적중률의 95% 구간(윌슨), 점은 관측 0.75")
    ax.set_ylabel("적중 수/지명 수")
    ax.grid(axis="x", color="#aaaaaa", lw=0.3, ls=":")
    return fig


# ----------------------------------------------------------------------- 그림 g: 나루의 위치와 계절의 값
def fig_ford(mode, ice):
    C = colors(mode)
    fig, ax = new(mode, 2.7)
    xs_ = sorted(ice["by_n"])
    r = [ice["by_n"][x][2] / ice["by_n"][x][1] for x in xs_]
    rs = [ice["by_n"][x][0] / ice["by_n"][x][1] for x in xs_]
    ax.plot(xs_, r, "-o", color=C["b"] if mode == "color" else "black", ms=4.5, label="합집합 / 겨울")
    ax.plot(xs_, rs, "--s", color=C["a"] if mode == "color" else "black", mfc="white", ms=4.5, label="여름 / 겨울")
    ax.axhline(1.0, color=C["g"], lw=0.6)
    ax.axvline(95, color=C["g"], lw=0.8, ls=":")
    ax.text(97, 0.07, "읍에서 북동쪽으로\n곧장 가면 강과 만나는 곳", fontsize=FS, va="bottom", ha="left")
    ax.set_xlabel("나루의 동쪽 위치 (km)")
    ax.set_ylabel("넓이의 비")
    ax.set_ylim(0, 1.75)
    ax.legend(loc="upper center", frameon=False, ncol=2)
    ax.grid(color="#aaaaaa", lw=0.3, ls=":")
    return fig


def figures():
    ensure_dir()
    cal = all_calc(False)
    ice, extra = case_ice(False)
    real = cal["real"]
    out = []
    for mode in ("color", "bw"):
        out.append(save(fig_timeline(mode), "ch19", "fig19-a-timeline", mode))
        out.append(save(fig_windows(mode, real), "ch19", "fig19-b-windows", mode))
        out.append(save(fig_xijing(mode, real), "ch19", "fig19-c-xijing", mode))
        out.append(save(fig_ice(mode, ice, extra), "ch19", "fig19-d-ice", mode))
        out.append(save(fig_layers(mode), "ch19", "fig19-e-layers", mode))
        out.append(save(fig_wilson(mode, cal["wil"]), "ch19", "fig19-f-wilson", mode))
        out.append(save(fig_ford(mode, ice), "ch19", "fig19-g-ford", mode))
    return out


if __name__ == "__main__":
    if "--calc" in sys.argv:
        c_ = all_calc(True)
        formula_calc(c_["real"], True)
        river_share(3.0, True)
    else:
        c_ = all_calc(True)
        formula_calc(c_["real"], True)
        river_share(3.0, True)
        for p_ in figures():
            print(p_)
