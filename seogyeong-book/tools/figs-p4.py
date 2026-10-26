"""figs-p4.py - 4장(증거 DB 설계) 새 그림. 사용: python3 tools/figs-p4.py
출력: 그림/ch04/fig04-a-timeline, fig04-b-fk, fig04-c-row, fig04-d-digits (color, bw)
숫자 출처: fig04-d는 아래 계산(WGS84 평균 반지름 기반)."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import *
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

FS = 8.5


def box(ax, x, y, w, h, t, fc, ec, fs=FS, ls="-", bold=False, hatch=None, lw=1.1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.02", fc=fc, ec=ec,
                                lw=lw, ls=ls, hatch=hatch))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", linespacing=1.3)


def arr(ax, a, b, ls="-", c="#222", lw=1.1):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=10, lw=lw, color=c, ls=ls,
                                 shrinkA=0, shrinkB=0))


# ---------------------------------------------------------------- A. 연대기
EVENTS = [  # (연도, 줄, 위/아래, 글, 표시)
    (1970, 0, +1, "1970 Codd\n관계형 모델", "o"),
    (1976, 0, -1, "1976 Chen\n개체-관계 모델", "o"),
    (1984, 0, +1, "1984\nWGS 84", "o"),
    (2015, 0, +1, "2015 FIPS 180-4\n(SHA-256)", "o"),
    (1982, 1, +1, "1982\n중국역사지도집", "s"),
    (2001, 1, +1, "2001 Berman\nCHGIS 지명사전", "s"),
    (2006, 1, -1, "2006\nPleiades 시작", "s"),
    (2017, 1, +1, "2017\nWHG 자문회의", "s"),
    (2011, 2, +1, "2011 Peng\n재현 가능한 연구", "^"),
    (2016, 2, -1, "2016 Wilkinson 등\nFAIR 원칙", "^"),
]


def fig_a(mode):
    c = STY[mode]
    fig, ax = new(mode, 3.4)
    ax.set_xlim(1944, 2030); ax.set_ylim(-0.75, 3.1)
    lanes = {0: "모델·표준", 1: "지명 사전", 2: "재현성"}
    ys = {0: 2.35, 1: 1.25, 2: 0.15}
    for k, y in ys.items():
        ax.hlines(y, 1966, 2024, color=c["ref"], lw=0.9, ls=["-", "--", ":"][k])
        ax.text(1944.5, y, lanes[k], fontsize=FS, fontweight="bold", va="center", ha="left")
    for yr, lane, side, t, mk in EVENTS:
        y = ys[lane]
        ax.plot(yr, y, mk, ms=6.5, mfc=c["fill"] if mode == "color" else ("white" if mk != "s" else "#999999"),
                mec=c["ref"], mew=1.0, zorder=5)
        ax.annotate(t, (yr, y), xytext=(0, 9 * side), textcoords="offset points", ha="center",
                    va="bottom" if side > 0 else "top", fontsize=8, linespacing=1.2)
    ax.set_yticks([])
    ax.set_xticks(range(1970, 2031, 10))
    ax.tick_params(axis="x", labelsize=FS)
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", color=c["grid"], lw=0.3, ls=":")
    ax.set_xlabel("연도")
    return save(fig, "ch04", "fig04-a-timeline", mode)


# ---------------------------------------------------------------- B. 외래키 관계
def fig_b(mode):
    c = STY[mode]
    fig, ax = new(mode, 3.7); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    W, H = 0.25, 0.15
    pos = {"source_text": (0.02, 0.78, "사료 원문"), "place": (0.375, 0.78, "지명"),
           "place_alias": (0.73, 0.78, "이표기와 개명"),
           "evidence": (0.02, 0.42, "사료에서 뽑은 제약"), "coord": (0.375, 0.42, "좌표(출처 필수)"),
           "run": (0.73, 0.42, "기법별 계산 이력"),
           "paper": (0.02, 0.06, "선행 논문"), "geodata": (0.375, 0.06, "지리 자료"),
           }
    for k, (x, y, t) in pos.items():
        if k in ("evidence", "run"):
            fc, ls = c["fill"], "-"
        elif k in ("paper", "geodata"):
            fc, ls = "#ffffff", "--"
        else:
            fc, ls = c["fill2"], "-"
        box(ax, x, y, W, H, f"{k}\n{t}", fc, c["ref"], ls=ls)
    box(ax, 0.73, 0.06, W, H, "book_* 14개 표\n원고·표·그림 저장", "#ffffff", c["gray"], ls=":")
    # 외래키: 자식 -> 부모 (화살표 끝이 부모)
    arr(ax, (0.145, 0.57), (0.145, 0.78))
    ax.text(0.135, 0.675, "src_id", fontsize=8, ha="right", va="center")
    arr(ax, (0.27, 0.57), (0.42, 0.78))
    ax.text(0.345, 0.64, "place_id\nref_place_id", fontsize=8, ha="left", va="center", linespacing=1.15)
    arr(ax, (0.60, 0.57), (0.60, 0.78))
    ax.text(0.61, 0.675, "place_id", fontsize=8, va="center")
    arr(ax, (0.73, 0.855), (0.625, 0.855))
    ax.text(0.677, 0.875, "place_id", fontsize=8, ha="center", va="bottom")
    arr(ax, (0.83, 0.57), (0.68, 0.78))
    ax.text(0.845, 0.64, "target_\nplace_id", fontsize=8, ha="left", va="center", linespacing=1.15)
    return save(fig, "ch04", "fig04-b-fk", mode)


# ---------------------------------------------------------------- C. 한 구절 -> 행
def fig_c(mode):
    c = STY[mode]
    fig, ax = new(mode, 3.9); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    W, H = 0.29, 0.20
    hum = dict(ls="--", lw=1.6)   # 사람이 판단하는 단계: 굵은 점선
    box(ax, 0.02, 0.74, W, H, "1 적재\nsource_text에 넣고\nverified = 0", c["fill2"], c["ref"])
    box(ax, 0.355, 0.74, W, H, "2 대조 (사람)\n인쇄본과 같으면\nverified = 1", c["fill2"], c["ref"], **hum)
    box(ax, 0.69, 0.74, W, H, "3 추출 (사람)\n구절 하나에서\n증거 3행", c["fill"], c["ref"], **hum)
    arr(ax, (0.31, 0.84), (0.355, 0.84)); arr(ax, (0.645, 0.84), (0.69, 0.84))
    chips = [("방위\n서쪽", 0.64), ("거리\n50리", 0.78), ("인접\n강", 0.92)]
    for t, x in chips:
        box(ax, x - 0.055, 0.46, 0.11, 0.14, t, "#ffffff", c["ref"], fs=8)
        arr(ax, (0.835, 0.74), (x, 0.60), lw=0.8)
    ax.text(0.54, 0.53, "evidence 3행\n(같은 src_id)", fontsize=8, ha="right", va="center", linespacing=1.2)
    box(ax, 0.02, 0.18, W, H, "4 좌표\n기준 지명 을주만\n출처와 함께 coord에", c["fill2"], c["ref"])
    box(ax, 0.355, 0.18, W, H, "5 계통 (사람)\n베낀 구절이면\n한 건으로 센다", c["fill"], c["ref"], **hum)
    box(ax, 0.69, 0.18, W, H, "6 계산\nrun에 한 행이\n새로 쌓인다", c["fill2"], c["ref"])
    arr(ax, (0.31, 0.28), (0.355, 0.28)); arr(ax, (0.645, 0.28), (0.69, 0.28))
    ax.text(0.5, 0.02, "굵은 점선 테두리는 사람이 판단하는 단계. 가상 구절이며 서경의 결과가 아니다.",
            ha="center", fontsize=8, color=c["gray"])
    return save(fig, "ch04", "fig04-c-row", mode)


# ---------------------------------------------------------------- E. 소수 자릿수와 오차
A_, F_ = 6378137.0, 1 / 298.257223563
B_ = A_ * (1 - F_)
R1 = (2 * A_ + B_) / 3                      # 평균 반지름(m)
DEG = R1 * math.pi / 180                    # 1도의 길이(m)


def fig_d(mode):
    c = STY[mode]
    fig, ax = new(mode, 3.1)
    ds = list(range(0, 6))
    lat = [0.5 * 10 ** -d * DEG for d in ds]
    lon = [v * math.cos(math.radians(30)) for v in lat]
    ax.plot(ds, lat, "o-", color=c["ref"], mfc=c["fill"] if mode == "color" else "white", ms=6, label="위도 방향")
    ax.plot(ds, lon, "s--", color=c["gray"], mfc="white", ms=5, label="경도 방향(위도 30도)")
    ax.set_yscale("log")
    def fmt(m):
        if m >= 1000: return f"{m / 1000:.3g} km"
        return f"{m:.3g} m"
    for d, v in zip(ds, lat):
        ax.annotate(fmt(v), (d, v), xytext=(5, 6), textcoords="offset points", fontsize=8)
    ax.set_xlabel("소수점 아래 자릿수 d"); ax.set_ylabel("반올림 오차의 한계 (m, 로그 눈금)")
    ax.set_xticks(ds); ax.set_ylim(0.2, 2e5); ax.set_xlim(-0.3, 5.8)
    ax.grid(color=c["grid"], lw=0.3, ls=":")
    ax.legend(loc="lower left", frameon=False, fontsize=FS)
    return save(fig, "ch04", "fig04-d-digits", mode)


if __name__ == "__main__":
    for m in ("color", "bw"):
        for f in (fig_a, fig_b, fig_c, fig_d):
            print(f(m))
