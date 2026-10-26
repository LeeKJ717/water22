"""t5_graph.py - 기법 5: 지명 그래프와 앵커 MDS (알려진 노드 고정, 미지 노드 위치 추정)"""
import numpy as np
import networkx as nx
from scipy.optimize import least_squares


def build_graph(edges):
    """edges: [(a, b, lo_km, hi_km, w)] → 무방향 그래프(간선 길이=구간 중앙값, 가중=w)"""
    G = nx.Graph()
    for a, b, lo, hi, w in edges:
        G.add_edge(a, b, lo=lo, hi=hi, d=(lo + hi) / 2.0, w=w)
    return G


def centrality_table(G):
    deg = nx.degree_centrality(G)
    btw = nx.betweenness_centrality(G, weight="d")
    pr = nx.pagerank(G, weight="w")
    return {n: dict(degree=deg[n], betweenness=btw[n], pagerank=pr[n]) for n in G.nodes}


def anchored_mds(G, anchors, init=None, seed=0, restarts=20, mode="mid"):
    """anchors: {노드: (x,y)}. 미지 노드 좌표를 간선 길이와의 편차 제곱합이 최소가 되게 푼다.
    mode="mid": 구간 중앙값과의 편차(점 추정, 유일해). mode="interval": 구간 [lo,hi]를 벗어난 만큼만 벌점(구간 안이면 0이라 해가 한 점이 아니라 집합).
    다중 시작점으로 국소해를 피한다."""
    unk = [n for n in G.nodes if n not in anchors]
    if not unk:
        return {}, 0.0
    ix = {n: i for i, n in enumerate(unk)}
    rng = np.random.default_rng(seed)
    A = np.array(list(anchors.values()))
    lo_xy, hi_xy = A.min(0) - 100, A.max(0) + 100

    def pos(z, n):
        return anchors[n] if n in anchors else z[2 * ix[n]:2 * ix[n] + 2]

    def resid(z):
        r = []
        for a, b, d in G.edges(data=True):
            dist = np.hypot(*(np.asarray(pos(z, a)) - np.asarray(pos(z, b))))
            if mode == "mid":
                e = dist - d["d"]
            else:
                e = 0.0 if d["lo"] <= dist <= d["hi"] else (d["lo"] - dist if dist < d["lo"] else dist - d["hi"])
            r.append(np.sqrt(d["w"]) * e)
        return np.array(r)

    best = None
    for k in range(restarts):
        z0 = rng.uniform(np.tile(lo_xy, len(unk)), np.tile(hi_xy, len(unk))) if init is None or k else np.ravel([init[n] for n in unk])
        sol = least_squares(resid, z0)
        if best is None or sol.cost < best.cost:
            best = sol
    est = {n: tuple(best.x[2 * ix[n]:2 * ix[n] + 2]) for n in unk}
    return est, float(best.cost)


def jackknife_edges(G, anchors, target, n_drop=1, seed=0, reps=60):
    """간선 일부를 빼고 다시 풀어 목표 노드 위치의 흔들림을 본다(증거 한 건에 얼마나 기대는가)."""
    rng = np.random.default_rng(seed)
    edges = list(G.edges(data=True))
    pts = []
    for _ in range(reps):
        drop = set(rng.choice(len(edges), n_drop, replace=False))
        H = nx.Graph()
        for i, (a, b, d) in enumerate(edges):
            if i not in drop:
                H.add_edge(a, b, **d)
        if target not in H or any(n not in H for n in anchors if H.degree(n) == 0):
            continue
        est, _ = anchored_mds(H, {k: v for k, v in anchors.items() if k in H}, seed=int(rng.integers(1e6)), restarts=6)
        if target in est:
            pts.append(est[target])
    return np.array(pts)
