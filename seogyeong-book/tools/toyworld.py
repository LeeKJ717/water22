"""toyworld.py - 맛보기(가상) 세계: 모든 기법의 예제와 검산에 쓰는 합성 자료.
※ 이 세계의 지명·좌표·수치는 전부 코드로 만든 가상 자료이며 실제 지리와 무관하다."""
import numpy as np
from placeloc.geo import Grid
from placeloc.t1_csp import Interval

U_TRUE = 0.42                 # 가상 단위 '리'의 참값(km)
U_BAND = (0.36, 0.48)         # 사료 해석자가 아는 단위 길이의 범위
REL_SIGMA = 0.10              # 서술 거리의 상대 오차(로그정규 시그마)

REFS = {"갑성": (70.0, 310.0), "을진": (90.0, 60.0), "병포": (300.0, 340.0), "정령": (350.0, 90.0)}
RIVER = np.array([[120, 400], [200, 250], [235, 180], [330, 100], [400, 40]], float)
TRUTH = np.array([233.0, 185.0])


def make_grid(step=4.0):
    return Grid(0, 400, 0, 400, step)


def mountain_dem(grid, seed=0):
    """가상 DEM(m): 남북으로 뻗은 능선 + 고개(통로) + 완만한 기복"""
    X, Y = grid.X, grid.Y
    ridge = 1100 * np.exp(-0.5 * ((X - 170) / 14.0) ** 2) * (1 - 0.92 * np.exp(-0.5 * ((Y - 215) / 20.0) ** 2))
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, 1, X.shape)
    from scipy.ndimage import gaussian_filter
    hills = 90 * gaussian_filter(noise, 6) / gaussian_filter(noise, 6).std()
    return np.clip(60 + ridge + hills, 0, None)


class World:
    def __init__(self, seed=7, n_ctrl=12, random_truth=False, u_true=U_TRUE):
        self.rng = np.random.default_rng(seed)
        self.grid = make_grid()
        if random_truth == "river":      # 하천 가까이(서술 '강 10리 이내'가 참이 되도록)
            seg = np.hypot(*np.diff(RIVER, axis=0).T)
            i = int(self.rng.choice(len(seg), p=seg / seg.sum()))
            t = self.rng.random()
            p = RIVER[i] + (RIVER[i + 1] - RIVER[i]) * t
            nrm = np.array([-(RIVER[i + 1] - RIVER[i])[1], (RIVER[i + 1] - RIVER[i])[0]])
            nrm = nrm / np.hypot(*nrm)
            self.truth = np.clip(p + nrm * self.rng.normal(0, 1.5), 5, 395)
        elif random_truth:
            self.truth = self.rng.uniform(110, 290, 2)
        else:
            self.truth = TRUTH.copy()
        self.refs = dict(REFS)
        self.river = RIVER.copy()
        # 거리 서술(리): 참 거리/참 단위 × 로그정규 오차, 10리 단위 반올림
        self.dist_obs = {}
        for k, (x, y) in self.refs.items():
            d = np.hypot(x - self.truth[0], y - self.truth[1]) / u_true
            self.dist_obs[k] = float(np.round(d * np.exp(self.rng.normal(0, REL_SIGMA)), -1))
        # 방위 서술: 8방위로 뭉뚱그려 말함 (기준점 → 목표)
        names = ["북", "북동", "동", "남동", "남", "남서", "서", "북서"]
        self.bear_obs = {}
        for k, (x, y) in self.refs.items():
            az = (np.degrees(np.arctan2(self.truth[0] - x, self.truth[1] - y)) + 360) % 360
            i = int(np.round(az / 45.0)) % 8
            self.bear_obs[k] = (names[i], i * 45.0)
        # 하천 근접 서술: '강에서 10리 이내'
        self.near_river_km = 10 * U_TRUE * 1.5
        # 지도 기준점(기법 2): 고지도 화상 좌표(픽셀)와 현대 좌표(km) 쌍
        self._make_oldmap(n_ctrl)
        # 이동시간 서술(기법 4): 갑성에서 '이틀 길'
        self.days_obs = None

    def _make_oldmap(self, n):
        rng = self.rng
        pts = rng.uniform(20, 380, (n, 2))
        self.ctrl_dst = pts                       # 현대 좌표(km)
        def distort(p):
            q = p.copy()
            # 아핀 부분(회전 7도, 축척 0.9/1.1, 이동) + 부드러운 비선형 뒤틀림
            th = np.radians(7)
            R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
            q = (q - 200) @ R.T * np.array([0.9, 1.1]) + 200
            q[:, 0] += 18 * np.sin(p[:, 1] / 70.0)
            q[:, 1] += 14 * np.sin(p[:, 0] / 90.0 + 1.0)
            return q * 2.0 + 50                   # 화상 좌표(픽셀, 임의 단위)
        self.distort = distort
        self.ctrl_src = distort(pts) + rng.normal(0, 3.0, pts.shape)   # 기준점 위치 오차(화상 단위)
        self.target_src = distort(self.truth[None, :])[0]


def band_from_li(obs_li, slack=0.25):
    """원문 수치(리) × 단위 길이 구간 × 서술 오차 여유 → km 구간 (구간 연산)"""
    return Interval(obs_li) * Interval(*U_BAND) * Interval(1 - slack, 1 + slack)
