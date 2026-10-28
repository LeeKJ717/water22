"""figs-m17.py - 17장(요하 유역) 새 그림과 새 사례 계산.
실행: python3 tools/figs-m17.py  (그림/ch17 에 컬러·흑백 PDF 생성, 계산 결과를 표준출력에 JSON으로 인쇄)
모든 세계는 가상이며 서경의 결과가 아니다. 이름·좌표·숫자는 연습용이다.
실제 지명의 지리 사실(위키백과 확인)은 본문에만 쓰고, 이 파일의 계산에는 아래 두 현대 좌표 외에 쓰지 않는다.
"""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from math import gcd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from figlib import *

FS = 8.5
STEP = 0.5
L = 120.0
XS = np.arange(0, L + 1e-9, STEP)
GX, GY = np.meshgrid(XS, XS)           # GY[i, j]=북, GX[i, j]=동
CELL = STEP * STEP
U_LO, U_HI, U_MID = 0.36, 0.48, 0.42   # km/리 (이 책의 연습용 가정)


# ------------------------------------------------------------------ 공통 도구
def dist(c):
    return np.hypot(GX - c[0], GY - c[1])


def bearing(c):
    return (np.degrees(np.arctan2(GX - c[0], GY - c[1])) + 360) % 360


def ring(c, lo, hi):
    d = dist(c)
    return ((d >= lo) & (d <= hi))


def sector(c, brg, half):
    diff = np.abs((bearing(c) - brg + 180) % 360 - 180)
    return diff <= half


def area(mask):
    return float(np.sum(mask) * CELL)


def phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def haversine(lat1, lon1, lat2, lon2, R=6371.0):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1; dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def river_x(y, kind="new"):
    if kind == "new":
        return 62.0 + 5.0 * np.sin(2 * np.pi * y / 70.0)
    return 46.0 + 4.0 * np.sin(2 * np.pi * (y + 8.0) / 70.0)


def marsh_mask():
    xr = river_x(GY, "new")
    return (GX >= xr - 24) & (GX <= xr - 2) & (GY >= 15) & (GY <= 105)


# ------------------------------------------------------------------ 사례 계산
def li2km(li, tol=0.10):
    return li * (1 - tol) * U_LO, li * (1 + tol) * U_HI


def case_b1():
    """도하 문형: 정읍(92,60)에서 '강을 건너 서쪽으로 칠십 리'"""
    c = (92.0, 60.0)
    lo, hi = li2km(70)
    rs = ring(c, lo, hi) & sector(c, 270.0, 22.5)
    west = GX < river_x(GY, "new")
    both = rs & west
    # 나루가 어디인지 모르는 대신, 강 중심선에서 3 km 이내(둑)는 어느 쪽이든 허용하는 완화판
    near = np.abs(GX - river_x(GY, "new")) <= 3.0
    relax = rs & (west | near)
    out = dict(c=c, lo=lo, hi=hi, A_ring=area(ring(c, lo, hi)),
               A_sector_theory=0.125 * math.pi * (hi ** 2 - lo ** 2),
               A_rs=area(rs), A_both=area(both), A_relax=area(relax),
               frac_west=area(both) / area(rs))
    out["rs"], out["both"], out["relax"] = rs, both, relax
    return out


def case_b2(n=200000, seed=3, sigma=8.0):
    """옛 유로와 지금 유로: 강에서 3 km 이내(허용 폭 b)로 읽었을 때 참 위치를 배제하는 비율"""
    rng = np.random.default_rng(seed)
    d = np.abs(rng.normal(0, sigma, n))            # 옛·지금 유로 사이 가로 간격(km)
    u = rng.uniform(0, 3.0, n)                     # 참 위치와 옛 유로 사이 간격(km, 3 km 이내)
    side = rng.choice([-1, 1], n)                  # 참 위치가 옛 유로의 어느 쪽 둑인가
    dist_new = np.abs(d + side * u)                # 참 위치와 지금 유로 사이 간격
    out = dict(sigma=sigma)
    rows = []
    for b in (3, 6, 10, 15, 20):
        ex = float(np.mean(dist_new > b))
        rows.append(dict(b=b, band=2 * b, mult=b / 3.0, excl=ex, excl3=ex, ind3=ex ** 3, share3=ex))
    out["rows"] = rows
    # 세 기법이 같은 지금 유로를 쓰면 배제가 한꺼번에: 같은 d를 공유하므로 모두 틀리는 비율 = 단일 배제율
    out["cover_sigma"] = {b: 2 * (1 - phi(b / sigma)) for b in (3, 6, 10, 15, 20)}
    # 간격이 12 km 로 알려진 경우의 폭
    out["d12"] = {b: float(np.mean(np.abs(12.0 + side * u) > b)) for b in (3, 6, 10, 15, 20)}
    # 옛 유로를 합집합으로 허용하는 판: 지금 유로 b 이내이거나 옛 유로 b 이내(옛 유로 위치를 알고 있을 때)
    out["union_excl"] = 0.0
    return out


