"""figs-b.py - 9~12장 그림(기법 5~8) + 표 CSV. 실행: python3 figs-b.py"""
import sys, csv, os, json
sys.path.insert(0, ".")
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from figlib import *
from toyworld import *
from toypost import *
from placeloc import t1_csp as t1, t3_bayes as t3, t5_graph as t5, t6_gazetteer as t6, t8_cross as t8

W = World(seed=7)
G = W.grid
P, ctx = toy_posteriors(W)
PL = list(P.values())
SHORT = ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]


def fig9_1(mode):
    s = STY[mode]
    fig, axs = new(mode, 2.9, ncols=2)
    ax = axs[0]
    base(ax, W, mode, "(a) 앵커 MDS가 푼 목표 위치", river=False, truth=True)
    est = ctx["est5"]
    for k, (x, y) in W.refs.items():
        ax.plot([x, est[0]], [y, est[1]], color=s["gray"], lw=0.8, ls="--")
    ax.plot(*est, "D", color="white", mec="black", ms=6, zorder=8, label="추정")
    ax.legend(frameon=True, loc="lower left", fontsize=8.5)
    ax = axs[1]
    c = ctx["cloud5"]
    base(ax, W, mode, "(b) 간선 하나씩 뺀 재추정", river=False, truth=True, label_refs=False)
    ax.plot(c[:, 0], c[:, 1], ".", ms=2.0, color=s["gray"], alpha=0.6)
    ax.set_xlim(150, 320); ax.set_ylim(110, 260); ax.set_xticks(range(150, 321, 50)); ax.set_yticks(range(110, 261, 50))
    ax.set_ylabel("")
    return save(fig, "ch09", "fig09-1-anchormds", mode)


def toy_network():
    rng = np.random.default_rng(21)
    pts = {k: np.array(v) for k, v in W.refs.items()}
    for i, nm in enumerate(["가나", "다라", "마바", "사아", "자차", "카타"]):
        pts[nm] = rng.uniform(40, 360, 2)
    pts["목표"] = W.truth.copy()
    Gx = nx.Graph()
    names = list(pts)
    for a in names:
        d = sorted(((np.hypot(*(pts[a] - pts[b])), b) for b in names if b != a))[:3]
        for dd, b in d:
            Gx.add_edge(a, b, d=dd, w=1.0 / dd)
    return Gx, pts


def fig9_2(mode):
    s = STY[mode]
    fig, ax = new(mode, 3.3)
    Gx, pts = toy_network()
    btw = nx.betweenness_centrality(Gx, weight="d")
    pr = nx.pagerank(Gx, weight="w")
    for a, b in Gx.edges:
        ax.plot([pts[a][0], pts[b][0]], [pts[a][1], pts[b][1]], color=s["gray"], lw=0.8, zorder=1)
    for n, p in pts.items():
        ax.scatter(*p, s=40 + 900 * btw[n], color=s["fill"] if mode == "color" else "white", edgecolor="black", lw=0.8, zorder=3)
        ax.annotate(n, p, xytext=(0, -3), textcoords="offset points", ha="center", va="center", fontsize=8.5, zorder=5)
    ax.set_xlim(0, 400); ax.set_ylim(0, 400); ax.set_aspect("equal")
    ax.set_xlabel("동 (km)"); ax.set_ylabel("북 (km)")
    ax.set_title("가상 지명 그래프 — 원의 크기 = 매개중심성", loc="left")
    ctx["btw"] = btw; ctx["pr"] = pr
    return save(fig, "ch09", "fig09-2-graph", mode)


