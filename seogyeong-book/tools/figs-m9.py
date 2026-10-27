"""figs-m9.py - 9장(기법 5. 그래프 이론) 새 그림. 사용: python3 tools/figs-m9.py
출력: 그림/ch09/fig09-3-timeline, fig09-4-mirror, fig09-5-interval, fig09-6-sagyeong,
      fig09-7-pynet, fig09-8-wae, fig09-9-citation (color, bw)
숫자 출처: 각 함수 안의 계산(python). 서경의 결과가 아니라 방법을 보이는 그림이다."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import networkx as nx
from figlib import *
from matplotlib.patches import FancyArrowPatch, Rectangle

FS = 8.5


def arrow(ax, a, b, c="#222", ls="-", lw=1.0, rad=0.0, ms=9):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=ms, lw=lw, color=c, ls=ls,
                                 shrinkA=0, shrinkB=0, connectionstyle=f"arc3,rad={rad}"))


# ---------------------------------------------------------------- 3. 연대기 종합 그림
# 확인 경로: 참고문헌/ch09.txt (Euler 1736, Quenouille 1949/1956, Tukey 1958, Torgerson 1952,
# Kruskal 1964, Kruskal&Wish 1978, Freeman 1977, Page 등 1996~1999, Brandes 2001, Newman 2010, Brughmans 2013, 2023)
def tmap(y):
    """연도를 가로 위치로: 1736은 왼쪽 끝, 1945년 이후는 선형(가운데에 끊김 표시)"""
    if y < 1800:
        return 0.0
    return 0.9 + (y - 1945) / (2030 - 1945) * 4.2


def fig_timeline(mode):
    c = STY[mode]
    fig, ax = new(mode, 4.7)
    lanes = [("점과 선", "-"), ("거리에서\n배치", "--"), ("중요한 점", "-."), ("하나 빼기", ":"), ("고고학", "-"), ("이 책", "-")]
    ys = {i: 5.35 - i * 0.95 for i in range(6)}
    # (연도, 줄, 위/아래, 글, 가로 보정)
    ev = [
        (1736, 0, +1, "1736 오일러", 0.0),
        (2010, 0, +1, "2010 뉴먼\n교과서", 0.0),
        (1952, 1, +1, "1952\n토거슨", 0.0),
        (1964, 1, -1, "1964\n크러스컬", 0.0),
        (1978, 1, +1, "1978 크러스컬\n·위시 책", 0.35),
        (1977, 2, -1, "1977 프리먼", -0.2),
        (1998, 2, +1, "1998 페이지\n랭크", -0.2),
        (2001, 2, -1, "2001\n브랜데스", 0.25),
        (1949, 3, +1, "1949\n퀴누이", -0.1),
        (1956, 3, -1, "1956\n퀴누이", 0.0),
        (1958, 3, +1, "1958 튜키\n이름", 0.45),
        (2013, 4, +1, "2013 브루그만스\n·냅핏", -0.2),
        (2023, 4, -1, "2023 브루그만스\n·피플스", -0.15),
        (2026, 5, 0, "앵커 MDS + 구간 방식 + 증거 그물", 0.0),
    ]
    ax.set_xlim(-0.35, 5.35); ax.set_ylim(-0.1, 6.45)
    for i, (nm, ls) in enumerate(lanes):
        y = ys[i]
        ax.hlines(y, 0.75 if i else -0.15, 5.1, color=c["ref"], lw=0.9, ls=ls)
        ax.text(-0.3, y + 0.28, nm, fontsize=FS, fontweight="bold", va="bottom", ha="left", linespacing=1.1)
    for yr, ln, side, t, dx in ev:
        x = tmap(yr); y = ys[ln]
        mk = "o" if ln in (0, 4) else ("s" if ln in (1, 3) else ("^" if ln == 2 else "*"))
        ax.plot(x, y, mk, ms=6.5, mfc=c["fill"] if mode == "color" else "white", mec=c["ref"], mew=1.0, zorder=5)
        if side == 0:
            ax.annotate(t, (x, y), xytext=(x + 0.1, y + 0.14), textcoords="data", ha="right", va="bottom", fontsize=FS)
            continue
        ax.annotate(t, (x, y), xytext=(x + dx, y + 0.12 * side), textcoords="data", ha="center",
                    va="bottom" if side > 0 else "top", fontsize=FS, linespacing=1.1,
                    arrowprops=dict(arrowstyle="-", lw=0.5, color=c["gray"], shrinkA=0, shrinkB=2) if abs(dx) > 0.2 else None)
    # 끊김 표시
    ax.text(0.5, 0.12, "//", fontsize=FS + 1, ha="center", va="center", fontweight="bold")
    ax.text(0.5, -0.02, "끊김", fontsize=FS, ha="center", va="top", color=c["gray"])
    for yr in range(1950, 2031, 20):
        ax.vlines(tmap(yr), 0.2, 6.0, color=c["grid"], lw=0.3, ls=":", zorder=0)
        ax.text(tmap(yr), 0.12, str(yr), ha="center", va="center", fontsize=FS)
    ax.axis("off")
    return save(fig, "ch09", "fig09-3-timeline", mode)


# ---------------------------------------------------------------- 4. 거울상: 앵커가 둘이면 해가 둘
def stress_grid(anchors, dists, X, Y):
    S = np.zeros_like(X)
    for (ax_, ay_), d in zip(anchors, dists):
        S += (np.hypot(X - ax_, Y - ay_) - d) ** 2
    return S


def fig_mirror(mode):
    c = STY[mode]
    fig, axs = new(mode, 2.7, ncols=2)
    X, Y = np.meshgrid(np.linspace(-2, 14, 321), np.linspace(-8, 11, 381))
    A, B, C = (0, 0), (10, 0), (5, 9)
    z = (5.55, 2.28)   # 두 원이 만나는 점의 근삿값(본문의 풀이)
    dA, dB = 6.0, 5.0
    # 정확한 교점
    xz = (dA ** 2 - dB ** 2 + 100) / 20.0
    yz = math.sqrt(dA ** 2 - xz ** 2)
    dC = math.hypot(5 - xz, 9 - yz)
    lev = [0.5, 2, 5, 10, 20, 40]
    for k, ax in enumerate(axs):
        anchors = [A, B] if k == 0 else [A, B, C]
        dists = [dA, dB] if k == 0 else [dA, dB, dC]
        S = stress_grid(anchors, dists, X, Y)
        cs = ax.contourf(X, Y, S, levels=[0] + lev + [1000], cmap=c["cmap"], alpha=0.85)
        ax.contour(X, Y, S, levels=lev, colors="black", linewidths=0.35)
        for a in anchors:
            ax.plot(*a, "^", color="black", ms=6, mfc="black" if mode == "color" else "white", mew=0.8, zorder=5)
        for nm, a in zip("ABC", anchors):
            ax.annotate(nm, a, xytext=(4, 3), textcoords="offset points", fontsize=FS)
        ax.plot(xz, yz, "*", ms=10, color=c["truth"], mec="black", mew=0.5, zorder=6)
        if k == 0:
            ax.plot(xz, -yz, "*", ms=10, color=c["truth"], mec="black", mew=0.5, zorder=6)
            ax.annotate("해 1", (xz, yz), xytext=(6, 4), textcoords="offset points", fontsize=FS)
            ax.annotate("거울상 해 2", (xz, -yz), xytext=(6, -10), textcoords="offset points", fontsize=FS)
            ax.set_title("(a) 앵커 둘: 스트레스 0인 곳이 둘", loc="left", fontsize=9)
        else:
            ax.annotate("해", (xz, yz), xytext=(6, -2), textcoords="offset points", fontsize=FS)
            ax.set_title("(b) 앵커 셋: 한 곳", loc="left", fontsize=9)
        ax.set_xlim(-2, 14); ax.set_ylim(-8, 11); ax.set_aspect("equal")
        ax.set_xlabel("가로 (km)")
        if k == 0:
            ax.set_ylabel("세로 (km)")
        ax.set_xticks(range(0, 13, 4)); ax.set_yticks(range(-8, 12, 4))
    return save(fig, "ch09", "fig09-4-mirror", mode)


# ---------------------------------------------------------------- 5. 중앙값 방식과 구간 방식
def interval_zero_set():
    A = {"A": ((0, 0), (62, 76)), "B": ((100, 0), (44, 54)), "C": ((50, 80), (46, 56)), "D": ((100, 80), (58, 72))}
    xs = np.arange(40, 91, 1.0); ys = np.arange(10, 61, 1.0)
    pts = []
    for x in xs:
        for y in ys:
            ok = True
            for (p, (lo, hi)) in A.values():
                r = math.hypot(x - p[0], y - p[1])
                if r < lo - 1e-9 or r > hi + 1e-9:
                    ok = False; break
            if ok:
                pts.append((x, y))
    return A, np.array(pts)


def fig_interval(mode):
    c = STY[mode]
    A, pts = interval_zero_set()
    fig, axs = new(mode, 2.9, ncols=2)
    th = np.linspace(0, 2 * np.pi, 400)
    for k, ax in enumerate(axs):
        for nm, (p, (lo, hi)) in A.items():
            if k == 0:
                r = (lo + hi) / 2
                ax.plot(p[0] + r * np.cos(th), p[1] + r * np.sin(th), color=c["ref"], lw=0.8, ls={"A": "-", "B": "--", "C": "-.", "D": ":"}[nm])
            else:
                for r in (lo, hi):
                    ax.plot(p[0] + r * np.cos(th), p[1] + r * np.sin(th), color=c["gray"], lw=0.5,
                            ls={"A": "-", "B": "--", "C": "-.", "D": ":"}[nm])
            ax.plot(*p, "^", color="black", ms=5, mfc="black" if mode == "color" else "white", zorder=5)
        ax.set_xlim(40, 90); ax.set_ylim(10, 60); ax.set_aspect("equal")
        ax.set_xticks(range(40, 91, 10)); ax.set_yticks(range(10, 61, 10)); ax.set_xlabel("동 (km)")
        ax.plot(62, 31, "*", ms=10, color=c["truth"], mec="black", mew=0.5, zorder=7)
        if k == 0:
            ax.set_ylabel("북 (km)")
            ax.set_title("(a) 중앙값 방식: 원 네 개", loc="left", fontsize=9)
            ax.plot(61.7, 29.1, "D", ms=6, mfc="white", mec="black", zorder=7)
            ax.annotate("점 추정", (61.7, 29.1), xytext=(-6, -16), textcoords="offset points", fontsize=FS)
        else:
            ax.set_title(f"(b) 구간 방식: 영역 {len(pts)}칸", loc="left", fontsize=9)
            ax.scatter(pts[:, 0], pts[:, 1], s=7, marker="s", color=c["fill"] if mode == "color" else "#777777", zorder=3, linewidths=0)
    return save(fig, "ch09", "fig09-5-interval", mode), len(pts), pts


# ---------------------------------------------------------------- 6. 사경: 네 이웃까지의 거리와 삼각부등식
def fig_sagyeong(mode):
    c = STY[mode]
    fig, axs = new(mode, 2.9, ncols=2, gridspec_kw=dict(width_ratios=[1, 1.15]))
    a = {"동": (31, 0), "서": (-42, 0), "남": (0, -25), "북": (0, 31)}
    ax = axs[0]
    ax.plot(0, 0, "o", ms=7, mfc="black" if mode == "color" else "white", mec="black", zorder=5)
    ax.annotate("평양부", (0, 0), xytext=(4, 4), textcoords="offset points", fontsize=FS)
    for nm, (x, y) in a.items():
        ax.plot([0, x], [0, y], color=c["ref"], lw=1.0)
        ax.plot(x, y, "s", ms=6, mfc=c["fill"] if mode == "color" else "#999999", mec="black", zorder=5)
    ax.annotate("동 31", a["동"], xytext=(2, 6), textcoords="offset points", fontsize=FS)
    ax.annotate("서 42", a["서"], xytext=(-2, 6), textcoords="offset points", fontsize=FS, ha="left")
    ax.annotate("남 25", a["남"], xytext=(5, -4), textcoords="offset points", fontsize=FS)
    ax.annotate("북 31", a["북"], xytext=(5, -2), textcoords="offset points", fontsize=FS)
    ax.plot([a["동"][0], a["북"][0]], [a["동"][1], a["북"][1]], color=c["gray"], lw=0.8, ls="--")
    ax.annotate("43.8", (15.5, 15.5), xytext=(5, 2), textcoords="offset points", fontsize=FS)
    ax.set_xlim(-52, 44); ax.set_ylim(-34, 40); ax.set_aspect("equal")
    ax.set_xlabel("동 (리)"); ax.set_ylabel("북 (리)")
    ax.set_xticks(range(-40, 41, 20)); ax.set_yticks(range(-20, 41, 20))
    ax.set_title("(a) 별 모양 그물(방위는 가정)", loc="left", fontsize=9)
    ax.grid(color=c["grid"], lw=0.3, ls=":")
    # (b) 쌍별 가능한 거리 범위
    ax = axs[1]
    names = list(a); import itertools
    pairs = list(itertools.combinations(names, 2))
    dist = {"동": 31, "서": 42, "남": 25, "북": 31}
    for i, (p, q) in enumerate(pairs[::-1]):
        lo, hi = abs(dist[p] - dist[q]), dist[p] + dist[q]
        ax.hlines(i, lo, hi, color="black", lw=5, alpha=0.35 if mode == "color" else 0.5)
        ax.plot([lo, hi], [i, i], "|", color="black", ms=8)
        r = math.hypot(dist[p], dist[q])
        opp = {("동", "서"), ("남", "북")}
        v = hi if (p, q) in opp else r
        ax.plot(v, i, "D", ms=6, mfc=c["truth"] if mode == "color" else "white", mec="black", zorder=5)
    ax.set_yticks(range(len(pairs))); ax.set_yticklabels([f"{p}-{q}" for p, q in pairs[::-1]])
    ax.set_xlim(0, 78); ax.set_xlabel("두 이웃 사이 거리 (리)")
    ax.set_title("(b) 삼각부등식이 허락하는 범위", loc="left", fontsize=9)
    ax.grid(axis="x", color=c["grid"], lw=0.3, ls=":")
    return save(fig, "ch09", "fig09-6-sagyeong", mode)


# ---------------------------------------------------------------- 7. 평양부 지명 관계 그물과 매개중심성
def pynet():
    G = nx.Graph()
    E = [("부", "대동강", "동"), ("부", "대성산", "북"), ("부", "토산", "북"), ("부", "동명왕묘", "손방 30리쯤"),
         ("부", "대동문", "성문"), ("대동문", "진명소", "밖"), ("진명소", "대동강", "강가"), ("부", "진분소", "동"),
         ("진분소", "대동강", "강가")]
    for a, b, t in E:
        G.add_edge(a, b, t=t)
    return G


def fig_pynet(mode):
    c = STY[mode]
    G = pynet()
    btw = nx.betweenness_centrality(G, normalized=False)
    pos = {"부": (0.0, 0.0), "대동강": (2.7, 0.2), "대성산": (-0.3, 1.9), "토산": (-2.1, 1.1), "동명왕묘": (-1.0, -1.7),
           "대동문": (1.4, 1.35), "진명소": (2.7, 1.55), "진분소": (1.55, -1.2)}
    fig, ax = new(mode, 3.3)
    for a, b in G.edges:
        ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]], color=c["gray"], lw=1.0, zorder=1)
    off = {"대성산": (0, 0.38), "토산": (0, 0.38), "동명왕묘": (0, -0.42), "대동문": (-0.1, 0.4), "진명소": (0, 0.4),
           "대동강": (0.0, -0.45), "진분소": (0, -0.42)}
    for n, p in pos.items():
        ax.scatter(*p, s=60 + 130 * btw[n], color=c["fill"] if mode == "color" else "white", edgecolor="black", lw=0.9, zorder=3)
        if n == "부":
            ax.annotate(f"{n}\n{btw[n]:.1f}", p, ha="center", va="center", fontsize=FS, zorder=5, linespacing=1.1)
        else:
            dx, dy = off[n]
            ax.annotate(f"{n} {btw[n]:.1f}", (p[0] + dx, p[1] + dy), ha="center", va="center", fontsize=FS, zorder=5)
    ax.set_xlim(-3.0, 3.5); ax.set_ylim(-2.95, 2.5); ax.set_aspect("equal"); ax.axis("off")
    ax.text(-2.95, -2.9, "원의 크기와 이름 옆 숫자 = 매개중심성(쌍의 수)", fontsize=FS, va="bottom", ha="left")
    return save(fig, "ch09", "fig09-7-pynet", mode), btw


# ---------------------------------------------------------------- 8. 왜인조 구간 합 (서경 밖 참고 실례)
def fig_wae(mode):
    c = STY[mode]
    seg = [("군→구야한국", 7000), ("→대해국", 1000), ("→일대국", 1000), ("→말로국", 1000), ("→이도국", 500), ("→노국", 100)]
    tot = sum(v for _, v in seg)
    fig, ax = new(mode, 2.7)
    x = 0
    fills = [c["fill"], c["fill2"]]
    hs = ["", "//", "", "//", "", "//"] if mode == "bw" else [""] * 6
    for i, (nm, v) in enumerate(seg):
        ax.barh(1, v, left=x, height=0.5, color=(fills[i % 2] if mode == "color" else ("white" if i % 2 else "#cccccc")),
                edgecolor="black", lw=0.7, hatch=hs[i] if mode == "bw" else None)
        if i == 0:
            ax.text(x + v / 2, 1, f"{nm}\n{v:,}", ha="center", va="center", fontsize=FS, linespacing=1.15)
        else:
            ax.annotate(f"{v:,}", (x + v / 2, 1.25), xytext=(x + v / 2 + (0 if i < 4 else (i - 3.5) * 650 - 150), 1.65 + 0.0 * i),
                        ha="center", va="bottom", fontsize=FS, arrowprops=dict(arrowstyle="-", lw=0.5, color=c["gray"]))
        x += v
    ax.barh(0, 12000, left=0, height=0.5, color="white", edgecolor="black", lw=0.9, ls="-")
    ax.barh(0, tot, left=0, height=0.5, color=c["fill2"] if mode == "color" else "#dddddd", edgecolor="black", lw=0.9)
    ax.barh(0, 12000 - tot, left=tot, height=0.5, color="white", edgecolor="black", lw=0.9, hatch="xx", ls="--")
    ax.text(tot / 2, 0, f"발췌한 구간의 합 {tot:,}", ha="center", va="center", fontsize=FS)
    ax.annotate(f"차이 {12000 - tot:,}\n(발췌에 없는 구간?)", (tot + (12000 - tot) / 2, -0.25), xytext=(tot + 80, -0.85), ha="center",
                va="top", fontsize=FS, arrowprops=dict(arrowstyle="-", lw=0.5, color=c["gray"]), linespacing=1.1)
    ax.text(0, 1.45, "구간별 숫자", fontsize=FS, va="bottom", ha="left", fontweight="bold")
    ax.text(0, 0.38, "합계 비교: 바깥 테두리 = 사료의 총합 12,000여", fontsize=FS, va="bottom", ha="left", fontweight="bold")
    ax.set_xlim(-200, 12600); ax.set_ylim(-1.5, 2.15)
    ax.set_yticks([]); ax.set_xlabel("리 (사료의 숫자 그대로)")
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    return save(fig, "ch09", "fig09-8-wae", mode)


# ---------------------------------------------------------------- 9. 사료 인용 그래프와 페이지랭크(가상)
def fig_citation(mode):
    c = STY[mode]
    D = nx.DiGraph([("갑", "을"), ("병", "을"), ("정", "을"), ("을", "갑")])
    pr = nx.pagerank(D, alpha=0.85)
    cnt = dict(D.in_degree())
    pos = {"을": (0.0, 0.0), "갑": (-1.7, 0.0), "병": (1.1, 1.25), "정": (1.1, -1.25)}
    fig, axs = new(mode, 2.6, ncols=2, gridspec_kw=dict(width_ratios=[1.25, 1]))
    ax = axs[0]
    for a, b in D.edges:
        p, q = np.array(pos[a]), np.array(pos[b])
        v = (q - p) / np.hypot(*(q - p))
        rad = 0.25 if (a, b) in (("갑", "을"), ("을", "갑")) else 0.0
        sh = lambda n: math.sqrt((500 + 3000 * pr[n]) / math.pi) / 47.0 + 0.06
        arrow(ax, p + v * sh(a), q - v * sh(b), c=c["gray"], rad=rad, lw=1.1)
    for n, p in pos.items():
        ax.scatter(*p, s=500 + 3000 * pr[n], color=c["fill"] if mode == "color" else "white", edgecolor="black", lw=0.9, zorder=3)
        ax.annotate(f"{n}\n{pr[n]:.3f}", p, ha="center", va="center", fontsize=FS, zorder=5, linespacing=1.05)
    ax.set_xlim(-2.5, 1.7); ax.set_ylim(-1.9, 1.9); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("(a) 가상 문헌 인용 그물", loc="left", fontsize=9)
    ax = axs[1]
    names = ["갑", "을", "병", "정"]
    xs = np.arange(4)
    tot_in = sum(cnt.values())
    ax.bar(xs - 0.2, [cnt[n] / tot_in for n in names], 0.38, color="white", edgecolor="black", hatch="//", label="들어온 화살 비율")
    ax.bar(xs + 0.2, [pr[n] for n in names], 0.38, color=c["fill"] if mode == "color" else "#777777", edgecolor="black", label="페이지랭크")
    ax.set_xticks(xs); ax.set_xticklabels(names); ax.set_ylabel("값"); ax.set_ylim(0, 0.95)
    ax.legend(frameon=False, fontsize=FS, loc="upper right")
    ax.set_title("(b) 두 중요도 비교", loc="left", fontsize=9)
    return save(fig, "ch09", "fig09-9-citation", mode), pr


if __name__ == "__main__":
    for mode in ("color", "bw"):
        print(fig_timeline(mode)); print(fig_mirror(mode))
        p, n, pts = fig_interval(mode); print(p, "구간 방식 영역 칸 수", n)
        print(fig_sagyeong(mode)); p, b = fig_pynet(mode); print(p, {k: round(v, 2) for k, v in b.items()})
        print(fig_wae(mode)); p, pr = fig_citation(mode); print(p, {k: round(v, 4) for k, v in pr.items()})
