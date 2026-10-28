"""figs-m15.py - 15장(서경 위치의 결론과 신뢰구간) 새 그림과 사례 계산.
실행: python3 tools/figs-m15.py        (그림/ch15 에 컬러·흑백 PDF 생성, 계산 결과 출력)
      python3 tools/figs-m15.py --nums (그림 없이 계산 결과만 출력)
이 파일의 계산(가상 구역 네 곳, 사후 확률, 지역 크기·경계 민감도, 보정 실험, 구간 비교)이 원고의 숫자의 근거이다.
모든 세계는 가상이며 서경의 결과가 아니다.
"""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from figlib import *

FS = 8.5
# ======================================================================= 가상 세계 틀
STEP = 1.0
L = 100
XS = np.arange(STEP / 2, L, STEP)          # 칸 가운데
GX, GY = np.meshgrid(XS, XS)               # GY[i,j] = 북, GX[i,j] = 동
CELL = STEP * STEP
U_MID = 0.42                               # km/리 (연습용 가정)
SD_REL = 0.15                              # 거리 어림 15% (단위 불확실 + 읽기 오차)
SD_ANG = 20.0                              # 방위 어림(도)
FLOOR = 1e-4                               # 바닥값(최댓값에 대한 비율)

# 가상 구역(갑·을·병·정): (x0, x1, y0, y1)
REG0 = {"H0": (10, 40, 40, 60), "H1": (55, 95, 55, 75), "H2": (10, 30, 5, 25), "H3": (60, 80, 10, 30)}
NAMES = {"H0": "갑", "H1": "을", "H2": "병", "H3": "정"}


def rect_mask(r):
    x0, x1, y0, y1 = r
    return ((GX >= x0) & (GX <= x1) & (GY >= y0) & (GY <= y1)).astype(float)


def scale_rect(r, f, fy=None):
    """중심은 그대로, 가로를 f배, 세로를 fy배(기본 f) 한다. 연구 창 안으로 자른다."""
    fy = f if fy is None else fy
    x0, x1, y0, y1 = r
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = (x1 - x0) * f / 2, (y1 - y0) * fy / 2
    return (max(0, cx - w), min(L, cx + w), max(0, cy - h), min(L, cy + h))


def norm(p):
    s = p.sum()
    return p / s if s > 0 else p


def dist(c):
    return np.hypot(GX - c[0], GY - c[1])


def bearing(c):
    return (np.degrees(np.arctan2(GX - c[0], GY - c[1])) + 360) % 360


def like_dist(c, li, rel=SD_REL, u=U_MID):
    mu = li * u
    return np.exp(-0.5 * ((dist(c) - mu) / (rel * mu)) ** 2)


def like_brg(c, brg, sd=SD_ANG):
    d = np.abs((bearing(c) - brg + 180) % 360 - 180)
    return np.exp(-0.5 * (d / sd) ** 2)


def like_line_y(y0, sd):
    """산의 남쪽 기슭처럼 '대략 이 위도 근처'만 말하는 약한 서술"""
    return np.exp(-0.5 * ((GY - y0) / sd) ** 2)


def with_error(l, eps):
    """서술 하나가 필사 오류일 확률 eps: 오류면 위치와 무관(창 평균)"""
    return (1 - eps) * l + eps * l.mean()


def hpd_mask(p, level=0.95):
    flat = p.ravel()
    order = np.argsort(-flat)
    cs = np.cumsum(flat[order])
    k = int(np.searchsorted(cs, level * cs[-1]) + 1)
    m = np.zeros_like(flat, dtype=bool)
    m[order[:k]] = True
    return m.reshape(p.shape)


def hpd_area(p, level=0.95):
    return float(hpd_mask(p, level).sum() * CELL)


def pieces(mask):
    lab, n = ndimage.label(mask)
    return n


def posterior_regions(lik, regs, prior):
    """주변 우도 = 구역 안 균등 사전 아래 우도의 평균. 반환: (주변 우도, 사후 확률)"""
    ml = {}
    for k, r in regs.items():
        m = rect_mask(r) > 0
        ml[k] = float(lik[m].mean()) if m.any() else 0.0
    num = {k: ml[k] * prior[k] for k in regs}
    s = sum(num.values())
    return ml, {k: num[k] / s for k in regs}


PRIOR_U = {k: 0.25 for k in REG0}
PRIOR_C = {"H0": 0.70, "H1": 0.10, "H2": 0.10, "H3": 0.10}

# 가상 증거: 참 위치 T=(25,50) 는 H0 안. (가상 사례 전용. 서경의 결과가 아니다.)
T = (25.0, 50.0)
REFS = {"가군": (50.0, 45.0), "나진": (40.0, 25.0), "다현": (30.0, 70.0)}
KIND = {"가군": "d", "나진": "db", "다현": "db"}   # d: 거리만, db: 거리와 방위
# 읽은 값(리)과 방위(도): 참 위치에서 재어 5리 단위로 반올림한 문형
def make_reads():
    out = {}
    for k, c in REFS.items():
        d = math.hypot(T[0] - c[0], T[1] - c[1])
        li = d / U_MID
        li5 = 5 * round(li / 5)
        brg = (math.degrees(math.atan2(T[0] - c[0], T[1] - c[1])) + 360) % 360
        out[k] = dict(c=c, d=d, li=li, li5=li5, brg=brg)
    return out