def travel_hours(cost, src, v=5.0):
    """격자 위 최단 시간(시간). 16방향 이웃, 간선 비용 = 길이 x 두 끝 칸 비용의 평균. 방향 어림 오차는 약 2.6% 이하"""
    n = cost.shape[0]
    idx = np.arange(n * n).reshape(n, n)
    rows = []; colsl = []; w = []
    for dx in (-2, -1, 0, 1, 2):
        for dy in (-2, -1, 0, 1, 2):
            if (dx, dy) == (0, 0) or gcd(abs(dx), abs(dy)) != 1:
                continue
            i0, i1 = max(0, -dy), min(n, n - dy)
            j0, j1 = max(0, -dx), min(n, n - dx)
            a = idx[i0:i1, j0:j1]; b = idx[i0 + dy:i1 + dy, j0 + dx:j1 + dx]
            ca = cost[i0:i1, j0:j1]; cb = cost[i0 + dy:i1 + dy, j0 + dx:j1 + dx]
            rows.append(a.ravel()); colsl.append(b.ravel())
            w.append((math.hypot(dx, dy) * STEP * 0.5 * (ca + cb)).ravel())
    M = coo_matrix((np.concatenate(w), (np.concatenate(rows), np.concatenate(colsl))), shape=(n * n, n * n)).tocsr()
    d = dijkstra(M, directed=True, indices=src)
    return d.reshape(n, n) / v


def case_b3():
    """습지 비용: 무진(80,60)에서 '하루 길'(8시간, 5 km/h) - 서쪽 습지의 시간 배율 k"""
    c = (80.0, 60.0)
    m = marsh_mask()
    v = 5.0
    res = {}
    cum = {}
    i0, j0 = int(c[1] / STEP), int(c[0] / STEP)
    src = i0 * len(XS) + j0
    for k in (1, 2, 3, 4):
        cost = np.where(m, float(k), 1.0)
        hrs = travel_hours(cost, src, v)
        cum[k] = hrs
        band = (hrs >= 7.0) & (hrs <= 9.0)
        row = int(60 / STEP)
        west_x = XS[np.where(hrs[row, :j0 + 1] <= 8.0)[0].min()]
        east_x = XS[np.where(hrs[row, j0:] <= 8.0)[0].max() + j0]
        res[k] = dict(A_band=area(band), A_reach=area(hrs <= 8.0), west_reach=c[0] - west_x, east_reach=east_x - c[0],
                      A_band_west=area(band & sector(c, 270.0, 45.0)))
    return dict(c=c, res=res, cum=cum, marsh=m, v=v)


def case_b4():
    """이름 충돌: 후보 A·B의 영역에 같은 문헌의 영역이 얼마나 걸치는가"""
    ref = (60.0, 60.0)
    lo, hi = li2km(40)
    R = ring(ref, lo, hi) & sector(ref, 270.0, 22.5)
    A = dist((40.0, 62.0)) <= 12.0
    B = dist((36.0, 48.0)) <= 12.0
    Rn = area(R)
    ov_A = area(R & A); ov_B = area(R & B)
    out = dict(ref=ref, lo=lo, hi=hi, R=Rn, a=area(A), b=area(B), ov_A=ov_A, ov_B=ov_B,
               pA=ov_A / area(A), pB=ov_B / area(B))
    out["LR"] = out["pA"] / out["pB"]
    prior = 1.0                                            # A:B = 1:1
    odds_doc = prior * out["LR"]
    out["odds_doc"] = odds_doc
    out["P_doc"] = odds_doc / (1 + odds_doc)
    # 날짜 문헌: A쪽 정권의 시기와 맞을 가능성이 2배라고 둔 가정(연습)
    out["LR_date"] = 2.0
    odds2 = odds_doc * 2.0
    out["odds2"] = odds2; out["P2"] = odds2 / (1 + odds2)
    # 이름 증거: B 지역에만 같은 이름의 도읍 기록이 있는 줄 알고 LR=1/6(B쪽으로 6배)을 넣은 경우
    out["LR_name"] = 1 / 6.0
    odds3 = odds2 * out["LR_name"]
    out["odds3"] = odds3; out["P3"] = odds3 / (1 + odds3)
    # 이름 증거를 두 번 센 경우
    odds4 = odds2 * out["LR_name"] ** 2
    out["odds4"] = odds4; out["P4"] = odds4 / (1 + odds4)
    out["R_mask"], out["A_mask"], out["B_mask"] = R, A, B
    return out


def case_b5(n=40000, seed=5):
    """해로 경유: 갑포(100,20)에서 동북 이틀, 해안을 끼고 남쪽 하루. 배 60 km/일(40~80), 방위 8방위 반폭 22.5도"""
    rng = np.random.default_rng(seed)
    start = np.array([100.0, 20.0])
    def leg(b, days):
        th = np.radians(b + rng.uniform(-22.5, 22.5, n))
        sp = rng.uniform(40, 80, n)
        return np.stack([np.sin(th), np.cos(th)], 1) * (sp * days)[:, None]
    p1 = start + leg(45.0, 2.0)
    p2 = p1 + leg(180.0, 1.0)
    nominal1 = start + 60 * 2 * np.array([math.sin(math.radians(45)), math.cos(math.radians(45))])
    nominal2 = nominal1 + 60 * 1 * np.array([0.0, -1.0])
    # 95% 영역 면적: 2차원 히스토그램의 높은 칸부터 95%
    H, xe, ye = np.histogram2d(p2[:, 0], p2[:, 1], bins=[np.arange(-30, 260, 2.0), np.arange(-30, 260, 2.0)])
    flat = np.sort(H.ravel())[::-1]; cs = np.cumsum(flat)
    k = int(np.searchsorted(cs, 0.95 * cs[-1]) + 1)
    a95 = k * 4.0
    cov = np.cov((p2 - p2.mean(0)).T)
    ev = np.sort(np.linalg.eigvalsh(cov))[::-1]
    straight = np.hypot(*(nominal2 - start))
    out = dict(start=start, nominal1=nominal1, nominal2=nominal2, A95=a95, med=np.median(p2, 0),
               major=2 * 1.96 * math.sqrt(ev[0]), minor=2 * 1.96 * math.sqrt(ev[1]),
               straight=float(straight), nominal_leg_sum=60 * 3.0, sdx=float(p2[:, 0].std()), sdy=float(p2[:, 1].std()),
               pts=p2[:3000], H=H, xe=xe, ye=ye)
    out["dist_q"] = [float(np.percentile(np.hypot(*(p2 - start).T), q)) for q in (5, 50, 95)]
    out["off_nominal_q"] = [float(np.percentile(np.hypot(*(p2 - nominal2).T), q)) for q in (50, 95)]
    return out


