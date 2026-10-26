"""test-placeloc.py - 8기법 라이브러리 검산(assert). 실행: python3 test-placeloc.py"""
import numpy as np, sys
sys.path.insert(0, ".")
from placeloc import geo, t1_csp as t1, t2_georef as t2, t3_bayes as t3, t4_lcp as t4, t5_graph as t5, t6_gazetteer as t6, t7_toponym as t7, t8_cross as t8
from toyworld import *

W = World(seed=7)
G = W.grid

# --- geo ---
fr = geo.Frame(125.0, 38.0)
x, y = fr.to_xy(127.0, 39.0)
lo, la = fr.to_lonlat(x, y)
assert abs(lo - 127.0) < 1e-9 and abs(la - 39.0) < 1e-9, "방위등거리 왕복"
assert abs(np.hypot(x, y) - geo.haversine_km(125, 38, 127, 39)) < 1e-6, "중심 기준 거리 보존"

# --- 기법 1 ---
a = Interval(10, 12) * Interval(0.9, 1.1)
assert abs(a.lo - 9.0) < 1e-9 and abs(a.hi - 13.2) < 1e-9
masks = []
sizes = []
for k, (x, y) in W.refs.items():
    masks.append(t1.c_distance(G, x, y, band_from_li(W.dist_obs[k])))
    r = t1.solve(masks)
    sizes.append(G.area(r["feasible"]))
assert all(s2 <= s1 + 1e-9 for s1, s2 in zip(sizes, sizes[1:])), "제약을 더하면 영역은 줄어야 함"
ix = int(np.argmin(np.abs(G.xs - TRUTH[0]))); iy = int(np.argmin(np.abs(G.ys - TRUTH[1])))
assert r["feasible"][iy, ix], "참 위치가 가능 영역에 있어야 함"
bad = t1.c_distance(G, *W.refs["갑성"], Interval(10, 20))        # 일부러 모순 증거
assert not t1.solve(masks + [bad])["consistent"], "모순 증거는 공집합을 만들어야 함"
# 호 일관성
dA = np.zeros(G.shape, bool); dA[iy, ix] = True
dom = {"A": np.ones(G.shape, bool), "B": dA}
out = t1.arc_consistency(dom, [("A", "B", Interval(40, 44))], G)
assert out["A"].sum() > 0 and out["A"].sum() < G.shape[0] * G.shape[1], "호 일관성 가지치기"

# --- 기법 2 ---
src, dst = W.ctrl_src, W.ctrl_dst
res_s, e_s = t2.loocv(t2.fit_similarity, src, dst)
res_a, e_a = t2.loocv(t2.fit_affine, src, dst)
res_t, e_t = t2.loocv(t2.fit_tps, src, dst, lam=0.01)
assert e_t < e_a < e_s, f"비선형 뒤틀림 자료에서는 TPS<아핀<닮음 이어야 함 ({e_t:.1f},{e_a:.1f},{e_s:.1f})"
f = t2.fit_tps(src, dst, lam=0.0)
assert np.allclose(f(src), dst, atol=1e-5), "정칙화 0인 TPS는 기준점을 정확히 재현"

# --- 기법 3 ---
prior = t3.prior_uniform(G)
liks = [t3.lik_distance(G, *W.refs[k], W.dist_obs[k], REL_SIGMA, unit_samples=np.linspace(*U_BAND, 15)) for k in W.refs]
post = t3.posterior(prior, liks)
assert abs(post.sum() - 1) < 1e-9
assert t3.hpd_mask(post, 0.95)[iy, ix], "참 위치가 95% HPD 안"
assert t3.hpd_mask(post, 0.5).sum() < t3.hpd_mask(post, 0.95).sum()
lp = lambda p: (np.log(post[min(max(int(round(p[1] / G.step)), 0), 100), min(max(int(round(p[0] / G.step)), 0), 100)] + 1e-300))
chain, acc = t3.metropolis(lp, W.truth, n=15000, step=6.0, seed=1)
mean_grid = np.array(G.centroid(post))
assert np.hypot(*(chain[3000:].mean(0) - mean_grid)) < 12.0, "메트로폴리스 평균 ≈ 격자 평균"

