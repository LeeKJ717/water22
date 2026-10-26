"""exp-slack.py - 5장 실험: 서술 오차 여유폭에 따른 가능 영역의 크기와 참 위치 보존율 (합성 세계 300개)"""
import sys, csv, json
sys.path.insert(0, ".")
import numpy as np
from toyworld import *
from toypost import idx_of
from placeloc import t1_csp as t1

G = make_grid()
NW = 300
SL = (0.05, 0.10, 0.15, 0.25, 0.40)
hit = {s: 0 for s in SL}; area = {s: [] for s in SL}; empty = {s: 0 for s in SL}
for k in range(NW):
    w = World(seed=3000 + k, random_truth="river")
    iy, ix = idx_of(G, w.truth)
    near = t1.c_near_polyline(G, w.river, w.near_river_km)
    for s in SL:
        ms = [t1.c_distance(G, x, y, band_from_li(w.dist_obs[n], s)) for n, (x, y) in w.refs.items()] + [near]
        m = np.all(ms, axis=0)
        hit[s] += bool(m[iy, ix]); empty[s] += (not m.any())
        if m.any():
            area[s].append(G.area(m))
with open("../표/ch05-slack.csv", "w", encoding="utf-8", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["서술 오차 여유폭", "참 위치를 보존한 세계 비율", "해가 없는(공집합) 세계 비율", "가능 영역 면적 중앙값 (km2)"])
    for s in SL:
        wr.writerow([f"{s:.2f}", f"{hit[s]/NW:.3f}", f"{empty[s]/NW:.3f}", f"{np.median(area[s]):.0f}" if area[s] else "-"])
json.dump({f"s{int(s*100):02d}": dict(hit=hit[s] / NW, empty=empty[s] / NW, area=float(np.median(area[s])) if area[s] else None) for s in SL},
          open("../그림/data/ch05-slack.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(open("../표/ch05-slack.csv", encoding="utf-8").read())