def case_b6():
    """지형 조건의 정보량: 하천 띠 3 km, 산 띠 5 km"""
    out = {}
    worlds = {}
    # 평야 한 줄기: 큰 강 하나, 산 3곳(반경 4 km)
    def riv(xc, amp=5.0, per=70.0, ph=0.0):
        return np.abs(GX - (xc + amp * np.sin(2 * np.pi * (GY + ph) / per)))
    d_main = riv(62.0)
    d_net = np.minimum.reduce([riv(62.0), riv(20.0, 4.0, 55.0, 10.0), riv(95.0, 3.0, 60.0, 5.0), riv(40.0, 6.0, 80.0, 20.0), riv(78.0, 5.0, 45.0, 30.0)])
    hills3 = [(72, 25, 4.0), (70, 70, 4.0), (75, 100, 4.0)]
    hills10 = hills3 + [(20, 30, 4.0), (30, 90, 4.0), (100, 100, 4.0), (15, 60, 4.0), (45, 15, 4.0), (100, 45, 4.0), (110, 80, 4.0)]
    def hill_dist(hs):
        return np.minimum.reduce([np.maximum(dist((x, y)) - r, 0) for x, y, r in hs])
    scen = [("큰 강 하나, 산 3곳", d_main, hill_dist(hills3)),
            ("큰 강 하나, 산 10곳", d_main, hill_dist(hills10)),
            ("강 5줄기, 산 3곳", d_net, hill_dist(hills3)),
            ("강 5줄기, 산 10곳", d_net, hill_dist(hills10))]
    rows = []
    inside = (GX >= 0) & (GX <= L) & (GY >= 0) & (GY <= L)
    tot = area(inside)
    for nm, dr, dh in scen:
        fr = area((dr <= 3.0) & inside) / tot
        fh = area((dh <= 5.0) & inside) / tot
        fb = area((dr <= 3.0) & (dh <= 5.0) & inside) / tot
        rows.append(dict(name=nm, fr=fr, fh=fh, fb=fb, bits_r=math.log2(1 / fr), bits_h=math.log2(1 / fh), bits_b=math.log2(1 / fb)))
    out["rows"] = rows
    out["total"] = tot
    out["masks"] = {nm: ((dr <= 3.0), (dh <= 5.0)) for nm, dr, dh in scen}
    return out


def case_b7():
    """같은 이름의 두 강: '갑수 서쪽 칠십 리'와 '갑수 동쪽 이십 리'"""
    lo1, hi1 = li2km(70); lo2, hi2 = li2km(20)
    x_east_river = 50.0
    x_west_river = 10.0
    d1 = (x_east_river - hi1, x_east_river - lo1)                   # 문헌 1: 동쪽 강의 서쪽
    d2_same = (x_east_river + lo2, x_east_river + hi2)             # 문헌 2를 같은 강으로 읽을 때
    d2_other = (x_west_river + lo2, x_west_river + hi2)            # 문헌 2의 갑수가 서쪽 강일 때
    def inter(a, b):
        lo, hi = max(a[0], b[0]), min(a[1], b[1])
        return (lo, hi) if hi > lo else None
    out = dict(lo1=lo1, hi1=hi1, lo2=lo2, hi2=hi2, d1=d1, d2_same=d2_same, d2_other=d2_other,
               inter_same=inter(d1, d2_same), inter_other=inter(d1, d2_other))
    io = out["inter_other"]
    out["width_other"] = io[1] - io[0] if io else 0
    out["width1"] = d1[1] - d1[0]; out["width2"] = d2_other[1] - d2_other[0]
    out["frac_other"] = out["width_other"] / out["width2"] if io else 0
    return out


def case_b8(n=200000, seed=9):
    """하루 이틀 길: 속도 4~5.5 km/h, 하루 6~9시간, 일수 1~2"""
    rng = np.random.default_rng(seed)
    v = rng.uniform(4.0, 5.5, n); h = rng.uniform(6.0, 9.0, n); dd = rng.uniform(1.0, 2.0, n)
    D = v * h * dd
    q = [float(np.percentile(D, p)) for p in (5, 50, 95)]
    fixed = {k: (k * 20, k * 40) for k in (1,)}
    return dict(q=q, fixed_lo=20 * 1, fixed_hi=40 * 2, book_lo=40.0, book_hi=80.0, mean=float(D.mean()), lo=float(D.min()), hi=float(D.max()))