READS = make_reads()
# 문장에서 쓴 방위(8방위로 반올림)
def b8(brg):
    names = ["북", "북동", "동", "남동", "남", "남서", "서", "북서"]
    i = int(round(brg / 45)) % 8
    return names[i], i * 45.0


def lik_set(names, reads=None, rel=SD_REL, sd=SD_ANG, u=U_MID, eps=0.0):
    """이름 목록의 서술을 곱한 우도 지도. 서술마다 거리만(d) 또는 거리+방위(db)"""
    reads = reads or READS
    out = np.ones_like(GX)
    for item in names:
        k, kind = (item, KIND[item]) if isinstance(item, str) else item
        r = reads[k]
        l = like_dist(r["c"], r["li5"], rel, u)
        if "b" in kind:
            l = l * like_brg(r["c"], b8(r["brg"])[1], sd)
        out = out * (with_error(l, eps) if eps > 0 else l)
    return out


E_A = ["가군"]
E_B = ["가군", "다현"]
E_C = ["가군", "나진", "다현"]


def lik_three(**kw):
    return lik_set(E_C, **kw)


def cell_prior(prior=PRIOR_U, regs=REG0):
    return sum(rect_mask(r) / max(rect_mask(r).sum(), 1) * prior[k] for k, r in regs.items())


def floor_lik(l):
    return np.maximum(l, FLOOR * l.max())


# ======================================================================= 사례 계산
def reg_post(lik, regs=REG0, prior=PRIOR_U):
    ml, pu = posterior_regions(lik, regs, prior)
    return ml, pu


def case_post():
    """사례 1: 거리만 말하는 한 줄(가군에서 육십 리)과 네 구역의 사후 확률(두 사전)"""
    lik = floor_lik(lik_set(E_A))
    ml, pu = posterior_regions(lik, REG0, PRIOR_U)
    _, pc = posterior_regions(lik, REG0, PRIOR_C)
    post = norm(lik * cell_prior())
    hp = hpd_mask(post)
    bf = {}
    for a, b in (("H0", "H1"), ("H0", "H3"), ("H0", "H2")):
        bf[a + b] = ml[a] / ml[b]
    return dict(ml=ml, pu=pu, pc=pc, hpd_area=float(hp.sum() * CELL), hpd_pieces=pieces(hp), post=post, mask=hp, bf=bf,
                reads=READS, areas={k: float(rect_mask(r).sum() * CELL) for k, r in REG0.items()}, lik=lik,
                has_T=bool(hp[int(T[1] / STEP), int(T[0] / STEP)]))


def case_seq():
    """사례 2: 서술을 하나씩 더하며 사후 확률 갱신"""
    steps = [("가군 거리", [("가군", "d")]), ("+ 나진 거리", [("가군", "d"), ("나진", "d")]),
             ("+ 다현 거리", [("가군", "d"), ("나진", "d"), ("다현", "d")]), ("(대안) 가군 + 다현 거리", [("가군", "d"), ("다현", "d")])]
    rows = []
    for nm, E in steps:
        lik = floor_lik(lik_set(E))
        ml, pu = posterior_regions(lik, REG0, PRIOR_U)
        _, pc = posterior_regions(lik, REG0, PRIOR_C)
        post = norm(lik * cell_prior())
        hp = hpd_mask(post)
        rows.append(dict(name=nm, pu=pu, pc=pc, area=float(hp.sum() * CELL), pieces=pieces(hp), ml=ml))
    return rows


def case_size():
    """사례 3: H0의 세로 길이를 0.5·1·1.5·2배로 늘릴 때(가로 고정) 주변 우도와 사후 확률. 증거: 가군 거리 + 다현 거리"""
    lik = floor_lik(lik_set([("가군", "d"), ("다현", "d")]))
    rows = []
    for fy in (0.5, 1.0, 1.5, 2.0):
        regs = dict(REG0); regs["H0"] = scale_rect(REG0["H0"], 1.0, fy)
        ml, pu = posterior_regions(lik, regs, PRIOR_U)
        _, pc = posterior_regions(lik, regs, PRIOR_C)
        rows.append(dict(fy=fy, area=float(rect_mask(regs["H0"]).sum() * CELL), ml=ml["H0"], pu=pu["H0"], pc=pc["H0"],
                         has_T=bool(rect_mask(regs["H0"])[int(T[1]), int(T[0])] > 0)))
    return rows


