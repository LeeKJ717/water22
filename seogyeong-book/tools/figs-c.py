"""figs-c.py - 4부 지역 지도(임시판: Natural Earth 1:10m). DEM이 있는 환경에서는 노트북 쪽 스크립트가 고도대 바탕으로 대체한다.
하천: Natural Earth 1:10m 하천 중심선(중소 하천 일부 누락, 예: 대동강). 산맥: Natural Earth 지형 구역 윤곽과 대표 봉우리."""
import os, sys, json, math
sys.path.insert(0, ".")
import numpy as np
from shapely.geometry import shape, box, Polygon, MultiPolygon, LineString
from shapely.ops import unary_union
from figlib import *
GEO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "geo")

def load(n):
    return json.load(open(os.path.join(GEO, n), encoding="utf-8"))["features"]
def P(f):
    return {k.lower(): v for k, v in f["properties"].items()}
BIG = box(112, 31, 134, 49)
def clip(feats, tol=0.003):
    out = []
    for f in feats:
        g = shape(f["geometry"])
        if not g.is_valid:
            g = g.buffer(0)
        g = g.intersection(BIG)
        if not g.is_empty:
            out.append((P(f), g.simplify(tol)))
    return out
LAND = unary_union([g for _, g in clip(load("ne_10m_land.geojson"))])
LAKES = clip(load("ne_10m_lakes.geojson"))
RIV = clip(load("ne_10m_rivers_scale_rank.geojson"))
REG = [(p, g) for p, g in clip(load("ne_10m_geography_regions_polys.geojson"), 0.01) if p.get("featurecla") == "Range/mtn"]
PK = [(P(f), f["geometry"]["coordinates"]) for f in load("ne_10m_geography_regions_elevation_points.geojson")]
CTY = clip(load("ne_10m_admin_0_countries.geojson"), 0.005)

RIVER_KO = {"Yalu": "압록강", "Tumen": "두만강", "Liao": "요하", "Xiliao": "서요하", "Songhua": "송화강", "Huang": "황하", "Han": "한강",
            "Daling": "대릉하", "Nen": "눈강", "Amur": "흑룡강", "Hai": "해하", "Luan": "난하", "Namhan": "남한강", "Nakdong": "낙동강",
            "Di’er Songhua": "제2송화강", "Yongding": "영정하", "Muling": "목릉하", "Tao’er": "조아하", "Huai": "회하", "Sanggan": "상건하"}
RANGE_KO = {"hamgyong mts.": "함경산맥", "taihang mts.": "태항산맥", "lüliang mts.": "여량산맥", "qinling mountains": "진령산맥",
            "lesser khingan range": "소흥안령", "sikhote-alin’ range": "시호테알린산맥", "greater khingan range": "대흥안령", "dabie mts.": "대별산맥"}
PEAKS = [("백두산", 128.08, 42.00), ("묘향산", 126.30, 40.00), ("설악산", 128.47, 38.14), ("지리산", 127.73, 35.34), ("한라산", 126.53, 33.36),
         ("오대산", 113.57, 39.09), ("태산", 117.10, 36.25), ("의무려산", 121.72, 41.63)]
RANGES = [("랑림산맥", 127.68, 41.31), ("함경산맥", 128.4, 41.3), ("태항산맥", 113.8, 38.6), ("소흥안령", 130.0, 48.5), ("대흥안령", 123.16, 49.38), ("장백산맥", 128.0, 41.99)]
SEAS = [("황해", 123.6, 35.7), ("동해", 130.4, 39.0), ("발해", 120.0, 38.6)]
FRAMES = {"서북": (124.0, 128.6, 37.4, 41.6, "한반도 서북부"), "요하": (119.5, 125.5, 39.4, 43.6, "요하 유역"),
          "산동": (114.5, 122.9, 34.2, 38.9, "산동 지역"), "만주": (121.0, 132.0, 41.0, 47.0, "만주")}

