"""figs-a.py - 5~8장 그림(기법 1~4). 실행: python3 figs-a.py"""
import sys, csv, os
sys.path.insert(0, ".")
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from figlib import *
from toyworld import *
from toypost import *
from placeloc import t1_csp as t1, t2_georef as t2, t3_bayes as t3, t4_lcp as t4

W = World(seed=7)
G = W.grid
P, ctx = toy_posteriors(W)
OUT = {}


def fig5_1(mode):
    s = STY[mode]
    fig, ax = new(mode, 2.3)
    b0 = Interval(W.dist_obs["갑성"])
    steps = [("원문 수치 (리)", b0, "리"),
             ("× 단위 길이 [0.36, 0.48] km/리", b0 * Interval(*U_BAND), "km"),
             ("× 서술 오차 [0.75, 1.25]", band_from_li(W.dist_obs["갑성"]), "km")]
    for i, (lab, iv, u) in enumerate(steps[1:]):
        y = 1 - i
        ax.barh(y, iv.hi - iv.lo, left=iv.lo, height=0.5, color=s["fill"] if i == 0 else s["fill2"], edgecolor="black",
                hatch="" if mode == "color" else ("//" if i == 0 else ".."), lw=0.6)
        ax.text(iv.hi + 6, y, f"[{iv.lo:.0f}, {iv.hi:.0f}] km", va="center", fontsize=8.5)
        ax.text(0, y + 0.38, lab, va="bottom", fontsize=8.5)
    d_true = np.hypot(*(np.array(W.refs["갑성"]) - W.truth))
    ax.axvline(d_true, color=s["truth"], ls="--", lw=1.0)
    ax.text(d_true, -0.62, "가상의 참 거리", ha="center", va="top", fontsize=8.5)
    ax.set_xlim(0, 360); ax.set_ylim(-0.9, 1.9); ax.set_yticks([]); ax.set_xlabel("갑성에서 목표까지 거리 (km)")
    ax.set_title(f"원문 '{W.dist_obs['갑성']:.0f}리'를 구간으로 환산하는 과정", loc="left")
    return save(fig, "ch05", "fig05-1-interval", mode)


def fig5_2(mode):
    s = STY[mode]
    fig, axs = new(mode, 5.0, ncols=3, nrows=2)
    steps = []
    masks = []
    labels = []
    for k, (x, y) in W.refs.items():
        masks.append(t1.c_distance(G, x, y, band_from_li(W.dist_obs[k])))
        labels.append(f"{k} 거리")
    masks.append(t1.c_near_polyline(G, W.river, W.near_river_km)); labels.append("강 10리 이내")
    shows = [1, 2, 3, 4, 5]
    for n, ax in zip(range(1, 7), axs.ravel()):
        if n <= 5:
            m = np.all(masks[:n], axis=0)
            ax.contourf(G.X, G.Y, m.astype(float), levels=[0.5, 1.5], colors=[s["fill"]], hatches=[None if mode == "color" else "//"])
            ax.contour(G.X, G.Y, masks[n - 1].astype(float), levels=[0.5], colors=[s["gray"]], linewidths=0.7, linestyles="--")
            ttl = f"({'abcde'[n-1]}) +{labels[n-1]}"
            base(ax, W, mode, ttl, label_refs=False)
            ax.text(8, 8, f"{G.area(m):,.0f} km²", fontsize=8.5, bbox=dict(fc="white", ec="none", pad=1))
            ax.plot(*W.truth, "*", color=s["truth"], ms=8, mec="black", mew=0.4, zorder=8)
        else:
            ax.axis("off")
            ax.text(0, 0.9, "범례", fontsize=9, weight="bold", transform=ax.transAxes)
            ax.text(0, 0.72, "▲ 기준 지명", fontsize=8.5, transform=ax.transAxes)
            ax.text(0, 0.58, "★ 가상의 참 위치", fontsize=8.5, transform=ax.transAxes)
            ax.text(0, 0.44, "음영 = 지금까지의 가능 영역", fontsize=8.5, transform=ax.transAxes)
            ax.text(0, 0.30, "점선 = 이번에 더한 제약", fontsize=8.5, transform=ax.transAxes)
            ax.text(0, 0.16, "−·− 하천", fontsize=8.5, transform=ax.transAxes)
    for ax in axs.ravel():
        ax.tick_params(labelsize=8.5)
    return save(fig, "ch05", "fig05-2-layers", mode)