def case_weak():
    """사례 4: '산의 남쪽 기슭' 같은 약한 서술(위도 근처만 말함)"""
    res = {}
    for sd in (30.0, 15.0, 8.0):
        lik = floor_lik(like_line_y(45.0, sd))
        ml, pu = posterior_regions(lik, REG0, PRIOR_U)
        _, pc = posterior_regions(lik, REG0, PRIOR_C)
        res[sd] = dict(ml=ml, pu=pu, pc=pc)
    return res


def case_two_peaks(eps=0.05):
    """사례 5: 두 문헌이 서로 다른 곳을 말함. 필사 오류율 eps"""
    c1, c2 = (5.0, 45.0), (98.0, 66.0)
    l1 = like_dist(c1, 50) * like_brg(c1, 90.0)
    l2 = like_dist(c2, 60) * like_brg(c2, 270.0)
    lik = floor_lik(with_error(l1, eps) * with_error(l2, eps))
    ml, pu = posterior_regions(lik, REG0, PRIOR_U)
    _, pc = posterior_regions(lik, REG0, PRIOR_C)
    post = norm(lik * cell_prior())
    m = hpd_mask(post)
    lab, n = ndimage.label(m)
    shares = [float(post[lab == i].sum()) for i in range(1, n + 1)]
    areas = [float((lab == i).sum() * CELL) for i in range(1, n + 1)]
    lik0 = l1 * l2
    # 오류율 0 이면: 두 문헌의 곱이 어디서든 얼마나 작은가
    ml0, pu0 = posterior_regions(floor_lik(lik0), REG0, PRIOR_U)
    return dict(ml=ml, pu=pu, pc=pc, n=n, shares=shares, areas=areas, post=post, mask=m, c1=c1, c2=c2,
                prod_max=float(lik0.max()), l1max=float(l1.max()), l2max=float(l2.max()), eps=eps, pu0=pu0,
                lik_max_eps=float(lik.max()))


BASE2 = [("가군", "d"), ("다현", "d")]


def case_sens_unit():
    """사례 6: 1리의 길이 가정을 바꾸었을 때 영역 면적과 H0 사후 확률(증거: 가군 거리 + 다현 거리)"""
    rows = []
    for u in (0.336, 0.378, 0.42, 0.462, 0.504):
        lik = floor_lik(lik_set(BASE2, u=u))
        ml, pu = posterior_regions(lik, REG0, PRIOR_U)
        post = norm(lik * cell_prior())
        hp = hpd_mask(post)
        cx = float((GX * post).sum()); cy = float((GY * post).sum())
        rows.append(dict(u=u, area=float(hp.sum() * CELL), pH0=pu["H0"], cx=cx, cy=cy, pieces=pieces(hp),
                         has_T=bool(hp[int(T[1]), int(T[0])]), cdist=math.hypot(cx - T[0], cy - T[1])))
    return rows


def case_sens_bound():
    """사례 7: 모든 구역의 경계를 20% 줄이거나 넓힐 때 H0의 사후 확률(증거: 가군 거리 + 다현 거리)"""
    lik = floor_lik(lik_set(BASE2))
    rows = []
    for f in (0.8, 1.0, 1.2, 1.4):
        regs = {k: scale_rect(r, f) for k, r in REG0.items()}
        ml, pu = posterior_regions(lik, regs, PRIOR_U)
        _, pc = posterior_regions(lik, regs, PRIOR_C)
        rows.append(dict(f=f, pu=pu["H0"], pc=pc["H0"], pu1=pu["H1"], areas={k: float(rect_mask(r).sum() * CELL) for k, r in regs.items()}))
    return rows


# ---- 보정 실험(눈 가린 검증): 가상 세계를 많이 만들어 사후 확률이 맞는 비율로 맞는지 센다
NOISE_LN = 0.10
def sample_world(rng, u_true):
    k = rng.choice(list(REG0))
    x0, x1, y0, y1 = REG0[k]
    tx, ty = rng.uniform(x0, x1), rng.uniform(y0, y1)
    refs = []
    while len(refs) < 2:
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(15, 40)
        rx, ry = tx + d * math.sin(a), ty + d * math.cos(a)
        if 0 <= rx <= L and 0 <= ry <= L:
            refs.append((rx, ry))
    reads = []
    for (rx, ry) in refs:
        d = math.hypot(tx - rx, ty - ry)
        li = d / u_true * (1 + rng.normal(0, NOISE_LN))
        li5 = max(5, 5 * round(li / 5))
        reads.append((rx, ry, li5))
    return k, (tx, ty), reads


def analyze(reads, prior=PRIOR_U):
    lik = np.ones_like(GX)
    for (rx, ry, li5) in reads:
        lik = lik * like_dist((rx, ry), li5)
    lik = floor_lik(lik)
    ml, pu = posterior_regions(lik, REG0, prior)
    post = norm(lik * cell_prior(prior))
    return pu, post