def conversions():
    rows = []
    for li in (10, 20, 40, 70, 1000, 2000, 4000):
        rows.append(dict(li=li, lo=li * U_LO, mid=li * U_MID, hi=li * U_HI, lo_tol=li * 0.9 * U_LO, hi_tol=li * 1.1 * U_HI))
    # 위키백과 infobox 좌표: 요양 41°16′44″N 123°10′34″E (백탑공원), 심양 41°48′09″N 123°25′41″E (심하구)
    ly = (41 + 16 / 60 + 44 / 3600, 123 + 10 / 60 + 34 / 3600)
    sy = (41 + 48 / 60 + 9 / 3600, 123 + 25 / 60 + 41 / 3600)
    d = haversine(ly[0], ly[1], sy[0], sy[1])
    return dict(rows=rows, ly=ly, sy=sy, d=d, li_lo=d / U_HI, li_hi=d / U_LO, li_mid=d / U_MID)


def river_facts():
    f = dict(liao_len=1345, liao_basin=232000, xiliao_len=449, xiliao_basin=136000, dongliao_len=360, dongliao_basin=11500,
             daliao_len=94, daliao_basin=1926, hun_len=415.4, taizi_len=464)
    f["xiliao_share"] = f["xiliao_basin"] / f["liao_basin"]
    f["dongliao_share"] = f["dongliao_basin"] / f["liao_basin"]
    f["daliao_li_lo"] = f["daliao_len"] / U_HI; f["daliao_li_hi"] = f["daliao_len"] / U_LO
    f["daliao_over_liao"] = f["daliao_len"] / f["liao_len"]
    f["xiliao_over_liao"] = f["xiliao_len"] / f["liao_len"]
    return f


def case_b10():
    """종합: 무진(80,60)에서 '강을 건너 서쪽으로 칠십 리'와 '하루 길(7~9시간)'을 함께 읽기. 습지 배율 k=1~4, 40리 변형도"""
    c = (80.0, 60.0)
    B3 = case_b3()
    west = GX < river_x(GY, "new")
    out = {}
    for li in (40, 70):
        lo, hi = li2km(li)
        r1 = ring(c, lo, hi) & sector(c, 270.0, 22.5)
        r1w = r1 & west
        row = dict(li=li, lo=lo, hi=hi, A_r1=area(r1), A_r1w=area(r1w), per_k={})
        masks = []
        for k in (1, 2, 3, 4):
            hrs = B3["cum"][k]
            band = (hrs >= 7.0) & (hrs <= 9.0)
            m = band & r1w
            masks.append(m)
            row["per_k"][k] = dict(A=area(m), frac=(area(m) / area(r1w)) if area(r1w) > 0 else 0.0)
        row["A_union"] = area(np.logical_or.reduce(masks))
        row["A_inter"] = area(np.logical_and.reduce(masks))
        out[li] = row
    return out


def sector_area(r_lo, r_hi, theta=45.0):
    """부채꼴 고리의 닫힌 식 넓이 (km2)"""
    return theta / 360.0 * math.pi * (r_hi ** 2 - r_lo ** 2)


def extra_numbers():
    """본문 사례 묶음 A의 추가 사례(A8~A13), 사례 묶음 C, 민감도 표에 쓰는 숫자. 모두 닫힌 식 또는 격자·모의 실험"""
    out = {}
    # A9 (RE08) 동서 6리의 성: 폭과 격자 칸 수
    lo, hi = li2km(6)
    out["A9"] = dict(lo=lo, hi=hi, cells_lo=lo / STEP, cells_hi=hi / STEP)
    # A10 (RE01) '10여 리'(위쪽 한계 없음): 위쪽을 19리 또는 29리로 가정
    lo10 = li2km(10)[0]
    rows = []
    for up in (19, 29):
        hi_up = li2km(up)[1]
        rows.append(dict(upper_li=up, lo=lo10, hi=hi_up, one=sector_area(lo10, hi_up), two=2 * sector_area(lo10, hi_up)))
    out["A10"] = rows
    # A11 (RE12) 손방(동남) 삼십 리쯤
    lo, hi = li2km(30)
    out["A11"] = dict(lo=lo, hi=hi, area=sector_area(lo, hi), frac=45.0 / 360.0)
    # A12 (RE11) 사경: 동 31, 서 42, 남 25, 북 31 리
    ew = li2km(31 + 42); ns = li2km(25 + 31)
    out["A12"] = dict(ew=ew, ns=ns, a_lo=ew[0] * ns[0], a_hi=ew[1] * ns[1])
    # A13 (RE22, RE23, RE24) 새긴 글의 숫자: 12리, 10리/10일, 21리/21일
    out["A13"] = dict(r12=li2km(12), r10=li2km(10), d10=(10 * 40 * 0.9, 10 * 40 * 1.1),
                      r21=li2km(21), d21=(21 * 40 * 0.9, 21 * 40 * 1.1))
    # 민감도 표: 70리, 서쪽 부채꼴. 단위를 한 값으로 고정한 경우와 구간으로 쓴 경우, 어림 폭 t 세 가지
    sens = []
    for t in (0.05, 0.10, 0.20):
        row = dict(t=t)
        for u in (U_LO, U_MID, U_HI):
            row["u%.2f" % u] = sector_area(70 * (1 - t) * u, 70 * (1 + t) * u)
        row["range"] = sector_area(70 * (1 - t) * U_LO, 70 * (1 + t) * U_HI)
        sens.append(row)
    out["sens"] = sens
    out["sens_closed_check"] = math.pi / 2 * 0.10 * 70 ** 2 * U_MID ** 2     # 고정 u일 때 넓이 = (pi/2) t N^2 u^2
    # C1 사이: A(50,60)에서 30리 고리, B(80,60)에서 40리 고리의 겹침
    a = li2km(30); b = li2km(40)
    mA = ring((50.0, 60.0), *a); mB = ring((80.0, 60.0), *b)
    out["C1"] = dict(a=a, b=b, area_A=area(mA), area_B=area(mB), inter=area(mA & mB),
                     theory_A=math.pi * (a[1] ** 2 - a[0] ** 2), theory_B=math.pi * (b[1] ** 2 - b[0] ** 2),
                     frac_of_A=area(mA & mB) / area(mA), frac_of_B=area(mA & mB) / area(mB))
    # C2 합류점: 반폭 b 두 띠가 각도 phi 로 만나는 평행사변형의 넓이 (2b)^2 / sin(phi)
    out["C2"] = {str(phi): (2 * 3.0) ** 2 / math.sin(math.radians(phi)) for phi in (90, 60, 30, 10)}
    # C3 강을 따라: 지금 유로의 북쪽 120 km 구간 길이
    y = np.linspace(0, L, 200001)
    x = river_x(y, "new")
    seg = np.hypot(np.diff(x), np.diff(y)).sum()
    out["C3"] = dict(length=float(seg), straight=L, sinuosity=float(seg / L), extra_pct=float(100 * (seg / L - 1)))
    # C4 사흘 길의 분포: 속도 4~5.5, 하루 6~9시간, 일수 3 고정
    rng = np.random.default_rng(11)
    n = 200000
    D3 = rng.uniform(4.0, 5.5, n) * rng.uniform(6.0, 9.0, n) * 3.0
    out["C4"] = dict(q=[float(np.percentile(D3, p)) for p in (5, 50, 95)], fixed=3 * 40.0,
                     inside=float(np.mean((D3 >= 3 * 40 * 0.9) & (D3 <= 3 * 40 * 1.1))))
    # C5 산 기슭: 반경 4 km 산에서 5리, 기슭에서 재면 / 한가운데에서 재면
    lo, hi = li2km(5)
    out["C5"] = dict(lo=lo, hi=hi, rim=(4 + lo, 4 + hi), area_rim=sector_area(4 + lo, 4 + hi),
                     area_center=sector_area(lo, hi))
    out["B10"] = case_b10()
    return out


