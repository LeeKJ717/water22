"""t1_csp.py - 기법 1: 제약 만족 문제와 구간 연산"""
import numpy as np
from scipy.signal import fftconvolve
from .geo import ang_diff


class Interval:
    """닫힌 구간 [lo,hi]. 단위 환산 불확실성을 끝까지 전파한다(Moore, 1966)."""

    def __init__(self, lo, hi=None):
        hi = lo if hi is None else hi
        assert lo <= hi, f"구간 오류 [{lo},{hi}]"
        self.lo, self.hi = float(lo), float(hi)

    def __add__(self, o):
        o = o if isinstance(o, Interval) else Interval(o)
        return Interval(self.lo + o.lo, self.hi + o.hi)

    __radd__ = __add__

    def __sub__(self, o):
        o = o if isinstance(o, Interval) else Interval(o)
        return Interval(self.lo - o.hi, self.hi - o.lo)

    def __mul__(self, o):
        o = o if isinstance(o, Interval) else Interval(o)
        c = [self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi]
        return Interval(min(c), max(c))

    __rmul__ = __mul__

    def __contains__(self, v):
        return self.lo <= v <= self.hi

    def intersect(self, o):
        lo, hi = max(self.lo, o.lo), min(self.hi, o.hi)
        return Interval(lo, hi) if lo <= hi else None

    @property
    def width(self):
        return self.hi - self.lo

    def __repr__(self):
        return f"[{self.lo:.4g}, {self.hi:.4g}]"


# --- 제약(격자 위의 불리언 마스크를 만든다) ---
def c_distance(grid, x, y, band):
    """기준점에서 거리가 band(Interval, km)에 드는 칸"""
    d = grid.dist(x, y)
    return (d >= band.lo) & (d <= band.hi)


def c_bearing(grid, x, y, az_lo, az_hi):
    """기준점에서 본 방위가 [az_lo, az_hi] (시계방향 도, 북=0)에 드는 칸"""
    a = grid.azimuth(x, y)
    mid = (az_lo + az_hi) / 2.0
    half = ((az_hi - az_lo) % 360.0) / 2.0
    return np.abs(ang_diff(a, mid)) <= half + 1e-9


def c_region(mask):
    return np.asarray(mask, bool)


def c_near_polyline(grid, pts, r_km):
    """하천·해안 등 선에서 r_km 안인 칸 (선을 칸 크기 이하로 조밀하게 쪼개 최근접 거리 계산)"""
    from scipy.spatial import cKDTree
    pts = np.asarray(pts, float)
    dense = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(1, int(np.hypot(*(b - a)) / (grid.step / 2)))
        for t in np.linspace(0, 1, n + 1)[1:]:
            dense.append(a + (b - a) * t)
    tree = cKDTree(np.array(dense))
    d, _ = tree.query(np.c_[grid.X.ravel(), grid.Y.ravel()])
    return (d <= r_km).reshape(grid.shape)


def c_pair_distance(dom_a, dom_b, grid, band):
    """두 미지 지점 A,B의 거리가 band에 드는 쌍이 존재하는 A의 값만 남김(호 일관성).
    B 영역과 고리(annulus) 커널의 합성곱으로 계산한다."""
    k = int(np.ceil(band.hi / grid.step))
    ax = np.arange(-k, k + 1) * grid.step
    KX, KY = np.meshgrid(ax, ax)
    kd = np.hypot(KX, KY)
    ring = ((kd >= band.lo) & (kd <= band.hi)).astype(float)
    cnt = fftconvolve(dom_b.astype(float), ring, mode="same")
    return dom_a & (cnt > 0.5)


def solve(masks):
    """모든 제약의 교집합과 만족 개수 지도(max-CSP)를 돌려준다.
    교집합이 공집합이면 모순 증거가 있다는 뜻이며, 만족 개수가 최대인 칸이 차선해다."""
    stack = np.stack([np.asarray(m, bool) for m in masks])
    score = stack.sum(axis=0)
    feasible = score == len(masks)
    best = score == score.max()
    return dict(feasible=feasible, score=score, best=best, n=len(masks),
                consistent=bool(feasible.any()))


def arc_consistency(domains, pair_constraints, grid, max_iter=20):
    """AC-3 형태의 반복 가지치기. domains: {이름: 마스크}, pair_constraints: [(a,b,Interval)]"""
    dom = {k: v.copy() for k, v in domains.items()}
    for _ in range(max_iter):
        changed = False
        for a, b, band in pair_constraints:
            for u, v in ((a, b), (b, a)):
                new = c_pair_distance(dom[u], dom[v], grid, band)
                if new.sum() != dom[u].sum():
                    dom[u] = new
                    changed = True
        if not changed:
            break
    return dom
