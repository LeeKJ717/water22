"""t4_lcp.py - 기법 4: 최소비용 경로·이동시간면 (Tobler 1993 하이킹 함수 + 다익스트라)"""
import numpy as np
import scipy.sparse as sp
from scipy.sparse.csgraph import dijkstra


def tobler_speed_kmh(slope):
    """slope = 오르막 정도(dh/dx, 무차원, 오르막 +). Tobler(1993): 6·exp(-3.5·|S+0.05|) km/h"""
    return 6.0 * np.exp(-3.5 * np.abs(slope + 0.05))


def build_graph(dem, cell_km, passable=None, river_penalty=None, speed=tobler_speed_kmh):
    """8방향 이웃 방향성 그래프. 간선 비용 = 이동 시간(시간).
    dem: 고도(m) 2차원, passable: 불리언(False=바다·호수 등 통행 불가), river_penalty: 칸별 추가 시간(시간)"""
    H, W = dem.shape
    idx = np.arange(H * W).reshape(H, W)
    if passable is None:
        passable = np.ones((H, W), bool)
    rows, cols, cost = [], [], []
    for dy, dx in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
        y0, y1 = max(0, -dy), H - max(0, dy)
        x0, x1 = max(0, -dx), W - max(0, dx)
        a = (slice(y0, y1), slice(x0, x1))
        b = (slice(y0 + dy, y1 + dy), slice(x0 + dx, x1 + dx))
        horiz = cell_km * np.hypot(dy, dx)
        dz = (dem[b] - dem[a]) / 1000.0
        slope = dz / horiz
        v = speed(slope)
        t = np.sqrt(horiz ** 2 + dz ** 2) / v
        if river_penalty is not None:
            t = t + 0.5 * (river_penalty[a] + river_penalty[b])
        ok = passable[a] & passable[b]
        rows.append(idx[a][ok]); cols.append(idx[b][ok]); cost.append(t[ok])
    G = sp.csr_matrix((np.concatenate(cost), (np.concatenate(rows), np.concatenate(cols))), shape=(H * W, H * W))
    return G


def travel_time(G, shape, src_rc, return_pred=False):
    """출발점 (행,열)에서 모든 칸까지의 최단 이동시간(시간)"""
    s = int(src_rc[0] * shape[1] + src_rc[1])
    if return_pred:
        t, pred = dijkstra(G, directed=True, indices=s, return_predecessors=True)
        return t.reshape(shape), pred
    return dijkstra(G, directed=True, indices=s).reshape(shape)


def path_to(pred, shape, src_rc, dst_rc):
    s = src_rc[0] * shape[1] + src_rc[1]
    cur = dst_rc[0] * shape[1] + dst_rc[1]
    out = [cur]
    while cur != s and cur >= 0:
        cur = pred[cur]
        out.append(cur)
    out = out[::-1]
    return [(i // shape[1], i % shape[1]) for i in out if i >= 0]


def isochrone_mask(t_hours, lo_h, hi_h):
    """'~일 걸리는 곳'이라는 서술을 만족하는 칸 (일일 이동 시간 h를 곱해 lo_h~hi_h로 환산해서 넣는다)"""
    return (t_hours >= lo_h) & (t_hours <= hi_h)
