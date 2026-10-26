"""figlib.py - 그림 공통 스타일: 컬러판·흑백판 동시 출력, B5 본문폭 130 mm(5.12 in), 글자 8.5 pt 이상"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

for p in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
    if os.path.exists(p):
        fm.fontManager.addfont(p)
plt.rcParams.update({
    "font.family": "Noto Sans CJK KR", "font.size": 8.5, "axes.labelsize": 8.5, "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5, "legend.fontsize": 8.5, "axes.titlesize": 9, "axes.unicode_minus": False,
    "pdf.fonttype": 42, "axes.linewidth": 0.6, "lines.linewidth": 1.0,
})
WIDTH = 5.12   # inch = 130 mm
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "그림")

STY = {
    "color": dict(river="#1f6fb8", river_ls="-", fill="#f0b45a", fill2="#7fb3d5", ref="#222222", truth="#c0392b",
                  cmap="YlOrBr", cmap_div="RdBu_r", line="#222", grid="#bbbbbb", accent="#2e7d32", gray="#777777"),
    "bw": dict(river="#000000", river_ls="-.", fill="#bdbdbd", fill2="#e0e0e0", ref="#000000", truth="#000000",
               cmap="Greys", cmap_div="Greys", line="#000", grid="#aaaaaa", accent="#000000", gray="#555555"),
}


def new(mode, h, ncols=1, nrows=1, **kw):
    fig, ax = plt.subplots(nrows, ncols, figsize=(WIDTH, h), constrained_layout=True, **kw)
    return fig, ax


def save(fig, ch, name, mode):
    d = os.path.join(ROOT, ch)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{name}-{mode}.pdf")
    fig.savefig(path)
    plt.close(fig)
    return path


def base(ax, W, mode, title=None, refs=True, river=True, truth=False, label_refs=True):
    """가상 세계 공통 바탕: 하천, 기준 지명, (선택) 가상의 참 위치"""
    s = STY[mode]
    ax.set_xlim(0, 400); ax.set_ylim(0, 400); ax.set_aspect("equal")
    ax.set_xlabel("동 (km)"); ax.set_ylabel("북 (km)")
    ax.set_xticks(range(0, 401, 100)); ax.set_yticks(range(0, 401, 100))
    ax.grid(color=s["grid"], lw=0.3, ls=":")
    if river:
        ax.plot(W.river[:, 0], W.river[:, 1], color=s["river"], ls=s["river_ls"], lw=1.4, zorder=3)
    if refs:
        for k, (x, y) in W.refs.items():
            ax.plot(x, y, "^", color=s["ref"], ms=5, zorder=5, mfc=s["ref"] if mode == "color" else "white", mew=0.8)
            if label_refs:
                ax.annotate(k, (x, y), xytext=(4, 4), textcoords="offset points", fontsize=8.5, zorder=6)
    if truth:
        ax.plot(*W.truth, "*", color=s["truth"], ms=9, zorder=7, mec="black", mew=0.5)
    if title:
        ax.set_title(title, loc="left")
