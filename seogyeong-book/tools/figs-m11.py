"""figs-m11.py - 11장(지명 언어학적 추정) 보강 그림 6개: 연대기, 핵 영향과 평활, 실제 이름 표본, 표본 편향, 대역폭과 등어선, 개명 짝.
실행: python3 tools/figs-m11.py  (그림/ch11에 컬러·흑백 PDF 생성). 시뮬레이션 씨앗은 원고의 숫자와 같다."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from figlib import *

def kd(P, pts, h):
    d2 = ((P[:, None, :] - pts[None, :, :]) ** 2).sum(-1)
    return np.exp(-d2 / (2 * h * h)).sum(1)

def wilson(k, n, z=1.96):
    p = k / n; d = n + z * z
    c = (k + z * z / 2) / d; hw = z / d * math.sqrt(n * p * (1 - p) + z * z / 4)
    return p, c - hw, c + hw

# ---------- 1. 연대기 ----------
def chrono(mode):
    s = STY[mode]
    ink, acc = s["line"], s["accent"] if mode == "color" else "#000000"
    bar = "#7fb3d5" if mode == "color" else "#bdbdbd"
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(WIDTH, 5.5), gridspec_kw=dict(height_ratios=[1, 3.6]), constrained_layout=True)
    # 위: 1050-1850
    a1.set_xlim(1050, 1850); a1.set_ylim(-0.6, 1.6); a1.set_yticks([])
    a1.set_xticks(range(1100, 1851, 100))
    a1.grid(axis="x", color=s["grid"], lw=0.3, ls=":")
    for y, (b0, b1, nm, ev, evn, side) in enumerate([(1762, 1836, "정약용", 1811, "아방강역고 1811", "l"), (1075, 1151, "김부식", 1145, "삼국사기 1145경", "r")]):
        a1.barh(y, b1 - b0, left=b0, height=0.42, color=bar, ec=ink, lw=0.6, hatch="//" if mode == "bw" else None)
        a1.plot(ev, y, "D", color=ink, ms=5, mfc="white" if mode == "bw" else acc, zorder=5)
        if side == "r":
            a1.text(b1 + 12, y + 0.34, nm + "(1075~1151)", fontsize=8.5, va="bottom")
            a1.text(ev + 12, y - 0.34, evn, fontsize=8.5, va="top")
        else:
            a1.text(b0 - 12, y + 0.34, nm + "(1762~1836)", fontsize=8.5, va="bottom", ha="right")
            a1.text(ev - 12, y - 0.34, evn, fontsize=8.5, va="top", ha="right")
    a1.set_title("(a) 1050~1850년", loc="left")
    # 아래: 1850-2030
    a2.set_xlim(1850, 2068); a2.set_ylim(-0.8, 11.6); a2.invert_yaxis(); a2.set_yticks([])
    a2.set_xticks(range(1850, 2031, 20)); a2.tick_params(axis="x", labelsize=8.5)
    a2.grid(axis="x", color=s["grid"], lw=0.3, ls=":")
    rows = [
        (0.0, "bar", 1854, 1926, "질리에롱(1854~1926)", "◆ 언어지도 1902~10", 1906),
        (1.6, "bar", 1877, 1964, "에크월(1877~1964)", "◆ 영국 지명 사전 1936", 1936),
        (3.0, "pt", 1923, None, "영국지명학회 1922~23", None, None),
        (4.0, "pt", 1963, None, "모스텔러·월리스 1963", None, None),
        (5.0, "pt", 1970, None, "토블러 제1법칙 1970", None, None),
        (6.0, "pt", 1973, None, "세귀 방언계량학 1973", None, None),
        (7.0, "pt", 1986, None, "실버만 밀도추정 1986", None, None),
        (8.0, "pt", 2004, None, "베크위스 2004", None, None),
        (9.0, "pt", 2013, None, "보빈 2013", None, None),
        (10.0, "pt", 2015, None, "비얼링·네르보네 2015", None, None),
    ]
    for (yy, kind, y0, y1, nm, nm2, ex) in rows:
        if kind == "bar":
            a2.barh(yy, y1 - y0, left=y0, height=0.6, color=bar, ec=ink, lw=0.6, hatch="//" if mode == "bw" else None)
            a2.plot(ex, yy, "D", color=ink, ms=5, mfc="white" if mode == "bw" else acc, zorder=5)
            a2.text(y1 + 4, yy - 0.28, nm, fontsize=8.5, va="center")
            a2.text(y1 + 4, yy + 0.42, nm2, fontsize=8.5, va="center")
        else:
            a2.plot(y0, yy, "o", color=ink, ms=5, mfc="white" if mode == "bw" else acc, zorder=5)
            if y0 < 1990:
                a2.text(y0 + 4, yy, nm, fontsize=8.5, va="center")
            else:
                a2.text(y0 - 4, yy, nm, fontsize=8.5, va="center", ha="right")
    a2.set_title("(b) 1850~2030년  (막대는 생존 기간, ◆는 책, ●는 논문·제도)", loc="left", fontsize=8.5)
    return save(fig, "ch11", "fig11-m1-chrono", mode)

# ---------- 2. 핵 영향과 평활 ----------
def kernel(mode):
    s = STY[mode]
    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH, 2.7), constrained_layout=True)
    d = np.linspace(0, 200, 400)
    styles = [("-", 1.6), ("--", 1.2), (":", 1.6)]
    cols = ["#1f6fb8", "#c0392b", "#2e7d32"] if mode == "color" else ["#000000", "#444444", "#777777"]
    for (ls, lw), c, hh in zip(styles, cols, [22.5, 45, 90]):
        a.plot(d, np.exp(-d * d / (2 * hh * hh)), ls=ls, lw=lw, color=c, label=f"$h$={hh:g} km")
    for x in (45, 90, 135):
        a.plot(x, math.exp(-x * x / (2 * 45 ** 2)), "o", color=s["line"], ms=4)
        a.annotate(f"{math.exp(-x*x/(2*45**2)):.3f}".rstrip("0") if x == 135 else f"{math.exp(-x*x/(2*45**2)):.2f}", (x, math.exp(-x * x / (2 * 45 ** 2))), xytext=(4, 5), textcoords="offset points", fontsize=8.5)
    a.set_xlabel("지명까지의 거리 (km)"); a.set_ylabel("영향 (0~1)")
    a.set_title("(a) 거리에 따른 영향", loc="left"); a.legend(frameon=False, loc="upper right"); a.grid(color=s["grid"], lw=0.3, ls=":")
    rho = np.linspace(0, 10, 200)
    for (ls, lw), c, al in zip(styles, cols, [0.5, 1, 3]):
        b.plot(rho, al / (rho + al), ls=ls, lw=lw, color=c, label=rf"$\alpha$={al:g}")
    b.set_xlabel(r"주변 지명의 양 $\rho_{all}$"); b.set_ylabel("평균 쪽으로 당기는 몫")
    b.set_title("(b) 평활의 당김", loc="left"); b.legend(frameon=False, loc="upper right"); b.grid(color=s["grid"], lw=0.3, ls=":")
    b.set_ylim(0, 1.02)
    return save(fig, "ch11", "fig11-m2-kernel", mode)

# ---------- 3. 실제 이름 표본 ----------
def realnames(mode):
    s = STY[mode]
    cats = ["산(山)", "물(江·水·津·灘)", "성(城)", "섬(島)", "도읍·고을"]
    before = [6, 6, 4, 1, 7]; after = [4, 5, 4, 1, 7]
    fig, ax = plt.subplots(figsize=(WIDTH, 3.4), constrained_layout=True)
    y = np.arange(len(cats))
    c1, c2 = ("#7fb3d5", "#f0b45a") if mode == "color" else ("#bdbdbd", "#ffffff")
    for off, vals, n, col, lab, hat in [(-0.2, before, 24, c1, "이름 24개(이명을 따로 셈)", None), (0.2, after, 21, c2, "이름 21개(이명 셋을 묶음)", "//" if mode == "bw" else None)]:
        ps = [wilson(v, n) for v in vals]
        ax.barh(y + off, [p[0] * 100 for p in ps], height=0.36, color=col, ec=s["line"], lw=0.6, hatch=hat, label=lab)
        ax.errorbar([p[0] * 100 for p in ps], y + off, xerr=[[(p[0] - p[1]) * 100 for p in ps], [(p[2] - p[0]) * 100 for p in ps]], fmt="none", ecolor=s["line"], elinewidth=0.9, capsize=2)
        for yy, p, v in zip(y + off, ps, vals):
            ax.text(p[2] * 100 + 1.5, yy, f"{v}개 {p[0]*100:.1f}%", va="center", fontsize=8.5)
    ax.set_yticks(y); ax.set_yticklabels(cats); ax.invert_yaxis()
    ax.set_xlim(0, 80); ax.set_xlabel("표본 안의 비율 (%), 가로선은 95% 윌슨 구간")
    fig.legend(loc="outside lower center", frameon=False, ncol=1); ax.grid(axis="x", color=s["grid"], lw=0.3, ls=":")
    return save(fig, "ch11", "fig11-m3-realnames", mode)

# ---------- 4. 표본 편향 ----------
def bias(mode):
    s = STY[mode]
    xs = np.arange(0, 401, 5.0); river = np.c_[xs, 200 + 70 * np.sin(xs / 70.0)]
    rs2 = np.random.default_rng(21)
    t = rs2.uniform(10, 390, 40); jin = np.c_[t, 200 + 70 * np.sin(t / 70.0) + rs2.normal(0, 10, 40)]
    sg = rs2.uniform(10, 390, (40, 2))
    world = np.r_[jin, sg]; lab = np.array(["津"] * 40 + ["城"] * 40)
    cap = np.array([250.0, 171.0]); dcap = np.sqrt(((world - cap) ** 2).sum(1))
    prec = np.where(dcap < 80, 0.95, 0.10)
    rs3 = np.random.default_rng(4); obs = rs3.random(80) < prec
    g = np.arange(10, 400, 20.0); GX, GY = np.meshgrid(g, g); P = np.c_[GX.ravel(), GY.ravel()]
    def Lmap(pts, lb):
        rb = (lb == "津").mean()
        return ((kd(P, pts[lb == "津"], 45) + rb) / (kd(P, pts, 45) + 1) / rb).reshape(GX.shape)
    Lt = Lmap(world, lab); Lo = Lmap(world[obs], lab[obs])
    fig, axs = plt.subplots(2, 2, figsize=(WIDTH, 4.9), constrained_layout=True)
    mk_j = dict(marker="^", ls="none", ms=4.5, mfc=s["fill"] if mode == "color" else "white", mec=s["line"], mew=0.7)
    mk_s = dict(marker="o", ls="none", ms=4, mfc="white", mec=s["gray"], mew=0.7)
    def dots(ax, pts, lb, ttl):
        ax.plot(river[:, 0], river[:, 1], color=s["river"], ls=s["river_ls"], lw=1.2)
        ax.plot(*pts[lb == "津"].T, **mk_j); ax.plot(*pts[lb == "城"].T, **mk_s)
        th = np.linspace(0, 2 * math.pi, 100); ax.plot(cap[0] + 80 * np.cos(th), cap[1] + 80 * np.sin(th), color=s["line"], lw=0.8, ls="--")
        ax.set_xlim(0, 400); ax.set_ylim(0, 400); ax.set_aspect("equal"); ax.set_title(ttl, loc="left", fontsize=8.5)
        ax.set_xticks([0, 200, 400]); ax.set_yticks([0, 200, 400])
    dots(axs[0, 0], world, lab, "(a) 참 지명 80개: 津 ▲ 城 ○")
    dots(axs[0, 1], world[obs], lab[obs], "(b) 기록에 남은 24개")
    vmax = 1.75
    for ax, L, ttl in [(axs[1, 0], Lt, "(c) (a)로 만든 $\\Lambda$"), (axs[1, 1], Lo, "(d) (b)로 만든 $\\Lambda$")]:
        im = ax.imshow(L, origin="lower", extent=(0, 400, 0, 400), cmap=s["cmap"], vmin=0.4, vmax=vmax)
        ax.plot(river[:, 0], river[:, 1], color=s["river"] if mode == "color" else "#000000", ls=s["river_ls"], lw=1.0)
        th = np.linspace(0, 2 * math.pi, 100); ax.plot(cap[0] + 80 * np.cos(th), cap[1] + 80 * np.sin(th), color=s["line"], lw=0.8, ls="--")
        ax.set_title(ttl, loc="left", fontsize=8.5); ax.set_xticks([0, 200, 400]); ax.set_yticks([0, 200, 400])
    fig.colorbar(im, ax=axs[1, :], shrink=0.8, pad=0.02, label=r"$\Lambda$ (1이면 정보 없음)")
    return save(fig, "ch11", "fig11-m4-bias", mode)

# ---------- 5. 대역폭과 등어선 ----------
def bandwidth(mode):
    s = STY[mode]
    clu = np.r_[np.random.default_rng(101).normal([100, 100], [25, 25], (30, 2)),
                np.random.default_rng(102).normal([280, 150], [25, 25], (30, 2)),
                np.random.default_rng(103).normal([200, 320], [25, 25], (20, 2))]
    hs = [5, 10, 15, 20, 30, 45, 60, 90]; ll = []
    for hh in hs:
        d2 = ((clu[:, None, :] - clu[None, :, :]) ** 2).sum(-1)
        K = np.exp(-d2 / (2 * hh * hh)) / (2 * math.pi * hh * hh); np.fill_diagonal(K, 0)
        ll.append(np.log(K.sum(1) / (len(clu) - 1)).sum())
    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH, 2.8), constrained_layout=True)
    a.plot(hs, ll, "-o", color=s["line"], ms=4)
    i = int(np.argmax(ll)); a.plot(hs[i], ll[i], "o", ms=9, mfc="none", mec=s["truth"], mew=1.4)
    a.annotate(f"최고 $h$={hs[i]} km", (hs[i], ll[i]), xytext=(25, -45), textcoords="offset points", fontsize=8.5, arrowprops=dict(arrowstyle="->", lw=0.7))
    a.set_xlabel("대역폭 $h$ (km)"); a.set_ylabel("하나씩 빼기 로그우도"); a.set_title("(a) 대역폭 고르기", loc="left"); a.grid(color=s["grid"], lw=0.3, ls=":")
    r10 = np.random.default_rng(3)
    xa = np.clip(r10.normal(130, 50, 24), 0, 400); xb = np.clip(r10.normal(270, 50, 24), 0, 400)
    x = np.arange(0, 401, 2.0)
    def k1(x, p, hh): return np.exp(-(x[:, None] - p[None, :]) ** 2 / (2 * hh * hh)).sum(1)
    cols = ["#1f6fb8", "#c0392b", "#2e7d32"] if mode == "color" else ["#000000", "#444444", "#777777"]
    for (ls, lw), cc, hh in zip([("-", 1.6), ("--", 1.2), (":", 1.6)], cols, [20, 45, 90]):
        b.plot(x, k1(x, xa, hh) / (k1(x, xa, hh) + k1(x, xb, hh)), ls=ls, lw=lw, color=cc, label=f"$h$={hh} km")
    b.axhline(0.5, color=s["gray"], lw=0.6); b.axvline(197, color=s["gray"], lw=0.6, ls="-.")
    b.set_xlabel("동쪽으로 (km)"); b.set_ylabel("A형 이름의 비율"); b.set_title("(b) 등어선", loc="left")
    b.legend(frameon=False, loc="upper right", fontsize=8.5); b.set_ylim(0, 1.02); b.grid(color=s["grid"], lw=0.3, ls=":")
    return save(fig, "ch11", "fig11-m5-bandwidth", mode)

# ---------- 6. 개명 짝 ----------
def pairs(mode):
    s = STY[mode]
    P = [("買忽", "水城", "忽→城"), ("馬忽", "堅城", "忽→城"), ("鐵圓", "鐵城", "圓→城"), ("唐城", "唐恩", "앞글자 유지"),
         ("買省", "來蘇", "모두 바뀜"), ("夫如", "富平", "모두 바뀜"), ("牛岑", "牛峯", "앞글자 유지")]
    fig, ax = plt.subplots(figsize=(WIDTH, 3.5), constrained_layout=True)
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.4); ax.axis("off"); ax.invert_yaxis()
    ax.text(0.0, 0.1, "윗줄: 고구려 때 이름   아랫줄: 경덕왕 때 이름", fontsize=8.5, va="center")
    for i, (o, n, nt) in enumerate(P):
        r, c = divmod(i, 4)
        bx = 0.3 + c * 2.5; by = 0.9 + r * 2.7
        hi = nt.endswith("城")
        for k in (0, 1):
            x = bx + 0.3 + k * 0.9
            ax.text(x, by, o[k], ha="center", va="center", fontsize=11)
            ax.text(x, by + 1.1, n[k], ha="center", va="center", fontsize=11)
            same = o[k] == n[k]; thick = hi and k == 1
            ax.plot([x, x], [by + 0.3, by + 0.8], color=s["truth"] if (thick and mode == "color") else s["line"],
                    lw=2.4 if thick else (1.0 if same else 0.6), ls="-" if (thick or same) else ":")
        ax.text(bx + 0.75, by + 1.75, nt, ha="center", va="center", fontsize=8.5, fontweight="bold" if hi else "normal")
    ax.text(7.75, 4.4, "굵은 선: 둘째가 城\n실선: 글자 유지\n점선: 글자 바뀜", fontsize=8.5, va="center", linespacing=1.5)
    return save(fig, "ch11", "fig11-m6-pairs", mode)

# ---------- 본문 숫자 재현 ----------
def numbers():
    """원고 11장 보강 절의 숫자를 다시 계산해 출력한다. 실행: python3 tools/figs-m11.py --numbers"""
    from math import comb, exp, sqrt
    print("== R1 실제 이름 24개 (산6 물6 성4 섬1 고을7) 윌슨")
    for nm, v in zip(["산", "물", "성", "섬", "고을"], [6, 6, 4, 1, 7]): print(nm, v, [round(x, 3) for x in wilson(v, 24)])
    for nm, v in zip(["산", "물", "성", "섬", "고을"], [4, 5, 4, 1, 7]): print("묶은 뒤", nm, v, [round(x, 3) for x in wilson(v, 21)])
    print("== R2 부채꼴 겹침(창 30 km, 동쪽 +-22.5도)")
    def sector_in(px, py, ax, ay, R=30, half=22.5):
        dx = px - ax; dy = py - ay; r = np.hypot(dx, dy); ang = np.degrees(np.arctan2(dx, dy)) % 360
        return (r <= R) & (np.abs(((ang - 90 + 180) % 360) - 180) <= half)
    g = np.arange(-60, 90, 0.2); X, Y = np.meshgrid(g, g); base = sector_in(X, Y, 0, 0)
    for d in (0, 5, 10, 20, 40):
        print(d, [round((base & sector_in(X, Y, sx, sy)).sum() * 0.04, 1) for sx, sy in ((d, 0), (0, d))])
    print("== R4 사경", [(li, round(li * .36, 2), round(li * .48, 2)) for li in (31, 42, 25, 31)], wilson(2, 4))
    print("== R5", wilson(3, 7), wilson(3, 3), wilson(4, 12), wilson(8, 12))
    # 세계 만들기(씨앗 5): V1~V4
    def Lcalc(P, pts_m, pts_all, h=45, a=1.0):
        rb = len(pts_m) / len(pts_all); return ((kd(P, pts_m, h) + a * rb) / (kd(P, pts_all, h) + a)) / rb
    gg = np.arange(10, 400, 20.0); GX, GY = np.meshgrid(gg, gg); P = np.c_[GX.ravel(), GY.ravel()]
    xs = np.arange(0, 401, 5.0); river = np.c_[xs, 200 + 70 * np.sin(xs / 70.0)]
    dr = lambda pts: np.sqrt(((pts[:, None, :] - river[None, :, :]) ** 2).sum(-1)).min(1)
    tot = np.array([8, 9, 10, 11, 12, 12, 10, 9, 8, 8]); m = np.array([0, 0, 1, 3, 6, 5, 2, 0, 0, 1]); rb = m.sum() / tot.sum()
    print("== V1", [list(np.round(((m + a * rb) / (tot + a)) / rb, 2)) for a in (0, 1, 3)])
    rs = np.random.default_rng(5)
    t = rs.uniform(10, 390, 36); jin = np.c_[t, 200 + 70 * np.sin(t / 70.0) + rs.normal(0, 10, 36)]
    san = np.r_[rs.normal([320, 320], [25, 25], (14, 2)), rs.normal([70, 330], [25, 25], (14, 2))]
    seong = rs.uniform(10, 390, (40, 2)); allp = np.r_[jin, san, seong]; labs = np.array(["津"] * 36 + ["山"] * 28 + ["城"] * 40)
    dP = dr(P)
    print("== V2")
    for mm in ("津", "山", "城"):
        L = Lcalc(P, allp[labs == mm], allp); print(mm, round(L.max(), 2), round(L.min(), 2), round(np.corrcoef(np.log(L), dP)[0, 1], 3))
    rho_all = kd(P, allp, 45); K = np.exp(-((P[:, None, :] - allp[None, :, :]) ** 2).sum(-1) / (2 * 45 * 45))
    rr = np.random.default_rng(77)
    for n_ in (36, 28, 40):
        cr = []
        for _ in range(2000):
            sel = np.zeros(104, bool); sel[rr.choice(104, n_, replace=False)] = True
            rb_ = sel.mean(); L = ((K[:, sel].sum(1) + rb_) / (rho_all + 1)) / rb_; cr.append(np.corrcoef(np.log(L), dP)[0, 1])
        print(n_, np.round(np.quantile(cr, [0.01, 0.05, 0.95]), 2))
    print("== V3")
    A = rs.normal([100, 200], [20, 20], (10, 2)); B = rs.normal([300, 100], [20, 20], (6, 2)); bg = rs.uniform(10, 390, (44, 2))
    pa = np.r_[A, B, bg]; L = Lcalc(P, np.r_[A, B], pa); w = L / L.sum()
    nA = ((P - [100, 200]) ** 2).sum(1) <= 3600; nB = ((P - [300, 100]) ** 2).sum(1) <= 3600
    iA = np.argmin(((P - [100, 200]) ** 2).sum(1)); iB = np.argmin(((P - [300, 100]) ** 2).sum(1))
    print(round(L[iA], 2), round(L[iB], 2), round(L.mean(), 2), round(L.max(), 2), round(w[nA].sum(), 3), round(w[nB].sum(), 3), nA.sum())
    print("== V4")
    r4 = np.random.default_rng(8); hu = r4.normal([120, 300], [25, 25], (12, 2)); e1 = r4.uniform(10, 390, (24, 2)); e2 = r4.uniform(10, 390, (40, 2))
    mix = np.r_[hu, e1, e2]; sep = np.r_[hu, e1]; i = np.argmin(((P - [120, 300]) ** 2).sum(1)); j = np.argmin(((P - [330, 60]) ** 2).sum(1))
    Lm = Lcalc(P, hu, mix); Ls = Lcalc(P, hu, sep)
    print(round(Lm[i], 2), round(Ls[i], 2), round(Lm[j], 2), round(Ls[j], 2), round(Lm[i] / Ls[i], 2))
    print("== V5", [(n, k, round(sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n, 4)) for n, k in ((20, 15), (20, 12), (10, 8), (40, 26), (12, 9))], round(1 - .95 ** 4, 3))
    print("== V6 (그림과 같은 씨앗)")
    r6 = np.random.default_rng(21); t = r6.uniform(10, 390, 40); j6 = np.c_[t, 200 + 70 * np.sin(t / 70.0) + r6.normal(0, 10, 40)]; s6 = r6.uniform(10, 390, (40, 2))
    wd = np.r_[j6, s6]; lb = np.array(["津"] * 40 + ["城"] * 40); cap = np.array([250.0, 171.0]); dc = np.sqrt(((wd - cap) ** 2).sum(1))
    obs = np.random.default_rng(4).random(80) < np.where(dc < 80, 0.95, 0.10)
    Lt = Lcalc(P, wd[lb == "津"], wd); Lo = Lcalc(P, wd[obs & (lb == "津")], wd[obs]); nc = ((P - cap) ** 2).sum(1) < 6400; fr = (dP < 40) & (~nc)
    print(obs.sum(), (obs & (lb == "津")).sum(), (obs & (lb == "城")).sum(), round(kd(P[~nc], wd, 45).mean(), 2), round(kd(P[~nc], wd[obs], 45).mean(), 2),
          round(Lt[fr].mean(), 2), round(Lo[fr].mean(), 2), round(Lt.max(), 2), round(Lo.max(), 2), fr.sum(), round((obs & (lb == "津")).sum() / obs.sum(), 3))
    print("== V7", wilson(7, 10), wilson(3, 10), "V8", [round(1.5 ** J, 3) for J in (1, 2, 3, 5)])
    print("== V9, V10 은 그림 함수와 같은 자료")
    clu = np.r_[np.random.default_rng(101).normal([100, 100], [25, 25], (30, 2)), np.random.default_rng(102).normal([280, 150], [25, 25], (30, 2)), np.random.default_rng(103).normal([200, 320], [25, 25], (20, 2))]
    for hh in (5, 10, 15, 20, 30, 45, 60, 90):
        d2 = ((clu[:, None, :] - clu[None, :, :]) ** 2).sum(-1); Kk = np.exp(-d2 / (2 * hh * hh)) / (2 * math.pi * hh * hh); np.fill_diagonal(Kk, 0)
        print(hh, round(np.log(Kk.sum(1) / 79).sum(), 1))
    r10 = np.random.default_rng(3); xa = np.clip(r10.normal(130, 50, 24), 0, 400); xb = np.clip(r10.normal(270, 50, 24), 0, 400); xt = np.arange(0, 401, 5.0)
    k1 = lambda x, p, hh: np.exp(-(x[:, None] - p[None, :]) ** 2 / (2 * hh * hh)).sum(1)
    print("== V10", round(xa.mean(), 1), round(xb.mean(), 1))
    for hh in (20, 45, 90):
        ra = k1(xt, xa, hh) / (k1(xt, xa, hh) + k1(xt, xb, hh)); ix = np.where(np.diff(np.sign(ra - 0.5)) != 0)[0]
        print(hh, [round(float(xt[q] + 5 * (0.5 - ra[q]) / (ra[q + 1] - ra[q])), 1) for q in ix], round(ra[26], 3), round(ra[54], 3))
    EXTRA_NUMBERS()

def EXTRA_NUMBERS():
    """사례 R6, R10, V11~V14의 숫자"""
    from math import sin, cos, radians, pi, sqrt
    print("== R6 손방 30리 허", 25 * .36, 35 * .48, round(.5 * (pi / 4) * ((35 * .48) ** 2 - (25 * .36) ** 2), 1), 30 * .42)
    d = 30 * .42; cz = 25 * .42
    print("중화까지(가운데값)", round(sqrt((d * sin(radians(45))) ** 2 + (cz - d * cos(radians(45))) ** 2), 2))
    vs = [sqrt((a * u * sin(radians(45))) ** 2 + (25 * u2 - a * u * cos(radians(45))) ** 2) for a in (25, 30, 35) for u in (.36, .48) for u2 in (.36, .48)]
    print("범위", round(min(vs), 2), round(max(vs), 2))
    print("== R10", wilson(8, 12), wilson(5, 12))
    rs = np.random.default_rng(5)
    t = rs.uniform(10, 390, 36); jin = np.c_[t, 200 + 70 * np.sin(t / 70.0) + rs.normal(0, 10, 36)]
    san = np.r_[rs.normal([320, 320], [25, 25], (14, 2)), rs.normal([70, 330], [25, 25], (14, 2))]
    seong = rs.uniform(10, 390, (40, 2)); allp = np.r_[jin, san, seong]; labs = np.array(["津"] * 36 + ["山"] * 28 + ["城"] * 40)
    def lam(pts, lab, C):
        sel = lab == "津"; rb = sel.mean(); return ((kd(C, pts[sel], 45) + rb) / (kd(C, pts, 45) + 1)) / rb
    cands = np.array([[150.0, 200 + 70 * sin(150 / 70)], [350.0, 350.0], [250.0, 60.0]])
    print("== V11", np.round(lam(allp, labs, cands), 2))
    rb_ = np.random.default_rng(99); B = []
    for _ in range(1000):
        ix = rb_.integers(0, 104, 104); B.append(lam(allp[ix], labs[ix], cands))
    B = np.array(B); print(np.round(np.quantile(B, 0.025, 0), 2), np.round(np.quantile(B, 0.975, 0), 2))
    print("== V12")
    for cell in (10, 20, 40, 80):
        g = np.arange(cell / 2, 400, cell); GX, GY = np.meshgrid(g, g); P = np.c_[GX.ravel(), GY.ravel()]; L = lam(allp, labs, P)
        print(cell, len(P), round(L.max(), 2), int((L > 1.2).sum() * cell * cell), round(L.min(), 2))
    xs = np.arange(0, 401, 5.0); river = np.c_[xs, 200 + 70 * np.sin(xs / 70.0)]
    dr = np.sqrt(((allp[:, None, :] - river[None, :, :]) ** 2).sum(-1)).min(1)
    print("== V14")
    tot = []; jn = []
    for a, b in zip([0, 10, 30, 60], [10, 30, 60, 1e9]):
        sel = (dr >= a) & (dr < b); tot.append(int(sel.sum())); jn.append(int((sel & (labs == "津")).sum()))
    rbar = 36 / 104; print(tot, jn, [round(((j + rbar) / (t_ + 1)) / rbar, 2) for j, t_ in zip(jn, tot)])
    print("== V13", [round((v + 1) / 14, 4) for v in (5, 2, 1)], round(1 / 14, 4))

def EXTRA2():
    """손 계산 예제, 사례 V15~V20의 숫자"""
    from math import comb, exp
    print("== 한 차원 예제")
    x = np.arange(1, 11.0); lab = np.array([0, 0, 1, 1, 0, 1, 0, 0, 0, 0])  # 津 위치 3,4,6
    # 위치 1~10, 津 3개, 전체 10개, h=2, alpha=1
    h = 2.0; rb = lab.mean()
    rho_m = np.array([sum(exp(-(p - q) ** 2 / (2 * h * h)) for q in x[lab == 1]) for p in x])
    rho_a = np.array([sum(exp(-(p - q) ** 2 / (2 * h * h)) for q in x) for p in x])
    r = (rho_m + rb) / (rho_a + 1)
    print("rb", rb); print("rho_m", np.round(rho_m, 2)); print("rho_a", np.round(rho_a, 2)); print("r", np.round(r, 3)); print("L", np.round(r / rb, 2))
    print("== V15 방위 쌍 부호검정")
    def binom_two(k, n):
        pr = [comb(n, i) / 2 ** n for i in range(n + 1)]; return sum(p for p in pr if p <= pr[k] + 1e-12)
    print(binom_two(10, 12), binom_two(9, 12), binom_two(7, 12))
    print("== V16 동명이소")
    rs = np.random.default_rng(5)
    t_ = rs.uniform(10, 390, 36); jin = np.c_[t_, 200 + 70 * np.sin(t_ / 70.0) + rs.normal(0, 10, 36)]
    san = np.r_[rs.normal([320, 320], [25, 25], (14, 2)), rs.normal([70, 330], [25, 25], (14, 2))]
    seong = rs.uniform(10, 390, (40, 2)); allp = np.r_[jin, san, seong]
    print("== V17 판독")
    print("== V18 피셔")
    def fisher(a, b, c, d):
        n = a + b + c + d; r1 = a + b; c1 = a + c
        def pr(k): return comb(r1, k) * comb(n - r1, c1 - k) / comb(n, c1)
        p0 = pr(a); return sum(pr(k) for k in range(max(0, c1 - (n - r1)), min(r1, c1) + 1) if pr(k) <= p0 + 1e-12)
    print(round(fisher(9, 3, 3, 9), 4), round(fisher(4, 8, 2, 10), 4))
    print("== V19 사전 오즈")
    o = (1 / 4) * 2.43; print(round(o, 3), round(o / (1 + o), 3))
    o2 = o * 0.85; print(round(o2, 3), round(o2 / (1 + o2), 3))
    print("== V20 무작위 이름표의 최대 Lambda")
    K = np.exp(-((np.c_[np.meshgrid(np.arange(10, 400, 20.0), np.arange(10, 400, 20.0))[0].ravel(), np.meshgrid(np.arange(10, 400, 20.0), np.arange(10, 400, 20.0))[1].ravel()][:, None, :] - allp[None, :, :]) ** 2).sum(-1) / (2 * 45 * 45))
    rho_all = K.sum(1); rr = np.random.default_rng(31)
    for n_ in (3, 5, 10, 20, 28, 36, 40):
        mx = []
        for _ in range(2000):
            sel = np.zeros(104, bool); sel[rr.choice(104, n_, replace=False)] = True; rb_ = sel.mean()
            mx.append((((K[:, sel].sum(1) + rb_) / (rho_all + 1)) / rb_).max())
        print(n_, np.round(np.quantile(mx, [0.5, 0.95]), 2))

def EXTRA3():
    """실제 사례 R11~R13의 숫자"""
    print("== R11 실례 30개 분류")
    A = [2, 3, 6, 7, 8, 12, 13, 14, 15, 16, 17, 18, 20, 25, 27, 28, 29, 30]
    B = [i for i in range(1, 31) if i not in A]
    L2 = set(range(22, 28)); print("A", len(A), "B", len(B), B, "2층 A", [i for i in A if i in L2], "2층 B", [i for i in B if i in L2])
    print("wilson A", [round(x, 3) for x in wilson(len(A), 30)], "B", [round(x, 3) for x in wilson(len(B), 30)])
    print("== R12 성 비율", [round(x, 3) for x in wilson(4, 24)], [round(x, 3) for x in wilson(5, 25)], [round(x, 3) for x in wilson(4, 25)])
    print("== R13 길이별", [round(x, 3) for x in wilson(7, 13)], [round(x, 3) for x in wilson(0, 11)], [round(x, 3) for x in wilson(6, 13)], [round(x, 3) for x in wilson(11, 11)])
    names = {"山": ["大城山", "九龍山", "魯陽山", "木覓山", "龍山", "兔山"], "水": ["大同江", "浿水", "浿江", "烏灘", "亇屯津", "九津溺水"], "城": ["東黃城", "國北新城", "長安城", "邑石城"], "島": ["椒島"], "邑": ["平壤", "西京", "祥原", "江西", "中和", "順安", "漢城"]}
    from collections import Counter
    c = Counter((len(n), k) for k, v in names.items() for n in v); print(sorted(c.items()))
    print(Counter(len(n) for v in names.values() for n in v))

def EXTRA4():
    """사례 V19(평활 상수 민감도), V20(대역폭별 순위 일치), 山 작성 예"""
    from math import sin
    rs = np.random.default_rng(5)
    t_ = rs.uniform(10, 390, 36); jin = np.c_[t_, 200 + 70 * np.sin(t_ / 70.0) + rs.normal(0, 10, 36)]
    san = np.r_[rs.normal([320, 320], [25, 25], (14, 2)), rs.normal([70, 330], [25, 25], (14, 2))]
    seong = rs.uniform(10, 390, (40, 2)); allp = np.r_[jin, san, seong]; labs = np.array(["津"] * 36 + ["山"] * 28 + ["城"] * 40)
    def lam(C, h=45, a=1.0, lab="津"):
        sel = labs == lab; rb = sel.mean(); return ((kd(C, allp[sel], h) + a * rb) / (kd(C, allp, h) + a)) / rb
    cands = np.array([[150.0, 200 + 70 * sin(150 / 70)], [350.0, 350.0], [250.0, 60.0]])
    print("== V19")
    for a in (0.1, 0.5, 1, 2, 5, 10): print(a, np.round(lam(cands, a=a), 2))
    g = np.arange(10, 400, 20.0); GX, GY = np.meshgrid(g, g); P = np.c_[GX.ravel(), GY.ravel()]
    rank = lambda x: np.argsort(np.argsort(x))
    Ls = {h: lam(P, h=h) for h in (20, 30, 45, 60, 90)}
    print("== V20 순위 상관과 상위 40칸 겹침")
    ks = list(Ls)
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            print(a, b, round(np.corrcoef(rank(Ls[a]), rank(Ls[b]))[0, 1], 3), len(set(np.argsort(-Ls[a])[:40]) & set(np.argsort(-Ls[b])[:40])))
    print("== 山 네 칸")
    C = np.array([[320., 320.], [200., 200.], [70., 330.], [330., 60.]]); sel = labs == "山"; rb = sel.mean()
    rm = kd(C, allp[sel], 45); ra = kd(C, allp, 45); r = (rm + rb) / (ra + 1)
    print(np.round(rm, 2), np.round(ra, 2), round(rb, 3), np.round(r, 3), np.round(r / rb, 2))

if __name__ == "__main__":
    if "--numbers4" in sys.argv:
        EXTRA4(); sys.exit()
    if "--numbers3" in sys.argv:
        EXTRA3(); sys.exit()
    if "--numbers2" in sys.argv:
        EXTRA2(); sys.exit()
    if "--numbers" in sys.argv:
        numbers(); sys.exit()
    for mode in ("color", "bw"):
        for f in (chrono, kernel, realnames, bias, bandwidth, pairs):
            print(f(mode))
