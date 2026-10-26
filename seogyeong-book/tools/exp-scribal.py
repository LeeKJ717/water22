"""exp-scribal.py - 3장 실험: 필사·판각 오류(거리 수치가 틀린 서술)가 섞였을 때 기법의 견고함"""
import sys, os, csv
sys.path.insert(0, ".")
import numpy as np
from toyworld import *
from toypost import idx_of
from placeloc import t1_csp as t1, t3_bayes as t3

G = make_grid()
NW = 300
P_ERR = 0.10
rng = np.random.default_rng(99)
res = {k: dict(hit=0, area=[], n=0) for k in ("csp", "bayes", "robust")}
n_err_worlds = 0
sub = {k: dict(hit=0, n=0) for k in ("csp", "bayes", "robust")}      # 오류가 실제 섞인 세계만
for s in range(NW):
    w = World(seed=2000 + s, random_truth=True)
    obs = dict(w.dist_obs)
    corrupted = False
    for k in obs:
        if rng.random() < P_ERR:
            f = rng.choice([rng.uniform(0.3, 0.7), rng.uniform(1.4, 2.5)])
            obs[k] = float(np.round(obs[k] * f, -1)); corrupted = True
    n_err_worlds += corrupted
    iy, ix = idx_of(G, w.truth)
    dl = [(*w.refs[k], obs[k]) for k in w.refs]
    masks = [t1.c_distance(G, x, y, band_from_li(d)) for x, y, d in dl]
    r = t1.solve(masks)
    csp_mask = r["feasible"]                        # 경성 제약: 공집합이면 해 없음
    out = {
        "csp": (bool(csp_mask[iy, ix]), G.area(csp_mask) if csp_mask.any() else np.nan),
    }
    prior = t3.prior_uniform(G)
    pb = t3.posterior_shared_unit(G, prior, dl, REL_SIGMA, np.linspace(*U_BAND, 15))
    pr = t3.posterior_shared_unit_robust(G, prior, dl, REL_SIGMA, np.linspace(*U_BAND, 15), eps=0.10)
    out["bayes"] = (bool(t3.hpd_mask(pb, 0.95)[iy, ix]), G.area(t3.hpd_mask(pb, 0.95)))
    out["robust"] = (bool(t3.hpd_mask(pr, 0.95)[iy, ix]), G.area(t3.hpd_mask(pr, 0.95)))
    for k, (hit, area) in out.items():
        res[k]["hit"] += hit; res[k]["n"] += 1
        if not np.isnan(area): res[k]["area"].append(area)
        if corrupted:
            sub[k]["hit"] += hit; sub[k]["n"] += 1
os.makedirs("../표", exist_ok=True)
names = {"csp": "경성 제약 (구간 교집합)", "bayes": "베이즈 (오류 없음 가정)", "robust": "베이즈 (오류 허용 ε=0.10)"}
with open("../표/ch03-scribal.csv", "w", encoding="utf-8", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["방법", "전체 세계에서 참 위치 포함", "오류가 섞인 세계에서 포함", "영역 면적 중앙값 (km2)"])
    for k in ("csp", "bayes", "robust"):
        wr.writerow([names[k], f"{res[k]['hit']/res[k]['n']:.3f}", f"{sub[k]['hit']/max(1,sub[k]['n']):.3f}",
                     f"{np.median(res[k]['area']):.0f}" if res[k]["area"] else "-"])
import json
json.dump(dict(nw=NW, p_err=P_ERR, n_err_worlds=int(n_err_worlds),
               csp_all=res["csp"]["hit"] / NW, csp_err=sub["csp"]["hit"] / max(1, sub["csp"]["n"]),
               bayes_all=res["bayes"]["hit"] / NW, bayes_err=sub["bayes"]["hit"] / max(1, sub["bayes"]["n"]),
               robust_all=res["robust"]["hit"] / NW, robust_err=sub["robust"]["hit"] / max(1, sub["robust"]["n"]),
               csp_area=float(np.median(res["csp"]["area"])) if res["csp"]["area"] else None,
               bayes_area=float(np.median(res["bayes"]["area"])), robust_area=float(np.median(res["robust"]["area"]))),
          open("../그림/data/ch03-scribal.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", n_err_worlds, "of", NW, "worlds corrupted")