# ------------------------------------------------------------------ 그림 도구
def cols(mode):
    if mode == "color":
        return dict(a="#1f6fb8", b="#2e7d32", c="#c0392b", d="#e69f00", light="#cfe3f3", marsh="#9ccc9c", land="#f4efe4", mid="#7fb3d5")
    return dict(a="#000000", b="#444444", c="#777777", d="#222222", light="#e6e6e6", marsh="#cccccc", land="#ffffff", mid="#bdbdbd")


def frame(ax, xlim=(0, L), ylim=(0, L), ticks=20):
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal")
    ax.set_xticks(range(int(xlim[0]), int(xlim[1]) + 1, ticks)); ax.set_yticks(range(int(ylim[0]), int(ylim[1]) + 1, ticks))
    ax.tick_params(labelsize=FS)
    ax.grid(color="#bbbbbb", lw=0.3, ls=":")


def draw_river(ax, mode, kind="new", lw=1.4, ls=None, label=None):
    s = STY[mode]
    y = np.linspace(0, L, 200)
    ax.plot(river_x(y, kind), y, color=s["river"], ls=(ls or s["river_ls"]), lw=lw, zorder=3, label=label)


# ------------------------------------------------------------------ 그림 a: 연대기
def _tx(yr):
    """연도 -> 가로 위치. 1000~1400년은 압축, 1400~1750년은 끊음, 1750~2010년은 확대"""
    yr = np.asarray(yr, float)
    out = np.where(yr <= 1400, (yr - 1000) * 0.0020,
                   np.where(yr <= 1750, 0.8 + (yr - 1400) * (0.2 / 350.0), 1.0 + (yr - 1750) * 0.0115))
    return out


