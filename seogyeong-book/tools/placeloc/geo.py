"""geo.py - 지표 좌표계, 격자, 거리·방위 (구면 근사, 반경 6371.0088 km)"""
import numpy as np

R_EARTH = 6371.0088


def haversine_km(lon1, lat1, lon2, lat2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dl = np.radians(lon2) - np.radians(lon1)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R_EARTH * np.arcsin(np.sqrt(a))


class Frame:
    """방위등거리도법(구면) - 중심 (lon0,lat0), 단위 km. x=동, y=북."""

    def __init__(self, lon0, lat0):
        self.lon0, self.lat0 = lon0, lat0
        self.p0 = np.radians(lat0)
        self.l0 = np.radians(lon0)

    def to_xy(self, lon, lat):
        lon, lat = np.asarray(lon, float), np.asarray(lat, float)
        p, l = np.radians(lat), np.radians(lon)
        cosc = np.sin(self.p0) * np.sin(p) + np.cos(self.p0) * np.cos(p) * np.cos(l - self.l0)
        c = np.arccos(np.clip(cosc, -1, 1))
        k = np.where(c < 1e-12, 1.0, c / np.sin(np.where(c < 1e-12, 1.0, c)))
        x = R_EARTH * k * np.cos(p) * np.sin(l - self.l0)
        y = R_EARTH * k * (np.cos(self.p0) * np.sin(p) - np.sin(self.p0) * np.cos(p) * np.cos(l - self.l0))
        return x, y

    def to_lonlat(self, x, y):
        x, y = np.asarray(x, float), np.asarray(y, float)
        rho = np.hypot(x, y)
        c = rho / R_EARTH
        sc, cc = np.sin(c), np.cos(c)
        rho_ = np.where(rho < 1e-12, 1.0, rho)
        lat = np.arcsin(np.clip(cc * np.sin(self.p0) + y * sc * np.cos(self.p0) / rho_, -1, 1))
        lon = self.l0 + np.arctan2(x * sc, rho_ * np.cos(self.p0) * cc - y * np.sin(self.p0) * sc)
        lat = np.where(rho < 1e-12, self.p0, lat)
        lon = np.where(rho < 1e-12, self.l0, lon)
        return np.degrees(lon), np.degrees(lat)


class Grid:
    """km 평면의 정규 격자. 모든 기법의 공통 정의역."""

    def __init__(self, xmin, xmax, ymin, ymax, step):
        self.step = step
        self.xs = np.arange(xmin, xmax + 1e-9, step)
        self.ys = np.arange(ymin, ymax + 1e-9, step)
        self.X, self.Y = np.meshgrid(self.xs, self.ys)
        self.shape = self.X.shape
        self.cell_area = step * step

    def dist(self, x, y):
        return np.hypot(self.X - x, self.Y - y)

    def azimuth(self, x, y):
        """기준점 (x,y)에서 각 칸을 본 방위각(북=0, 시계방향, 도)"""
        return (np.degrees(np.arctan2(self.X - x, self.Y - y)) + 360.0) % 360.0

    def centroid(self, mask_or_w):
        w = np.asarray(mask_or_w, float)
        s = w.sum()
        if s == 0:
            return (np.nan, np.nan)
        return ((w * self.X).sum() / s, (w * self.Y).sum() / s)

    def area(self, mask):
        return float(np.asarray(mask).sum() * self.cell_area)


def ang_diff(a, b):
    """두 방위각의 부호 있는 차(−180,180]"""
    d = (np.asarray(a) - np.asarray(b) + 180.0) % 360.0 - 180.0
    return d
