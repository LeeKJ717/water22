"""calc-numbers.py - 원고 본문에 들어가는 수치를 계산해 numbers.json으로 저장한다(본문에는 {{키}}로 참조)."""
import sys, os, csv, json
sys.path.insert(0, ".")
import numpy as np
from toyworld import *
from toypost import *
from placeloc import t1_csp as t1, t2_georef as t2, t3_bayes as t3, t4_lcp as t4, t5_graph as t5, t8_cross as t8

W = World(seed=7)
G = W.grid
P, ctx = toy_posteriors(W)
iy, ix = idx_of(G, W.truth)
N = {}
N["toy"] = dict(truth_x=float(W.truth[0]), truth_y=float(W.truth[1]), u_true=U_TRUE, u_lo=U_BAND[0], u_hi=U_BAND[1],
                rel_sigma=REL_SIGMA, grid_step=G.step, ncells=int(G.X.size),
                d_gap=W.dist_obs["갑성"], d_eul=W.dist_obs["을진"], d_byeong=W.dist_obs["병포"], d_jeong=W.dist_obs["정령"],
                dtrue_gap=float(np.hypot(*(np.array(W.refs["갑성"]) - W.truth))))
# 5장
masks = []; areas = []
for k, (x, y) in W.refs.items():
    masks.append(t1.c_distance(G, x, y, band_from_li(W.dist_obs[k]))); areas.append(G.area(np.all(masks, axis=0)))
nr = t1.c_near_polyline(G, W.river, W.near_river_km); masks.append(nr); areas.append(G.area(np.all(masks, axis=0)))
b = band_from_li(W.dist_obs["갑성"])
bad = t1.c_distance(G, *W.refs["갑성"], Interval(40, 70))
r = t1.solve(masks[:4] + [bad])
N["ch05"] = dict(a1=areas[0], a2=areas[1], a3=areas[2], a4=areas[3], a5=areas[4], band_lo=b.lo, band_hi=b.hi, band_w=b.width,
                 raw_lo=W.dist_obs["갑성"] * U_BAND[0], raw_hi=W.dist_obs["갑성"] * U_BAND[1],
                 bad_max_score=int(r["score"].max()), bad_area_best=G.area(r["best"]), near_km=W.near_river_km,
                 centroid_x=G.centroid(masks[0] & masks[1] & masks[2] & masks[3] & masks[4])[0],
                 centroid_y=G.centroid(masks[0] & masks[1] & masks[2] & masks[3] & masks[4])[1])
# 6장
src, dst = W.ctrl_src, W.ctrl_dst
_, es = t2.loocv(t2.fit_similarity, src, dst)
_, ea = t2.loocv(t2.fit_affine, src, dst)
lam_tab = {}
for lam in (0.0, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0):
    lam_tab[str(lam)] = t2.loocv(t2.fit_tps, src, dst, lam=lam)[1]
N["ch06"] = dict(n_ctrl=len(src), e_sim=es, e_aff=ea, e_tps0=lam_tab["0.0"], e_tps001=lam_tab["0.01"], e_tps1=lam_tab["1.0"],
                 target_err=float(np.hypot(*(np.array(ctx["cloud2"]).mean(0) - W.truth))),
                 cloud_sd=float(np.sqrt(np.cov(ctx["cloud2"].T).trace())), lam_best=ctx["lam"])
# 7장
rows = list(csv.DictReader(open("../그림/data/ch07-calibration.csv", encoding="utf-8")))
cal = {}
for m in ("shared", "indep", "biased"):
    for lv in ("0.5", "0.8", "0.95"):
        cal[f"{m}_{lv.replace('.', '')}"] = float([x for x in rows if x["mode"] == m and float(x["level"]) == float(lv)][0]["coverage"])
    cal[f"{m}_area"] = float([x for x in rows if x["mode"] == m][0]["median_area95_km2"])
post = P["T3 베이즈"]
sm = t3.summarize(G, post)
N["ch07"] = dict(cal, map_x=sm["map_xy"][0], map_y=sm["map_xy"][1], mean_x=sm["mean_xy"][0], mean_y=sm["mean_xy"][1],
                 hpd50=sm["hpd50_km2"], hpd95=sm["hpd95_km2"], err=float(np.hypot(sm["mean_xy"][0] - W.truth[0], sm["mean_xy"][1] - W.truth[1])),
                 nworlds=int(rows[0]["n_worlds"]))