def fig10_1(mode):
    s = STY[mode]
    fig, axs = new(mode, 3.7, nrows=2, gridspec_kw=dict(height_ratios=[1.1, 1]))
    ax = axs[0]
    recs = [("g1 西津 (갑 지점)", 900, 1500), ("g2 西津 (을 지점)", 900, 1500), ("g3 東津", 900, 1500)]
    # 시간 겹침을 보이기 위해 맛보기 사전에 폐지·이설 시기를 더한다
    recs = [("g1 西津 · 갑 지점", 900, 1500), ("g2 西津 · 을 지점", 900, 1180), ("g2' 西津 · 병 지점", 1180, 1600), ("g3 東津", 900, 1500)]
    for i, (lab, a, b) in enumerate(recs[::-1]):
        ax.barh(i, b - a, left=a, height=0.55, color=s["fill"] if i % 2 else s["fill2"], edgecolor="black", lw=0.6, hatch="" if mode == "color" else ("//" if i % 2 else ".."))
    ax.set_yticks(range(len(recs))); ax.set_yticklabels([r[0] for r in recs[::-1]])
    ax.axvline(1100, color=s["truth"], ls="--", lw=1.0)
    ax.text(1108, 0.0, "본문의 시점\n1100년", fontsize=8.5, va="center")
    ax.set_xlim(880, 1620); ax.set_xlabel("연도")
    ax.set_title("(a) 시간 조각내기 — 1100년에 '西津'으로 불린 곳", loc="left")
    ax = axs[1]
    cand = ctx["cand6"]
    labs = [r.rid + " " + r.name_han for _, r, _ in cand]
    comp = np.array([c for _, _, c in cand])
    wts = (0.5, 0.3, 0.2)
    left = np.zeros(len(cand))
    for j, (nm, h) in enumerate(zip(["이름", "시기", "공간"], ["", "//", ".."])):
        v = comp[:, j] * wts[j]
        ax.barh(range(len(cand))[::-1], v, left=left, height=0.55, label=f"{nm} (가중 {wts[j]})",
                color=[s["fill"], s["fill2"], "#b9d9b0"][j] if mode == "color" else ["#444", "#999", "#ddd"][j], edgecolor="black", lw=0.5)
        left += v
    ax.set_yticks(range(len(cand))[::-1]); ax.set_yticklabels(labs)
    for i, (sc, _, _) in enumerate(cand):
        ax.text(sc + 0.01, len(cand) - 1 - i, f"{sc:.2f}", va="center", fontsize=8.5)
    ax.set_xlim(0, 1.15); ax.set_xlabel("정합 점수 (이름·시기·공간의 가중합)")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=3, fontsize=8.5)
    ax.set_title("(b) 후보 사전 항목의 점수 분해", loc="left")
    return save(fig, "ch10", "fig10-1-gazetteer", mode)


def fig11_1(mode):
    s = STY[mode]
    fig, axs = new(mode, 2.9, ncols=2)
    ax = axs[0]
    rows = ctx["rows7"]
    style = {"津": ("o", 14), "山": ("^", 14), "城": (".", 8)}
    for suf, (mk, sz) in style.items():
        pts = np.array([(x, y) for n, x, y in rows if n.endswith(suf)])
        ax.scatter(pts[:, 0], pts[:, 1], marker=mk, s=sz, color=s["ref"] if suf != "津" else s["river"],
                   facecolor="none" if (mode == "bw" and suf == "津") else None, label=f"-{suf}", lw=0.7)
    base(ax, W, mode, "(a) 가상 지명 사전", refs=False, river=True)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.26), fontsize=8.5, ncol=3, columnspacing=0.8, handletextpad=0.2)
    ax = axs[1]
    L = ctx["L7"]
    cs = ax.contourf(G.X, G.Y, np.log10(L), levels=12, cmap=s["cmap"])
    base(ax, W, mode, "(b) '津'을 가진 이름의 우도", refs=False, river=True, truth=True)
    fig.colorbar(cs, ax=ax, shrink=0.7).set_label("log10 우도비")
    ax.set_ylabel("")
    return save(fig, "ch11", "fig11-1-morph", mode)


def pooled_all():
    return t8.log_pool(PL)


def fig12_1(mode):
    s = STY[mode]
    fig, axs = new(mode, 3.5, ncols=4, nrows=2)
    pool = pooled_all()
    items = list(P.items()) + [("T8 교차검증(로그 풀링)", pool)]
    iy, ix = idx_of(G, W.truth)
    for ax, (nm, p) in zip(axs.ravel(), items):
        ax.contourf(G.X, G.Y, p / p.max(), levels=np.linspace(0.02, 1, 10), cmap=s["cmap"])
        ax.contour(G.X, G.Y, t3.hpd_mask(p, 0.95).astype(float), levels=[0.5], colors=[s["line"]], linewidths=0.8)
        ax.plot(*W.truth, "*", color=s["truth"], ms=7, mec="black", mew=0.4, zorder=8)
        ax.set_xlim(0, 400); ax.set_ylim(0, 400); ax.set_aspect("equal")
        ax.set_title(nm.replace(" ", "\n", 1) if nm != "T8 교차검증(로그 풀링)" else "T8 교차검증\n(로그 풀링)", fontsize=8.5)
        ax.set_xticks([0, 200, 400]); ax.set_yticks([0, 200, 400])
        ax.tick_params(labelsize=8.5)
    return save(fig, "ch12", "fig12-1-eight", mode)


