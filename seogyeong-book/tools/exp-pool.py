"""exp-pool.py - 12장 보정 실험: 기법별 영역과 합친 영역의 실제 적중률 (합성 세계 N개)"""
import sys, os, csv
sys.path.insert(0, ".")
import numpy as np
from toypost import *
from placeloc import t3_bayes as t3, t8_cross as t8

N = int(sys.argv[1]) if len(sys.argv) > 1 else 150
SCEN = sys.argv[2] if len(sys.argv) > 2 else "ok"           # ok: 단위 길이가 가정 범위 안 / bias: 참 단위가 범위(0.36~0.48) 밖 0.54
LEV = [0.5, 0.8, 0.95]
G = make_grid()
W_DEP = [1 / 3, 1, 1 / 3, 1, 1 / 3, 1, 1]      # T1·T3·T5는 같은 거리 서술 4건을 공유 → 가중 1/3
acc = {}
area = {}
def add(name, p, iy, ix):
    for l in LEV:
        acc.setdefault((name, l), 0)
        acc[(name, l)] += bool(t3.hpd_mask(p, l)[iy, ix])
    area.setdefault(name, []).append(G.area(t3.hpd_mask(p, 0.95)))
for s in range(N):
    W = World(seed=5000 + s, random_truth="river", u_true=(0.54 if SCEN == "bias" else U_TRUE))
    P, ctx = toy_posteriors(W, seed=s)
    PL = list(P.values())
    iy, ix = idx_of(G, W.truth)
    for nm, p in P.items():
        add(nm, p, iy, ix)
    add("풀링-독립가정(가중 1)", t8.log_pool(PL), iy, ix)
    add("풀링-공유증거 보정(T1·T3·T5 가중 1/3)", t8.log_pool(PL, W_DEP), iy, ix)
    add("선형 풀링(평균)", t8.linear_pool(PL), iy, ix)
os.makedirs("../그림/data", exist_ok=True)
with open(("../그림/data/ch12-pool-calibration.csv" if SCEN == "ok" else "../그림/data/ch12-pool-calibration-bias.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["name", "level", "coverage", "n_worlds", "median_area95_km2"])
    for (nm, l), v in acc.items():
        w.writerow([nm, l, f"{v/N:.4f}", N, f"{np.median(area[nm]):.0f}"])
print("saved", N)