def fig_timeline(mode):
    c = cols(mode)
    fig, ax = plt.subplots(figsize=(WIDTH, 5.3))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.985, bottom=0.075)
    ax.set_xlim(-0.02, 4.02); ax.set_ylim(-12.0, 8.9)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_yticks([])
    tk = [1000, 1200, 1400, 1800, 1900, 2000]
    ax.set_xticks([float(_tx(v)) for v in tk]); ax.set_xticklabels([str(v) for v in tk]); ax.tick_params(labelsize=FS)
    ax.set_xlabel("연도 (1400~1750년은 생략)", fontsize=FS)
    ax.axhline(1.0, color="#999999", lw=0.5)
    ax.text(0.0, 8.7, "사료와 사건", fontsize=FS, fontweight="bold", va="top")
    ax.text(0.0, -0.2, "연구자의 생몰년", fontsize=FS, fontweight="bold", va="top")
    # 왼쪽 묶음: 글자는 표식의 오른쪽
    left = [(1044, 3.1, "요 서경 대동부 지정 1044", "o"), (1344, 2.0, "『요사』 완성 1344", "s")]
    for yr, ty, t, mk in left:
        x = float(_tx(yr))
        ax.plot([x, x], [1.0, ty], color=c["a"], lw=0.6, zorder=2)
        ax.plot(x, 1.0, mk, ms=5.5, color=(c["a"] if mode == "color" else "white"), mec=c["a"], mew=1.0, zorder=4)
        ax.text(x + 0.03, ty, t, fontsize=FS, va="center", ha="left")
    # 오른쪽 묶음: 글자는 선의 왼쪽, 높이는 연도가 늦을수록 높게
    right = [(1811, 4.0, "『아방강역고』 1811", "o"), (1906, 4.8, "『역대여지도』 1906~1911", "s"), (1908, 5.6, "홍산후 유적 발견 1908", "D"),
             (1958, 6.4, "외료하 상류 차단 1958", "^"), (1981, 7.2, "구계유형론 발표 1981", "D")]
    for yr, ty, t, mk in right:
        x = float(_tx(yr))
        ax.plot([x, x], [1.0, ty], color=c["a"], lw=0.6, zorder=2)
        ax.plot(x, 1.0, mk, ms=5.5, color=(c["a"] if mode == "color" else "white"), mec=c["a"], mew=1.0, zorder=4)
        ax.text(x - 0.03, ty, t, fontsize=FS, va="center", ha="right")
    x1, x2 = float(_tx(1982)), float(_tx(1988))
    ax.plot([x1, x2], [1.0, 1.0], color=c["c"], lw=3.5, zorder=3)
    ax.plot([x2, x2], [1.0, 8.0], color=c["c"], lw=0.6, zorder=2)
    ax.text(x2 - 0.03, 8.0, "역사지도집 1982~1988", fontsize=FS, va="center", ha="right")
    # 끊김 표시
    for xb in (0.84, 0.96):
        ax.plot([xb - 0.015, xb + 0.015], [0.8, 1.2], color="#555555", lw=0.9)
    ps = [("탈탈", 1314, 1356), ("정약용", 1762, 1836), ("양수경", 1839, 1915), ("시라토리 구라키치", 1865, 1942),
          ("도리이 류조", 1870, 1953), ("쓰다 소키치", 1873, 1961), ("소병기", 1909, 1997), ("담기양", 1911, 1992)]
    ys = [-1.6, -3.0, -4.4, -5.8, -7.2, -8.6, -10.0, -11.4]
    hat = ["", "//", "", "//", "", "//", "", "//"]
    for (nm, a, b), y, h in zip(ps, ys, hat):
        xa, xb2 = float(_tx(a)), float(_tx(b))
        ax.barh(y, xb2 - xa, left=xa, height=0.9, color=c["mid"], ec=c["a"], lw=0.8, hatch=h)
        if a > 1700:
            ax.text(xa - 0.03, y, f"{nm} {a}~{b}", fontsize=FS, va="center", ha="right")
        else:
            ax.text(xb2 + 0.03, y, f"{nm} {a}~{b}", fontsize=FS, va="center", ha="left")
    return save(fig, "ch17", "fig17-a-timeline", mode)


# ------------------------------------------------------------------ 그림 b: 도하 문형
def fig_crossing(mode, B1):
    c = cols(mode); s = STY[mode]
    fig, axs = plt.subplots(1, 3, figsize=(WIDTH, 2.35), constrained_layout=True)
    titles = ["(가) 고리·부채꼴", "(나) 강 서쪽만", "(다) 둑 3 km 허용"]
    masks = [B1["rs"], B1["both"], B1["relax"]]
    for ax, t, m in zip(axs, titles, masks):
        frame(ax, (40, 100), (30, 90), 20)
        ax.set_title(t, fontsize=FS, loc="left")
        ax.contourf(GX, GY, m.astype(float), levels=[0.5, 1.5], colors=[c["marsh"] if mode == "color" else "#bbbbbb"], zorder=1)
        ax.contour(GX, GY, m.astype(float), levels=[0.5], colors=[s["line"]], linewidths=0.9, zorder=2)
        draw_river(ax, mode, lw=1.3)
        ax.plot(*B1["c"], "^", color=s["ref"], ms=6, mfc=s["ref"] if mode == "color" else "white", mew=0.8, zorder=5)
        ax.text(B1["c"][0] - 2, B1["c"][1] + 3.5, "정읍", fontsize=FS, ha="center")
        ax.text(42, 32.5, f"{area(m):.0f} km²", fontsize=FS, ha="left", bbox=dict(fc="white", ec="none", pad=0.8))
    axs[0].set_ylabel("북 (km)")
    for ax in axs: ax.set_xlabel("동 (km)")
    return save(fig, "ch17", "fig17-b-crossing", mode)