def calib(n=1500, seed=15, u_lo=0.36, u_hi=0.48):
    rng = np.random.default_rng(seed)
    probs, hits, cover, top = [], [], [], []
    for _ in range(n):
        u = rng.uniform(u_lo, u_hi)
        k, (tx, ty), reads = sample_world(rng, u)
        pu, post = analyze(reads)
        for kk in REG0:
            probs.append(pu[kk]); hits.append(1 if kk == k else 0)
        top.append(max(pu, key=pu.get) == k)
        hp = hpd_mask(post)
        cover.append(bool(hp[int(ty / STEP), int(tx / STEP)]))
    return np.array(probs), np.array(hits), np.array(cover), np.array(top)


def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    cen = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return cen - half, cen + half


def rel_table(probs, hits, edges=(0, 0.2, 0.4, 0.6, 0.8, 1.0001)):
    rows = []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (probs >= a) & (probs < b)
        if m.sum() > 0:
            rows.append(dict(lo=a, hi=min(b, 1.0), n=int(m.sum()), mean_p=float(probs[m].mean()), freq=float(hits[m].mean())))
    return rows


def case_calibration():
    out = {}
    for nm, (lo, hi) in (("정상", (0.36, 0.48)), ("어긋남", (0.27, 0.33))):
        pr, ht, cv, tp = calib(1500, 15, lo, hi)
        n150 = 150
        k150 = int(cv[:n150].sum())
        out[nm] = dict(rel=rel_table(pr, ht), cover=float(cv.mean()), k150=k150, n150=n150, w150=wilson(k150, n150),
                       cover_all=int(cv.sum()), n_all=len(cv), top=float(tp.mean()), probs=pr, hits=ht)
    return out


def case_info():
    """사례 8: 다음에 채울 자료 고르기. 기본(가군 거리 + 다현 거리)에 서술 하나를 더할 때 95% 영역 면적과 조각 수"""
    base = lik_set(BASE2)
    pc_ = cell_prior()
    lb = floor_lik(base)
    hp0 = hpd_mask(norm(lb * pc_))
    out = {"base_area": float(hp0.sum() * CELL), "base_pieces": pieces(hp0), "cands": {}}
    cands = {}
    c = (50.0, 20.0); d = math.hypot(T[0] - c[0], T[1] - c[1]); li = 5 * round(d / U_MID / 5)
    cands["가: 다른 쪽에서 거리"] = (like_dist(c, li), c, li)
    c = (60.0, 52.0); d = math.hypot(T[0] - c[0], T[1] - c[1]); li = 5 * round(d / U_MID / 5)
    cands["나: 가까운 곳에서 거리"] = (like_dist(c, li), c, li)
    cands["다: 위도 근처만(약함)"] = (like_line_y(48.0, 15.0), None, None)
    c = (60.0, 50.0); brg = (math.degrees(math.atan2(T[0] - c[0], T[1] - c[1])) + 360) % 360
    cands["라: 방위만"] = (like_brg(c, b8(brg)[1], SD_ANG), c, b8(brg))
    for k, (l, c, extra) in cands.items():
        lk = floor_lik(base * l)
        hp = hpd_mask(norm(lk * pc_))
        out["cands"][k] = dict(area=float(hp.sum() * CELL), pieces=pieces(hp), c=c, extra=extra)
    return out


def case_interval():
    """사례 10: 신뢰구간과 신용구간(1차원): 같아지는 경우와 달라지는 경우"""
    x, s = 21.0, 2.1
    ci = (x - 1.96 * s, x + 1.96 * s)
    mu0, s0 = 18.0, 3.0
    prec = 1 / s ** 2 + 1 / s0 ** 2
    var = 1 / prec
    mean = (x / s ** 2 + mu0 / s0 ** 2) * var
    sd = math.sqrt(var)
    cred = (mean - 1.96 * sd, mean + 1.96 * sd)
    # 반복 실험: 참값이 N(24,1) 에서 나오는데 분석자는 사전 N(18,3) 을 쓴 경우의 적중
    rng = np.random.default_rng(3)
    n = 200000
    truth = rng.normal(24.0, 1.0, n)
    obs = truth + rng.normal(0, s, n)
    cov_ci = float(((obs - 1.96 * s <= truth) & (truth <= obs + 1.96 * s)).mean())
    post_mean = (obs / s ** 2 + mu0 / s0 ** 2) * var
    cov_cr = float(((post_mean - 1.96 * sd <= truth) & (truth <= post_mean + 1.96 * sd)).mean())
    # 사전이 맞을 때: 참값이 N(18,3)에서 나옴
    truth2 = rng.normal(mu0, s0, n)
    obs2 = truth2 + rng.normal(0, s, n)
    pm2 = (obs2 / s ** 2 + mu0 / s0 ** 2) * var
    cov_cr_ok = float(((pm2 - 1.96 * sd <= truth2) & (truth2 <= pm2 + 1.96 * sd)).mean())
    cov_ci_ok = float(((obs2 - 1.96 * s <= truth2) & (truth2 <= obs2 + 1.96 * s)).mean())
    return dict(ci=ci, cred=cred, mean=mean, sd=sd, cov_ci=cov_ci, cov_cr=cov_cr, cov_cr_ok=cov_cr_ok, cov_ci_ok=cov_ci_ok,
                wid_ci=ci[1] - ci[0], wid_cr=cred[1] - cred[0])


