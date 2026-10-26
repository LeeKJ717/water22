"""toypost.py - 맛보기 세계에서 7가지 기법이 각각 내놓는 사후분포(또는 영역) 지도를 만든다.
8번째 기법(교차검증)은 이 지도들을 합치는 단계이므로 별도(t8_cross)로 계산한다."""
import numpy as np
from scipy.ndimage import gaussian_filter
from placeloc import t1_csp as t1, t2_georef as t2, t3_bayes as t3, t4_lcp as t4, t5_graph as t5, t6_gazetteer as t6, t7_toponym as t7
from toyworld import *

NAMES = ["T1 제약·구간", "T2 기하 보간", "T3 베이즈", "T4 최소비용", "T5 그래프", "T6 지명 정합", "T7 언어학"]


def idx_of(grid, p):
    return int(np.argmin(np.abs(grid.ys - p[1]))), int(np.argmin(np.abs(grid.xs - p[0])))


def cloud_to_map(grid, pts, sigma_cells=2.0):
    H, _, _ = np.histogram2d(pts[:, 1], pts[:, 0], bins=[np.r_[grid.ys - grid.step / 2, grid.ys[-1] + grid.step / 2],
                                                           np.r_[grid.xs - grid.step / 2, grid.xs[-1] + grid.step / 2]])
    H = gaussian_filter(H, sigma_cells) + 1e-12
    return H / H.sum()


def toy_gazetteer(W, n=160, seed=11):
    """가상 지명 사전: 津(나루)은 강 가까이, 山은 능선 가까이, 城은 어디서나."""
    rng = np.random.default_rng(seed)
    G = W.grid
    from scipy.spatial import cKDTree
    dense = [W.river[0]]
    for a, b in zip(W.river[:-1], W.river[1:]):
        for t in np.linspace(0, 1, 40)[1:]:
            dense.append(a + (b - a) * t)
    tree = cKDTree(np.array(dense))
    rows = []
    for i in range(n):
        x, y = rng.uniform(0, 400, 2)
        dr, _ = tree.query([x, y])
        dm = abs(x - 170)
        p_jin = 0.65 * np.exp(-dr / 40.0)
        p_san = 0.55 * np.exp(-dm / 30.0)
        u = rng.random()
        suf = "津" if u < p_jin else ("山" if u < p_jin + p_san else "城")
        rows.append((f"가{i:03d}{suf}", x, y))
    return rows


def toy_posteriors(W, seed=0):
    rng = np.random.default_rng(seed)
    G = W.grid
    iy, ix = idx_of(G, W.truth)
    ctx = {}
    uns = np.linspace(*U_BAND, 15)
    # T1: 구간 연산 + 방위 + 강 근접
    masks = []
    for k, (x, y) in W.refs.items():
        masks.append(t1.c_distance(G, x, y, band_from_li(W.dist_obs[k])))
    masks.append(t1.c_near_polyline(G, W.river, W.near_river_km))
    r1 = t1.solve(masks)
    m1 = r1["feasible"] if r1["consistent"] else r1["best"]
    p1 = (m1 / m1.sum()).astype(float)
    ctx["mask1"] = m1
    # T3: 베이즈 (거리 우도 + 하천 근접 우도)
    prior = t3.prior_uniform(G)
    near = t1.c_near_polyline(G, W.river, W.near_river_km).astype(float) * 0.97 + 0.03
    dl = [(*W.refs[k], W.dist_obs[k]) for k in W.refs]
    p3 = t3.posterior_shared_unit(G, prior, dl, REL_SIGMA, uns, extra=near)
    # T2: 지도 기준점 부트스트랩 (TPS, lam 선택은 LOOCV로)
    best_lam, best_e = None, 1e9
    for lam in (0.0, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0):
        _, e = t2.loocv(t2.fit_tps, W.ctrl_src, W.ctrl_dst, lam=lam)
        if e < best_e:
            best_lam, best_e = lam, e
    cloud2 = t2.bootstrap_target(t2.fit_tps, W.ctrl_src, W.ctrl_dst, W.target_src, n=400, seed=seed, lam=best_lam)
    p2 = cloud_to_map(G, cloud2, 2.0)
    ctx.update(cloud2=cloud2, lam=best_lam, loocv2=best_e)
    # T4: 이동시간 서술 (갑성에서 '며칠 길')
    dem = mountain_dem(G)
    Gr = t4.build_graph(dem, G.step)
    src = idx_of(G, W.refs["갑성"])
    tt = t4.travel_time(Gr, G.shape, src)
    t_true = tt[iy, ix]
    W.days_obs = float(np.round(t_true / 8.0 * np.exp(rng.normal(0, 0.10)), 1))
    mu = np.log(W.days_obs * 8.0)
    tt_ = np.maximum(tt, 1e-3)
    L4 = np.exp(-0.5 * ((np.log(tt_) - mu) / 0.2) ** 2) / tt_
    p4 = t3.posterior(prior, [L4, near])
    ctx.update(tt=tt, dem=dem, t_true=t_true, src=src)
    # T5: 지명 그래프 앵커 MDS + 간선 잭나이프
    edges = []
    for k, (x, y) in W.refs.items():
        b = band_from_li(W.dist_obs[k])
        edges.append((k, "목표", b.lo, b.hi, 1.0))
    Gg = t5.build_graph(edges)
    est, _ = t5.anchored_mds(Gg, dict(W.refs), seed=2)
    jk = t5.jackknife_edges(Gg, dict(W.refs), "목표", n_drop=1, seed=3, reps=60)
    # 잭나이프 표본에 개별 간선 구간 내부 임의 위치 지터를 더해 퍼짐을 만든다
    cloud5 = np.vstack([jk + rng.normal(0, 8.0, jk.shape) for _ in range(20)]) if len(jk) else np.array([est["목표"]])
    p5 = cloud_to_map(G, cloud5, 2.5)
    ctx.update(est5=est["목표"], cloud5=cloud5)
    # T6: 지명 사전 정합 - 동명이지 둘 중 하나를 본문 힌트(대략 위치)로 고른다
    R = t6.Record
    g_true = R("g1", "西津", 900, 1500, W.truth[0] + rng.normal(0, 6), W.truth[1] + rng.normal(0, 6), 8.0, "나루")
    g_decoy = R("g2", "西津", 900, 1500, 90.0, 150.0, 8.0, "나루")
    g_other = R("g3", "東津", 900, 1500, 320.0, 250.0, 8.0, "나루")
    hint = (W.truth[0] + rng.normal(0, 40), W.truth[1] + rng.normal(0, 40))
    m = t6.Mention("m", "西津", 1100, 1100, hint_xy=hint, hint_sigma_km=90.0)
    al = t6.align([m], [g_true, g_decoy, g_other])
    rec = al["m"][0]
    p6 = np.exp(-0.5 * ((G.X - rec.x) ** 2 + (G.Y - rec.y) ** 2) / (rec.sigma_km + 10.0) ** 2)
    p6 = p6 / p6.sum()
    ctx.update(gaz=[g_true, g_decoy, g_other], mention=m, aligned=rec, cand6=t6.candidates(m, [g_true, g_decoy, g_other]))
    # T7: 형태소 공간분포 (西津의 津)
    rows = toy_gazetteer(W)
    L7 = t7.location_likelihood(G, rows, ["津"], bw_km=45.0, alpha=1.0)
    p7 = t3.posterior(prior, [L7])
    ctx.update(rows7=rows, L7=L7)
    return dict(zip(NAMES, [p1, p2, p3, p4, p5, p6, p7])), ctx