# ------------------------------------------------------------------ 그림 c: 하도 이동
def fig_avulsion(mode, B2):
    c = cols(mode); s = STY[mode]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(WIDTH, 2.9), gridspec_kw=dict(width_ratios=[1, 1.15]), constrained_layout=True)
    frame(ax1, (20, 90), (20, 100), 20)
    y = np.linspace(0, L, 300)
    xn = river_x(y, "new"); xo = river_x(y, "old")
    ax1.fill_betweenx(y, xn - 3, xn + 3, color=c["light"], zorder=1)
    ax1.plot(xn, y, color=s["river"], ls="-", lw=1.5, zorder=3)
    ax1.plot(xo, y, color=s["river"], ls="--", lw=1.5, zorder=3)
    ax1.plot(xo[190] + 1.5, y[190], "*", color=s["truth"], ms=11, mec="black", mew=0.5, zorder=6)
    ax1.text(xn[100] + 5, y[100] + 20, "지금 유로\n(띠 ±3 km)", fontsize=FS, ha="left", linespacing=1.05)
    ax1.text(xo[100] - 3, y[100] - 6, "옛 유로", fontsize=FS, ha="right")
    ax1.text(xo[190] - 3, y[190] + 4, "참 위치", fontsize=FS, ha="right")
    ax1.set_xlabel("동 (km)"); ax1.set_ylabel("북 (km)")
    ax1.set_title("(가) 두 유로", fontsize=FS, loc="left")
    bs = [r["b"] for r in B2["rows"]]
    ex = [r["excl"] for r in B2["rows"]]
    ind = [r["ind3"] for r in B2["rows"]]
    ax2.plot(bs, [100 * e for e in ex], "o-", color=c["a"], lw=1.4, ms=5, label="세 기법이 같은 하천망을 쓸 때")
    ax2.plot(bs, [100 * e for e in ind], "s--", color=c["c"], lw=1.2, ms=5, mfc="white", label="독립이라고 가정한 계산")
    for b, e in zip(bs, ex):
        ax2.text(b + 0.5, 100 * e + 3.0, f"{100 * e:.0f}%", fontsize=FS, ha="left")
    ax2.set_xlabel("허용 폭 b (km)"); ax2.set_ylabel("참 위치를 배제하는 비율 (%)")
    ax2.set_xticks(bs); ax2.set_xlim(1.5, 23); ax2.set_ylim(0, 105); ax2.tick_params(labelsize=FS)
    ax2.legend(fontsize=FS, loc="upper right", frameon=False)
    ax2.set_title("(나) 배제 비율", fontsize=FS, loc="left")
    ax2.grid(color="#bbbbbb", lw=0.3, ls=":")
    return save(fig, "ch17", "fig17-c-avulsion", mode)


# ------------------------------------------------------------------ 그림 d: 습지 비용
def fig_marsh(mode, B3):
    c = cols(mode); s = STY[mode]
    fig, axs = plt.subplots(2, 2, figsize=(WIDTH, 4.3), constrained_layout=True)
    for ax, k in zip(axs.ravel(), (1, 2, 3, 4)):
        frame(ax, (20, 120), (20, 100), 20)
        hrs = B3["cum"][k]
        ax.contourf(GX, GY, B3["marsh"].astype(float), levels=[0.5, 1.5], colors=[c["marsh"]], hatches=[".." if mode == "bw" else None], zorder=1)
        ax.contourf(GX, GY, ((hrs >= 7) & (hrs <= 9)).astype(float), levels=[0.5, 1.5], colors=[c["d"] if mode == "color" else "#888888"], alpha=0.65, zorder=2)
        ax.contour(GX, GY, hrs, levels=[8.0], colors=[s["line"]], linewidths=1.1, zorder=3)
        draw_river(ax, mode, lw=1.1)
        ax.plot(*B3["c"], "^", color=s["ref"], ms=6, mfc=s["ref"] if mode == "color" else "white", mew=0.8, zorder=6)
        r = B3["res"][k]
        ax.set_title(f"k={k}: 서쪽 {r['west_reach']:.1f} km, 띠 {r['A_band']:.0f} km²", fontsize=FS, loc="left")
        ax.text(81, 63, "무진", fontsize=FS)
    for ax in axs[1]: ax.set_xlabel("동 (km)")
    for ax in axs[:, 0]: ax.set_ylabel("북 (km)")
    return save(fig, "ch17", "fig17-d-marsh", mode)


# ------------------------------------------------------------------ 그림 e: 이름 충돌
def fig_homonym(mode, B4):
    c = cols(mode); s = STY[mode]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(WIDTH, 2.9), gridspec_kw=dict(width_ratios=[1, 1.2]), constrained_layout=True)
    frame(ax1, (10, 70), (30, 90), 20)
    ax1.contourf(GX, GY, B4["R_mask"].astype(float), levels=[0.5, 1.5], colors=[c["d"] if mode == "color" else "#aaaaaa"], alpha=0.7, zorder=1)
    ax1.contour(GX, GY, B4["A_mask"].astype(float), levels=[0.5], colors=[c["a"]], linewidths=1.3, linestyles="-", zorder=2)
    ax1.contour(GX, GY, B4["B_mask"].astype(float), levels=[0.5], colors=[c["c"]], linewidths=1.3, linestyles="--", zorder=2)
    ax1.plot(*B4["ref"], "^", color=s["ref"], ms=6, mfc=s["ref"] if mode == "color" else "white", mew=0.8, zorder=5)
    ax1.text(61, 54, "정읍", fontsize=FS)
    ax1.text(40, 63, "A", fontsize=FS + 1, ha="center", fontweight="bold")
    ax1.text(36, 47, "B", fontsize=FS + 1, ha="center", fontweight="bold")
    ax1.set_xlabel("동 (km)"); ax1.set_ylabel("북 (km)")
    ax1.set_title("(가) 문헌 영역과 두 후보", fontsize=FS, loc="left")
    labs = ["문헌만", "문헌+날짜", "이름 한 번\n잘못 넣음", "이름 두 번\n잘못 넣음"]
    vals = [B4["P_doc"], B4["P2"], B4["P3"], B4["P4"]]
    hat = ["", "//", "xx", ".."]
    ax2.bar(range(4), [100 * v for v in vals], color=(c["mid"] if mode == "color" else "#cfcfcf"), ec=s["line"], lw=0.8, hatch=None)
    for i, h in enumerate(hat):
        ax2.patches[i].set_hatch(h)
    for i, v in enumerate(vals):
        ax2.text(i, 100 * v + 2, f"{100 * v:.0f}%", fontsize=FS, ha="center")
    ax2.axhline(50, color="#666666", lw=0.7, ls=":")
    ax2.set_xticks(range(4)); ax2.set_xticklabels(labs, fontsize=FS)
    ax2.set_ylabel("A가 맞을 확률 (%)"); ax2.set_ylim(0, 100); ax2.tick_params(labelsize=FS)
    ax2.set_title("(나) 이름 증거를 넣는 방식", fontsize=FS, loc="left")
    return save(fig, "ch17", "fig17-e-homonym", mode)


