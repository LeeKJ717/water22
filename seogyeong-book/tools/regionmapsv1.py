"""regionmapsv1.py - 4부 지역 지도(DEM 바탕판). 노트북(placeloc-db)에서 실행.
입력 : Desktop/notedb/placeloc-db/derived/dem900.npz (dembandsv1.py 출력), geo/ne_10m_land, lakes, rivers_lake_centerlines_scale_rank(.geojson)
출력 : derived/regionmaps/ch02/fig02-1-regions-{color,bw}.pdf, ch16..ch19/fig1N-1-*-{color,bw}.pdf  → 책 폴더 그림/ 아래에 같은 이름으로 덮어쓰면 DEM판이 된다.
규칙 : 폭 130 mm, 글자 8.5 pt 이상, 위도 코사인 보정, 하천·산맥(고도대+음영) 표시. 환경 변수 PLACELOC_BASE로 기본 폴더 변경 가능.
주의 : Natural Earth 하천에는 대동강 등 중소 하천이 빠져 있다. DEM 유로 추출(흐름 누적)은 다음 판에서 추가한다."""
import os, json, math, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource, ListedColormap, BoundaryNorm
from shapely.geometry import shape, box, Polygon, LineString

BASE = os.environ.get("PLACELOC_BASE", os.path.join(os.path.expanduser("~"), "Desktop", "notedb", "placeloc-db"))
GEO, DER = os.path.join(BASE, "geo"), os.path.join(BASE, "derived")
OUT = os.path.join(DER, "regionmaps")
for f in ("Malgun Gothic", "Noto Sans CJK KR", "NanumGothic", "AppleGothic"):
    plt.rcParams["font.family"] = f if any(f == x.name for x in matplotlib.font_manager.fontManager.ttflist) else plt.rcParams["font.family"]
plt.rcParams.update({"font.size": 8.5, "axes.unicode_minus": False, "pdf.fonttype": 42})
Z = np.load(os.path.join(DER, "dem900.npz")); DEM, LON0, LAT1, N = Z["dem"], float(Z["lon0"]), float(Z["lat1"]), int(Z["n"])
H, W = DEM.shape
LEV = [100, 300, 500, 800, 1200, 1700, 2200]
CC = ["#efe9d4", "#e0d3ac", "#cdb98a", "#b79c6c", "#9a7d52", "#7d6340", "#5f4a30"]
CB = ["#f4f4f4", "#e0e0e0", "#c8c8c8", "#b0b0b0", "#969696", "#7a7a7a", "#5a5a5a"]

def load(n):
    for cand in (n, n.replace("rivers_lake_centerlines_scale_rank", "rivers_lake_centerlines")):
        p = os.path.join(GEO, cand)
        if os.path.exists(p):
            return json.load(open(p, encoding="utf-8"))["features"]
    return []
LAKES = [shape(f["geometry"]) for f in load("ne_10m_lakes.geojson")]
RIV = [({k.lower(): v for k, v in f["properties"].items()}, shape(f["geometry"])) for f in load("ne_10m_rivers_lake_centerlines_scale_rank.geojson")]
RKO = {"Yalu": "압록강", "Tumen": "두만강", "Liao": "요하", "Xiliao": "서요하", "Songhua": "송화강", "Huang": "황하", "Han": "한강", "Daling": "대릉하",
       "Nen": "눈강", "Amur": "흑룡강", "Hai": "해하", "Luan": "난하", "Namhan": "남한강", "Nakdong": "낙동강", "Di’er Songhua": "제2송화강", "Yongding": "영정하"}
PEAKS = [("백두산", 128.08, 42.00), ("묘향산", 126.30, 40.00), ("설악산", 128.47, 38.14), ("지리산", 127.73, 35.34), ("한라산", 126.53, 33.36),
         ("오대산", 113.57, 39.09), ("태산", 117.10, 36.25), ("의무려산", 121.72, 41.63)]
FR = {"서북": (124.0, 128.6, 37.4, 41.6), "요하": (119.5, 125.5, 39.4, 43.6), "산동": (114.5, 122.9, 34.2, 38.9), "만주": (121.0, 132.0, 41.0, 47.0)}
OUTF = {"서북": ("ch16", "fig16-1-nwkorea", 4.2), "요하": ("ch17", "fig17-1-liao", 4.4), "산동": ("ch18", "fig18-1-shandong", 3.6), "만주": ("ch19", "fig19-1-manchuria", 4.0)}