def fig5_3(mode):
    s = STY[mode]
    fig, ax = new(mode, 3.0)
    masks = [t1.c_distance(G, x, y, band_from_li(W.dist_obs[k])) for k, (x, y) in W.refs.items()]
    bad = t1.c_distance(G, *W.refs["갑성"], Interval(40, 70))
    r = t1.solve(masks + [bad])
    sc = r["score"].astype(float)
    cs = ax.contourf(G.X, G.Y, sc, levels=np.arange(-0.5, 6, 1), cmap=s["cmap"], alpha=0.85)
    base(ax, W, mode, "모순 증거가 섞였을 때: 만족한 제약의 개수", label_refs=True, truth=True)
    cb = fig.colorbar(cs, ax=ax, ticks=range(0, 6), shrink=0.8)
    cb.set_label("만족한 제약 수 (5개 중)")
    ax.text(200, 385, f"전부 만족하는 칸: {int(r['feasible'].sum())}개 (공집합)", ha="center", fontsize=8.5,
            bbox=dict(fc="white", ec="none", pad=1))
    return save(fig, "ch05", "fig05-3-conflict", mode)


def fig6_1(mode):
    s = STY[mode]
    src, dst = W.ctrl_src, W.ctrl_dst
    fig, axs = new(mode, 2.6, ncols=3)
    for ax, (nm, fit, kw) in zip(axs, [("닮음변환", t2.fit_similarity, {}), ("아핀변환", t2.fit_affine, {}), ("박판스플라인", t2.fit_tps, dict(lam=0.01))]):
        res, e = t2.loocv(fit, src, dst, **kw)
        ax.set_xlim(0, 400); ax.set_ylim(0, 400); ax.set_aspect("equal")
        ax.plot(dst[:, 0], dst[:, 1], "o", ms=3, color=s["ref"])
        pred = dst + 5.0 * res
        for a, b in zip(dst, pred):
            ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color=s["truth"], lw=1.0, mutation_scale=7))
        ax.set_title(f"{nm}\n잔차 {e:.1f} km (화살표 5배)", fontsize=8.5)
        ax.set_xticks([0, 200, 400]); ax.set_yticks([0, 200, 400]); ax.set_xlabel("동 (km)")
        if ax is axs[0]:
            ax.set_ylabel("북 (km)")
        ax.grid(color=s["grid"], lw=0.3, ls=":")
    return save(fig, "ch06", "fig06-1-residual", mode)


def fig6_2(mode):
    s = STY[mode]
    fig, axs = new(mode, 2.7, ncols=2)
    f = t2.fit_tps(W.ctrl_src, W.ctrl_dst, lam=0.01)
    lo = W.ctrl_src.min(0) - 30; hi = W.ctrl_src.max(0) + 30
    lines = t2.grid_distortion(f, (lo[0], hi[0]), (lo[1], hi[1]), n=9)
    ax = axs[0]
    for L in lines:
        ax.plot(L[:, 0], L[:, 1], color=s["gray"], lw=0.6)
    ax.plot(W.ctrl_dst[:, 0], W.ctrl_dst[:, 1], "o", ms=3, color=s["ref"])
    ax.set_xlim(-60, 460); ax.set_ylim(-60, 460); ax.set_aspect("equal")
    ax.set_title("(a) 고지도의 정방 격자를\n현대 좌표로 옮긴 모양", fontsize=8.5)
    ax.set_xlabel("동 (km)"); ax.set_ylabel("북 (km)")
    ax = axs[1]
    sx = np.linspace(lo[0], hi[0], 15); sy = np.linspace(lo[1], hi[1], 15)
    X, Y = np.meshgrid(sx, sy)
    Z = f(np.c_[X.ravel(), Y.ravel()])
    # 국소 축척: 고지도 1단위당 현대 km (작은 차분)
    h = 1.0
    J = []
    for p in np.c_[X.ravel(), Y.ravel()]:
        a = (f((p + [h, 0])[None, :]) - f((p - [h, 0])[None, :]))[0] / (2 * h)
        b = (f((p + [0, h])[None, :]) - f((p - [0, h])[None, :]))[0] / (2 * h)
        J.append(np.sqrt(abs(a[0] * b[1] - a[1] * b[0])))
    J = np.array(J)
    sc = ax.scatter(Z[:, 0], Z[:, 1], c=J, s=22, cmap=s["cmap"], edgecolor="black" if mode == "bw" else "none", lw=0.3)
    ax.set_xlim(-60, 460); ax.set_ylim(-60, 460); ax.set_aspect("equal")
    cb = fig.colorbar(sc, ax=ax, shrink=0.75); cb.set_label("국소 축척 (km/화상단위)")
    ax.set_title("(b) 곳에 따라 달라지는 축척", fontsize=8.5)
    ax.set_xlabel("동 (km)")
    return save(fig, "ch06", "fig06-2-warp", mode)