def fig12_2(mode):
    s = STY[mode]
    fig, ax = new(mode, 3.6)
    M = t8.conflict_matrix(PL)
    im = ax.imshow(M, cmap=s["cmap"], vmin=0, vmax=1)
    ax.set_xticks(range(7)); ax.set_xticklabels(SHORT); ax.set_yticks(range(7)); ax.set_yticklabels(SHORT)
    for i in range(7):
        for j in range(7):
            ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=8.5, color="white" if (M[i, j] > 0.55 and mode == "bw") or (M[i, j] > 0.75) else "black")
    fig.colorbar(im, ax=ax, shrink=0.8).set_label("겹침 계수")
    ax.set_title("기법 사이의 사후분포 겹침", loc="left")
    ctx["M"] = M
    return save(fig, "ch12", "fig12-2-conflict", mode)


def fig12_3(mode):
    s = STY[mode]
    fig, ax = new(mode, 2.6)
    pool = pooled_all()
    loo = t8.leave_one_out(PL)
    c0 = np.array(G.centroid(pool))
    shifts = [np.hypot(*(np.array(G.centroid(l)) - c0)) for l in loo]
    ax.bar(range(7), shifts, color=s["fill"], edgecolor="black", hatch="" if mode == "color" else "//", lw=0.6)
    ax.set_xticks(range(7)); ax.set_xticklabels([f"{n} 제외" for n in SHORT], fontsize=8.5)
    ax.set_ylabel("합의 중심의 이동 (km)")
    ax.grid(axis="y", color=s["grid"], lw=0.3, ls=":")
    ctx["loo_shift"] = shifts
    return save(fig, "ch12", "fig12-3-loo", mode)


def fig12_4(mode):
    s = STY[mode]
    fig, ax = new(mode, 3.3)
    masks = [t3.hpd_mask(p, 0.95) for p in PL]
    pl, K = t8.dempster(masks, [0.8] * 7)
    cs = ax.contourf(G.X, G.Y, pl / pl.max(), levels=np.linspace(0.02, 1, 12), cmap=s["cmap"])
    base(ax, W, mode, f"Dempster 결합의 가능도 지도 (충돌량 K = {K:.3f})", truth=True)
    fig.colorbar(cs, ax=ax, shrink=0.8).set_label("가능도 (최댓값 = 1)")
    ctx["K"] = K
    ctx["pl_area"] = G.area(pl >= 0.5 * pl.max())
    return save(fig, "ch12", "fig12-4-dempster", mode)


def fig12_5(mode):
    """오염된 기법이 하나 섞였을 때: 로그 풀링·선형 풀링·Dempster"""
    s = STY[mode]
    bad = np.exp(-0.5 * ((G.X - 90.0) ** 2 + (G.Y - 150.0) ** 2) / 18.0 ** 2)
    bad /= bad.sum()
    PLb = list(PL)
    PLb[5] = bad                                 # T6이 동명이지(을 지점)를 골랐다고 가정
    lp = t8.log_pool(PLb)
    ln = t8.linear_pool(PLb)
    masks = [t3.hpd_mask(p, 0.95) for p in PLb]
    pl, K = t8.dempster(masks, [0.8] * 7)
    loo = t8.leave_one_out(PLb)
    c_all = np.array(G.centroid(lp))
    shifts = [np.hypot(*(np.array(G.centroid(l)) - c_all)) for l in loo]
    fig, axs = new(mode, 2.8, ncols=3)
    for ax, (ttl, Z) in zip(axs, [("(a) 로그 풀링", lp), ("(b) 선형 풀링", ln), (f"(c) Dempster (K={K:.2f})", pl)]):
        Z = Z / Z.max()
        ax.contourf(G.X, G.Y, Z, levels=np.linspace(0.02, 1, 10), cmap=s["cmap"])
        ax.plot(*W.truth, "*", color=s["truth"], ms=7, mec="black", mew=0.4, zorder=8)
        ax.plot(90, 150, "x", color="black", ms=6, zorder=8)
        ax.set_xlim(0, 400); ax.set_ylim(0, 400); ax.set_aspect("equal"); ax.set_title(ttl, fontsize=8.5)
        ax.set_xticks([0, 200, 400]); ax.set_yticks([0, 200, 400]); ax.set_xlabel("동 (km)")
        if ax is axs[0]:
            ax.set_ylabel("북 (km)")
    ctx["bad"] = dict(K=float(K), shifts=[float(x) for x in shifts], lp_c=[float(x) for x in c_all],
                      ln_c=[float(x) for x in G.centroid(ln)], pl_area=float(G.area(pl >= 0.5 * pl.max())))
    return save(fig, "ch12", "fig12-5-contaminated", mode)