def case_eps():
    """사례 B11: 사례 B4의 두 문헌에서 필사 오류율을 바꿀 때의 조각 수, 조각 몫, 구역 확률"""
    rows = []
    for eps in (0.01, 0.05, 0.10, 0.20, 0.40):
        D = case_two_peaks(eps)
        rows.append(dict(eps=eps, n=D["n"], shares=D["shares"], areas=D["areas"], pu=D["pu"], pc=D["pc"]))
    return rows


def calib_double(n=1500, seed=15, u_lo=0.36, u_hi=0.48, power=2.0):
    """사례 B12: 같은 서술을 power번 센 경우(우도를 power제곱)의 95% 영역 적중과 구역 확률의 보정"""
    rng = np.random.default_rng(seed)
    probs, hits, cover, areas = [], [], [], []
    for _ in range(n):
        u = rng.uniform(u_lo, u_hi)
        k, (tx, ty), reads = sample_world(rng, u)
        lik = np.ones_like(GX)
        for (rx, ry, li5) in reads:
            lik = lik * like_dist((rx, ry), li5) ** power
        lik = floor_lik(lik)
        ml, pu = posterior_regions(lik, REG0, PRIOR_U)
        post = norm(lik * cell_prior(PRIOR_U))
        hp = hpd_mask(post)
        for kk in REG0:
            probs.append(pu[kk]); hits.append(1 if kk == k else 0)
        cover.append(bool(hp[int(ty / STEP), int(tx / STEP)]))
        areas.append(float(hp.sum() * CELL))
    return np.array(probs), np.array(hits), np.array(cover), np.array(areas)


def case_double():
    out = {}
    for pw in (1.0, 2.0, 3.0):
        pr, ht, cv, ar = calib_double(1500, 15, 0.36, 0.48, pw)
        out[pw] = dict(cover=float(cv.mean()), k150=int(cv[:150].sum()), w150=wilson(int(cv[:150].sum()), 150), area=float(ar.mean()),
                       med_area=float(np.median(ar)), rel=rel_table(pr, ht))
    return out


def all_cases():
    return dict(post=case_post(), seq=case_seq(), size=case_size(), weak=case_weak(), two=case_two_peaks(), unit=case_sens_unit(),
                bound=case_sens_bound(), calib=case_calibration(), info=case_info(), interval=case_interval(), eps=case_eps(), double=case_double())


# ======================================================================= 그림
def box(ax, x, y, w, h, text, mode, fc=None, ls="-", fs=FS, bold=False, hatch=None):
    s = STY[mode]
    fc = fc or ("#ffffff" if mode == "bw" else "#fdf3e1")
    p = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=fc, ec=s["line"],
                       lw=0.9, ls=ls, hatch=hatch, zorder=3)
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, zorder=4, fontweight="bold" if bold else "normal", linespacing=1.15,
            bbox=dict(fc="white", ec="none", pad=1.5) if hatch else None)


def arrow(ax, x1, y1, x2, y2, mode, ls="-", lw=1.1):
    s = STY[mode]
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=s["line"], lw=lw, ls=ls,
                                                                 shrinkA=0, shrinkB=0), zorder=2)


def fig_timeline(mode):
    """연대기 종합 그림: 가로 시간축 1600~2020, 세 줄. 글자는 모두 줄 위에, 연도 눈금은 줄 아래에"""
    s = STY[mode]
    cA = "#1f6fb8" if mode == "color" else "#000000"
    cB = "#2e7d32" if mode == "color" else "#444444"
    cC = "#c0392b" if mode == "color" else "#777777"
    fig, ax = plt.subplots(figsize=(WIDTH, 5.0))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.99, bottom=0.01)
    ax.set_xlim(1585, 2100); ax.set_ylim(-1.6, 12.4); ax.axis("off")
    ys = {"A": 8.6, "B": 4.4, "C": 0.6}
    cols = {"A": cA, "B": cB, "C": cC}
    mk = {"A": "o", "B": "s", "C": "D"}
    lab = {"A": "확률과 구간 추정", "B": "불확실성 보고와 검증", "C": "한국의 역사지리"}
    for k, y in ys.items():
        ax.plot([1600, 2090], [y, y], color=cols[k], lw=2.0, ls={"A": "-", "B": "--", "C": "-."}[k], zorder=2)
        ax.text(1587, y - 0.35, lab[k], fontsize=FS, fontweight="bold", color=cols[k], ha="left", va="top")
        for yr in range(1600, 2001, 100):
            ax.plot([yr, yr], [y - 0.12, y + 0.12], color=s["line"], lw=0.8, zorder=3)
            ax.text(yr, y - 0.95 if yr > 1700 else y - 1.0, str(yr), ha="center", va="top", fontsize=FS, color=s["gray"])
    # (줄, 해, 글자 가운데 x, 높이 단계, 글자)
    items = [
        ("A", 1763, 1725, 1, "베이즈\n1763"), ("A", 1774, 1805, 2, "라플라스\n1774"),
        ("A", 1890, 1880, 1, "챔벌린\n1890"), ("A", 1927, 1928, 2, "윌슨\n1927"),
        ("A", 1937, 1970, 1, "네이만\n1937"), ("A", 1939, 2022, 1, "제프리스\n1939"),
        ("B", 1982, 1945, 1, "다위드\n1982"), ("B", 1995, 1990, 2, "캐스·래프터리\n1995"),
        ("B", 2010, 2006, 1, "IPCC\n2010"), ("B", 2014, 2068, 1, "호크스트라\n외 2014"),
        ("C", 1615, 1640, 1, "한백겸\n1615"), ("C", 1811, 1811, 1, "정약용\n1811"),
    ]
    for k, yr, tx, lv, t in items:
        y = ys[k]
        ty = y + 0.8 + (lv - 1) * 1.45
        ax.plot([yr, tx], [y, ty], color=cols[k], lw=0.7, zorder=2)
        ax.plot(yr, y, mk[k], ms=5, color=cols[k] if mode == "color" else "white", mec=cols[k], mew=1.0, zorder=4)
        ax.text(tx, ty, t, ha="center", va="bottom", fontsize=FS, linespacing=1.05)
    ax.text(2096, -1.4, "이 장의 결론 문장은 세 줄이 만나는 자리에 놓인다", ha="right", va="bottom", fontsize=FS)
    return save(fig, "ch15", "fig15-a-timeline", mode)


