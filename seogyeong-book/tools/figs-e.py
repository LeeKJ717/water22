"""figs-e.py - 책의 지도(앞부분) 그림. 사용: python3 tools/figs-e.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import *
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def box(ax, x, y, w, h, t, fc, ec, fs=8.5, ls="-", bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.02", fc=fc, ec=ec, lw=1.1, ls=ls))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal", linespacing=1.35)

def arr(ax, a, b, ls="-", c="#222"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=10, lw=1.1, color=c, ls=ls))

def fig_map(mode):
    c = STY[mode]
    fig, ax = new(mode, 4.3)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    f1, f2, f3 = c["fill2"], c["fill"], "#ffffff"
    box(ax, 0.30, 0.86, 0.40, 0.11, "서장\n왜 서경인가, 이 책의 원칙", f3, c["ref"], bold=True)
    box(ax, 0.04, 0.55, 0.92, 0.22, "", f1, c["ref"])
    ax.text(0.5, 0.745, "준비 (1~4장): 계산하기 전에 알아야 할 것", ha="center", fontsize=8.8, fontweight="bold")
    for i, t in enumerate(["1장\n사료 목록과\n증거의 종류", "2장\n기존 학설과\n이 책의 자리", "3장\n사료 비판\n(단위·방향·오류)", "4장\n증거 DB\n(판단을 적는 법)"]):
        box(ax, 0.07 + i * 0.225, 0.58, 0.20, 0.13, t, "#ffffff", c["ref"], fs=8)
    box(ax, 0.04, 0.24, 0.92, 0.22, "", f2, c["ref"])
    ax.text(0.5, 0.435, "방법 (5~8장): 같은 증거를 네 가지 방식으로 읽는다", ha="center", fontsize=8.8, fontweight="bold")
    for i, t in enumerate(["5장\n제약 전파\n(조건으로 깎기)", "6장\n지오레퍼런싱\n(옛 지도 펴기)", "7장\n베이즈 추정\n(칸마다 점수)", "8장\n최소비용 경로\n(걷는 시간)"]):
        box(ax, 0.07 + i * 0.225, 0.27, 0.20, 0.13, t, "#ffffff", c["ref"], fs=8)
    box(ax, 0.04, 0.04, 0.40, 0.12, "맺음말\n총평과 더 나아갈 길", f3, c["ref"], bold=True)
    box(ax, 0.50, 0.04, 0.22, 0.12, "2권\n도구·자료·GPU", f3, c["gray"], ls="--")
    box(ax, 0.75, 0.04, 0.21, 0.12, "3권\n통합·지역 적용", f3, c["gray"], ls="--")
    arr(ax, (0.5, 0.86), (0.5, 0.78)); arr(ax, (0.5, 0.55), (0.5, 0.47)); arr(ax, (0.3, 0.24), (0.3, 0.17))
    arr(ax, (0.44, 0.10), (0.50, 0.10), ls="--", c=c["gray"]); arr(ax, (0.72, 0.10), (0.75, 0.10), ls="--", c=c["gray"])
    return save(fig, "ch00", "fig0-map", mode)


from matplotlib.patches import Wedge, Rectangle

def fig_ch01(mode):
    c = STY[mode]
    fig, ax = new(mode, 3.6); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    src = ["관찬 사서", "지리지", "외국 사료", "사행 기록·견문록", "고지도", "금석문·고고 자료"]
    ev = ["거리(리·보·일)", "방위", "하천·산 근접", "포함·인접 관계", "시기와 이름의 변천", "지명의 글자", "지도 위 상대 배치"]
    ax.text(0.17, 0.97, "사료의 여섯 무리", ha="center", fontsize=9.5, fontweight="bold")
    ax.text(0.83, 0.97, "뽑아내는 증거의 유형", ha="center", fontsize=9.5, fontweight="bold")
    for i, t in enumerate(src):
        y = 0.80 - i * 0.125
        box(ax, 0.02, y - 0.04, 0.30, 0.09, t, c["fill2"], c["ref"], fs=8.5)
    for i, t in enumerate(ev):
        y = 0.82 - i * 0.108
        box(ax, 0.66, y - 0.04, 0.32, 0.08, t, c["fill"], c["ref"], fs=8.5)
    arr(ax, (0.34, 0.50), (0.64, 0.50))
    ax.text(0.49, 0.545, "구절을 읽어서\n증거표의 한 줄로", ha="center", fontsize=8.3)
    box(ax, 0.34, 0.06, 0.30, 0.13, "계통과 독립성 점검\n베낀 책은 한 번만 센다", "#ffffff", c["ref"], fs=8, ls="--")
    return save(fig, "ch01", "fig1-sources", mode)

def fig_ch03(mode):
    import numpy as np
    c = STY[mode]
    fig, axs = new(mode, 2.9, ncols=2)
    ax = axs[0]; ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")
    ax.text(5, 3.7, "단위: 한 점이 아니라 구간", ha="center", fontsize=9, fontweight="bold")
    ax.annotate("", xy=(9.6, 2.3), xytext=(0.4, 2.3), arrowprops=dict(arrowstyle="-|>", lw=1))
    ax.plot(0.4, 2.3, "o", color=c["truth"]); ax.text(0.4, 2.65, "기준점", ha="center", fontsize=8)
    ax.add_patch(Rectangle((4.2, 2.1), 3.4, 0.4, fc=c["fill"], ec=c["ref"], lw=1))
    ax.text(5.9, 1.65, "'50리'가 닿는 거리의 구간", ha="center", fontsize=8)
    ax.text(4.2, 1.15, "50 × 짧은 쪽", ha="center", fontsize=7.5, color=c["gray"]); ax.text(7.6, 1.15, "50 × 긴 쪽", ha="center", fontsize=7.5, color=c["gray"])
    ax.text(5, 0.35, "리의 길이를 구간 [a, b]로 두면\n거리도 구간 [50a, 50b]가 된다", ha="center", fontsize=8)
    ax = axs[1]; ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.45, 1.35); ax.set_aspect("equal"); ax.axis("off")
    ax.text(0, 1.25, "방향: '서쪽'은 한 방향이 아니라 부채꼴", ha="center", fontsize=9, fontweight="bold")
    ax.add_patch(Wedge((0, 0), 1.0, 180 - 22.5, 180 + 22.5, fc=c["fill"], ec=c["ref"], alpha=0.55, lw=1))
    ax.add_patch(Wedge((0, 0), 0.72, 180 - 15, 180 + 15, fc=c["fill2"], ec=c["ref"], alpha=0.9, lw=1))
    for a, t in [(0, "동"), (90, "북"), (180, "서"), (270, "남")]:
        ax.text(1.12 * np.cos(np.radians(a)), 1.12 * np.sin(np.radians(a)) - 0.04, t, ha="center", fontsize=8.5)
    ax.plot(0, 0, "o", color=c["truth"], ms=4)
    ax.text(0, -1.3, "8방위이면 45도, 12방위이면 30도의 폭", ha="center", fontsize=8)
    return save(fig, "ch03", "fig3-unit-direction", mode)

def fig_ch04(mode):
    c = STY[mode]
    fig, ax = new(mode, 3.7); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    W, H = 0.27, 0.13
    pos = {"source_text": (0.03, 0.80, "사료 원문"), "place": (0.365, 0.80, "지명"), "paper": (0.70, 0.80, "선행 논문"),
           "evidence": (0.03, 0.50, "사료에서 뽑은 제약"), "coord": (0.365, 0.50, "좌표(출처 필수)"), "geodata": (0.70, 0.50, "지리 자료와 라이선스"),
           "place_alias": (0.365, 0.20, "이표기와 개명"), "run": (0.03, 0.20, "기법별 계산 이력")}
    for k, (x, y, t) in pos.items():
        fc = c["fill"] if k in ("evidence", "run") else (c["fill2"] if k in ("source_text", "place", "coord", "place_alias") else "#ffffff")
        box(ax, x, y, W, H, f"{k}\n{t}", fc, c["ref"], fs=8)
    def cen(k, dx=0, dy=0): x, y, _ = pos[k]; return (x + W / 2 + dx, y + H / 2 + dy)
    arr(ax, (0.165, 0.80), (0.165, 0.63));     arr(ax, (0.50, 0.80), (0.50, 0.63)); arr(ax, (0.165, 0.50), (0.165, 0.33))
    ax.text(0.5, 0.05, "표의 구성을 나눠 그린 개략도이며, 화살표는 대표적인 흐름만 나타낸다. 열의 전체 목록은 부록 C.", ha="center", fontsize=7.6, color=c["gray"])
    return save(fig, "ch04", "fig4-db", mode)

if __name__ == "__main__":
    for m in ("color", "bw"):
        print(fig_map(m)); print(fig_ch01(m)); print(fig_ch03(m)); print(fig_ch04(m))