def draw(ax, bb, mode):
    x0, x1, y0, y1 = bb
    c0, c1 = int((x0 - LON0) * N), int((x1 - LON0) * N); r0, r1 = int((LAT1 - y1) * N), int((LAT1 - y0) * N)
    sub = DEM[r0:r1, c0:c1]
    ext = [x0, x1, y0, y1]
    ls = LightSource(azdeg=315, altdeg=40)
    hs = ls.hillshade(sub, vert_exag=0.02, dx=0.9, dy=0.9)
    ax.imshow(np.where(sub > 0, 1.0, np.nan) * 0 + 0, extent=ext, cmap=ListedColormap(["#d6e8f3" if mode == "color" else "white"]), origin="upper", aspect="auto")
    cm = ListedColormap((CC if mode == "color" else CB))
    nrm = BoundaryNorm([0] + LEV + [9000], cm.N + 1) if False else BoundaryNorm([-1] + LEV[:-1] + [9000], len(CC))
    layer = np.where(sub > 0, sub, np.nan)
    ax.imshow(layer, extent=ext, cmap=cm, norm=nrm, origin="upper", aspect="auto", interpolation="nearest")
    ax.imshow(np.where(sub > 0, hs, np.nan), extent=ext, cmap="gray", alpha=0.35, origin="upper", aspect="auto")
    for g in LAKES:
        for q in ([g] if isinstance(g, Polygon) else list(getattr(g, "geoms", []))):
            if isinstance(q, Polygon) and q.intersects(box(x0, y0, x1, y1)):
                ax.fill(*q.exterior.xy, fc="#d6e8f3" if mode == "color" else "white", ec="#1f6fb8" if mode == "color" else "black", lw=0.5)
    lab = set()
    for p, g in RIV:
        w = 0.5 + 0.18 * max(0, 9 - int(p.get("scalerank", 9)))
        for l in ([g] if isinstance(g, LineString) else list(getattr(g, "geoms", []))):
            if isinstance(l, LineString):
                ax.plot(*l.xy, color="#1f6fb8" if mode == "color" else "black", lw=w)
        ko = RKO.get(p.get("name"))
        if ko and ko not in lab:
            gg = g.intersection(box(x0, y0, x1, y1))
            if not gg.is_empty:
                ls_ = [gg] if isinstance(gg, LineString) else [t for t in gg.geoms if isinstance(t, LineString)]
                lb = max(ls_, key=lambda t: t.length)
                if lb.length > 0.25 * (x1 - x0):
                    c = lb.interpolate(0.5, normalized=True)
                    ax.text(c.x, c.y, ko, ha="center", va="bottom", bbox=dict(fc="white", ec="none", alpha=0.7, pad=0.4)); lab.add(ko)
    for nm, lo, la in PEAKS:
        if x0 < lo < x1 and y0 < la < y1:
            ax.plot(lo, la, "^", color="#222", ms=5); ax.text(lo + 0.05, la, nm, va="center", bbox=dict(fc="white", ec="none", alpha=0.6, pad=0.3))
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect(1 / math.cos(math.radians((y0 + y1) / 2)))
    ax.grid(color="#999", lw=0.3, ls=":"); ax.set_xlabel("동경 (도)"); ax.set_ylabel("북위 (도)")

def save(fig, ch, name, mode):
    d = os.path.join(OUT, ch); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"{name}-{mode}.pdf"); fig.savefig(p); plt.close(fig); return p

for mode in ("color", "bw"):
    fig, ax = plt.subplots(figsize=(5.12, 4.9), constrained_layout=True); draw(ax, (114, 132, 33, 47), mode)
    for k, (a, b, c, d) in FR.items():
        ax.add_patch(plt.Rectangle((a, c), b - a, d - c, fill=False, ec="#c0392b" if mode == "color" else "black", lw=1.2, ls="-" if mode == "color" else "--"))
        ax.text(a + 0.15, d - 0.3, {"서북": "한반도 서북부", "요하": "요하 유역", "산동": "산동 지역", "만주": "만주"}[k], color="#c0392b" if mode == "color" else "black", weight="bold",
                bbox=dict(fc="white", ec="none", alpha=0.7, pad=0.3))
    print(save(fig, "ch02", "fig02-1-regions", mode))
    for k, (ch, nm, h) in OUTF.items():
        fig, ax = plt.subplots(figsize=(5.12, h), constrained_layout=True); draw(ax, FR[k], mode); print(save(fig, ch, nm, mode))
