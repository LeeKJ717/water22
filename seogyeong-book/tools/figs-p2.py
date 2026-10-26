"""figs-p2.py - 2장(기존 학설 정리) 새 그림. 실행: python3 tools/figs-p2.py  (그림/ch02에 컬러·흑백 PDF)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from figlib import *

FS = 8.5


def box(ax, x, y, w, h, text, mode, fc=None, hatch=None, fs=FS, bold=False):
    s = STY[mode]
    fc = fc or ("#ffffff" if mode == "bw" else "#fdf3e0")
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.015", fc=fc, ec=s["line"], lw=0.8, hatch=hatch))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal", linespacing=1.25)


def arrow(ax, p, q, mode, ls="-", rad=0.0):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=STY[mode]["line"], lw=0.9, ls=ls,
                                                   connectionstyle=f"arc3,rad={rad}", shrinkA=1, shrinkB=1))


def fig_timeline(mode):
    s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 5.6))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.07)
    x0, x1 = 1420, 2040
    ax.set_xlim(x0, x1); ax.set_ylim(0, 13.2)
    ax.set_xlim(x0, x1)
    # 시기 띠
    bands = [(1420, 1600, "①"), (1600, 1830, "②"), (1830, 1945, "③"), (1945, 1990, "④"), (1990, 2000, "⑤"), (2000, 2040, "⑥")]
    shade = {"color": ["#f7efe0", "#e8f0f8"], "bw": ["#ececec", "#ffffff"]}[mode]
    for i, (a, b, t) in enumerate(bands):
        ax.add_patch(Rectangle((a, 0.6), b - a, 12.0, fc=shade[i % 2], ec="none", zorder=0, lw=0))
        ax.text((a + b) / 2, 12.85, t, ha="center", va="center", fontsize=9, fontweight="bold")
    ax.set_yticks([]); ax.set_xticks([1450, 1600, 1750, 1900, 2000])
    ax.tick_params(axis="x", labelsize=FS)
    for sp in ("left", "right", "top"):
        ax.spines[sp].set_visible(False)
    c = s["line"]
    # 생몰 막대: (행 y, 시작, 끝, 라벨, 라벨 위치)
    def life(y, a, b, label, side="r", dash=False):
        ax.plot([a, b], [y, y], color=c, lw=4, solid_capstyle="butt", ls=(":" if dash else "-"), zorder=3)
        if side == "r":
            ax.text(b + 6, y, label, va="center", ha="left", fontsize=FS)
        else:
            ax.text(a - 6, y, label, va="center", ha="right", fontsize=FS)
    def dot(y, x, label, side="r", dx=6):
        ax.plot(x, y, "o", color=c, mfc=(c if mode == "color" else "white"), ms=5, zorder=4)
        ax.text(x + (dx if side == "r" else -dx), y, label, va="center", ha=("left" if side == "r" else "right"), fontsize=FS)
    dot(11.6, 1450, "지리지(15세기 중엽~16세기 초)")
    life(10.4, 1552, 1615, "한백겸 동국지리지(1615경)")
    life(9.2, 1712, 1791, "안정복(동사강목 1759)", "l")
    life(8.2, 1712, 1781, "신경준(강계고)", "l")
    life(7.0, 1762, 1836, "정약용 아방강역고(1811)", "l")
    life(5.8, 1804, 1866, "김정호 대동여지도(1861)", "l", dash=True)
    life(4.6, 1880, 1936, "신채호", "l")
    dot(3.6, 1946, "정인보 1946", "l")
    dot(2.8, 1948, "이병도 1948·1976", "l")
    dot(2.0, 1963, "리지린 1963", "r")
    dot(1.6, 1994, "윤내현 1994", "l")
    dot(0.9, 2008, "지명사전 연구 2008", "l")
    ax.plot(1976, 2.8, "o", color=c, mfc=(c if mode == "color" else "white"), ms=5, zorder=4)
    # 영향 관계(확인된 것만)
    arrow(ax, (1452, 11.4), (1560, 10.6), mode)              # 지리지 -> 동국지리지(인용)
    arrow(ax, (1456, 11.4), (1795, 7.2), mode, rad=-0.1)     # 지리지 -> 아방강역고(비판)
    arrow(ax, (1830, 5.8), (1861, 5.8), mode, ls="--")        # 청구도/대동지지 -> 지도
    ax.text(1470, 5.0, "화살표: 앞 기록을\n인용하거나 비판함", fontsize=FS, va="center", ha="left", linespacing=1.3)
    ax.set_xlabel("연도(서력)", fontsize=FS)
    return save(fig, "ch02", "fig02-2-timeline", mode)


def fig_popper(mode):
    s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 2.7))
    fig.subplots_adjust(left=0.20, right=0.97, top=0.95, bottom=0.2)
    ax.set_xlim(0, 100); ax.set_ylim(0, 3)
    ax.set_yticks([2.2, 1.2, 0.4]); ax.set_yticklabels(["가설 A\n(좁게 예측)", "가설 B\n(넓게 예측)", "관측값"], fontsize=FS)
    ax.set_xlabel("가상의 관측 가능 범위: 어느 지점까지의 거리(리)", fontsize=FS)
    fa = "#e57373" if mode == "color" else "#aaaaaa"
    fb = "#64b5f6" if mode == "color" else "#dddddd"
    ax.add_patch(Rectangle((40, 2.0), 10, 0.4, fc=fa, ec=s["line"], lw=0.8, hatch="xx" if mode == "bw" else None))
    ax.add_patch(Rectangle((20, 1.0), 60, 0.4, fc=fb, ec=s["line"], lw=0.8, hatch="..", ))
    ax.text(51.5, 2.2, "허용 40~50", fontsize=FS, va="center")
    ax.text(50, 1.2, "허용 20~80", fontsize=FS, va="center", ha="center", bbox=dict(fc="white", ec="none", pad=1))
    ax.axvline(70, color=s["line"], ls="--", lw=0.9)
    ax.plot(70, 0.4, "D", color=s["truth"], ms=7, mec="black")
    ax.text(72, 0.4, "관측 70리", fontsize=FS, va="center")
    ax.annotate("A는 금지한 곳\n→ 반증", (70, 2.2), xytext=(80, 2.55), fontsize=FS, ha="left", va="center", arrowprops=dict(arrowstyle="-|>", color=s["line"], lw=0.8))
    ax.annotate("B는 허용한 곳\n→ 살아남음", (70, 1.2), xytext=(81, 1.75), fontsize=FS, ha="left", va="center", arrowprops=dict(arrowstyle="-|>", color=s["line"], lw=0.8))
    return save(fig, "ch02", "fig02-3-popper", mode)


def fig_bayes(mode):
    s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 2.7))
    fig.subplots_adjust(left=0.17, right=0.93, top=0.93, bottom=0.2)
    labels = ["처음", "증거 1\n(우도비 3)", "증거 2\n(우도비 0.5)", "증거 3\n(우도비 2)"]
    odds = [0.25]
    for lr in (3, 0.5, 2):
        odds.append(odds[-1] * lr)
    p = [o / (1 + o) for o in odds]
    xs = range(4)
    ax.plot(xs, p, "-o", color=s["accent"] if mode == "color" else "black", ms=6, lw=1.4)
    for x, v, o in zip(xs, p, odds):
        ax.text(x, v + 0.055, f"확률 {v:.2f}\n오즈 {o:.3g}", ha="center", fontsize=FS, va="bottom")
    ax.axhline(0.5, color=s["grid"], ls=":", lw=0.8)
    ax.text(-0.35, 0.51, "0.5", fontsize=FS, va="bottom", ha="left")
    ax.set_xticks(list(xs)); ax.set_xticklabels(labels, fontsize=FS)
    ax.set_ylim(0, 0.8); ax.set_xlim(-0.4, 3.6)
    ax.set_ylabel("가설 A가 맞을 확률(가상)", fontsize=FS)
    return save(fig, "ch02", "fig02-4-bayes", mode)


def fig_fork(mode):
    s = STY[mode]
    fig, ax = plt.subplots(figsize=(WIDTH, 4.3))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    box(ax, 0.28, 0.88, 0.44, 0.10, "같은 문헌 묶음\n(지리지, 사서, 중국 사서)", mode, fc="#e8e8e8" if mode == "bw" else "#e3eef9")
    prem = ["전제 1\n어느 지명을\n같은 곳으로 보나", "전제 2\n어느 기록을\n먼저 믿나", "전제 3\n땅에서 나온 물증을\n어떻게 읽나"]
    xs = [0.03, 0.36, 0.69]
    for x, t in zip(xs, prem):
        box(ax, x, 0.58, 0.28, 0.16, t, mode)
        arrow(ax, (0.5, 0.88), (x + 0.14, 0.74), mode)
    box(ax, 0.10, 0.44, 0.80, 0.08, "세 전제를 어떻게 고르느냐에 따라 조합이 달라진다", mode, fc="#ffffff")
    for x in xs:
        arrow(ax, (x + 0.14, 0.58), (x + 0.14, 0.52), mode)
    ans = [("조합 가\n(전제를 한쪽으로)", 0.03), ("조합 나\n(전제를 다른 쪽으로)", 0.36), ("조합 다\n(전제를 섞어서)", 0.69)]
    for t, x in ans:
        box(ax, x, 0.24, 0.28, 0.14, t, mode, fc="#ffffff")
        arrow(ax, (0.5, 0.44), (x + 0.14, 0.38), mode)
    box(ax, 0.03, 0.04, 0.94, 0.14, "갈림길은 자료가 아니라 전제에 있다.\n이 책은 전제마다 장부에 한 줄을 적어 둔다 (결론은 이 장에서 내지 않음).", mode, fc="#f2f2f2" if mode == "bw" else "#fdf3e0")
    arrow(ax, (0.5, 0.24), (0.5, 0.18), mode)
    return save(fig, "ch02", "fig02-5-fork", mode)


if __name__ == "__main__":
    for mode in ("color", "bw"):
        for f in (fig_timeline, fig_popper, fig_bayes, fig_fork):
            print(f(mode))
