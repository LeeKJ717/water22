"""figs-d.py - 1권 보강 그림: 실제 좌표 지도와 가상 세계 도해. 사용: python3 tools/figs-d.py (tools 폴더에서 실행해도 되고 책 루트에서 해도 됨)"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from matplotlib.patches import Wedge, Circle, Polygon as MPoly, FancyArrowPatch
from figlib import *
import matplotlib.pyplot as plt

def km(lon, lat, lon0=125.7475, lat0=39.0167):
    return ((lon - lon0) * 111.32 * math.cos(math.radians(lat0)), (lat - lat0) * 111.2)
def dms(d, m, s=0): return d + m / 60 + s / 3600
PY = km(dms(125, 44, 51), dms(39, 1, 0))
MO = km(dms(125, 45, 30), dms(39, 2, 25))
AN = km(dms(125, 50, 2), dms(39, 3, 42))
TS = km(dms(125, 49, 42), dms(39, 4, 26))

def fig_real(mode):
    c = STY[mode]
    fig, ax = new(mode, 4.6)
    pts = {"평양(현재 시가 중심)": PY, "모란봉": MO, "안학궁 터": AN, "대성산": TS}
    for u, a in [(0.48, 0.10), (0.36, 0.10)]:
        pass
    for n_ri in (10, 20):
        r0, r1 = n_ri * 0.36, n_ri * 0.48
        ax.add_patch(Wedge(PY, r1, 0, 360, width=r1 - r0, facecolor=c["fill"], alpha=0.45, edgecolor="none"))
        ax.text(PY[0] + r1 * 0.70 + 0.2, PY[1] - r1 * 0.70 - 0.3, f"{n_ri}리 (0.36~0.48 km/리 가정)", fontsize=8, color=c["gray"], ha="left", va="top")
    for n, (x, y) in pts.items():
        mk = "o" if "평양" in n else ("^" if "산" in n else "s")
        ax.plot(x, y, mk, ms=7, color=c["truth"] if "평양" in n else c["ref"], zorder=5)
        ax.annotate(n, (x, y), textcoords="offset points", xytext=(6, 5), fontsize=8.5)
    for n in ("모란봉", "안학궁 터", "대성산"):
        x, y = pts[n]; d = math.hypot(x - PY[0], y - PY[1])
        ax.plot([PY[0], x], [PY[1], y], ls=":", color=c["gray"], lw=0.8)
        ax.text((PY[0] + x) / 2 + 0.2, (PY[1] + y) / 2 - 0.5, f"{d:.1f} km", fontsize=8.5, color=c["gray"])
    ax.set_xlim(-8, 11); ax.set_ylim(-9, 11); ax.set_aspect("equal")
    ax.set_xlabel("동쪽으로 (km, 평양 중심점 기준)"); ax.set_ylabel("북쪽으로 (km)")
    ax.grid(color=c["grid"], lw=0.4)
    return save(fig, "ch05", "fig5-4-pyeongyang", mode)

# 가상 세계 격자 도우미
def grid(n=60, ext=30.0):
    xs = np.linspace(-ext, ext, n); X, Y = np.meshgrid(xs, xs); return X, Y

def fig_csp(mode):
    c = STY[mode]
    fig, axs = new(mode, 2.5, ncols=4, sharex=True, sharey=True)
    X, Y = grid(); A = (-6.0, 4.0); B = (-20.0, 10.0)
    d1 = np.hypot(X - A[0], Y - A[1]); d2 = np.hypot(X - B[0], Y - B[1])
    m1 = (d1 >= 10 * 0.36) & (d1 <= 15 * 0.48)
    m2 = (d2 >= 20 * 0.36) & (d2 <= 30 * 0.48)
    ang = np.degrees(np.arctan2(Y - A[1], X - A[0]))
    m3 = np.abs(((ang - 180 + 180) % 360) - 180) <= 45
    titles = ["① A에서 10~15리", "② B에서 20~30리", "③ A의 서쪽(±45°)", "①②③ 모두 만족"]
    ms = [m1, m2, m3, m1 & m2 & m3]
    for ax, m, t in zip(axs, ms, titles):
        ax.imshow(np.where(m, 1, 0), extent=(-30, 30, -30, 30), origin="lower", cmap=c["cmap"], vmin=0, vmax=1.6, alpha=0.85)
        ax.plot(*A, "k^", ms=5); ax.plot(*B, "ks", ms=5); ax.set_title(t, fontsize=8.5)
        ax.text(A[0] + 1, A[1] + 1.5, "A", fontsize=8.5); ax.text(B[0] + 1, B[1] + 1.5, "B", fontsize=8.5)
        ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    return save(fig, "ch05", "fig5-5-layers", mode)

def fig_geo(mode):
    c = STY[mode]
    fig, axs = new(mode, 2.9, ncols=3)
    old = np.array([[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1], [0, 2], [1, 2], [2, 2]], float)
    ctrl = np.array([[0, 0], [2, 0], [0, 2], [2, 2]], float)
    th = math.radians(12); R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    new_ctrl = (ctrl * 8.0 @ R.T) + np.array([3, 2]) + np.array([[0, 0], [0.8, 0], [0.0, 0.6], [1.0, 1.2]])
    axs[0].set_title("옛 지도 (그림 좌표)", fontsize=8.5)
    for i in range(3):
        axs[0].plot([0, 2], [i, i], color=c["gray"], lw=0.6); axs[0].plot([i, i], [0, 2], color=c["gray"], lw=0.6)
    axs[0].plot(*ctrl.T, "o", color=c["truth"], ms=6)
    # 닮음변환(최소제곱)
    def sim(src, dst):
        mu_s, mu_d = src.mean(0), dst.mean(0); S = src - mu_s; D = dst - mu_d
        U, sg, Vt = np.linalg.svd(D.T @ S); Rr = U @ Vt
        if np.linalg.det(Rr) < 0: Vt[-1] *= -1; sg[-1] *= -1; Rr = U @ Vt
        s = sg.sum() / (S ** 2).sum(); return lambda p: s * (p - mu_s) @ Rr.T + mu_d
    def aff(src, dst):
        M = np.c_[src, np.ones(len(src))]; W, *_ = np.linalg.lstsq(M, dst, rcond=None); return lambda p: np.c_[p, np.ones(len(p))] @ W
    for ax, f, t in [(axs[1], sim(ctrl, new_ctrl), "닮음변환 (회전·확대만)"), (axs[2], aff(ctrl, new_ctrl), "아핀변환 (기울임 포함)")]:
        ax.set_title(t, fontsize=8.5)
        for i in range(3):
            line = np.array([[0, i], [2, i]], float); ax.plot(*f(np.array([[0, i], [2, i]], float)).T, color=c["gray"], lw=0.6)
            ax.plot(*f(np.array([[i, 0], [i, 2]], float)).T, color=c["gray"], lw=0.6)
        ax.plot(*new_ctrl.T, "o", color=c["truth"], ms=6); fc = f(ctrl)
        for p, q in zip(fc, new_ctrl): ax.plot([p[0], q[0]], [p[1], q[1]], color=c["ref"], lw=1.2)
        err = np.hypot(*(fc - new_ctrl).T).mean(); ax.text(0.03, 0.04, f"평균 어긋남 {err:.2f}", transform=ax.transAxes, fontsize=8.5)
    for ax in axs: ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    return save(fig, "ch06", "fig6-4-warp", mode)

def fig_bayes(mode):
    c = STY[mode]
    fig, axs = new(mode, 2.6, ncols=3, sharex=True, sharey=True)
    X, Y = grid(); A = (-4.0, 2.0)
    prior = np.exp(-((X + 2) ** 2 + (Y - 6) ** 2) / (2 * 12 ** 2)) * (1 + 0.8 * (Y < 0))
    d = np.hypot(X - A[0], Y - A[1]); u = 0.42
    like = np.exp(-0.5 * ((np.log(np.maximum(d, 1e-3) / u) - math.log(15)) / 0.25) ** 2)
    post = prior * like; post /= post.sum()
    for ax, z, t in zip(axs, [prior, like, post], ["사전 확률 (지형·인구 단서)", "× 우도 (A에서 15리)", "= 사후 확률"]):
        z = z / z.max()
        ax.imshow(z, extent=(-30, 30, -30, 30), origin="lower", cmap=c["cmap"]); ax.plot(*A, "k^", ms=5)
        ax.set_title(t, fontsize=8.5); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    p = post.ravel(); idx = np.argsort(-p); cum = np.cumsum(p[idx]); thr = p[idx][np.searchsorted(cum, 0.95)]
    axs[2].contour(X, Y, post, levels=[thr], colors=[c["truth"]], linewidths=1.2)
    return save(fig, "ch07", "fig7-4-prior-like-post", mode)

def fig_lcp(mode):
    c = STY[mode]
    import heapq
    n = 61; X, Y = grid(n, 30.0)
    hill = 1.0 * np.exp(-((X - 0) ** 2 + (Y - 2) ** 2) / (2 * 7 ** 2)) + 0.8 * np.exp(-((X - 8) ** 2 + (Y + 14) ** 2) / (2 * 6 ** 2))
    cost = 1 + 12 * hill
    S = (5, 30); T = (55, 30)
    dist = np.full((n, n), np.inf); prev = {}; dist[S] = 0; pq = [(0, S)]
    nb = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    while pq:
        d0, (i, j) = heapq.heappop(pq)
        if d0 > dist[i, j]: continue
        if (i, j) == T: break
        for di, dj in nb:
            a, b = i + di, j + dj
            if 0 <= a < n and 0 <= b < n:
                w = math.hypot(di, dj) * 0.5 * (cost[i, j] + cost[a, b]) * 1.0
                if d0 + w < dist[a, b]: dist[a, b] = d0 + w; prev[(a, b)] = (i, j); heapq.heappush(pq, (d0 + w, (a, b)))
    path = [T]
    while path[-1] != S: path.append(prev[path[-1]])
    path = np.array(path)
    fig, ax = new(mode, 3.4)
    ax.imshow(hill, extent=(-30, 30, -30, 30), origin="lower", cmap=c["cmap"])
    xs = lambda k: -30 + 60 * k / (n - 1)
    ax.plot([xs(S[1]), xs(T[1])], [xs(S[0]), xs(T[0])], "--", color=c["gray"], lw=1.2, label="직선")
    ax.plot(xs(path[:, 1]), xs(path[:, 0]), "-", color=c["truth"], lw=1.8, label="최소비용 경로")
    ax.plot(xs(S[1]), xs(S[0]), "ko", ms=6); ax.plot(xs(T[1]), xs(T[0]), "ks", ms=6)
    ax.text(xs(S[1]) - 1, xs(S[0]) + 2.0, "출발", fontsize=8.5, ha="right"); ax.text(xs(T[1]) + 1, xs(T[0]) + 2.0, "도착", fontsize=8.5)
    ax.legend(loc="lower right"); ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
    return save(fig, "ch08", "fig8-3-lcp", mode)

if __name__ == "__main__":
    for m in ("color", "bw"):
        for f in (fig_real, fig_csp, fig_geo, fig_bayes, fig_lcp):
            print(f(m))