def fig_blanks(mode):
    """일곱 빈칸이 어느 장에서 채워지는가"""
    s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 3.5))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.99, bottom=0.01)
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.6); ax.axis("off")
    xs = [1.6, 5.0, 8.4]
    for nm, x in zip(["13장에서", "14장에서", "15장에서"], xs):
        ax.text(x, 6.2, nm, ha="center", va="center", fontsize=FS + 1, fontweight="bold")
    cells = [(1, "증거 집합 E", 0, 0), (2, "영역 R, 면적 A,\n조각 m", 0, 1), (3, "눈 가린 검증\n적중률 c", 0, 2),
             (6, "공유 가정\n민감도", 1, 1), (4, "사후 확률\n(무차별 사전)", 2, 0), (5, "사후 확률\n(보수적 사전)", 2, 1), (7, "영역 경계\n민감도", 2, 2)]
    fc_gray = "#dddddd" if mode == "bw" else "#f6d5d0"
    for n, t, c, r in cells:
        y = 5.0 - r * 1.75
        crit = n in (3, 6)
        box(ax, xs[c], y, 2.9, 1.2, f"빈칸 {n}\n{t}", mode, ls="--" if crit else "-", fc=fc_gray if crit else None)
    ax.text(5.0, 0.55, "회색 점선 상자(빈칸 3, 6)가 비면 신용영역이라 부르지 않는다.", ha="center", va="center", fontsize=FS)
    return save(fig, "ch15", "fig15-b-blanks", mode)


def fig_post_bars(mode, C):
    """무차별·보수적 사전에서 네 구역의 사후 확률(가상 사례 1)"""
    s = STY[mode]
    P = C["post"]
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 2.9), constrained_layout=True, gridspec_kw=dict(width_ratios=[1, 1.15]))
    # (가) 가상 구역 지도
    ax = axs[0]
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.set_aspect("equal")
    ax.set_xticks(range(0, 101, 50)); ax.set_yticks(range(0, 101, 50))
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    ax.set_title("(가) 구역과 한 줄의 거리", fontsize=FS, loc="left")
    hat = {"H0": "", "H1": "//", "H2": "..", "H3": "xx"}
    fills = {"H0": "#f0b45a", "H1": "#7fb3d5", "H2": "#a5d6a7", "H3": "#d7bde2"} if mode == "color" else {"H0": "#bdbdbd", "H1": "#ffffff", "H2": "#e0e0e0", "H3": "#ffffff"}
    for k, (x0, x1, y0, y1) in REG0.items():
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fills[k], ec=s["line"], lw=0.8, hatch=hat[k], alpha=0.9))
        ax.text(x0 + 1.5, y1 - 1.5, k, ha="left", va="top", fontsize=FS, bbox=dict(fc="white", ec="none", pad=0.8))
    c = REFS["가군"]
    ax.plot(*c, "^", color=s["ref"], ms=5, mfc=s["ref"] if mode == "color" else "white", mew=0.8, zorder=6)
    ax.annotate("가군", c, xytext=(3, -11), textcoords="offset points", fontsize=FS)
    th = np.linspace(0, 2 * math.pi, 200)
    mu = READS["가군"]["li5"] * U_MID
    ax.plot(c[0] + mu * np.sin(th), c[1] + mu * np.cos(th), color=s["line"], lw=1.0, ls="--", zorder=5)
    ax.plot(*T, "*", color=s["truth"], ms=9, mec="black", mew=0.5, zorder=6)
    # (나) 막대
    ax = axs[1]
    ks = list(REG0)
    xs = np.arange(4)
    w = 0.38
    ax.bar(xs - w / 2, [P["pu"][k] for k in ks], w, color="#1f6fb8" if mode == "color" else "#ffffff", ec=s["line"], hatch="" if mode == "color" else "//", label="무차별 사전")
    ax.bar(xs + w / 2, [P["pc"][k] for k in ks], w, color="#f0b45a" if mode == "color" else "#555555", ec=s["line"], label="보수적 사전")
    for i, k in enumerate(ks):
        ax.text(i, P["pu"][k] + 0.02, f"{P['pu'][k]:.3f}", ha="right", fontsize=FS - 0.5)
        ax.text(i, P["pc"][k] + 0.02, f"{P['pc'][k]:.3f}", ha="left", fontsize=FS - 0.5)
    ax.set_xticks(xs); ax.set_xticklabels(ks); ax.set_ylim(0, 1.15)
    ax.set_ylabel("사후 확률")
    ax.set_title("(나) 두 사전의 사후 확률", fontsize=FS, loc="left")
    ax.legend(loc="upper right", frameon=False)
    return save(fig, "ch15", "fig15-c-post-bars", mode)


