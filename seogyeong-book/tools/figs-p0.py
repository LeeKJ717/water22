"""figs-p0.py - 준비편 머리말·서장·맺음말 그림: 네 권의 구성, 준비편 장 사이의 연결"""
import sys
from figlib import *
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


def box(ax, x, y, w, h, txt, mode, hi=False, fs=8.5, dash=False):
    s = STY[mode]
    fc = s["fill"] if hi else ("white")
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.05", fc=fc, ec=s["line"], lw=1.1 if hi else 0.8, ls="--" if dash else "-")
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs, linespacing=1.35)


def arrow(ax, x0, y0, x1, y1, mode):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=9, lw=0.9, color=STY[mode]["line"], shrinkA=0, shrinkB=0))


def series(mode):
    fig, ax = plt.subplots(figsize=(WIDTH, 2.3), constrained_layout=True)
    ax.set_xlim(0, 10); ax.set_ylim(0, 4.6); ax.axis("off")
    names = [("1권  준비편", "사료 · 학설사\n사료 비판 · 증거 DB", True),
             ("2권  방법편", "기법 1~4\n제약 · 지도 · 베이즈\n최소비용경로", False),
             ("3권  실행편", "도구 · 자료 · GPU\n기법 5~8", False),
             ("4권  통합·적용편", "여덟 방법 비교\n서경 통합 추정\n네 지역 적용", False)]
    for i, (t, d, hi) in enumerate(names):
        x = 0.1 + i * 2.5
        box(ax, x, 1.3, 2.1, 2.5, "", mode, hi=hi)
        ax.text(x + 1.05, 3.35, t, ha="center", va="center", fontsize=9, fontweight="bold")
        ax.text(x + 1.05, 2.25, d, ha="center", va="center", fontsize=8.5, linespacing=1.4)
        if i < 3:
            arrow(ax, x + 2.12, 2.55, x + 2.48, 2.55, mode)
    ax.text(0.1 + 1.05, 0.85, "이 책", ha="center", va="center", fontsize=8.5, fontweight="bold")
    ax.annotate("", xy=(0.1, 1.05), xytext=(2.2, 1.05), arrowprops=dict(arrowstyle="-", lw=1.4, color=STY[mode]["line"]))
    ax.text(5.0, 0.3, "여덟 가지 방법은 2권(넷)과 3권(넷)에 나뉘어 있고, 4권이 모두 합친다", ha="center", fontsize=8.5)
    save(fig, "ch00", "fig0p-series", mode)


def flow(mode):
    fig, ax = plt.subplots(figsize=(WIDTH, 3.1), constrained_layout=True)
    ax.set_xlim(0, 10); ax.set_ylim(-0.5, 6.4); ax.axis("off")
    rows = [("1장  사료", "무엇을 재료로\n삼는가"), ("2장  학설사", "누가 어떤 근거로\n말해 왔는가"),
            ("3장  사료 비판", "그 재료는 얼마나\n믿을 수 있는가"), ("4장  증거 DB", "믿을 수 있는 만큼\n어떻게 적어 두는가")]
    for i, (t, d) in enumerate(rows):
        y = 4.6 - i * 1.45
        box(ax, 0.2, y, 2.6, 1.1, t, mode, hi=True, fs=9)
        ax.text(3.1, y + 0.55, d, va="center", fontsize=8.5, linespacing=1.35)
        if i < 3:
            arrow(ax, 1.5, y - 0.02, 1.5, y - 0.33, mode)
    ax.text(5.3, 5.95, "각 장이 다음 장에 넘겨 주는 것", fontsize=9, fontweight="bold", va="center")
    hands = ["사료 목록과\n층위(1·2·3층)", "가설 장부와\n학설의 전제", "단위·방향·오류의\n구간과 부채꼴", "증거표 한 줄,\n계산 이력"]
    for i, h in enumerate(hands):
        y = 4.6 - i * 1.45
        box(ax, 6.5, y, 3.3, 1.1, h, mode, fs=8.5)
        arrow(ax, 6.0, y + 0.55, 6.45, y + 0.55, mode)
    ax.text(5.3, -0.2, "네 장을 거친 증거표가 2권 방법편의 입력이 된다", ha="center", fontsize=8.5)
    save(fig, "ch00", "fig0p-flow", mode)


if __name__ == "__main__":
    for m in ("color", "bw"):
        series(m); flow(m)
