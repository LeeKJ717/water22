"""figs-p1.py - 1장(사료) 새 그림. 실행: python3 tools/figs-p1.py  (그림/ch01 에 컬러·흑백 PDF 생성)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from figlib import *

FS = 8.5


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


# ---------------------------------------------------------------- 그림 1: 두 줄 연대기
def fig_timeline(mode):
    s = STY[mode]
    c_top = "#1f6fb8" if mode == "color" else "#000000"
    c_bot = "#c0392b" if mode == "color" else "#444444"
    fig, ax = plt.subplots(figsize=(WIDTH, 4.7))
    fig.subplots_adjust(left=0.03, right=0.97, top=0.97, bottom=0.07)
    ax.set_xlim(1080, 1905); ax.set_ylim(-3.7, 6.0)
    ax.axis("off")
    yt, yb = 2.6, 0.0
    for y, c, ls in [(yt, c_top, "-"), (yb, c_bot, "-")]:
        ax.plot([1100, 1880], [y, y], color=c, lw=2.0, ls=ls, zorder=2)
    for yr in range(1100, 1900, 100):
        for y in (yt, yb):
            ax.plot([yr, yr], [y - 0.1, y + 0.1], color=s["line"], lw=0.8, zorder=3)
        ax.text(yr, (yt + yb) / 2 + 0.0, str(yr), ha="center", va="center", fontsize=FS, color=s["gray"],
                bbox=dict(fc="white", ec="none", pad=0.8), zorder=1)
    ax.text(1092, yt + 0.28, "학문사", fontsize=FS, fontweight="bold", color=c_top, ha="left", va="bottom")
    ax.text(1092, yb + 0.28, "사료 편찬", fontsize=FS, fontweight="bold", color=c_bot, ha="left", va="bottom")
    # (이름, 해, 글자 가운데 x, 높이 단계)
    top = [("발라\n1440", 1440, 1440, 1), ("한백겸\n1615", 1615, 1590, 1), ("고염무\n1670", 1670, 1655, 2),
           ("마비용\n1681", 1681, 1720, 1), ("정약용\n1811", 1811, 1785, 1), ("랑케\n1824", 1824, 1840, 2),
           ("라흐만\n1831", 1831, 1865, 1)]
    for t, yr, tx, lv in top:
        ty = yt + 0.55 + (lv - 1) * 0.95
        ax.plot([yr, tx], [yt, ty], color=c_top, lw=0.7, zorder=2)
        ax.plot(yr, yt, "o", ms=5, color=c_top if mode == "color" else "white", mec=c_top, mew=1.0, zorder=4)
        ax.text(tx, ty, t, ha="center", va="bottom", fontsize=FS, linespacing=1.05)
    bot = [("고려도경\n1124", 1124, 1124, 1), ("삼국사기\n1145", 1145, 1190, 2), ("신찬팔도\n지리지\n1432", 1432, 1350, 1),
           ("고려사\n1451", 1451, 1385, 2), ("세종실록\n지리지\n1454", 1454, 1480, 2),
           ("동국여지\n승람\n1481", 1481, 1510, 1), ("신증동국\n여지승람\n1530", 1530, 1610, 2), ("동국지리지\n1615", 1615, 1685, 1),
           ("아방강역고\n1811", 1811, 1790, 1), ("대동여지도\n1861", 1861, 1865, 2)]
    for t, yr, tx, lv in bot:
        ty = yb - 0.55 - (lv - 1) * 1.15
        ax.plot([yr, tx], [yb, ty + 0.08], color=c_bot, lw=0.7, zorder=2)
        ax.plot(yr, yb, "s", ms=5, color=c_bot if mode == "color" else "white", mec=c_bot, mew=1.0, zorder=4)
        ax.text(tx, ty, t, ha="center", va="top", fontsize=FS, linespacing=1.05)
    # 같은 해의 짝(점선): 한백겸-동국지리지, 정약용-아방강역고
    for yr in (1615, 1811):
        ax.plot([yr, yr], [yb, yt], color=s["gray"], lw=0.8, ls=":", zorder=1)
    return save(fig, "ch01", "fig01-a-timeline", mode)


# ---------------------------------------------------------------- 그림 2: 지리지 계통(확인된 것만 실선)
def fig_lineage(mode):
    fig, ax = plt.subplots(figsize=(WIDTH, 3.9))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    ax.set_xlim(0, 10); ax.set_ylim(0, 8.2); ax.axis("off")
    box(ax, 1.5, 7.3, 2.7, 0.8, "각 도 지리지\n(1425년 경상도지리지 등)", mode)
    box(ax, 1.5, 5.6, 2.7, 0.8, "신찬팔도지리지\n1432", mode)
    box(ax, 1.5, 3.9, 2.7, 0.8, "세종실록지리지\n1454", mode, bold=True)
    box(ax, 1.5, 2.2, 2.7, 0.8, "동국여지승람\n1481", mode)
    box(ax, 1.5, 0.5, 2.7, 0.8, "신증동국여지승람\n1530", mode)
    box(ax, 8.1, 3.9, 3.0, 0.8, "『문헌통고』\n(중국 책)", mode, hatch="//" if mode == "bw" else None,
        fc="#ffffff" if mode == "bw" else "#e3eef8")
    arrow(ax, 1.5, 6.9, 1.5, 6.0, mode)
    arrow(ax, 1.5, 5.2, 1.5, 4.3, mode)
    arrow(ax, 1.5, 3.5, 1.5, 2.6, mode, ls="--")
    arrow(ax, 1.5, 1.8, 1.5, 0.9, mode)
    arrow(ax, 6.6, 3.9, 2.9, 3.9, mode)
    for y, t in [(6.45, "저본이 됨 (확인)"), (4.75, "실록에 부록 (확인)"), (3.05, "관계 미확인"), (1.35, "증보 (확인)")]:
        ax.text(1.75, y, t, fontsize=FS, va="center", ha="left")
    ax.text(5.0, 4.45, "머리말에서 인용\n(본문에서 확인)", fontsize=FS, ha="center", va="bottom")
    ax.text(5.0, 7.3, "실선 화살표: 편찬 기록이나\n본문으로 확인한 관계\n점선 화살표: 아직 확인하지 못한 관계", fontsize=FS,
            ha="left", va="center")
    ax.text(5.0, 1.3, "이 그림은 지리지 계통의 일부만\n보여 준다. 다른 지리지와의 관계는\n이 책이 아직 모른다.", fontsize=FS, ha="left",
            va="center")
    return save(fig, "ch01", "fig01-b-lineage", mode)


# ---------------------------------------------------------------- 그림 3: 가상 사본 계통
def fig_copies(mode):
    c1 = "#c0392b" if mode == "color" else "#000000"
    c2 = "#1f6fb8" if mode == "color" else "#555555"
    fig, ax = plt.subplots(figsize=(WIDTH, 3.4))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.97, bottom=0.02)
    ax.set_xlim(0, 10); ax.set_ylim(0, 7.2); ax.axis("off")
    box(ax, 5.0, 6.5, 2.6, 0.8, "원본 X (사라짐)", mode)
    box(ax, 2.6, 4.6, 2.0, 0.8, "사본 A", mode)
    box(ax, 7.4, 4.6, 2.0, 0.8, "사본 B", mode)
    box(ax, 1.4, 2.5, 1.9, 0.8, "사본 C", mode)
    box(ax, 3.8, 2.5, 1.9, 0.8, "사본 D", mode)
    box(ax, 7.4, 2.5, 1.9, 0.8, "사본 E", mode)
    for a, b in [((5.0, 6.1), (2.9, 5.0)), ((5.0, 6.1), (7.1, 5.0)), ((2.4, 4.2), (1.5, 2.9)), ((2.8, 4.2), (3.7, 2.9)),
                 ((7.4, 4.2), (7.4, 2.9))]:
        arrow(ax, a[0], a[1], b[0], b[1], mode)
    ax.text(0.15, 5.6, "오류 ①\n(A에서 생김)", fontsize=FS, color=c1, va="center", ha="left", fontweight="bold")
    ax.text(9.85, 5.6, "오류 ②\n(B에서 생김)", fontsize=FS, color=c2, va="center", ha="right", fontweight="bold")
    ax.plot(2.6, 4.05, "D", ms=7, color=c1, mec=c1, zorder=5)
    ax.plot(7.4, 4.05, "s", ms=7, color=c2, mec=c2, zorder=5)
    for x in (1.4, 3.8):
        ax.plot(x, 1.95, "D", ms=7, color=c1, mec=c1, zorder=5)
    ax.plot(7.4, 1.95, "s", ms=7, color=c2, mec=c2, zorder=5)
    ax.text(2.6, 1.05, "C, D는 ①을 물려받았다 (◆)", fontsize=FS, color=c1, ha="center", va="center")
    ax.text(7.4, 1.05, "E는 ②를 물려받았다 (■)", fontsize=FS, color=c2, ha="center", va="center")
    ax.text(5.0, 0.2, "가상 사례: 서경의 결과가 아니다.", fontsize=FS, ha="center", va="center", color=STY[mode]["gray"])
    return save(fig, "ch01", "fig01-c-copies", mode)


# ---------------------------------------------------------------- 그림 4: 사본이 거듭될 때 오류 수
def err(N, p, k):
    return N * (1 - (1 - p) ** k)


def fig_errors(mode):
    s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 2.9), constrained_layout=True)
    ks = np.arange(0, 11)
    cols = ["#1f6fb8", "#2e7d32", "#c0392b"] if mode == "color" else ["#000000", "#444444", "#888888"]
    lss = ["-", "--", "-."]
    mks = ["o", "s", "^"]
    for p, c, ls, mk in zip([0.001, 0.002, 0.005], cols, lss, mks):
        ax.plot(ks, err(1000, p, ks), color=c, ls=ls, marker=mk, ms=4, lw=1.3, label=f"한 번에 틀릴 확률 p = {p}")
    ax.set_xlabel("사본을 거듭한 횟수 k (번)")
    ax.set_ylabel("틀린 글자 수 (자)")
    ax.set_xticks(range(0, 11))
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    ax.legend(loc="upper left", frameon=False)
    ax.set_title("가상 값: 글자 1000자를 베껴 쓸 때", loc="left")
    return save(fig, "ch01", "fig01-d-errors", mode)


# ---------------------------------------------------------------- 그림 5: 증거의 세 층
def fig_layers(mode):
    s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 3.5))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    ax.set_xlim(0, 10); ax.set_ylim(0, 9.4); ax.axis("off")
    fcs = ["#f0b45a", "#9fc5e8", "#d9d9d9"] if mode == "color" else ["#ffffff", "#e6e6e6", "#bdbdbd"]
    hs = [None, "..", "//"] if mode == "bw" else [None, None, None]
    rows = [(7.7, "1층", "옛 문헌의 구절", "고려사 문종 35년 기사(E1)\n삼국사기 고국원왕 13년 주(E3)\n신증동국여지승람 평양부(E6)\n해동역사 궁실지(E9)"),
            (4.6, "2층", "연구자가 읽거나 잰 것", "각자성석 판독문(E8, E10~E12)\n장안성 구역 면적(E5)"),
            (1.5, "3층", "연구자의 해석", "동쪽 좌궁=안학궁이라는 견해(E2)")]
    for (y, a, b, ex), fc, h in zip(rows, fcs, hs):
        box(ax, 1.5, y, 2.5, 1.5 if a == "1층" else 1.3, f"{a}\n{b}" if a != "2층" else f"{a}\n{b}", mode, fc=fc, hatch=h, bold=True, fs=FS)
        ax.text(3.2, y, ex, fontsize=FS, va="center", ha="left")
    arrow(ax, 8.9, 1.0, 8.9, 8.6, mode, lw=1.3)
    ax.text(9.1, 4.8, "증거로 쓰는 무게", rotation=90, fontsize=FS, va="center", ha="left")
    ax.text(8.7, 9.2, "무겁다", fontsize=FS, ha="right", va="center")
    ax.text(8.7, 0.3, "가볍다", fontsize=FS, ha="right", va="center")
    return save(fig, "ch01", "fig01-e-layers", mode)


# ---------------------------------------------------------------- 그림 6: 표결과 계통 세기
def fig_vote(mode):
    s = STY[mode]
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 2.5), constrained_layout=True)
    c = ["#1f6fb8", "#c0392b"] if mode == "color" else ["#666666", "#000000"]
    h = [None, None] if mode == "color" else ["//", ".."]
    ax = axs[0]
    ax.bar(["12리\n(A, C, D)", "5리\n(B, E)"], [3, 2], color=c, edgecolor=s["line"], hatch=None, lw=0.8)
    for i, hh in enumerate(h):
        if hh: ax.patches[i].set_hatch(hh)
    ax.set_ylim(0, 4); ax.set_yticks(range(0, 5)); ax.set_ylabel("사본의 수 (개)")
    ax.set_title("(가) 사본 수로 센 표결", loc="left", fontsize=9)
    ax = axs[1]
    ax.bar(["12리\n(A 계통)", "5리\n(B 계통)"], [1, 1], color=c, edgecolor=s["line"], lw=0.8)
    for i, hh in enumerate(h):
        if hh: ax.patches[i].set_hatch(hh)
    ax.set_ylim(0, 4); ax.set_yticks(range(0, 5)); ax.set_ylabel("독립 증거의 수 (건)")
    ax.set_title("(나) 계통으로 센 독립 증거", loc="left", fontsize=9)
    return save(fig, "ch01", "fig01-f-vote", mode)


if __name__ == "__main__":
    for m in ("color", "bw"):
        for f in (fig_timeline, fig_lineage, fig_copies, fig_errors, fig_layers):
            print(f(m))
