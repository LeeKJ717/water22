"""figs-m18.py - 18장(산동 지역) 새 그림과 새 사례 계산.
실행: python3 tools/figs-m18.py        (그림/ch18 에 컬러·흑백 PDF 생성, 계산 결과를 표준 출력으로 인쇄)
      python3 tools/figs-m18.py --nums  (그림 없이 계산 결과만 인쇄)
이 파일의 계산 함수는 원고의 새 숫자의 근거이다. 모든 가상 사례는 서경의 결과가 아니다.
실제 지명의 좌표·높이·연도는 원고 본문에 출처를 단 것만 쓴다(위키백과 상자 값).
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from figlib import *

FS = 8.5
U_LO, U_HI, U_MID = 0.36, 0.48, 0.42   # km/리, 12장과 같은 연습용 가정


def dms(d, m=0, s=0):
    return d + m / 60 + s / 3600


def hav(a, b):
    R = 6371.0
    la1, lo1 = map(math.radians, a); la2, lo2 = map(math.radians, b)
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


# ======================================================================= 1. 실제 지리 사실(위키백과 상자 값)로 하는 계산
PLACES = {
    "penglai": (dms(37, 49), dms(120, 44)),          # 봉래(옛 등주), 37°49′N 120°44′E
    "lushun": (dms(38, 51, 3), dms(121, 15, 25)),    # 여순구, 38°51′03″N 121°15′25″E
    "taishan": (dms(36, 15, 21), dms(117, 6, 27)),   # 태산 옥황정, 36°15′21″N 117°06′27″E
    "dongying": (dms(37, 54), dms(118, 57)),         # 황하삼각주 보호구, 37°54′N 118°57′E
    "shandong": (dms(36, 24), dms(118, 24)),         # 산동성 상자 좌표, 36°24′N 118°24′E
}
SD_AREA = 157100.0   # km², 산동성(위키백과)


def real_numbers():
    o = {}
    for a, b in [("penglai", "lushun"), ("penglai", "taishan"), ("taishan", "dongying"), ("penglai", "dongying"),
                 ("shandong", "penglai"), ("shandong", "taishan"), ("shandong", "dongying")]:
        o[f"{a}-{b}"] = hav(PLACES[a], PLACES[b])
    o["sd_side"] = math.sqrt(SD_AREA)
    o["tai_diff"] = (1545 - 1532.7, 1534 - 1532.7)
    o["yr_span"] = 602 + 1946 - 1
    o["flood_rate"] = 1593 / o["yr_span"]
    o["flood_3yr"] = o["flood_rate"] * 3
    o["change_century"] = 26 / o["yr_span"] * 100
    o["change_gap"] = o["yr_span"] / 26
    lam = 26 / o["yr_span"]
    o["lambda"] = lam
    o["p_nochange"] = {T: math.exp(-lam * T) for T in (10, 20, 50, 100, 200)}
    o["south_years"] = 1855 - 1128
    o["mouth_years"] = 1976 - 1855
    o["mouth_gap"] = o["mouth_years"] / 50
    o["delta_km2_yr"] = 3240 / 100
    o["reserve_diff_pct"] = (154000 - 153000) / 153000 * 100
    o["gap_1081_1128"] = 1128 - 1081
    o["gap_1128_1145"] = 1145 - 1128
    o["gap_1128_1135"] = 1135 - 1128
    o["gap_1048_1081"] = 1081 - 1048
    o["gap_1081_1099"] = 1099 - 1081
    o["gap_1099_1128"] = 1128 - 1099
    o["incl_552_593"] = (593 - 552, 593 - 552 + 1)
    return o


def li_km(li, lo=U_LO, hi=U_HI):
    return li * lo, li * hi


def unit_table():
    rows = []
    for name, li in [("12리(각자성석 제2석)", 12), ("25~42리(평양부 네 경계)", 42), ("30리(동명왕묘)", 30),
                     ("1000리(후한서 고구려)", 1000), ("2000리(북사 동서)", 2000), ("4000리(현도군~낙양)", 4000)]:
        a, b = li_km(li)
        rows.append((name, li, a, b, b - a, a / math.sqrt(SD_AREA), b / math.sqrt(SD_AREA)))
    return rows


# ======================================================================= 2. 가상 사례 계산
STEP = 0.5
XS = np.arange(0, 60 + 1e-9, STEP)
GX, GY = np.meshgrid(XS, XS)
CELL = STEP * STEP


def dist(c):
    return np.hypot(GX - c[0], GY - c[1])


def bearing(c):
    return (np.degrees(np.arctan2(GX - c[0], GY - c[1])) + 360) % 360


def ring(c, lo, hi):
    d = dist(c)
    return ((d >= lo) & (d <= hi)).astype(float)


def sector(c, brg, half):
    b = bearing(c)
    diff = np.abs((b - brg + 180) % 360 - 180)
    return (diff <= half).astype(float)


def area(mask):
    return float(mask.sum() * CELL)


def case_b1(n=200000, seed=18):
    """가상: 바닷길 세 구간. 구간마다 방위는 8방위의 반폭 22.5도 안에서 고르게, 거리는 리 수 x 단위(0.36~0.48)."""
    rng = np.random.default_rng(seed)
    legs = [(45.0, 300), (180.0, 200), (315.0, 150)]   # (방위각, 리)
    out = {"legs": legs}
    for mode_name in ("단위 공유", "단위 따로"):
        pos = np.zeros((n, 2))
        res = []
        if mode_name == "단위 공유":
            u_shared = rng.uniform(U_LO, U_HI, n)
        for k, (brg, li) in enumerate(legs, 1):
            u = u_shared if mode_name == "단위 공유" else rng.uniform(U_LO, U_HI, n)
            th = np.radians(brg + rng.uniform(-22.5, 22.5, n))
            d = li * u
            pos = pos + np.stack([d * np.sin(th), d * np.cos(th)], axis=1)
            # 95% 영역 넓이: 1 km 칸 히스토그램의 HPD
            H, xe, ye = np.histogram2d(pos[:, 0], pos[:, 1], bins=[np.arange(pos[:, 0].min() - 1, pos[:, 0].max() + 2, 1.0), np.arange(pos[:, 1].min() - 1, pos[:, 1].max() + 2, 1.0)])
            flat = np.sort(H.ravel())[::-1]
            cs = np.cumsum(flat) / flat.sum()
            kk = int(np.searchsorted(cs, 0.95) + 1)
            res.append(dict(k=k, area95=kk * 1.0, cx=float(pos[:, 0].mean()), cy=float(pos[:, 1].mean()),
                            sdx=float(pos[:, 0].std()), sdy=float(pos[:, 1].std()), snap=pos[:1500].copy()))
        out[mode_name] = res
        out[mode_name + "_pos"] = pos[:4000].copy()
    # 결정적 중심 경로(단위 중간값, 방위 가운데)
    mid = np.zeros(2); path = [mid.copy()]
    for brg, li in legs:
        d = li * U_MID; th = math.radians(brg)
        mid = mid + np.array([d * math.sin(th), d * math.cos(th)]); path.append(mid.copy())
    out["mid_path"] = np.array(path)
    out["leg_km"] = [li * U_MID for _, li in legs]
    out["total_km"] = sum(out["leg_km"])
    out["sd_area_ratio"] = {m: [r["area95"] / SD_AREA for r in out[m]] for m in ("단위 공유", "단위 따로")}
    return out


def case_b2():
    """가상: 육로와 해로가 섞인 서술의 분류와 계산 가능 비율"""
    sents = [
        ("갑포에서 서쪽으로 육로 사십 리", "육", "리", True),
        ("을포에서 배로 사흘", "해", "일", False),
        ("병진에서 동북으로 바닷길 이백 리", "해", "리", False),
        ("정현에서 북쪽으로 육로 하루 길", "육", "일", True),
        ("무도에서 남쪽으로 바다를 건너 백 리", "해", "리", False),
        ("기성은 갑포의 동쪽 삼십 리", "육", "리", True),
        ("경성에서 배로 이틀, 육로로 하루", "혼합", "일", False),
    ]
    n = len(sents)
    land_ok = sum(1 for s in sents if s[3])
    return dict(sents=sents, n=n, land_ok=land_ok, frac=land_ok / n, n_sea=sum(1 for s in sents if s[1] == "해"),
                n_mix=sum(1 for s in sents if s[1] == "혼합"))


def case_b3():
    """가상: 같은 문장을 옛 하도와 새 하도로 읽을 때 후보 영역이 얼마나 달라지나.
    문장: '성은 갑군의 동쪽 오십 리, 강의 북쪽 오 리 안'. 참 위치는 옛 하도 시기에 만들어진 성."""
    gun = (9.0, 30.0)
    # 옛 하도: 동쪽으로 완만한 S자(남북으로 흐름), 새 하도: 서쪽으로 15 km 이동한 직선
    yy = XS
    old_x = 36 + 4 * np.sin(yy / 60 * 2 * math.pi * 1.5)
    new_x = np.full_like(yy, 24.0)
    def river_band(rx, lo_km, hi_km):
        # 강 동쪽(하류 방향을 북으로 볼 때 강의 오른쪽) 아닌 '북쪽'이라는 말은 가상으로 '강 기준 동쪽 둑 쪽'으로 단순화
        m = np.zeros(GX.shape)
        for i in range(GX.shape[0]):
            dx = GX[i, :] - rx[i]
            m[i, :] = ((dx >= lo_km) & (dx <= hi_km)).astype(float)
        return m
    # '강의 동안(東岸)에서 2.4 km(5리) 안'을 만족하는 칸
    band_old = river_band(old_x, 0.0, 2.4)
    band_new = river_band(new_x, 0.0, 2.4)
    ring_g = ring(gun, 45 * U_LO, 55 * U_HI) * sector(gun, 90.0, 22.5)
    reg_old = band_old * ring_g
    reg_new = band_new * ring_g
    T = None
    # 참 위치: 옛 하도 동안 1.2 km 안, 갑군에서 21 km
    out = dict(ring_area=area(ring_g > 0), band_old=area(band_old > 0), band_new=area(band_new > 0),
               old_x=old_x, new_x=new_x, ring_g=ring_g, reg_old=reg_old, reg_new=reg_new)
    out["reg_old_area"] = area(reg_old > 0); out["reg_new_area"] = area(reg_new > 0)
    out["overlap_area"] = area((reg_old * reg_new) > 0)
    out["union_area"] = area(((reg_old + reg_new) > 0))
    out["gun"] = gun
    return out


def case_b4():
    """가상: 해안선이 퇴적으로 바다 쪽으로 나아갈 때 '바다에 임한다'를 읽는 법.
    1차원 단면. 가정 속도 r km/년, 경과 T년. 성은 해안에서 d 이내에 있어야 '임한다'."""
    r, T, d = 0.5, 80, 2.0
    shift = r * T
    return dict(r=r, T=T, d=d, shift=shift, gap=shift - d, r_alt=[0.1, 0.5, 2.2], shift_alt=[x * T for x in (0.1, 0.5, 2.2)],
                t_need=[d / x for x in (0.1, 0.5, 2.2)])


def case_b5():
    """가상: 같은 이름을 가진 세 후보(가, 나, 다)와 세 줄의 증거. 우도는 연습용 숫자."""
    prior = np.array([1 / 3, 1 / 3, 1 / 3])
    # 증거 1(거리 서술), 증거 2(지형 서술), 증거 3(시기 서술)에 대한 각 후보의 우도
    L = np.array([[0.30, 0.10, 0.05],
                  [0.20, 0.20, 0.10],
                  [0.40, 0.05, 0.40]])
    out = {"prior": prior, "L": L}
    post = prior * L.prod(axis=0)
    out["post"] = post / post.sum()
    out["loo"] = []
    for k in range(3):
        idx = [i for i in range(3) if i != k]
        p = prior * L[idx].prod(axis=0)
        out["loo"].append(p / p.sum())
    out["prod"] = L.prod(axis=0)
    # 증거 3 하나만 뺐을 때와 순서 바꿔 곱해도 같음
    return out


def case_b6():
    """가상: 같은 바닷길 거리를 두고 날 수 서술이 어떻게 달라지는가. 가정 속도(km/시)와 하루 항해 시간(시)."""
    d_km = 300 * U_MID                        # 300리 = 126 km
    h = 10.0
    sp = (2.0, 4.0)
    days = (d_km / (sp[1] * h), d_km / (sp[0] * h))
    inv = (3 * sp[0] * h, 3 * sp[1] * h)       # '사흘 길'이 말하는 거리(km)
    inv_li = (inv[0] / U_HI, inv[1] / U_LO)    # 리 수 범위(가정 단위 폭 포함)
    return dict(d_km=d_km, h=h, sp=sp, days=days, inv=inv, inv_li=inv_li)


def case_b7():
    """가상: 모형의 한계를 가설의 약점으로 읽는 실수. 우도비는 연습용 숫자."""
    lr_land = [2.0, 1.5, 0.8, 1.2]
    lr_sea_wrong = 0.05
    prior_odds = 1.0
    prod_land = float(np.prod(lr_land))
    odds_excl = prior_odds * prod_land
    odds_wrong = prior_odds * prod_land * lr_sea_wrong
    return dict(lr_land=lr_land, prod_land=prod_land, p_excl=odds_excl / (1 + odds_excl),
                p_wrong=odds_wrong / (1 + odds_wrong), odds_excl=odds_excl, odds_wrong=odds_wrong,
                lr_sea=lr_sea_wrong)


def case_b8():
    """가상: 이름 하나가 산동 쪽 후보와 다른 후보에 모두 맞을 때 '교류가 있었다'는 증거의 우도비"""
    pa, pb = 0.9, 0.9      # 증거 D1: 산동에 한반도 사람의 거주 기록이 있다
    pc, pd = 0.50, 0.02    # 증거 D2: 산동 지명 사전에 '서경'이라는 이름의 곳이 있다
    return dict(lr1=pa / pb, lr2=pc / pd, odds=1.0 * (pa / pb) * (pc / pd), post=((pa / pb) * (pc / pd)) / (1 + (pa / pb) * (pc / pd)))


def exercise_numbers():
    o = {}
    # 문제 1: 10여 리와 1리 구간
    o["p1"] = li_km(10)
    # 문제 2: 항해 3구간 총 길이
    o["p2"] = sum(li * U_MID for _, li in [(45, 300), (180, 200), (315, 150)])
    # 문제 3: Poisson
    lam = 26 / 2547
    o["p3"] = (math.exp(-lam * 30), 1 - math.exp(-lam * 30))
    # 문제 4: 해안선
    o["p4"] = 3.0 / 0.5
    # 문제 5: 우도비
    o["p5"] = (0.8 / 0.2, 1.0 * 4 / (1 + 4))
    return o


def dump():
    import json
    r = real_numbers()
    print("REAL", json.dumps({k: v for k, v in r.items()}, ensure_ascii=False, default=float, indent=1))
    for row in unit_table():
        print("UNIT", row[0], row[1], "%.2f %.2f w=%.2f  %.3f %.3f" % row[2:])
    b1 = case_b1()
    for m in ("단위 공유", "단위 따로"):
        print("B1", m, [(x["k"], round(x["area95"], 1), round(x["cx"], 2), round(x["cy"], 2), round(x["sdx"], 2), round(x["sdy"], 2)) for x in b1[m]])
    print("B1 mid", b1["mid_path"].round(2).tolist(), "legs", [round(x, 2) for x in b1["leg_km"]], "tot", round(b1["total_km"], 2))
    print("B1 ratio", {m: [round(x, 4) for x in v] for m, v in b1["sd_area_ratio"].items()})
    b2 = case_b2(); print("B2", b2["n"], b2["land_ok"], round(b2["frac"], 3), b2["n_sea"], b2["n_mix"])
    b3 = case_b3(); print("B3", {k: round(v, 2) for k, v in b3.items() if isinstance(v, float)})
    print("B3", b3["ring_area"], b3["band_old"], b3["band_new"], b3["reg_old_area"], b3["reg_new_area"], b3["overlap_area"], b3["union_area"])
    print("B4", case_b4())
    b5 = case_b5(); print("B5", b5["post"].round(4).tolist(), [x.round(4).tolist() for x in b5["loo"]], b5["prod"].round(5).tolist())
    print("B6", case_b6())
    print("B7", case_b7())
    print("B8", case_b8())
    print("EX", exercise_numbers())




# ======================================================================= 그림
def box(ax, x, y, w, h, text, mode, fc=None, ls="-", fs=FS, bold=False, hatch=None):
    s = STY[mode]
    fc = fc or ("#ffffff" if mode == "bw" else "#fdf3e1")
    p = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=fc, ec=s["line"],
                       lw=0.9, ls=ls, hatch=hatch, zorder=3)
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, zorder=4, fontweight="bold" if bold else "normal",
            linespacing=1.1, bbox=dict(fc="white", ec="none", pad=1.5) if hatch else None)


def arrow(ax, x1, y1, x2, y2, mode, ls="-", lw=1.1):
    s = STY[mode]
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=s["line"], lw=lw, ls=ls,
                                                                 shrinkA=0, shrinkB=0), zorder=2)


def pal(mode):
    if mode == "color":
        return dict(a="#1f6fb8", b="#2e7d32", c="#c0392b", g="#777777", f1="#f0b45a", f2="#7fb3d5", f3="#cfe8cf")
    return dict(a="#000000", b="#333333", c="#666666", g="#555555", f1="#bdbdbd", f2="#e0e0e0", f3="#f2f2f2")


def fig_timeline(mode):
    """연대기 종합 그림: 가로 시간축 700~2020, 세 줄(황하와 땅 / 바닷길과 사람 / 기록과 학문)"""
    P = pal(mode); s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 5.5))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.99, bottom=0.05)
    X0, X1 = 640, 2090
    ax.set_xlim(X0, X1); ax.set_ylim(-3.4, 13.6)
    ax.set_yticks([]); ax.spines[["left", "right", "top"]].set_visible(False)
    ax.set_xticks(range(700, 2001, 100)); ax.tick_params(axis="x", labelsize=8.5, length=3)
    for yr in range(700, 2001, 100):
        ax.axvline(yr, color=s["grid"], lw=0.35, ls=":", zorder=0)
    # 줄 이름
    ax.text(X0 + 5, 13.0, "황하와 땅", fontsize=FS, fontweight="bold", color=P["a"], va="center")
    ax.text(X0 + 5, 8.75, "바닷길과 사람", fontsize=FS, fontweight="bold", color=P["b"], va="center")
    ax.text(X0 + 5, 3.95, "기록과 학문", fontsize=FS, fontweight="bold", color=P["c"], va="center")
    for y in (8.35, 3.55):
        ax.axhline(y, color=s["grid"], lw=0.6, zorder=0)
    # 줄 1: 황하
    y = 11.0
    ax.plot([X0 + 10, 2080], [y, y], color=P["a"], lw=2.0, zorder=2)
    ev = [(1048, "두 갈래\n1048", 1, 1000), (1128, "남쪽으로\n1128", -1, 1150), (1855, "북쪽 복귀\n1855", 1, 1810), (1976, "현 하구\n1976", -1, 1995)]
    for yr, t, sg, tx in ev:
        ax.plot(yr, y, "o", ms=5.5, mfc=P["a"] if mode == "color" else "white", mec=P["a"], zorder=4)
        ty = y + sg * 0.55
        ax.plot([yr, tx], [y, ty], color=P["a"], lw=0.6)
        ax.text(tx, ty, t, ha="center", va="bottom" if sg > 0 else "top", fontsize=FS, linespacing=1.05)
    # 줄 2: 바닷길과 사람(막대)
    def bar(y, a, b, lab, side="right", col=None, open_end=False, hatch=None):
        col = col or P["b"]
        ax.add_patch(Rectangle((a, y - 0.22), b - a, 0.44, fc=P["f3"] if mode == "bw" else col, ec=col, lw=1.0, hatch=hatch, zorder=3, alpha=0.85 if mode == "color" else 1))
        if open_end:
            ax.annotate("", xy=(b + 55, y), xytext=(b, y), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.0, ls=":"))
        if side == "right":
            ax.text(b + (60 if open_end else 10), y, lab, ha="left", va="center", fontsize=FS)
        else:
            ax.text(a - 10, y, lab, ha="right", va="center", fontsize=FS)
    bar(7.7, 730, 805, "가탐 730~805")
    bar(6.9, 788, 846, "장보고 약 788~846", hatch="//")
    bar(6.1, 794, 864, "엔닌 794~864", hatch="xx")
    for yr, t, ha in [(828, "청해진 설치 828", "left"), (1123, "서긍의 사행 1123", "left")]:
        ax.plot(yr, 5.3, "s", ms=5.5, mfc=P["b"] if mode == "color" else "white", mec=P["b"], zorder=4)
        ax.text(yr + 15, 5.3, t, ha=ha, va="center", fontsize=FS)
    # 줄 3: 기록과 학문
    bar(2.9, 1075, 1151, "김부식 1075~1151", col=P["c"])
    ax.plot(1145, 2.1, "D", ms=5, mfc="white", mec=P["c"], zorder=5)
    ax.text(1160, 2.1, "삼국사기 완성 1145", ha="left", va="center", fontsize=FS)
    ax.plot(1081, 2.1, "D", ms=5, mfc=P["c"] if mode == "color" else "white", mec=P["c"], zorder=5)
    ax.text(1066, 2.1, "문종 35년 1081", ha="right", va="center", fontsize=FS)
    bar(1.3, 1091, 1124, "서긍 1091~(사망 해 미확인)", col=P["c"], open_end=True, hatch="//")
    ax.plot(1613, 0.5, "D", ms=5, mfc=P["c"] if mode == "color" else "white", mec=P["c"], zorder=4)
    ax.text(1628, 0.5, "추측항법 용어 1613", ha="left", va="center", fontsize=FS)
    bar(-0.3, 1893, 1980, "고힐강 1893~1980", side="left", col=P["c"], hatch="//")
    bar(-1.1, 1911, 1992, "담기양 1911~1992", side="left", col=P["c"], hatch="xx")
    bar(-1.9, 1982, 1988, "중국역사지도집 1982~88", side="left", col=P["c"])
    bar(-2.7, 1972, 2013, "진평군 논쟁 1972~2013", side="left", col=P["c"], hatch="..")
    ax.text(2088, -3.1, "", fontsize=FS)
    return save(fig, "ch18", "fig18-a-timeline", mode)


def fig_course(mode):
    """황하 하구의 시기와 사료 연대를 한 줄에 놓기"""
    P = pal(mode); s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 3.5))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.12)
    X0, X1 = 1000, 1980
    ax.set_xlim(X0, X1); ax.set_ylim(-3.2, 3.5)
    ax.set_yticks([]); ax.spines[["left", "right", "top"]].set_visible(False)
    ax.set_xticks(range(1000, 1981, 100)); ax.tick_params(axis="x", labelsize=8.5, length=3)
    segs = [(1000, 1128, "여러 갈래", "xx", P["f2"]), (1128, 1855, "남쪽 하구(회하 계통)", "", P["f1"]), (1855, 1980, "북쪽(발해)", "//", P["f2"])]
    for a, b, t, h, c in segs:
        ax.add_patch(Rectangle((a, -0.45), b - a, 0.9, fc=c if mode == "color" else (P["f3"] if h == "" else "white"), ec=s["line"], lw=1.0, hatch=h, zorder=2))
        lab_x = (a + b) / 2
        ax.text(lab_x, 0, t, ha="center", va="center", fontsize=FS, zorder=4,
                bbox=dict(fc="white", ec="none", pad=1.2, alpha=0.9))
    # 하도 사건(아래)
    for yr, t, lv, tx in [(1048, "1048\n두 갈래로 갈라짐", 1, 1075), (1099, "1099\n동쪽 갈래 막음", 2, 1235), (1128, "1128\n남쪽으로 옮김", 1, 1280),
                          (1855, "1855\n북쪽 둑 터짐", 1, 1760), (1938, "1938\n둑을 일부러 끊음", 2, 1860)]:
        ya = -0.45
        ty = ya - 0.55 - (lv - 1) * 1.05
        ax.plot([yr, yr], [ya, ty + 0.15], color=s["line"], lw=0.7)
        ax.text(tx, ty, t, ha="center", va="top", fontsize=FS, linespacing=1.05,
                bbox=dict(fc="white", ec="none", pad=0.6))
    # 사료 연대(위)
    for yr, t, lv, tx in [(1081, "문종 35년\n1081", 1, 1062), (1135, "묘청의 난\n1135", 2, 1095), (1145, "삼국사기\n1145", 1, 1235)]:
        ya = 0.45
        ty = ya + 0.55 + (lv - 1) * 1.05
        ax.plot([yr, yr], [ya, ty - 0.1], color=P["c"], lw=0.9, ls="-" if mode == "color" else "--")
        ax.plot(yr, ya, "v", ms=5.5, mfc=P["c"] if mode == "color" else "white", mec=P["c"], zorder=5)
        ax.text(tx, ty, t, ha="center", va="bottom", fontsize=FS, linespacing=1.05, color="black")
    return save(fig, "ch18", "fig18-b-course", mode)


def fig_sea(mode, B1):
    """가상 바닷길 세 구간에서 끝점 구름이 커지는 모양과 95% 영역 넓이"""
    P = pal(mode); s = STY[mode]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(WIDTH, 3.0), gridspec_kw=dict(width_ratios=[1.35, 1]), constrained_layout=True)
    mk = ["o", "s", "^"]; cols = [P["a"], P["b"], P["c"]]
    for k, r in enumerate(B1["단위 공유"]):
        sn = r["snap"]
        ax.scatter(sn[:, 0], sn[:, 1], s=1.5, marker=".", color=cols[k], alpha=0.35 if mode == "color" else 0.5, zorder=2)
    mp = B1["mid_path"]
    ax.plot(mp[:, 0], mp[:, 1], "-", color="black", lw=1.0, zorder=4)
    for k in range(4):
        ax.plot(mp[k, 0], mp[k, 1], "k*" if k == 0 else mk[k - 1], ms=8 if k == 0 else 5.5, mfc="white" if k else "black", mec="black", zorder=5)
    ax.text(mp[0, 0] + 4, mp[0, 1] + 6, "출발", fontsize=FS, bbox=dict(fc="white", ec="none", pad=0.8, alpha=0.9), zorder=6)
    for k, (dx, dy) in enumerate([(-7, 6), (6, -2), (-8, 10)]):
        ax.text(mp[k + 1, 0] + dx, mp[k + 1, 1] + dy, f"{k+1}구간", fontsize=FS, ha="left" if dx > 0 else "right", bbox=dict(fc="white", ec="none", pad=0.8, alpha=0.9), zorder=6)
    ax.set_xlabel("동 (km)"); ax.set_ylabel("북 (km)"); ax.set_aspect("equal")
    ax.set_xlim(-10, 150); ax.set_ylim(-45, 135); ax.grid(color=s["grid"], lw=0.3, ls=":")
    ax.set_title("(가) 구간 끝점 구름", loc="left", fontsize=9)
    w = 0.38
    xs = np.arange(3)
    a1 = [r["area95"] for r in B1["단위 공유"]]; a2 = [r["area95"] for r in B1["단위 따로"]]
    ax2.bar(xs - w / 2, a1, w, color=P["f1"] if mode == "color" else "#bdbdbd", ec="black", lw=0.6, label="단위 공유", hatch="" )
    ax2.bar(xs + w / 2, a2, w, color=P["f2"] if mode == "color" else "white", ec="black", lw=0.6, label="단위 따로", hatch="//")
    for x, v in zip(xs - w / 2, a1):
        ax2.text(x, v + 250, f"{v:,.0f}", ha="center", fontsize=8.5, rotation=90, va="bottom")
    for x, v in zip(xs + w / 2, a2):
        ax2.text(x, v + 250, f"{v:,.0f}", ha="center", fontsize=8.5, rotation=90, va="bottom")
    ax2.set_xticks(xs); ax2.set_xticklabels(["1", "2", "3"]); ax2.set_xlabel("지난 구간 수")
    ax2.set_ylabel("95% 영역 넓이 (km²)"); ax2.set_ylim(0, 19500)
    ax2.legend(loc="upper left", frameon=False, fontsize=8.5)
    ax2.set_title("(나) 영역 넓이", loc="left", fontsize=9)
    return save(fig, "ch18", "fig18-c-sea", mode)


def fig_scale(mode):
    """사료의 거리 폭과 지역 크기: 로그 가로축"""
    P = pal(mode); s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 3.5))
    fig.subplots_adjust(left=0.36, right=0.97, top=0.96, bottom=0.16)
    rows = [("12리 (각자성석 제2석)", 12 * U_LO, 12 * U_HI, False), ("30리 (동명왕묘)", 30 * U_LO, 30 * U_HI, False),
            ("42리 (평양부 서쪽 경계)", 42 * U_LO, 42 * U_HI, False), ("1~2일 길 (가정 20~30 km/일)", 20, 60, True),
            ("1000리 (후한서 고구려)", 1000 * U_LO, 1000 * U_HI, False), ("2000리 (북사 동서)", 2000 * U_LO, 2000 * U_HI, False),
            ("4000리 (현도군~낙양)", 4000 * U_LO, 4000 * U_HI, False)]
    n = len(rows)
    for i, (t, a, b, assume) in enumerate(rows):
        y = n - 1 - i
        ax.barh(y, b - a, left=a, height=0.5, color=("white" if mode == "bw" else P["f2"]) if assume else (P["f1"] if mode == "color" else "#bdbdbd"),
                ec="black", lw=0.8, hatch="//" if assume else "", zorder=3)
        ax.text(b * 1.12, y, f"{a:,.0f}~{b:,.0f}" if a >= 100 else f"{a:.1f}~{b:.1f}", va="center", ha="left", fontsize=8.5)
    ax.set_yticks(range(n)); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=8.5)
    ax.set_xscale("log"); ax.set_xlim(2, 20000)
    ax.axvline(math.sqrt(SD_AREA), color=P["c"], lw=1.6, ls="--" if mode == "color" else "-.", zorder=4)
    ax.text(math.sqrt(SD_AREA) * 1.06, n - 0.45, "산동성의 한 변\n(넓이의 제곱근 396 km)", fontsize=8.5, va="top", ha="left")
    ax.set_xlabel("거리 (km, 로그 눈금)"); ax.grid(axis="x", color=s["grid"], lw=0.3, ls=":")
    ax.set_ylim(-0.6, n - 0.2)
    return save(fig, "ch18", "fig18-d-scale", mode)


def fig_flow(mode):
    """해로가 섞인 서술을 분류하는 순서"""
    P = pal(mode); s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 4.5))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    box(ax, 5, 9.3, 4.6, 0.9, "서경 사료의 한 문장", mode, bold=True)
    box(ax, 5, 7.7, 4.6, 0.95, "바다를 지나는 말이\n있는가?", mode)
    box(ax, 2.0, 5.9, 3.5, 1.0, "육상 서술\n(리, 하루 길, 방위)", mode)
    box(ax, 2.0, 3.9, 3.5, 1.0, "육상 기법으로\n계산한다", mode, fc="#e6f0fa" if mode == "color" else "#e8e8e8")
    box(ax, 7.6, 5.9, 4.4, 1.0, "해로 포함 서술\n(배로, 바닷길, 건너다)", mode)
    box(ax, 7.6, 4.0, 4.4, 1.0, "거리나 날수가\n적혀 있는가?", mode)
    box(ax, 5.6, 1.9, 3.7, 1.15, "있음: 구간을 나눠\n해상 구간은 '계산 불가'", mode, fc="#fde9e6" if mode == "color" else "#d9d9d9")
    box(ax, 8.9, 1.9, 2.0, 1.15, "없음: 연결\n점검에만 사용", mode, fc="#fde9e6" if mode == "color" else "#d9d9d9")
    box(ax, 5, 0.45, 8.6, 0.7, "두 결과(육상만, 전체)를 같은 표에 나란히 싣는다", mode, bold=True)
    arrow(ax, 5, 8.85, 5, 8.2, mode)
    arrow(ax, 4.0, 7.4, 2.4, 6.4, mode); ax.text(2.9, 6.95, "없음", fontsize=FS, ha="center")
    arrow(ax, 6.0, 7.4, 7.4, 6.4, mode); ax.text(7.2, 6.95, "있음", fontsize=FS, ha="center")
    arrow(ax, 2.0, 5.4, 2.0, 4.4, mode)
    arrow(ax, 7.6, 5.4, 7.6, 4.5, mode)
    arrow(ax, 6.9, 3.5, 5.9, 2.5, mode); arrow(ax, 8.5, 3.5, 8.8, 2.5, mode)
    arrow(ax, 2.0, 3.4, 2.0, 1.2, mode, ls=":"); arrow(ax, 2.0, 1.2, 3.0, 0.8, mode, ls=":")
    arrow(ax, 5.6, 1.3, 5.2, 0.8, mode); arrow(ax, 8.9, 1.3, 7.8, 0.8, mode)
    return save(fig, "ch18", "fig18-e-flow", mode)


def fig_coast(mode):
    """가상 모식: 해안선이 바다 쪽으로 나아가면 '바다에 임한다'의 뜻이 달라진다"""
    P = pal(mode); s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 2.8))
    fig.subplots_adjust(left=0.03, right=0.97, top=0.98, bottom=0.2)
    r = 0.5
    ax.set_xlim(-8, 50); ax.set_ylim(-1.3, 3.7); ax.set_yticks([])
    ax.spines[["left", "right", "top"]].set_visible(False)
    ax.set_xlabel("성에서 바다 쪽으로 잰 거리 (km)")
    ax.axhline(0, color="black", lw=0.8, zorder=1)
    for t, ls, lab, ty in [(0, "-", "성을 쌓은 때", 3.35), (40, "--", "40년 뒤", 2.7), (80, ":", "80년 뒤", 2.05)]:
        x = r * t
        ax.plot([x, x], [0, ty - 0.2], color=P["a"] if mode == "color" else "black", lw=1.7, ls=ls, zorder=3)
        ax.text(x + 0.7, ty, f"해안선 {lab}", fontsize=FS, va="center")
    ax.plot(-0.0, 0.0, "s", ms=8, mfc="black", mec="black", zorder=5, clip_on=False)
    ax.text(-1.2, 0.5, "성", fontsize=FS, ha="right", va="center", fontweight="bold")
    ax.add_patch(Rectangle((-2.0, -0.12), 2.0, 0.24, fc=P["f1"] if mode == "color" else "#bdbdbd", ec="black", lw=0.6, zorder=2))
    ax.text(-1.0, -0.55, "해안에서 2 km 안", fontsize=FS, ha="center", va="top")
    ax.annotate("", xy=(40, -0.2), xytext=(0, -0.2), arrowprops=dict(arrowstyle="<->", lw=1.0))
    ax.text(20, -0.45, "80년 동안 40 km 멀어짐 (가정 0.5 km/년)", ha="center", fontsize=FS, va="top",
            bbox=dict(fc="white", ec="none", pad=1.0))
    ax.text(49, 0.35, "바다 쪽", fontsize=FS, ha="right", va="center")
    ax.text(-7.5, 0.35, "육지 쪽", fontsize=FS, ha="left", va="center")
    return save(fig, "ch18", "fig18-f-coast", mode)


def fig_b3(mode, B3):
    """가상 사례: 같은 문장을 옛 하도와 새 하도로 읽었을 때 후보 영역"""
    P = pal(mode); s = STY[mode]
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 2.85), constrained_layout=True)
    for ax, key, rx, ttl in [(axs[0], "reg_old", B3["old_x"], "(가) 옛 하도로 읽음"), (axs[1], "reg_new", B3["new_x"], "(나) 새 하도로 읽음")]:
        ax.set_xlim(0, 60); ax.set_ylim(0, 60); ax.set_aspect("equal")
        ax.imshow(B3["ring_g"], origin="lower", extent=(-0.25, 60.25, -0.25, 60.25), cmap="Greys", alpha=0.25, vmin=0, vmax=1.2, zorder=1)
        m = B3[key]
        ax.imshow(np.ma.masked_where(m == 0, m), origin="lower", extent=(-0.25, 60.25, -0.25, 60.25), cmap="YlOrBr" if mode == "color" else "Greys", vmin=0, vmax=1.3, zorder=2)
        ax.plot(rx, XS, color=P["a"], lw=1.6, ls="-" if mode == "color" else "-.", zorder=3)
        ax.plot(*B3["gun"], "^", color="black", ms=6, zorder=5)
        ax.text(B3["gun"][0] + 1, B3["gun"][1] + 2, "갑군", fontsize=FS)
        ax.set_xlabel("동 (km)"); ax.set_title(ttl, loc="left", fontsize=9)
        ax.set_xticks([0, 20, 40, 60]); ax.set_yticks([0, 20, 40, 60])
    axs[0].set_ylabel("북 (km)")
    return save(fig, "ch18", "fig18-g-rivers", mode)


def figures():
    B1 = case_b1(); B3 = case_b3()
    out = []
    for mode in ("color", "bw"):
        out.append(fig_timeline(mode)); out.append(fig_course(mode)); out.append(fig_sea(mode, B1))
        out.append(fig_scale(mode)); out.append(fig_flow(mode)); out.append(fig_coast(mode)); out.append(fig_b3(mode, B3))
    return out


if __name__ == "__main__":
    if "--nums" in sys.argv:
        dump()
    else:
        dump()
        for p in figures():
            print("saved", p)
