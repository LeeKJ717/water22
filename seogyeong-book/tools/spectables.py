"""지도 아래 산맥·강 제원표 삽입 (idempotent). 값은 data/*.csv의 출처 확인 값만 사용, 빈칸은 '-'."""
import csv, re
FIGS = {"02-prior": None, "16-nwkorea": "서북", "17-liao": "요하", "18-shandong": "산동", "19-manchuria": "만주"}
def rd(p): return list(csv.DictReader(open(p, encoding="utf-8-sig")))
M, R = rd("data/mountains-v1.csv"), rd("data/rivers-v1.csv")
def f(x): return x if x else "-"
def fmt(v):
    try:
        x = float(v); return f"{x:,.0f}" if x == int(x) else f"{x:,.1f}"
    except: return "-"
def rivnote(n):
    m = re.search(r"길이:[^;]*", n); return m.group(0).replace("길이: ", "").replace("위키", "위키백과") if m else ""
def tables(key, tag):
    ms = [r for r in M if key is None or key in r["frame"]]
    rs = [r for r in R if key is None or key in r["frame"]]
    o = [f"<!--spec-{tag}-->", ""]
    o += [f"Table: 지도에 표시한 산맥·산의 제원 ({key or '전체'}). 높이와 길이는 위키백과 값이며 DEM 실측이 아니다. 빈칸은 출처에 없는 값이다.", "",
          "| 산맥·산 | 최고점 | 높이 (m) | 길이 (km) | 위치 |", "|---|---|---|---|---|"]
    for r in ms: o.append(f"| {r['range_ko']} | {f(r['highest_peak'])} | {fmt(r['height_m'])} | {fmt(r['length_km'])} | {f(r['location'])} |")
    o += ["", f"Table: 지도에 표시한 강의 제원 ({key or '전체'}). 길이와 유역 면적은 위키백과 값이며 출처마다 다르면 비고에 적었다.", "",
          "| 강 | 길이 (km) | 유역 면적 (km²) | 발원 | 하구 | 비고 |", "|---|---|---|---|---|---|"]
    for r in rs: o.append(f"| {r['river_ko']} | {fmt(r['length_km'])} | {fmt(r['basin_km2'])} | {f(r['source_place'])[:40]} | {f(r['mouth_place'])[:40]} | {rivnote(r['note'])} |")
    o += ["", f"<!--/spec-{tag}-->", ""]
    return "\n".join(o)
for ch, key in FIGS.items():
    p = f"원고/{ch}.md"; t = open(p, encoding="utf-8").read()
    t = re.sub(r"<!--spec-[^>]*-->.*?<!--/spec-[^>]*-->\n*", "", t, flags=re.S)
    lines = t.split("\n")
    i = next(k for k, l in enumerate(lines) if l.startswith("@@fig") and "regions" in l or l.startswith("@@fig") and key and ("fig" in l and ch.split("-")[0] in l))
    lines.insert(i + 1, "\n" + tables(key, ch.split("-")[0]))
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    print(ch, "ok")