def fig12_6(mode):
    s = STY[mode]
    fig, ax = new(mode, 2.9)
    rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "ch12-pool-calibration.csv"), encoding="utf-8")))
    names = ["풀링-독립가정(가중 1)", "풀링-공유증거 보정(T1·T3·T5 가중 1/3)", "선형 풀링(평균)"]
    labs = ["로그 풀링\n(독립 가정)", "로그 풀링\n(공유 증거 보정)", "선형 풀링\n(평균)"]
    w = 0.25
    for i, lv in enumerate((0.5, 0.8, 0.95)):
        ys = [float([r for r in rows if r["name"] == n and float(r["level"]) == lv][0]["coverage"]) for n in names]
        ax.bar(np.arange(3) + (i - 1) * w, ys, w, color=[s["fill2"], s["fill"], "#b9d9b0"][i] if mode == "color" else ["#ddd", "#999", "#444"][i], edgecolor="black", lw=0.6,
               label=f"명목 {int(lv*100)}%")
        ax.plot([-0.5 + 0 + (i - 1) * w + 0.5 - w / 2, 2 + (i - 1) * w + w / 2], [lv, lv], color=s["truth"], lw=0.8, ls="--") if False else None
    for i, lv in enumerate((0.5, 0.8, 0.95)):
        ax.axhline(lv, color=s["gray"], lw=0.6, ls=":")
    ax.set_xticks(range(3)); ax.set_xticklabels(labs, fontsize=8.5)
    ax.set_ylabel("참 위치가 영역 안에 든 비율"); ax.set_ylim(0, 1.05)
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.13))
    return save(fig, "ch12", "fig12-6-poolcal", mode)


def tables():
    os.makedirs(os.path.join(ROOT, "..", "표"), exist_ok=True)
    iy, ix = idx_of(G, W.truth)
    pool = pooled_all()
    rows = []
    for nm, p in list(P.items()) + [("T8 교차검증(로그 풀링)", pool)]:
        cx, cy = G.centroid(p)
        hp = t3.hpd_mask(p, 0.95)
        rows.append([nm, f"{cx:.1f}", f"{cy:.1f}", f"{np.hypot(cx-W.truth[0], cy-W.truth[1]):.1f}", f"{G.area(hp):.0f}", "예" if hp[iy, ix] else "아니오"])
    path = os.path.join(ROOT, "..", "표", "ch12-summary.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["기법", "중심 x(km)", "중심 y(km)", "참값과의 거리(km)", "95% 영역 면적(km2)", "참값 포함"])
        w.writerows(rows)
    return rows


if __name__ == "__main__":
    for mode in ("color", "bw"):
        for f in (fig9_1, fig9_2, fig10_1, fig11_1, fig12_1, fig12_2, fig12_3, fig12_4, fig12_5) + ((fig12_6,) if os.path.exists(os.path.join(ROOT, 'data', 'ch12-pool-calibration.csv')) else ()):
            f(mode)
    rows = tables()
    json.dump(dict(rows=rows, K=ctx["K"], loo_shift=[float(x) for x in ctx["loo_shift"]], M=ctx["M"].tolist(),
                   pl_area=ctx["pl_area"], days_obs=W.days_obs, t_true=float(ctx["t_true"]), lam=ctx["lam"], loocv2=float(ctx["loocv2"]),
                   btw={k: float(v) for k, v in ctx["btw"].items()}, bad=ctx.get("bad")),
              open(os.path.join(ROOT, "data", "ch12-numbers.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in rows:
        print(r)
