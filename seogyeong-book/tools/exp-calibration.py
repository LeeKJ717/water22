"""exp-calibration.py - 7장 보정 실험: 합성 세계 300개에서 신용 영역의 실제 적중률을 센다."""
import sys, os, csv
sys.path.insert(0, ".")
import numpy as np
from toyworld import *
from toypost import idx_of
from placeloc import t3_bayes as t3

G = make_grid()
LEVELS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
NW = 300
hits = {m: {l: 0 for l in LEVELS} for m in ("shared", "indep", "biased")}
areas = {m: [] for m in hits}
for s in range(NW):
    w = World(seed=1000 + s, random_truth=True)
    dl = [(*w.refs[k], w.dist_obs[k]) for k in w.refs]
    prior = t3.prior_uniform(G)
    posts = {
        "shared": t3.posterior_shared_unit(G, prior, dl, REL_SIGMA, np.linspace(*U_BAND, 15)),
        "indep": t3.posterior(prior, [t3.lik_distance(G, x, y, d, REL_SIGMA, unit_samples=np.linspace(*U_BAND, 15)) for x, y, d in dl]),
        "biased": t3.posterior_shared_unit(G, prior, dl, REL_SIGMA, np.array([U_TRUE * 1.15])),
    }
    iy, ix = idx_of(G, w.truth)
    for m, p in posts.items():
        for l in LEVELS:
            hits[m][l] += bool(t3.hpd_mask(p, l)[iy, ix])
        areas[m].append(G.area(t3.hpd_mask(p, 0.95)))
os.makedirs("../그림/data", exist_ok=True)
with open("../그림/data/ch07-calibration.csv", "w", encoding="utf-8", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["mode", "level", "coverage", "n_worlds", "median_area95_km2"])
    for m in hits:
        for l in LEVELS:
            wr.writerow([m, l, f"{hits[m][l]/NW:.4f}", NW, f"{np.median(areas[m]):.0f}"])
print("saved")