# 보정 검사: 단위를 공유하는 올바른 모형은 95% 영역이 실제로 약 95% 적중해야 함
hit = 0; nw = 120
for s_ in range(nw):
    w_ = World(seed=1000 + s_, random_truth=True)
    dl_ = [(*w_.refs[k], w_.dist_obs[k]) for k in w_.refs]
    po_ = t3.posterior_shared_unit(G, t3.prior_uniform(G), dl_, REL_SIGMA, np.linspace(*U_BAND, 15))
    jy = int(np.argmin(np.abs(G.ys - w_.truth[1]))); jx = int(np.argmin(np.abs(G.xs - w_.truth[0])))
    hit += bool(t3.hpd_mask(po_, 0.95)[jy, jx])
assert 0.88 <= hit / nw <= 1.0, f"95% 영역 적중률 {hit/nw:.3f}"

# --- 기법 4 ---
dem = mountain_dem(G)
Gr = t4.build_graph(dem, G.step)
t = t4.travel_time(Gr, G.shape, (iy, ix))
assert t[iy, ix] == 0 and np.isfinite(t).all()
flat_t = np.hypot(G.X - G.xs[ix], G.Y - G.ys[iy]) / 6.0
assert (t >= flat_t - 1e-6).all(), "어떤 칸도 평지 최고속도보다 빨리 갈 수 없음"
assert abs(t4.tobler_speed_kmh(-0.05) - 6.0) < 1e-9
t_pass = t4.travel_time(Gr, G.shape, (iy, 10))[iy, 90]
assert t_pass > 0

# --- 기법 5 ---
edges = [("갑성", "목표", 190, 230, 1), ("을진", "목표", 150, 190, 1), ("병포", "목표", 190, 240, 1), ("정령", "목표", 150, 200, 1)]
Gg = t5.build_graph(edges)
anc = {k: v for k, v in W.refs.items()}
est, cost = t5.anchored_mds(Gg, anc, seed=3)
assert "목표" in est and np.hypot(*(np.array(est["목표"]) - TRUTH)) < 60, "앵커 MDS가 목표를 대략 복원"

# --- 기법 6 ---
R = t6.Record
gaz = [R("g1", "西京", 918, 1392, 100, 200, 5, "도성"), R("g2", "西京", 907, 1125, 300, 50, 5, "도성"), R("g3", "西都", 918, 1392, 100, 200, 5, "도성")]
m = t6.Mention("m1", "西京", 1100, 1100)
assert len(t6.ambiguity("西京", 1100, gaz)) == 2, "같은 시기 같은 이름 두 곳"
m2 = t6.Mention("m2", "西京", 1100, 1100, hint_xy=(110, 190), hint_sigma_km=50)
al = t6.align([m2], gaz)
assert al["m2"][0].rid == "g1", "공간 힌트가 동명이지를 가름"

# --- 기법 7 ---
rows = [("買忽", 50, 50)] * 0 + [(f"{n}{s}", x, y) for n, s, x, y in [("a", "忽", 60, 80), ("b", "忽", 80, 60), ("c", "忽", 70, 90), ("d", "達", 300, 300), ("e", "達", 320, 280), ("f", "忽", 90, 70), ("g", "達", 310, 320)]]
L = t7.location_likelihood(G, rows, ["忽"], bw_km=40.0)
assert L[int(80 / 4), int(80 / 4)] > L[int(300 / 4), int(300 / 4)] * 3, "忽 지명은 忽 밀집 지역에서 우도가 높음"
cm = t7.learn_char_map([("買忽", "水城"), ("買伊", "水河")])
assert cm["買"][0][0] == "水"

# --- 기법 8 ---
p1 = t3.posterior(prior, liks[:2]); p2 = t3.posterior(prior, liks[2:])
pool = t8.log_pool([p1, p2])
assert abs(pool.sum() - 1) < 1e-9
assert t3.hpd_mask(pool, 0.95).sum() <= min(t3.hpd_mask(p1, 0.95).sum(), t3.hpd_mask(p2, 0.95).sum()), "풀링하면 영역이 줄어듦"
M = t8.conflict_matrix([p1, p2, post])
assert (np.diag(M) == 1).all() and (M <= 1 + 1e-9).all()
mk = [post > post.max() * 0.2, p1 > p1.max() * 0.2]
pl, K = t8.dempster(mk, [0.8, 0.7])
assert 0 <= K < 1 and pl.max() > 0
mk2 = [mk[0], ~mk[0]]
pl2, K2 = t8.dempster(mk2, [0.9, 0.9])
assert K2 > 0.5, "정반대 영역이면 충돌량이 커야 함"
print("모든 검사 통과")