# ------------------------------------------------------------------ 그림 f: 해로
def fig_sea(mode, B5):
    c = cols(mode); s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 3.5), constrained_layout=True)
    ax.set_aspect("equal"); ax.set_xlim(60, 260); ax.set_ylim(-35, 125)
    ax.tick_params(labelsize=FS); ax.grid(color="#bbbbbb", lw=0.3, ls=":")
    pts = B5["pts"]
    ax.plot(pts[:, 0], pts[:, 1], ".", color=(c["mid"] if mode == "color" else "#999999"), ms=1.6, alpha=0.5, zorder=1, rasterized=True)
    H, xe, ye = B5["H"], B5["xe"], B5["ye"]
    flat = np.sort(H.ravel())[::-1]; cs = np.cumsum(flat); thr = flat[int(np.searchsorted(cs, 0.95 * cs[-1]))]
    xc = (xe[:-1] + xe[1:]) / 2; yc = (ye[:-1] + ye[1:]) / 2
    ax.contour(xc, yc, H.T, levels=[thr], colors=[s["line"]], linewidths=1.3, zorder=3)
    st, n1, n2 = B5["start"], B5["nominal1"], B5["nominal2"]
    ax.plot([st[0], n1[0], n2[0]], [st[1], n1[1], n2[1]], "-", color=c["c"], lw=1.5, zorder=4)
    ax.plot(*st, "^", color=s["ref"], ms=7, mfc=s["ref"] if mode == "color" else "white", mew=0.9, zorder=6)
    ax.plot(*n2, "x", color=c["c"], ms=8, mew=1.8, zorder=6)
    ax.text(st[0] + 3, st[1] - 9, "갑포", fontsize=FS)
    ax.text((st[0] + n1[0]) / 2 - 4, (st[1] + n1[1]) / 2 + 10, "동북 2일", fontsize=FS, ha="right")
    ax.text(n2[0] + 4, n2[1] + 2, "남 1일 끝(기준값)", fontsize=FS, ha="left")
    ax.text(256, -31, f"95% 영역 {B5['A95']:.0f} km²", fontsize=FS, ha="right")
    ax.set_xlabel("동 (km)"); ax.set_ylabel("북 (km)")
    return save(fig, "ch17", "fig17-f-sea", mode)


# ------------------------------------------------------------------ 그림 g: 지형 정보량
def fig_terrain(mode, B6):
    c = cols(mode); s = STY[mode]
    rows = B6["rows"]
    fig, ax = plt.subplots(figsize=(WIDTH, 3.0), constrained_layout=True)
    n = len(rows); w = 0.26
    for j, (key, lab, h) in enumerate((("bits_r", "강 3 km 이내", ""), ("bits_h", "산 5 km 이내", "//"), ("bits_b", "둘 다", "xx"))):
        v = [r[key] for r in rows]
        col = [c["mid"], c["d"], c["c"]][j] if mode == "color" else ["#e0e0e0", "#a0a0a0", "#505050"][j]
        ax.bar(np.arange(n) + (j - 1) * w, v, w, color=col, ec=s["line"], lw=0.7, hatch=h, label=lab)
        for i, x in enumerate(v):
            ax.text(i + (j - 1) * w, x + 0.08, f"{x:.1f}", fontsize=FS, ha="center")
    ax.set_xticks(range(n)); ax.set_xticklabels([r["name"].replace(", ", ",\n") for r in rows], fontsize=FS)
    ax.set_ylabel("정보량 (비트)"); ax.set_ylim(0, 8.4); ax.tick_params(labelsize=FS)
    ax.legend(fontsize=FS, frameon=False, loc="upper left", ncol=3, columnspacing=0.8, handlelength=1.4)
    return save(fig, "ch17", "fig17-g-terrain", mode)


# ------------------------------------------------------------------ 실행
def to_py(o):
    if isinstance(o, dict):
        return {str(k): to_py(v) for k, v in o.items() if not isinstance(v, np.ndarray) or v.size < 20}
    if isinstance(o, (list, tuple)):
        return [to_py(x) for x in o]
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return o


def main():
    B1 = case_b1(); B2 = case_b2(); B3 = case_b3(); B4 = case_b4(); B5 = case_b5(); B6 = case_b6(); B7 = case_b7(); B8 = case_b8()
    CV = conversions(); RF = river_facts(); EX = extra_numbers()
    for mode in ("color", "bw"):
        fig_timeline(mode); fig_crossing(mode, B1); fig_avulsion(mode, B2); fig_marsh(mode, B3)
        fig_homonym(mode, B4); fig_sea(mode, B5); fig_terrain(mode, B6)
    drop = lambda d, ks: {k: v for k, v in d.items() if k not in ks}
    res = dict(B1=drop(B1, ("rs", "both", "relax")), B2=B2, B3=dict(c=B3["c"], res=B3["res"], v=B3["v"]),
               B4=drop(B4, ("R_mask", "A_mask", "B_mask")), B5=drop(B5, ("pts", "H", "xe", "ye")), B6=drop(B6, ("masks",)),
               B7=B7, B8=B8, CV=CV, RF=RF, EX=EX)
    print(json.dumps(to_py(res), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
