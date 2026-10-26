"""mk-tables.py - 수치에서 만들어지는 표(CSV)를 생성한다. 빌드 전에 실행."""
import sys, os, csv, json
sys.path.insert(0, ".")
import numpy as np
from toyworld import *
from toypost import *
from placeloc import t2_georef as t2
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
T = os.path.join(ROOT, "표")
N = json.load(open(os.path.join(ROOT, "그림", "data", "numbers.json"), encoding="utf-8"))
W = World(seed=7)

def w(name, rows):
    with open(os.path.join(T, name + ".csv"), "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)

# ch06
rows = [["변환 방식", "정칙화 λ", "하나 빼고 맞춘 잔차 RMSE (km)"]]
rows.append(["닮음변환", "-", f"{t2.loocv(t2.fit_similarity, W.ctrl_src, W.ctrl_dst)[1]:.1f}"])
rows.append(["아핀변환", "-", f"{t2.loocv(t2.fit_affine, W.ctrl_src, W.ctrl_dst)[1]:.1f}"])
for lam in (0.0, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0):
    rows.append(["박판스플라인", str(lam), f"{t2.loocv(t2.fit_tps, W.ctrl_src, W.ctrl_dst, lam=lam)[1]:.1f}"])
w("ch06-loocv", rows)
# ch07
cal = list(csv.DictReader(open(os.path.join(ROOT, "그림", "data", "ch07-calibration.csv"), encoding="utf-8")))
nm = {"shared": "단위 길이 공유(옳은 모형)", "indep": "증거마다 단위를 따로 뽑음", "biased": "단위를 +15%로 고정(틀린 모형)"}
rows = [["모형", "50% 영역", "80% 영역", "95% 영역", "95% 영역 면적 중앙값 (km2)"]]
for m in ("shared", "indep", "biased"):
    g = lambda lv: [float(x["coverage"]) for x in cal if x["mode"] == m and abs(float(x["level"]) - lv) < 1e-9][0]
    area = [x["median_area95_km2"] for x in cal if x["mode"] == m][0]
    rows.append([nm[m], f"{g(0.5):.3f}", f"{g(0.8):.3f}", f"{g(0.95):.3f}", f"{float(area):,.0f}"])
w("ch07-calib", rows)
# ch10
c = N["ch10"]
w("ch10-cand", [["후보", "총점", "이름", "시기", "공간"],
                [c["id1"] + " 西津(참)", f"{c['s1']:.2f}", f"{c['n1']:.2f}", f"{c['t1']:.2f}", f"{c['p1']:.2f}"],
                [c["id2"] + " 西津(동명이지)", f"{c['s2']:.2f}", f"{c['n2']:.2f}", f"{c['t2']:.2f}", f"{c['p2']:.2f}"],
                [c["id3"] + " 東津", f"{c['s3']:.2f}", "-", "-", "-"]])
print("tables ok")

# ch12 보정표(정상/편향 시나리오)
def pool_table(fn, out):
    p = os.path.join(ROOT, "그림", "data", fn)
    if not os.path.exists(p):
        return False
    rr = list(csv.DictReader(open(p, encoding="utf-8")))
    names = []
    for r in rr:
        if r["name"] not in names:
            names.append(r["name"])
    rows = [["방법", "50% 영역", "80% 영역", "95% 영역", "95% 영역 면적 중앙값 (km2)"]]
    for n in names:
        g = lambda lv: [float(x["coverage"]) for x in rr if x["name"] == n and abs(float(x["level"]) - lv) < 1e-9][0]
        a = [float(x["median_area95_km2"]) for x in rr if x["name"] == n][0]
        rows.append([n, f"{g(0.5):.2f}", f"{g(0.8):.2f}", f"{g(0.95):.2f}", f"{a:,.0f}"])
    w(out, rows)
    return True
pool_table("ch12-pool-calibration.csv", "ch12-calib")
print("bias table:", pool_table("ch12-pool-calibration-bias.csv", "ch12-calib-bias"))

# ch13 형식 견본(12장 결과에서)
_rows = list(csv.reader(open(os.path.join(T, "ch12-summary.csv"), encoding="utf-8")))
w("ch13-form", [["기법", "중심 x (km)", "중심 y (km)", "95% 영역 면적 (km2)", "서경 결과"]] + [[r[0], r[1], r[2], r[4], "미산출"] for r in _rows[1:]])