# 8장
tt = ctx["tt"]
straight = float(np.hypot(*(np.array(W.refs["갑성"]) - W.truth)))
N["ch08"] = dict(t_true=float(ctx["t_true"]), days_obs=W.days_obs, straight_km=straight, straight_h=straight / 5.04,
                 tmax_flat=straight / 6.0, v0=float(t4.tobler_speed_kmh(0.0)), vmax=float(t4.tobler_speed_kmh(-0.05)),
                 v_up10=float(t4.tobler_speed_kmh(np.tan(np.radians(10)))), v_dn10=float(t4.tobler_speed_kmh(-np.tan(np.radians(10)))),
                 detour=float(ctx["t_true"]) / (straight / 5.04))
# 9장
est = ctx["est5"]
N["ch09"] = dict(est_x=est[0], est_y=est[1], est_err=float(np.hypot(est[0] - W.truth[0], est[1] - W.truth[1])),
                 cloud_sd=float(np.sqrt(np.cov(ctx["cloud5"].T).trace())))
# 10장
c6 = ctx["cand6"]
N["ch10"] = dict(s1=float(c6[0][0]), s2=float(c6[1][0]), s3=float(c6[2][0]), id1=c6[0][1].rid, id2=c6[1][1].rid, id3=c6[2][1].rid,
                 n1=c6[0][2][0], t1=c6[0][2][1], p1=c6[0][2][2], n2=c6[1][2][0], t2=c6[1][2][1], p2=c6[1][2][2])
# 11장
rows7 = ctx["rows7"]
n_jin = sum(1 for n, _, _ in rows7 if n.endswith("津")); n_san = sum(1 for n, _, _ in rows7 if n.endswith("山")); n_seong = len(rows7) - n_jin - n_san
L7 = ctx["L7"]
N["ch11"] = dict(n=len(rows7), n_jin=n_jin, n_san=n_san, n_seong=n_seong, lr_truth=float(L7[iy, ix]), lr_max=float(L7.max()), lr_min=float(L7.min()),
                 lr_mean=float(L7.mean()))
# 12장
d12 = json.load(open("../그림/data/ch12-numbers.json", encoding="utf-8"))
N["ch12"] = {k: d12[k] for k in ("K", "loo_shift", "pl_area", "bad")}
N["ch12"]["rows"] = d12["rows"]
for tag, fn in (("ok", "ch12-pool-calibration.csv"), ("bias", "ch12-pool-calibration-bias.csv")):
    p = os.path.join("../그림/data", fn)
    if os.path.exists(p):
        rr = list(csv.DictReader(open(p, encoding="utf-8")))
        for x in rr:
            key = f"{tag}_{x['name'].split('(')[0].replace('-', '').replace(' ', '')}_{str(x['level']).replace('.', '')}"
            N["ch12"][key] = float(x["coverage"])
            N["ch12"][f"{tag}_{x['name'].split('(')[0].replace('-', '').replace(' ', '')}_area"] = float(x["median_area95_km2"])
json.dump(N, open("../그림/data/numbers.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("numbers.json saved;", {k: len(v) for k, v in N.items()})

# ---- 추가 수치: 의존성 문제, 여유폭 민감도, 3장 실험 ----
N = json.load(open("../그림/data/numbers.json", encoding="utf-8"))
u_lo, u_hi = U_BAND
d1, d2 = W.dist_obs["갑성"], W.dist_obs["병포"]
N["dep"] = dict(naive_lo=d1 * u_lo - d2 * u_hi, naive_hi=d1 * u_hi - d2 * u_lo, true_lo=(d1 - d2) * u_lo, true_hi=(d1 - d2) * u_hi,
                diff_li=d1 - d2, d1=d1, d2=d2)
N["ch10"]["margin"] = N["ch10"]["s1"] - N["ch10"]["s2"]
N["slack"] = json.load(open("../그림/data/ch05-slack.json", encoding="utf-8"))
N["ch03"] = json.load(open("../그림/data/ch03-scribal.json", encoding="utf-8"))
json.dump(N, open("../그림/data/numbers.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("추가 수치 저장", rows)
