"""figs-p3.py - 3장(사료 비판 입문)의 새 그림 다섯 장. 컬러판과 흑백판을 모두 만든다.
실행: python3 tools/figs-p3.py   (그림/ch03/ 아래에 PDF 생성)
수치 출처: 리(里) 길이는 Wikipedia contributors(n.d.)의 Li (unit), Korean units of measurement 쪽의 값을 그대로 옮긴 것이다.
나머지 숫자는 이 파일에서 직접 계산한다."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Rectangle
from figlib import *

FS = 8.5     # 그림 속 글자 크기(최소)
TXT = dict(fontsize=FS)


def cols(mode):
    if mode == "color":
        return dict(a="#1f6fb8", b="#c0392b", c="#2e7d32", d="#8e44ad", e="#e67e22", g="#777777", band="#f6e3b4", ink="#222222")
    return dict(a="#444444", b="#000000", c="#888888", d="#bbbbbb", e="#dddddd", g="#555555", band="#e6e6e6", ink="#000000")


# ---------------------------------------------------------------- 그림 1: 연대기 종합
def fig_chronicle(mode):
    C = cols(mode)
    fig = plt.figure(figsize=(WIDTH, 7.3))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.8, 4.9], hspace=0.28, left=0.04, right=0.97, top=0.965, bottom=0.075)
    # (가) 판각과 편찬, 어려운 읽기의 뿌리
    ax = fig.add_subplot(gs[0])
    ax.set_xlim(700, 1560); ax.set_ylim(-0.6, 4.7); ax.invert_yaxis()
    rows = [("751경 신라 대다라니경 인쇄", 751, None, "d", "o"),
            ("1145 삼국사기 편찬", 1145, None, "a", "s"),
            ("팔만대장경 판각 1236~1251", 1236, 1251, "b", "bar"),
            ("랍베이누 탐 1100~1171", 1100, 1171, "c", "bar"),
            ("에라스뮈스 주석 1500년대 초", 1500, 1519, "e", "bar")]
    for i, (lab, x0, x1, ck, kind) in enumerate(rows):
        y = i
        if kind == "bar":
            ax.add_patch(Rectangle((x0, y - 0.28), x1 - x0, 0.56, fc=C[ck], ec=C["ink"], lw=0.6, hatch="//" if mode == "bw" and i % 2 else None))
        else:
            ax.plot(x0, y, "D" if kind == "s" else "o", ms=7, mfc=C[ck], mec=C["ink"], mew=0.7)
        if x0 < 1000:
            ax.text(x0 + 18, y, lab, va="center", ha="left", **TXT)
        else:
            ax.text(x0 - 14, y, lab, va="center", ha="right", **TXT)
    ax.set_yticks([]); ax.set_xticks(range(700, 1601, 100))
    ax.tick_params(axis="x", labelsize=FS)
    ax.grid(axis="x", color=STY[mode]["grid"], lw=0.3, ls=":")
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    ax.set_title("(가) 700~1550년: 판각과 편찬, 어려운 읽기의 뿌리", loc="left", fontsize=9)
    ax.set_xlabel("연도 (서기)", fontsize=FS)
    # (나) 근대: 인물 수명, 단위 제도, 구간 해석학
    ax = fig.add_subplot(gs[1])
    ax.set_xlim(1620, 1985); ax.set_ylim(13.6, -1.1)
    people = [("염약거 1636~1704", 1636, 1704, [], "c"), ("벵겔 1687~1752", 1687, 1752, [1725, 1734], "c"),
              ("라흐만 1793~1851", 1793, 1851, [1850], "a"), ("랑케 1795~1886", 1795, 1886, [1824], "a"),
              ("랑글루아 1863~1929", 1863, 1929, [1898], "d"), ("블로크 1886~1944", 1886, 1944, [1949], "d")]
    ax.text(1622, -0.75, "사료 비판의 학자 (막대 = 생존 기간, ◆ = 주요 저서가 나온 해)", fontsize=FS, fontweight="bold", va="center")
    for i, (lab, x0, x1, works, ck) in enumerate(people):
        y = i * 1.3 + 0.55
        ax.add_patch(Rectangle((x0, y - 0.27), x1 - x0, 0.54, fc=C[ck], ec=C["ink"], lw=0.6, hatch=["", "//", "..", "xx", "\\\\", "--"][i] if mode == "bw" else None))
        for w in works:
            ax.plot(w, y, "D", ms=6, mfc="white", mec=C["ink"], mew=0.9, zorder=5)
            ha_ = "right" if w == 1725 else "left" if w == 1734 else "center"
            ax.text(w + (-2 if w == 1725 else 2 if w == 1734 else 0), y - 0.45, str(w), ha=ha_, va="bottom", fontsize=FS - 0.5)
        if x1 < 1800:
            ax.text(x1 + 6 if not works or max(works) < x1 else max(works) + 8, y + 0.02, lab, va="center", ha="left", **TXT)
        else:
            ax.text(x0 - 6, y + 0.02, lab, va="center", ha="right", **TXT)
    # 단위 제도
    y0 = 8.4
    ax.text(1622, y0 - 0.65, "단위 제도 (미터법)", fontsize=FS, fontweight="bold", va="center")
    for yr, ha, dy in [(1790, "right", 0), (1799, "left", 0), (1875, "right", 0), (1889, "left", 0)]:
        ax.plot(yr, y0 + 0.2, "o", ms=6, mfc=C["e"], mec=C["ink"], mew=0.7, zorder=5)
        ax.text(yr + (-5 if ha == "right" else 5), y0 + 0.2, str(yr), ha=ha, va="center", fontsize=FS)
    ax.plot([1790, 1889], [y0 + 0.2] * 2, color=C["ink"], lw=0.5, zorder=1)
    ax.text(1622, y0 + 0.95, "1790 학술원 제안 · 1799 기준 막대 · 1875 미터협약 · 1889 국제 원기", fontsize=FS, va="center", ha="left")
    # 구간 해석학
    y1 = 10.8
    ax.text(1622, y1 - 0.5, "구간 해석학", fontsize=FS, fontweight="bold", va="center")
    items = [("수나가 1958 (구간 대수)", 1958), ("무어 1962 (학위논문)", 1962), ("무어 1966 (책 『구간 해석』)", 1966)]
    for j, (lab, yr) in enumerate(items):
        yy = y1 + 0.35 + 0.9 * j
        ax.plot(yr, yy, "s", ms=6, mfc=C["b"], mec=C["ink"], mew=0.7, zorder=5)
        ax.text(yr - 6, yy, lab, ha="right", va="center", fontsize=FS)
    ax.set_yticks([]); ax.set_xticks(range(1650, 1951, 50))
    ax.tick_params(axis="x", labelsize=FS)
    ax.grid(axis="x", color=STY[mode]["grid"], lw=0.3, ls=":")
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    ax.set_title("(나) 1620~1985년: 인물, 단위 제도, 구간 해석학", loc="left", fontsize=9)
    ax.set_xlabel("연도 (서기)", fontsize=FS)
    return save(fig, "ch03", "fig03-1-chronicle", mode)


# ---------------------------------------------------------------- 그림 2: 리(里)의 길이
def fig_ri(mode):
    C = cols(mode)
    fig, ax = plt.subplots(figsize=(WIDTH, 3.3), constrained_layout=True)
    data = [("서주(西周) 기원전 1045~771", 358, 358, "a"), ("동주(東周) 기원전 770~250", 416, 416, "a"),
            ("한(漢) 기원전 205~기원후 220", 415.8, 415.8, "a"), ("당(唐) 618~907", 323, 323, "a"),
            ("청(淸) 1644~1911 (표의 폭)", 537, 645, "d"), ("현대 중국 1984~", 500, 500, "a"),
            ("한국 1905년 표준", 393, 393, "c"), ("한국 옛 값 (3세기~19세기)", 434, 450, "c")]
    ax.axvspan(360, 480, color=C["band"], zorder=0, hatch="//" if mode == "bw" else None, alpha=1 if mode == "color" else 0.6)
    ax.text(420, -0.85, "이 책의 가상 구간 360~480 m", ha="center", va="center", fontsize=FS)
    for i, (lab, lo, hi, ck) in enumerate(data):
        if lo == hi:
            ax.plot(lo, i, "o", ms=7, mfc=C[ck], mec=C["ink"], mew=0.7, zorder=4)
            ax.text(lo + 12, i, f"{lo:g} m", va="center", fontsize=FS)
        else:
            ax.plot([lo, hi], [i, i], color=C[ck], lw=6, solid_capstyle="butt", zorder=3, path_effects=None)
            ax.text(hi + 12, i, f"{lo:g}~{hi:g} m", va="center", fontsize=FS)
    ax.set_yticks(range(len(data))); ax.set_yticklabels([d[0] for d in data], fontsize=FS)
    ax.set_ylim(len(data) - 0.4, -1.3); ax.set_xlim(280, 760)
    ax.set_xlabel("1리(里)의 길이 (미터)", fontsize=FS)
    ax.grid(axis="x", color=STY[mode]["grid"], lw=0.3, ls=":")
    for s in ("right", "top"):
        ax.spines[s].set_visible(False)
    return save(fig, "ch03", "fig03-2-ri-values", mode)


# ---------------------------------------------------------------- 그림 3: 방위 부채꼴
def fig_wedges(mode):
    C = cols(mode)
    fig = plt.figure(figsize=(WIDTH, 3.3))
    D = 200.0
    specs = [("8방위: 서(西)는 45도", 45, ["북", "북동", "동", "남동", "남", "남서", "서", "북서"], 270),
             ("12지: 유(酉)는 30도", 30, ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"], 270)]
    for k, (ttl, th, labs, center) in enumerate(specs):
        ax = fig.add_axes([0.10 + 0.47 * k, 0.15, 0.34, 0.64], projection="polar")
        ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)
        ax.set_ylim(0, 245)
        t1, t2 = math.radians(center - th / 2), math.radians(center + th / 2)
        tt = np.linspace(t1, t2, 60)
        ax.fill_between(tt, 0, D, color=C["e"] if mode == "color" else "#cccccc", hatch="//" if mode == "bw" else None, ec=C["ink"], lw=0.6, zorder=1)
        ax.plot([t1, t1], [0, D], color=C["ink"], lw=0.8); ax.plot([t2, t2], [0, D], color=C["ink"], lw=0.8)
        ax.plot(tt, [D] * len(tt), color=C["ink"], lw=1.4)
        ax.set_thetagrids(np.arange(0, 360, 360 / len(labs)), labels=labs, fontsize=FS)
        ax.set_rgrids([100, 200], labels=["100", "200 km"], fontsize=FS, angle=160)
        ax.grid(color=STY[mode]["grid"], lw=0.4, ls=":")
        chord = 2 * D * math.sin(math.radians(th / 2))
        ax.set_title(ttl, fontsize=9, pad=12)
        fig.text(0.10 + 0.47 * k + 0.17, 0.03, f"거리 200 km에서 옆 폭 약 {chord:.0f} km", ha="center", fontsize=FS)
    return save(fig, "ch03", "fig03-3-wedges", mode)


# ---------------------------------------------------------------- 그림 4: 숫자 한 글자가 바뀌면
def fig_numerals(mode):
    C = cols(mode)
    fig, ax = plt.subplots(figsize=(WIDTH, 2.7), constrained_layout=True)
    o = 490
    vs = [("九→八 (사백팔십)", 480), ("十 빠짐 (사백구)", 409), ("四→三 (삼백구십)", 390), ("四→五 (오백구십)", 590)]
    ax.axvspan(-25, 25, color=C["band"], zorder=0, hatch="//" if mode == "bw" else None, alpha=1 if mode == "color" else 0.6)
    ax.text(0, -0.85, "기록자 어림 ±25%", ha="center", va="center", fontsize=FS)
    for i, (lab, v) in enumerate(vs):
        e = (v - o) / o * 100
        inside = abs(e) <= 25
        ax.barh(i, e, color=C["c"] if inside else C["b"], ec=C["ink"], lw=0.6, height=0.55, hatch=None if inside else ("//" if mode == "bw" else None), zorder=3)
        ax.text(e + (1.2 if e >= 0 else -1.2), i, f"{v}리 ({e:+.1f}%)", va="center", ha="left" if e >= 0 else "right", fontsize=FS)
    ax.axvline(0, color=C["ink"], lw=0.8, zorder=4)
    ax.set_yticks(range(len(vs))); ax.set_yticklabels([v[0] for v in vs], fontsize=FS)
    ax.set_xlim(-60, 60); ax.set_ylim(len(vs) - 0.4, -1.3)
    ax.set_xlabel("원래 값 490리에서 벗어난 정도 (%)", fontsize=FS)
    ax.grid(axis="x", color=STY[mode]["grid"], lw=0.3, ls=":")
    for s in ("right", "top"):
        ax.spines[s].set_visible(False)
    return save(fig, "ch03", "fig03-4-numeral-errors", mode)


# ---------------------------------------------------------------- 그림 5: 구간이 쌓이는 모양
def fig_stack(mode):
    C = cols(mode)
    lo, hi, n, eps = 0.36, 0.48, 490, 0.25
    a1, b1 = n * lo, n * hi
    a2, b2 = a1 * (1 - eps), b1 * (1 + eps)
    th = math.radians(45)
    A1 = 0.5 * th * (b1 ** 2 - a1 ** 2)
    A2 = 0.5 * th * (b2 ** 2 - a2 ** 2)
    fig = plt.figure(figsize=(WIDTH, 5.3))
    ax = fig.add_axes([0.25, 0.79, 0.71, 0.12])
    for i, (lab, x0, x1, ck) in enumerate([("단위만 (0.36~0.48 km)", a1, b1, "a"), ("단위 + 어림 ±25%", a2, b2, "b")]):
        ax.add_patch(Rectangle((x0, i - 0.25), x1 - x0, 0.5, fc=C[ck], ec=C["ink"], lw=0.6, hatch="//" if mode == "bw" and i else None))
        ax.text(x0 - 4, i, f"{x0:.1f}", ha="right", va="center", fontsize=FS)
        ax.text(x1 + 4, i, f"{x1:.1f} km", ha="left", va="center", fontsize=FS)
    ax.set_yticks([0, 1]); ax.set_yticklabels(["단위만\n(폭 58.8 km)", "단위 + 어림\n(폭 161.7 km)"], fontsize=FS)
    ax.set_xlim(90, 350); ax.set_ylim(1.5, -0.6)
    ax.set_xlabel("가상의 서술 '490리'가 허락하는 거리 (km)", fontsize=FS)
    for s in ("right", "top"):
        ax.spines[s].set_visible(False)
    fig.text(0.04, 0.955, "(가) 거리의 구간", fontsize=9, fontweight="bold")
    # (나) 띠와 부채꼴
    ax2 = fig.add_axes([0.04, 0.035, 0.92, 0.60])
    ax2.set_aspect("equal"); ax2.set_xlim(-320, 40); ax2.set_ylim(-125, 125)
    ax2.add_patch(Wedge((0, 0), b2, 180 - 22.5, 180 + 22.5, width=b2 - a2, fc=C["e"] if mode == "color" else "#dddddd", ec=C["ink"], lw=0.8, ls="--"))
    ax2.add_patch(Wedge((0, 0), b1, 180 - 22.5, 180 + 22.5, width=b1 - a1, fc=C["b"] if mode == "color" else "#555555", ec=C["ink"], lw=0.8, alpha=0.85))
    ax2.plot(0, 0, "^", ms=8, mfc=C["ink"], mec=C["ink"])
    ax2.text(6, 0, "기준 B", fontsize=FS, va="center")
    ax2.annotate(f"단위만 반영\n약 {A1:,.0f} km²", xy=(-(a1 + b1) / 2 * math.cos(math.radians(8)), -(a1 + b1) / 2 * math.sin(math.radians(8))), xytext=(-105, -85), fontsize=FS,
                 arrowprops=dict(arrowstyle="-", lw=0.7), va="center")
    ax2.annotate(f"어림까지 반영\n(점선 안쪽 전체)\n약 {A2:,.0f} km²", xy=(-(b2 - 8) * math.cos(math.radians(16)), (b2 - 8) * math.sin(math.radians(16))), xytext=(-105, 78), fontsize=FS,
                 arrowprops=dict(arrowstyle="-", lw=0.7), va="center")
    ax2.set_xlabel("서쪽으로 (km)", fontsize=FS); ax2.set_yticks([])
    for s in ("right", "top", "left"):
        ax2.spines[s].set_visible(False)
    fig.text(0.04, 0.68, "(나) 거리의 띠와 서쪽 45도 부채꼴이 겹친 영역", fontsize=9, fontweight="bold")
    return save(fig, "ch03", "fig03-5-interval-stack", mode)


if __name__ == "__main__":
    for mode in ("color", "bw"):
        print(fig_chronicle(mode)); print(fig_ri(mode)); print(fig_wedges(mode)); print(fig_numerals(mode)); print(fig_stack(mode))
    lo, hi, n, eps = 0.36, 0.48, 490, 0.25
    th = math.radians(45)
    print("A1", 0.5 * th * ((n * hi) ** 2 - (n * lo) ** 2), "A2", 0.5 * th * ((n * hi * (1 + eps)) ** 2 - (n * lo * (1 - eps)) ** 2))
