"""figs-f.py - 글자 도형(코드블록)을 그림으로 바꾼다. 원고의 코드블록에서 칸 값을 읽어 그린다.
실행: python3 tools/figs-f.py  (그림/ch05, 그림/ch08에 컬러·흑백 PDF 생성)"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from figlib import *
G = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs-f-grids.json"), encoding="utf-8"))

def grid(ax, rows, mapping, cols, title, step=None):
    a = np.array([[mapping.get(ch, 0) for ch in r] for r in rows])
    ax.imshow(a, cmap=ListedColormap(cols), vmin=0, vmax=len(cols) - 1, interpolation="nearest")
    n, m = a.shape
    ax.set_xticks(np.arange(-.5, m, 1), minor=True); ax.set_yticks(np.arange(-.5, n, 1), minor=True)
    ax.grid(which="minor", color="#ffffff", lw=0.5); ax.tick_params(which="both", length=0)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_title(title, fontsize=9)
    for s_ in ax.spines.values(): s_.set_linewidth(0.6)
    return a

def fig5_6(mode):
    c = {"color": ["#f3f3f3", "#f0b45a", "#c0392b"], "bw": ["#ffffff", "#aaaaaa", "#000000"]}[mode]
    fig, axs = plt.subplots(1, 4, figsize=(WIDTH, 1.9), constrained_layout=True)
    for ax, key, ttl in zip(axs, ["A", "B", "C", "D"], ["(A) 도넛 72칸", "(B) 부채꼴 48칸", "(C) 한계선 이남 104칸", "(D) 교집합 14칸"]):
        grid(ax, G["f56"][key], {"#": 1, "@": 2}, c, ttl)
    return save(fig, "ch05", "fig05-6-overlay", mode)

def fig8_x(mode):
    c = {"color": ["#f3f3f3", "#7fb3d5", "#8d6e63", "#2e7d32", "#c0392b"], "bw": ["#ffffff", "#b0b0b0", "#555555", "#e0e0e0", "#000000"]}[mode]
    fig, axs = plt.subplots(1, 3, figsize=(WIDTH, 2.15), constrained_layout=True)
    for ax, key, ttl in zip(axs, ["m", "v", "c"], ["산줄기 지형", "골짜기 지형", "해안 지형"]):
        grid(ax, G["f8"][key], {"o": 1, "^": 2, "~": 3, "@": 4}, [c[0], c[1], c[2], c[3], c[4]], ttl)
    return save(fig, "ch08", "fig08-9-isochrone-maps", mode)

if __name__ == "__main__":
    for mode in ("color", "bw"):
        print(fig5_6(mode)); print(fig8_x(mode))