def fig_size(mode, C):
    """지역 크기와 경계: (가) H0 세로를 늘릴 때 주변 우도와 사후 확률, (나) 경계를 늘릴 때 H0 사후 확률"""
    s = STY[mode]
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 2.9), constrained_layout=True)
    rows = C["size"]
    ax = axs[0]
    ar = [r["area"] for r in rows]
    ax.plot(ar, [r["ml"] for r in rows], "o-", color="#1f6fb8" if mode == "color" else "#000", label="H0의 주변 우도")
    for a, r in zip(ar, rows):
        ax.annotate(f"{r['ml']:.3f}", (a, r["ml"]), xytext=(0, 6), textcoords="offset points", ha="center", fontsize=FS - 0.5)
    ax.set_xlabel("H0의 면적 (km²)"); ax.set_ylabel("주변 우도(상대값)")
    ax.set_xlim(150, 1350); ax.set_ylim(0, max(r["ml"] for r in rows) * 1.25)
    ax.set_title("(가) 같은 증거, 넓어지는 H0", fontsize=FS, loc="left")
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    ax = axs[1]
    rb = C["bound"]
    fx = [r["f"] * 100 - 100 for r in rb]
    ax.plot(fx, [r["pu"] for r in rb], "o-", color="#1f6fb8" if mode == "color" else "#000", label="무차별 사전")
    ax.plot(fx, [r["pc"] for r in rb], "s--", color="#c0392b" if mode == "color" else "#555", label="보수적 사전")
    ax.set_xlabel("모든 구역의 경계를 바꾼 정도 (%)"); ax.set_ylabel("H0의 사후 확률")
    ax.set_ylim(0.55, 1.03); ax.set_xticks(fx)
    ax.set_title("(나) 경계를 바꾸면", fontsize=FS, loc="left")
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    ax.legend(loc="lower left", frameon=False)
    return save(fig, "ch15", "fig15-d-size-bound", mode)


def fig_calib(mode, C):
    """보정 곡선: 정상 가정 대 어긋난 가정"""
    s = STY[mode]
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 2.9), constrained_layout=True)
    ax = axs[0]
    ax.plot([0, 1], [0, 1], color=s["gray"], lw=0.8, ls=":")
    sty = {"정상": ("o-", "#1f6fb8" if mode == "color" else "#000"), "어긋남": ("s--", "#c0392b" if mode == "color" else "#555")}
    for nm in ("정상", "어긋남"):
        r = C["calib"][nm]["rel"]
        ax.plot([x["mean_p"] for x in r], [x["freq"] for x in r], sty[nm][0], color=sty[nm][1], label=("단위를 맞게 가정" if nm == "정상" else "단위 가정이 어긋남(실제 0.30)"))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02)
    ax.set_xlabel("말한 사후 확률"); ax.set_ylabel("실제로 맞은 비율")
    ax.set_title("(가) 구역 확률의 보정", fontsize=FS, loc="left")
    ax.legend(loc="upper left", frameon=False)
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    ax = axs[1]
    names = ["정상", "어긋남"]
    vals = [C["calib"][n]["cover"] * 100 for n in names]
    ax.bar([0, 1], vals, 0.5, color=["#1f6fb8", "#c0392b"] if mode == "color" else ["#ffffff", "#555555"], ec=s["line"], hatch="" if mode == "color" else "//")
    ax.axhline(95, color=s["line"], lw=0.9, ls="--")
    ax.text(0.5, 96, "명목 95%", ha="center", va="bottom", fontsize=FS)
    for i, v in enumerate(vals):
        ax.text(i, v + 1.5, f"{v:.1f}%", ha="center", fontsize=FS)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["단위 맞게", "단위 어긋남"]); ax.set_ylim(0, 112)
    ax.set_ylabel("95% 영역의 적중 (%)")
    ax.set_title("(나) 영역의 적중률", fontsize=FS, loc="left")
    return save(fig, "ch15", "fig15-e-calibration", mode)


