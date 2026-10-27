"""figs-m10.py - 10장(시공간 지명 정합) 새 그림 6개. 실행: python3 tools/figs-m10.py  (그림/ch10 에 컬러·흑백 PDF)
숫자는 원고 본문의 가상 사례와 같은 계산(이름 규칙, 시기 겹침 비율, 가우시안 공간 점수)에서 가져온다."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
from figlib import *

FS = 8.5


def box(ax, x, y, w, h, text, mode, fc=None, ls="-", fs=FS, bold=False):
    s = STY[mode]
    fc = fc or ("#ffffff")
    p = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.01,rounding_size=0.02", fc=fc, ec="black", lw=0.8, ls=ls, zorder=3)
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, zorder=4, fontweight="bold" if bold else "normal")


def arrow(ax, p, q, ls="-", lw=0.9, color="black", style="-|>", rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=9, lw=lw, ls=ls, color=color, shrinkA=0, shrinkB=0,
                                 connectionstyle=f"arc3,rad={rad}", zorder=2))


# ---------------------------------------------------------------- 그림 1: 연대기
def fig_timeline(mode):
    s = STY[mode]
    fig, axs = plt.subplots(2, 1, figsize=(WIDTH, 6.4), constrained_layout=True, gridspec_kw={"height_ratios": [1.0, 2.0]})
    c1 = "#1f6fb8" if mode == "color" else "#000000"
    c2 = "#c0392b" if mode == "color" else "#444444"
    c3 = "#2e7d32" if mode == "color" else "#777777"
    # (a) 서경과 이름의 시간표
    ax = axs[0]
    ax.set_xlim(880, 1600); ax.set_ylim(-2.0, 2.3); ax.set_yticks([])
    for sp in ("left", "right", "top"): ax.spines[sp].set_visible(False)
    ax.axhline(0, color="black", lw=1.0)
    ev = [(922, "922 분사 설치", 0.55, "c", "n"), (998, "998 호경", -0.55, "c", "n"), (1062, "1062 서경\n유수관", 1.35, "r", "n"),
          (1081, "1081 문종\n35년 기사", -1.35, "c", "e"), (1116, "1116 개경과\n같은 체제", 0.55, "l", "n"), (1530, "1530 신증동국\n여지승람", 0.55, "c", "g")]
    for x, t, ty, h, kind in ev:
        col = {"n": c1, "e": c2, "g": c3}[kind]
        mk = {"n": "o", "e": "*", "g": "s"}[kind]
        ha = {"c": "center", "r": "right", "l": "left"}[h]
        tx = x + {"c": 0, "r": 6, "l": -6}[h]
        ax.plot([x, x], [0, ty * (0.95 if abs(ty) > 1 else 0.6)], color="black", lw=0.6)
        ax.plot(x, 0, mk, color=col, mec="black", ms=9 if kind == "e" else 6.5, zorder=5, mfc=col if mode == "color" else ("white" if kind != "e" else "black"))
        ax.text(tx, ty, t, ha=ha, va="bottom" if ty > 0 else "top", fontsize=FS, linespacing=1.05)
    ax.set_xticks([900, 1000, 1100, 1200, 1300, 1400, 1500]); ax.tick_params(axis="x", labelsize=FS)
    ax.set_xlabel("서력 (년)")
    ax.set_title("(a) 서경이라는 이름의 시간표(원), 문종 기사(별), 지리지(네모)", loc="left", fontsize=9)
    # (b) 방법과 학문의 연대
    ax = axs[1]
    ax.set_xlim(1938, 2042); ax.set_ylim(-1.0, 6.3)
    lanes = {0: "디지털\n지명 사전", 1: "지도\n지명 사전", 2: "공간", 3: "문자열", 4: "짝짓기", 5: "기록 연결"}
    ax.set_yticks(list(lanes)); ax.set_yticklabels([lanes[k] for k in lanes], fontsize=FS)
    ax.grid(axis="x", color=s["grid"], lw=0.3, ls=":")
    for sp in ("right", "top"): ax.spines[sp].set_visible(False)
    def pt(x, y, txt, ty=0.28, ha="center", mk="o", col=c1, dx=0.0):
        ax.plot(x, y, mk, color=col, mec="black", ms=6, zorder=5, mfc=col if mode == "color" else "white")
        if txt:
            ax.text(x + dx, y + ty, txt, ha=ha, va="bottom" if ty > 0 else "top", fontsize=FS, linespacing=1.05)
    pt(1946, 5, "1946\nDunn", ha="center", ty=0.28)
    pt(1959, 5, "1959\n뉴컴 등", ty=0.28, ha="center")
    pt(1969, 5, "1969 펠레기\n· 선터", ty=0.28, ha="left", dx=-2.5)
    arrow(ax, (1960.3, 5.0), (1967.7, 5.0), lw=1.0)
    pt(1955, 4, "1955 쿤", ty=0.28, ha="right", dx=1.5)
    pt(1957, 4, "1957 먼크리스", ty=-0.28, ha="left", dx=-1.5)
    arrow(ax, (1955.6, 4.0), (1956.5, 4.0), lw=1.0)
    pt(1965, 3, "1965 레벤시타인", ty=0.0, ha="left", dx=2)
    pt(1970, 2, "1970 토블러", ty=0.0, ha="left", dx=2.5, mk="D", col=c2)
    ax.plot([1982, 1988], [1, 1], "-", color=c3, lw=6, solid_capstyle="butt", zorder=4)
    ax.text(1991, 1, "1982~88 중국역사지도집", ha="left", va="center", fontsize=FS)
    pt(2006, 0, "2006\n힐", ty=0.28, ha="center")
    pt(2008, 0, "2008 모스턴\n· 존슨", ty=-0.28, ha="right", dx=1.5)
    pt(2016, 0, "2016\n베르만 등", ty=-0.28, ha="left", dx=-3)
    ax.plot([2019, 2038], [0, 0], "-", color=c2, lw=6, solid_capstyle="butt", zorder=4)
    ax.text(2028.5, 0.28, "2019~ WHG", ha="center", va="bottom", fontsize=FS)
    ax.plot(2038, 5.0, "*", color=c2 if mode == "color" else "black", ms=12, mec="black")
    ax.text(2038, 5.35, "이 책", ha="center", va="bottom", fontsize=FS)
    ax.set_xticks(range(1940, 2041, 10)); ax.tick_params(labelsize=FS)
    ax.set_xlabel("서력 (년)")
    ax.set_title("(b) 이 장의 방법이 자란 연대(화살표는 확인된 계승 관계)", loc="left", fontsize=9)
    return save(fig, "ch10", "fig10-2-timeline", mode)


# ---------------------------------------------------------------- 그림 2: 이름과 장소의 세 관계
def fig_relations(mode):
    fig, axs = plt.subplots(3, 1, figsize=(WIDTH, 5.6), constrained_layout=True)
    g = "#e8e8e8"
    fcs = ("#ffffff", "#fbe3b3", "#cfe3f1") if mode == "color" else ("#ffffff", "#e6e6e6", "#cccccc")
    for ax in axs:
        ax.set_xlim(0, 10); ax.set_ylim(0, 3); ax.axis("off")
    ax = axs[0]
    ax.set_title("(a) 같은 이름, 다른 곳(동명이지)", loc="left", fontsize=9)
    box(ax, 1.2, 1.5, 1.7, 0.8, "西京", mode, fc=fcs[1], bold=True)
    for y, t in [(2.45, "고려의 평양\n(1062~1116년 포함)"), (1.5, "대동: 거란과 금의 서경\n(연대 원문 대조 필요)"), (0.55, "서안: 한·수·당의 서경\n(연대 원문 대조 필요)")]:
        box(ax, 7.0, y, 4.6, 0.8, t, mode, fc=fcs[2])
        arrow(ax, (2.05, 1.5), (4.65, y))
    ax = axs[1]
    ax.set_title("(b) 다른 이름, 같은 곳일 수 있음(이명동지)", loc="left", fontsize=9)
    for y, t in [(2.45, "大城山 대성산"), (1.5, "九龍山 구룡산"), (0.55, "魯陽山 노양산")]:
        box(ax, 1.9, y, 2.8, 0.8, t, mode, fc=fcs[1])
        arrow(ax, (3.35, y), (6.2, 1.5), ls="--")
    box(ax, 7.9, 1.5, 3.2, 1.0, "한 산?\n(단정하지 않음)", mode, fc=fcs[2], ls="--")
    ax = axs[2]
    ax.set_title("(c) 같은 이름, 시기마다 다른 곳(시간 조각내기, 가상)", loc="left", fontsize=9)
    xs = [0.6, 4.2, 6.7, 9.6]; labs = ["1000", "1180", "1260", "1400"]
    for (a, b), lab, f, pt in zip(zip(xs[:-1], xs[1:]), ["기록 X", "기록 Y", "기록 Z"], fcs[1:] * 2, ["갑 지점", "을 지점", "병 지점"]):
        ax.add_patch(plt.Rectangle((a, 1.5), b - a, 0.7, fc=f, ec="black", lw=0.8, hatch="//" if (mode == "bw" and lab == "기록 Y") else None))
        ax.text((a + b) / 2, 1.85, lab, ha="center", va="center", fontsize=FS)
        ax.text((a + b) / 2, 0.85, pt, ha="center", va="center", fontsize=FS)
        ax.plot([(a + b) / 2] * 2, [1.5, 1.1], color="black", lw=0.6)
    for x, l in zip(xs, labs):
        ax.text(x, 2.5, l, ha="center", va="bottom", fontsize=FS)
        ax.plot([x, x], [2.2, 2.4], color="black", lw=0.6)
    ax.text(5.0, 0.2, "1100년의 언급은 기록 X하고만 시기가 겹친다", ha="center", va="center", fontsize=FS)
    return save(fig, "ch10", "fig10-3-relations", mode)


# ---------------------------------------------------------------- 그림 3: 공간 점수
def fig_space(mode):
    s = STY[mode]
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 3.2), constrained_layout=True, gridspec_kw={"width_ratios": [1.0, 1.15]})
    ax = axs[0]
    d = np.linspace(0, 16, 300)
    sty = [("#1f6fb8", "-", 2.3), ("#c0392b", "--", 4.0), ("#2e7d32", ":", 8.0)] if mode == "color" else [("#000000", "-", 2.3), ("#444444", "--", 4.0), ("#777777", ":", 8.0)]
    for col, ls, sg in sty:
        ax.plot(d, np.exp(-0.5 * (d / sg) ** 2), color=col, ls=ls, lw=1.6, label=f"폭 {sg:g} km")
    ax.axhline(0.5, color=s["grid"], lw=0.6)
    ax.set_xlabel("거리 d (km)"); ax.set_ylabel("공간 점수"); ax.set_ylim(0, 1.05); ax.set_xlim(0, 16)
    ax.legend(frameon=False, loc="upper right", fontsize=FS)
    ax.set_title("(a) 폭이 클수록 느리게 준다", loc="left", fontsize=9)
    ax = axs[1]
    # (b) C1 사례 지도: 군(원점), 서쪽 이삼십 리, 세 기록
    cols = ["#1f6fb8", "#c0392b", "#2e7d32"] if mode == "color" else ["#000000", "#000000", "#000000"]
    for (mid, sg), ls in zip([(10.8, 2.08), (11.1, 3.29), (11.4, 4.5)], ["-", "--", ":"]):
        ax.add_patch(Circle((-mid, 0), sg, fill=False, ec="#444444" if mode == "bw" else "#555555", ls=ls, lw=1.1))
    ax.plot(0, 0, "^", color="black", ms=7, mfc="white")
    ax.text(0.4, 1.0, "군", fontsize=FS)
    ax.plot(-10.8, 0, "x", color="black", ms=6)
    recs = [("r1", -11.2, 1.5, "o"), ("r2", -4.0, 0.5, "s"), ("r3", -24.0, -3.0, "D")]
    for nm, x, y, mk in recs:
        ax.plot(x, y, mk, color="#222222" if mode == "bw" else "#c0392b", mfc="white" if mode == "bw" else "#c0392b", mec="black", ms=6, zorder=5)
        ax.text(x + 0.6, y + 1.1 if nm != "r1" else y + 1.9, nm, fontsize=FS)
    ax.set_xlim(-27, 3); ax.set_ylim(-8, 8); ax.set_aspect("equal")
    ax.set_xlabel("동 (km)"); ax.set_ylabel("북 (km)")
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    ax.set_title("(b) '서쪽 이삼십 리'의 세 읽기", loc="left", fontsize=9)
    return save(fig, "ch10", "fig10-4-spacescore", mode)


# ---------------------------------------------------------------- 그림 4: 욕심쟁이와 최적 배정
def fig_assign(mode):
    S = np.array([[.891, .050, .637, .351], [.403, .050, .998, .715], [.925, .675, .550, .800]])
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 3.0), constrained_layout=True)
    L = ["m1 서도", "m2 북진", "m3 동관"]; R = ["r1", "r2", "r3", "r4"]
    ly = [2.4, 1.4, 0.4]; ry = [2.7, 1.9, 0.9, 0.1]
    panels = [("(a) 욕심쟁이: 합 2.274", [(1, 2), (2, 0), (0, 3)], "--"), ("(b) 최적: 합 2.689", [(0, 0), (1, 2), (2, 3)], "-")]
    for ax, (ttl, prs, ls) in zip(axs, panels):
        ax.set_xlim(0, 4.6); ax.set_ylim(-0.4, 3.2); ax.axis("off")
        ax.set_title(ttl, loc="left", fontsize=9)
        for i, t in enumerate(L):
            ax.text(0.05, ly[i], t, ha="left", va="center", fontsize=FS)
        for j, t in enumerate(R):
            ax.text(4.5, ry[j], t, ha="right", va="center", fontsize=FS)
        for i, j in prs:
            col = ("#c0392b" if ls == "--" else "#1f6fb8") if mode == "color" else "black"
            ax.plot([1.2, 3.7], [ly[i], ry[j]], color=col, ls=ls, lw=2.0 if ls == "-" else 1.5)
            tt = 0.82 if ls == "--" else 0.22
            ax.text(1.2 + (3.7 - 1.2) * tt + (-0.1 if ls == "--" else 0.35), ly[i] + (ry[j] - ly[i]) * tt + 0.12, f"{S[i, j]:.3f}", ha="center", va="bottom", fontsize=FS,
                    bbox=dict(fc="white", ec="none", pad=0.4))
        ax.text(2.3, -0.3, "합 = 세 점수의 합", ha="center", fontsize=FS) if False else None
    return save(fig, "ch10", "fig10-5-assign", mode)


# ---------------------------------------------------------------- 그림 5: 가중치 삼각형
def fig_weights(mode):
    c1 = (1.0, .55, .85); c2 = (.8, 1.0, .95)
    fig, ax = plt.subplots(figsize=(WIDTH * 0.85, 3.7), constrained_layout=True)
    N = 80
    X, Y, D = [], [], []
    for i in range(N + 1):
        for j in range(N + 1 - i):
            wn, wt = i / N, j / N; ws = 1 - wn - wt
            s1 = wn * c1[0] + wt * c1[1] + ws * c1[2]; s2 = wn * c2[0] + wt * c2[1] + ws * c2[2]
            X.append(wt + ws * 0.5); Y.append(ws * math.sqrt(3) / 2); D.append(s1 - s2)
    cols = ("#f0b45a", "#7fb3d5") if mode == "color" else ("#9a9a9a", "#f2f2f2")
    ax.tricontourf(X, Y, D, levels=[-9, 0, 9], colors=[cols[1], cols[0]])
    if mode == "bw":
        ax.tricontourf(X, Y, D, levels=[0, 9], colors="none", hatches=["////"])
    ax.tricontour(X, Y, D, levels=[0], colors="black", linewidths=1.0, linestyles="--")
    ax.plot([0, 1, 0.5, 0], [0, 0, math.sqrt(3) / 2, 0], color="black", lw=0.8)
    for lab, (wn, wt, ws), mk in [("기준 (0.5, 0.3, 0.2)", (.5, .3, .2), "*"), ("똑같이 (1/3, 1/3, 1/3)", (1 / 3, 1 / 3, 1 / 3), "P")]:
        x = wt + ws * 0.5; y = ws * math.sqrt(3) / 2
        ax.plot(x, y, mk, ms=12 if mk == "*" else 8, color="#c0392b" if mode == "color" else "black", mec="black", mfc="white" if mk == "P" else None, zorder=6)
        ax.annotate(lab, (x, y), xytext=(8, 4) if mk == "*" else (8, 6), textcoords="offset points", fontsize=FS, bbox=dict(fc="white", ec="none", pad=0.8, alpha=0.85))
    ax.text(-0.02, -0.04, "이름 가중 1", ha="left", va="top", fontsize=FS)
    ax.text(1.02, -0.04, "시기 가중 1", ha="right", va="top", fontsize=FS)
    ax.text(0.5, math.sqrt(3) / 2 + 0.03, "공간 가중 1", ha="center", va="bottom", fontsize=FS)
    ax.text(0.2, 0.10, "후보 1이 이김", fontsize=FS, ha="center", bbox=dict(fc="white", ec="none", pad=0.8, alpha=0.85))
    ax.text(0.72, 0.10, "후보 2가 이김", fontsize=FS, ha="center", bbox=dict(fc="white", ec="none", pad=0.8, alpha=0.85))
    ax.set_xlim(-0.08, 1.08); ax.set_ylim(-0.12, 0.98); ax.set_aspect("equal"); ax.axis("off")
    return save(fig, "ch10", "fig10-6-weights", mode)


# ---------------------------------------------------------------- 그림 6: 점수의 구간과 이름 문턱
def fig_interval(mode):
    s = STY[mode]
    fig, axs = plt.subplots(1, 2, figsize=(WIDTH, 3.0), constrained_layout=True, gridspec_kw={"width_ratios": [1.0, 1.0]})
    ax = axs[0]
    labs = ["고려 서경", "대동 서경", "서안 서경"]
    lo = [1.0, 0.70, 0.70]; hi = [1.0, 1.0, 1.0]
    for i, (a, b) in enumerate(zip(lo, hi)):
        y = 2 - i
        if b > a:
            ax.barh(y, b - a, left=a, height=0.45, color="#bdbdbd" if mode == "bw" else "#f0b45a", ec="black", lw=0.8, hatch="//" if mode == "bw" else None)
        ax.plot([a, b], [y, y], "|", color="black", ms=14, mew=1.3)
        if b == a: ax.plot(a, y, "o", color="black", ms=6)
    ax.axvline(0.45, color="black", lw=0.8, ls="--")
    ax.text(0.43, 2.62, "기준 0.45", fontsize=FS, va="bottom", ha="left")
    ax.set_yticks([2, 1, 0]); ax.set_yticklabels(labs)
    ax.set_xlim(0.4, 1.05); ax.set_ylim(-0.6, 3.0); ax.set_xlabel("합산 점수 s")
    ax.text(0.47, 0.5, "시기를 모르면\n0.70~1.00", fontsize=FS, ha="left", va="center")
    ax.set_title("(a) 시기를 모르는 기록", loc="left", fontsize=9)
    ax = axs[1]
    names = ["東林寺院", "西林寺", "東山", "北寺", "南江驛"]
    nsc = [.375, .25, .125, .125, 0.0]
    ssum = [.688, .625, .562, .562, .5]
    x = np.arange(len(names))
    ax.bar(x, ssum, width=0.6, color="#bdbdbd" if mode == "bw" else "#7fb3d5", ec="black", lw=0.8)
    ax.axhline(0.45, color="black", lw=0.8, ls="--")
    ax.text(-0.45, 0.37, "기준 0.45", fontsize=FS, ha="left", va="top")
    for xi, v in zip(x, ssum):
        ax.text(xi, v + 0.015, f"{v:.2f}", ha="center", fontsize=FS)
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=40, ha="right")
    ax.set_ylim(0, 0.85); ax.set_ylabel("합산 점수 s")
    ax.set_title("(b) 이름이 달라도 통과(가상)", loc="left", fontsize=9)
    return save(fig, "ch10", "fig10-7-interval", mode)


if __name__ == "__main__":
    for mode in ("color", "bw"):
        for f in (fig_timeline, fig_relations, fig_space, fig_assign, fig_weights, fig_interval):
            print(f(mode))