def fig6_3(mode):
    s = STY[mode]
    fig, ax = new(mode, 2.4)
    lams = [0.0, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0]
    ets = [t2.loocv(t2.fit_tps, W.ctrl_src, W.ctrl_dst, lam=l)[1] for l in lams]
    ea = t2.loocv(t2.fit_affine, W.ctrl_src, W.ctrl_dst)[1]
    es = t2.loocv(t2.fit_similarity, W.ctrl_src, W.ctrl_dst)[1]
    xs = np.arange(len(lams))
    ax.plot(xs, ets, "o-", color=s["line"], label="박판스플라인")
    ax.axhline(ea, color=s["gray"], ls="--", label="아핀변환")
    ax.axhline(es, color=s["gray"], ls=":", label="닮음변환")
    ax.set_xticks(xs); ax.set_xticklabels([str(l) for l in lams])
    ax.set_xlabel("정칙화 계수 λ"); ax.set_ylabel("하나 빼고 적합한 잔차 RMSE (km)")
    ax.legend(frameon=False)
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    return save(fig, "ch06", "fig06-3-loocv", mode)


def fig7_1(mode):
    s = STY[mode]
    fig, axs = new(mode, 2.6, ncols=3)
    uns = np.linspace(*U_BAND, 15)
    prior = t3.prior_uniform(G)
    L1 = t3.lik_distance(G, *W.refs["갑성"], W.dist_obs["갑성"], REL_SIGMA, unit_samples=uns)
    post = P["T3 베이즈"]
    for ax, (ttl, Z) in zip(axs, [("(a) 사전분포", prior), ("(b) 우도: 갑성 거리 한 건", L1 / L1.sum()), ("(c) 사후분포: 모든 증거", post)]):
        ax.contourf(G.X, G.Y, Z / Z.max(), levels=np.linspace(0.02, 1, 12), cmap=s["cmap"])
        base(ax, W, mode, None, label_refs=False)
        ax.set_title(ttl, fontsize=8.5)
        ax.plot(*W.truth, "*", color=s["truth"], ms=8, mec="black", mew=0.4, zorder=8)
        ax.set_xticks([0, 200, 400]); ax.set_yticks([0, 200, 400])
        if ax is not axs[0]:
            ax.set_ylabel("")
    return save(fig, "ch07", "fig07-1-bayes", mode)


def fig7_2(mode):
    s = STY[mode]
    fig, ax = new(mode, 3.3)
    post = P["T3 베이즈"]
    lp = lambda p: np.log(post[min(max(int(round(p[1] / G.step)), 0), 100), min(max(int(round(p[0] / G.step)), 0), 100)] + 1e-300)
    iy, ix = idx_of(G, W.truth)
    chain, acc = t3.metropolis(lp, W.truth, n=12000, step=5.0, seed=1)
    h95, h50 = t3.hpd_mask(post, 0.95), t3.hpd_mask(post, 0.5)
    ax.contourf(G.X, G.Y, h95.astype(float), levels=[0.5, 1.5], colors=[s["fill2"]], hatches=[None if mode == "color" else ".."])
    ax.contourf(G.X, G.Y, h50.astype(float), levels=[0.5, 1.5], colors=[s["fill"]], hatches=[None if mode == "color" else "//"])
    sub = chain[3000::12]
    ax.plot(sub[:, 0], sub[:, 1], ".", ms=1.6, color=s["ref"], alpha=0.5)
    base(ax, W, mode, "신용 영역과 메트로폴리스 표본", truth=True)
    ax.set_xlim(180, 290); ax.set_ylim(130, 240)
    ax.set_xticks(range(180, 291, 20)); ax.set_yticks(range(130, 241, 20))
    ctx["mcmc"] = (len(sub), acc)
    return save(fig, "ch07", "fig07-2-hpd", mode)