def draw(ax, bb, mode, label_scale=1.0, lw=1.0):
    s = STY[mode]
    x0, x1, y0, y1 = bb
    sea = "#d6e8f3" if mode == "color" else "white"
    ax.set_facecolor(sea)
    def polys(g):
        return [g] if isinstance(g, Polygon) else [q for q in getattr(g, "geoms", []) if isinstance(q, Polygon)]
    for q in polys(LAND):
        xs, ys = q.exterior.xy
        ax.fill(xs, ys, fc="#f6f2e4" if mode == "color" else "#f4f4f4", ec="#555", lw=0.5, zorder=1)
    for p, g in LAKES:
        for q in polys(g):
            xs, ys = q.exterior.xy
            ax.fill(xs, ys, fc=sea, ec=s["river"], lw=0.5, zorder=3)
    placed = set()
    for p, g in RIV:
        nm = p.get("name")
        w = 0.5 + 0.18 * max(0, 9 - int(p.get("scalerank", 9)))
        for l in ([g] if isinstance(g, LineString) else list(getattr(g, "geoms", []))):
            if isinstance(l, LineString):
                xs, ys = l.xy
                ax.plot(xs, ys, color=s["river"], ls="-" if mode == "color" else "-", lw=w, zorder=4, solid_capstyle="round")
        ko = RIVER_KO.get(nm)
        if ko and ko not in placed:
            gg = g.intersection(box(x0, y0, x1, y1))
            if not gg.is_empty:
                ls_ = [gg] if isinstance(gg, LineString) else [t for t in gg.geoms if isinstance(t, LineString)]
                lbest = max(ls_, key=lambda t: t.length)
                if lbest.length > 0.25 * (x1 - x0):
                    c = lbest.interpolate(0.5, normalized=True)
                    ax.text(c.x, c.y, ko, fontsize=8.5, color="#0b3f73" if mode == "color" else "black", ha="center", va="bottom", zorder=7,
                            bbox=dict(fc="white", ec="none", alpha=0.7, pad=0.4))
                    placed.add(ko)
    for nm, lo, la in PEAKS:
        if x0 < lo < x1 and y0 < la < y1:
            ax.plot(lo, la, "^", color="#6b5530" if mode == "color" else "black", ms=5, zorder=8)
            ax.text(lo + 0.06 * (x1 - x0) / 5, la, nm, fontsize=8.5, zorder=8, va="center", bbox=dict(fc="white", ec="none", alpha=0.6, pad=0.3))
    for nm, lo, la in RANGES:
        if x0 < lo < x1 and y0 < la < y1:
            ax.plot(lo, la, "^", mfc="none", mec="#8a3b12" if mode == "color" else "black", mew=1.4, ms=8, zorder=8)
            ax.text(lo, la - 0.045 * (y1 - y0), nm, fontsize=8, ha="center", va="top", zorder=8, color="#8a3b12" if mode == "color" else "black", bbox=dict(fc="white", ec="none", alpha=0.6, pad=0.3))
    for nm, lo, la in SEAS:
        if x0 + + 0.5 < lo < x1 - 0.5 and y0 + 0.4 < la < y1 - 0.4:
            ax.text(lo, la, nm, fontsize=8.5, style="italic", color="#2d5b84" if mode == "color" else "black", ha="center", zorder=6)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
    ax.set_aspect(1 / math.cos(math.radians((y0 + y1) / 2)))
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    ax.set_xlabel("동경 (도)"); ax.set_ylabel("북위 (도)")

def overview(mode):
    s = STY[mode]
    fig, ax = new(mode, 4.9)
    draw(ax, (114, 132, 33, 47), mode)
    for k, (a, b, c, d, nm) in FRAMES.items():
        ax.add_patch(plt.Rectangle((a, c), b - a, d - c, fill=False, ec=s["truth"], lw=1.2, ls="-" if mode == "color" else "--", zorder=9))
        ax.text(a + 0.15, d - 0.3, nm, fontsize=8.5, color=s["truth"], weight="bold", zorder=9, bbox=dict(fc="white", ec="none", alpha=0.7, pad=0.3))
    return save(fig, "ch02", "fig02-1-regions", mode)

def region(key, mode, ch, name, h=3.8):
    a, b, c, d, nm = FRAMES[key]
    fig, ax = new(mode, h)
    draw(ax, (a, b, c, d), mode)
    return save(fig, ch, name, mode)

if __name__ == "__main__":
    for mode in ("color", "bw"):
        print(overview(mode))
        print(region("서북", mode, "ch16", "fig16-1-nwkorea", 4.2))
        print(region("요하", mode, "ch17", "fig17-1-liao", 4.4))
        print(region("산동", mode, "ch18", "fig18-1-shandong", 3.6))
        print(region("만주", mode, "ch19", "fig19-1-manchuria", 4.0))
