import math, re, itertools
import numpy as np
from scipy import ndimage
U_LO, U_HI = 0.36, 0.48          # 이 장의 단위 구간 (km/리)
LAT0 = 39 + 1/60                 # G1 평양 (위키백과 상자)
LON0 = 125 + 44/60 + 51/3600
KLAT = 111.2
KLON = 111.32*math.cos(math.radians(LAT0))   # 약 86.5
TLAT = 39 + 4/60 + 26/3600       # 대성산 (위키백과 상자)
TLON = 125 + 49/60 + 42/3600
def ll2xy(lat, lon):
    return ((lon-LON0)*KLON, (lat-LAT0)*KLAT)
def xy2ll(x, y):
    return (LAT0 + y/KLAT, LON0 + x/KLON)
def grid(xmin, xmax, ymin, ymax, h):
    xs = np.arange(xmin+h/2, xmax, h); ys = np.arange(ymin+h/2, ymax, h)
    X, Y = np.meshgrid(xs, ys); return X, Y
def az(X, Y, cx, cy):
    """compass azimuth (deg, N=0, clockwise) of cell from center"""
    return (np.degrees(np.arctan2(X-cx, Y-cy))) % 360
def dist(X, Y, cx, cy):
    return np.hypot(X-cx, Y-cy)
def ring(X, Y, c, r1, r2):
    d = dist(X, Y, *c); return (d >= r1) & (d <= r2)
def sector(X, Y, c, a1, a2):
    a = az(X, Y, *c); a1 %= 360; a2 %= 360
    return ((a >= a1) & (a <= a2)) if a1 <= a2 else ((a >= a1) | (a <= a2))
def area(m, h): return m.sum()*h*h
def brg(dx, dy): return math.degrees(math.atan2(dx, dy)) % 360
def fmt(v, spec):
    return format(v, spec)

def path_cells(prev,start,goal):
    p=[goal]
    while p[-1]!=start: p.append(prev[p[-1]])
    return p[::-1]
def path_len(p,cell=1.0): 
    return sum(cell*math.hypot(a[0]-b[0],a[1]-b[1]) for a,b in zip(p[:-1],p[1:]))