def fig7_3(mode):
    s = STY[mode]
    fig, ax = new(mode, 3.1)
    rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "ch07-calibration.csv"), encoding="utf-8")))
    levels = sorted({float(r["level"]) for r in rows})
    sty = {"shared": ("단위 길이를 공유한 모형 (옳음)", "o-", "-"), "indep": ("증거마다 단위를 따로 뽑은 모형", "s--", "--"),
           "biased": ("단위를 +15%로 잘못 고정한 모형", "^:", ":")}
    for key, (lab, mk, ls) in sty.items():
        ys = [float(r["coverage"]) for r in rows if r["mode"] == key]
        ax.plot(levels, ys, mk, ms=4, color=s["line"] if mode == "bw" else {"shared": "#2e7d32", "indep": "#1f6fb8", "biased": "#c0392b"}[key], label=lab, mfc="white" if key != "shared" else None)
    ax.plot([0, 1], [0, 1], color=s["gray"], lw=0.8)
    ax.set_xlabel("신용 수준 (명목)"); ax.set_ylabel("참 위치가 실제로 영역 안에 든 비율")
    ax.set_xlim(0.1, 1.0); ax.set_ylim(0, 1.02)
    ax.legend(frameon=False, loc="upper left")
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    return save(fig, "ch07", "fig07-3-calib", mode)


def fig8_1(mode):
    s = STY[mode]
    fig, axs = new(mode, 3.0, ncols=2)
    dem, tt = ctx["dem"], ctx["tt"]
    ls = LightSource(azdeg=315, altdeg=40)
    sh = ls.hillshade(dem, vert_exag=0.01, dx=G.step, dy=G.step)
    ax = axs[0]
    ax.imshow(sh, extent=[0, 400, 0, 400], origin="lower", cmap="gray", alpha=0.9)
    cs = ax.contour(G.X, G.Y, tt, levels=np.arange(8, 80, 8), colors=[s["line"] if mode == "bw" else "#8e2a0b"], linewidths=0.8)
    ax.clabel(cs, fmt="%d시간", fontsize=8.5, inline=True)
    base(ax, W, mode, "(a) 갑성에서의 이동시간(등시간선)", truth=True, river=True, label_refs=True)
    ax = axs[1]
    Gr = t4.build_graph(dem, G.step)
    t, pred = t4.travel_time(Gr, G.shape, ctx["src"], return_pred=True)
    iy, ix = idx_of(G, W.truth)
    path = t4.path_to(pred, G.shape, ctx["src"], (iy, ix))
    ax.imshow(sh, extent=[0, 400, 0, 400], origin="lower", cmap="gray", alpha=0.9)
    pp = np.array([(G.xs[c], G.ys[r]) for r, c in path])
    ax.plot(pp[:, 0], pp[:, 1], color=s["truth"] if mode == "color" else "white", lw=2.0, zorder=4, label="최소비용 경로")
    ax.plot([W.refs["갑성"][0], W.truth[0]], [W.refs["갑성"][1], W.truth[1]], color=s["gray"] if mode == "color" else "black", ls="--", lw=1.0, zorder=4, label="직선")
    base(ax, W, mode, "(b) 최소비용 경로와 직선", truth=True, label_refs=True)
    ax.legend(frameon=True, loc="lower left", framealpha=0.9)
    ax.set_ylabel("")
    ctx["path_len"] = float(np.hypot(*np.diff(pp, axis=0).T).sum())
    return save(fig, "ch08", "fig08-1-isochrone", mode)


def fig8_2(mode):
    s = STY[mode]
    fig, ax = new(mode, 2.3)
    sl = np.linspace(-0.6, 0.6, 400)
    ax.plot(np.degrees(np.arctan(sl)), t4.tobler_speed_kmh(sl), color=s["line"])
    ax.axvline(np.degrees(np.arctan(-0.05)), color=s["gray"], ls=":", lw=0.8)
    ax.text(np.degrees(np.arctan(-0.05)) + 1, 5.9, "최고속도 6 km/h\n(내리막 약 −2.9°)", fontsize=8.5, va="top")
    ax.set_xlabel("경사각 (도, 오르막 +)"); ax.set_ylabel("보행 속도 (km/h)")
    ax.set_ylim(0, 6.5)
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    return save(fig, "ch08", "fig08-2-tobler", mode)


if __name__ == "__main__":
    for mode in ("color", "bw"):
        for f in (fig5_1, fig5_2, fig5_3, fig6_1, fig6_2, fig6_3, fig7_1, fig7_2, fig7_3, fig8_1, fig8_2):
            print(f.__name__, mode, "->", f(mode))