def fig_two(mode, C):
    """두 문헌이 어긋날 때: 조각 둘"""
    s = STY[mode]
    D = C["two"]
    fig, ax = plt.subplots(figsize=(WIDTH, 3.0), constrained_layout=True)
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.set_aspect("equal")
    ax.set_xticks(range(0, 101, 25)); ax.set_yticks(range(0, 101, 25))
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    ax.imshow(D["post"], origin="lower", extent=(0, 100, 0, 100), cmap=s["cmap"], alpha=0.85)
    ax.contour(GX, GY, D["mask"].astype(float), levels=[0.5], colors=[s["line"]], linewidths=1.2)
    hat = {"H0": "", "H1": "//", "H2": "..", "H3": "xx"}
    for k, (x0, x1, y0, y1) in REG0.items():
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="none", ec=s["line"], lw=0.7, ls="--"))
        ax.text(x0 + 1.5, y1 - 1.5, k, ha="left", va="top", fontsize=FS, bbox=dict(fc="white", ec="none", pad=0.8))
    for c, nm in ((D["c1"], "가군"), (D["c2"], "라읍")):
        ax.plot(*c, "^", color=s["ref"], ms=5, mfc=s["ref"] if mode == "color" else "white", mew=0.8)
        ax.annotate(nm, c, xytext=(-8, -13), textcoords="offset points", fontsize=FS)
    ax.set_xlabel("동 (km)"); ax.set_ylabel("북 (km)")
    ax.set_title(f"두 문헌이 어긋난 가상 사례: 95% 영역은 조각 {D['n']}개", fontsize=FS, loc="left")
    return save(fig, "ch15", "fig15-f-two-pieces", mode)


def figures(C):
    out = []
    for mode in ("color", "bw"):
        out.append(fig_timeline(mode))
        out.append(fig_blanks(mode))
        out.append(fig_post_bars(mode, C))
        out.append(fig_size(mode, C))
        out.append(fig_calib(mode, C))
        out.append(fig_two(mode, C))
    return out


def show(C):
    P = C["post"]
    print("READS", {k: (round(v["d"], 2), round(v["li"], 1), v["li5"], round(v["brg"], 1), b8(v["brg"])) for k, v in READS.items()})
    print("areas", P["areas"])
    print("POST ml", {k: round(v, 4) for k, v in P["ml"].items()}, "pu", {k: round(v, 4) for k, v in P["pu"].items()}, "pc", {k: round(v, 4) for k, v in P["pc"].items()})
    print("   hpd", P["hpd_area"], P["hpd_pieces"], P["has_T"], "bf", {k: round(v, 3) for k, v in P["bf"].items()})
    print("SEQ")
    for r in C["seq"]:
        print("  ", r["name"], {k: round(v, 4) for k, v in r["pu"].items()}, {k: round(v, 4) for k, v in r["pc"].items()}, r["area"], r["pieces"])
    print("SIZE")
    for r in C["size"]:
        print("  ", r)
    print("WEAK")
    for sd, r in C["weak"].items():
        print("  ", sd, {k: round(v, 4) for k, v in r["ml"].items()}, {k: round(v, 4) for k, v in r["pu"].items()}, {k: round(v, 4) for k, v in r["pc"].items()})
    t = C["two"]
    print("TWO", {k: round(v, 5) for k, v in t["ml"].items()}, {k: round(v, 4) for k, v in t["pu"].items()}, {k: round(v, 4) for k, v in t["pc"].items()}, t["n"], t["shares"], t["areas"], t["prod_max"], t["l1max"], t["l2max"], t["pu0"], t["lik_max_eps"])
    print("UNIT")
    for r in C["unit"]:
        print("  ", r)
    print("BOUND")
    for r in C["bound"]:
        print("  ", r)
    print("CALIB")
    for nm, r in C["calib"].items():
        print("  ", nm, "cover", r["cover"], r["cover_all"], r["n_all"], "k150", r["k150"], r["w150"], "top", r["top"])
        for x in r["rel"]:
            print("      ", x)
    print("INFO", C["info"])
    print("INTERVAL", C["interval"])
    print("EPS")
    for r in C["eps"]:
        print("  ", r["eps"], r["n"], [round(x, 4) for x in r["shares"]], r["areas"], {k: round(v, 4) for k, v in r["pu"].items()}, {k: round(v, 4) for k, v in r["pc"].items()})
    print("DOUBLE")
    for pw, r in C["double"].items():
        print("  ", pw, "cover", r["cover"], "k150", r["k150"], r["w150"], "area mean", round(r["area"], 1), "median", r["med_area"])
        for x in r["rel"]:
            print("      ", x)


if __name__ == "__main__":
    C = all_cases()
    show(C)
    if "--nums" not in sys.argv:
        for p in figures(C):
            print(p)
