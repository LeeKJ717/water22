"""t8_cross.py - 기법 8: 다자료 교차검증 (로그 풀링, Dempster–Shafer, 충돌 지표, 한 기법 빼기)"""
import numpy as np
import itertools


def _norm(p):
    p = np.asarray(p, float)
    return p / p.sum()


def log_pool(posts, weights=None):
    """독립 전문가의 곱(Hinton, 2002) = 가중 로그 풀링. 한 기법이라도 0이면 그 칸은 사라진다."""
    k = len(posts)
    w = np.ones(k) if weights is None else np.asarray(weights, float)
    lp = sum(wi * np.log(np.asarray(p) + 1e-300) for wi, p in zip(w, posts))
    lp -= lp.max()
    return _norm(np.exp(lp))


def linear_pool(posts, weights=None):
    k = len(posts)
    w = np.ones(k) / k if weights is None else np.asarray(weights, float) / np.sum(weights)
    return _norm(sum(wi * _norm(p) for wi, p in zip(w, posts)))


def overlap(p, q):
    """겹침 계수 Σ min(p,q) (0~1). 1이면 같은 분포."""
    return float(np.minimum(_norm(p), _norm(q)).sum())


def hellinger(p, q):
    p, q = _norm(p), _norm(q)
    return float(np.sqrt(0.5 * ((np.sqrt(p) - np.sqrt(q)) ** 2).sum()))


def kl(p, q, eps=1e-12):
    p, q = _norm(p), _norm(q)
    return float((p * (np.log(p + eps) - np.log(q + eps))).sum())


def conflict_matrix(posts):
    n = len(posts)
    M = np.eye(n)
    for i in range(n):
        for j in range(i + 1, n):
            M[i, j] = M[j, i] = overlap(posts[i], posts[j])
    return M


def leave_one_out(posts, weights=None):
    """한 기법씩 빼고 풀링한 결과의 중심 이동 - 어느 기법이 결론을 끌고 가는지 본다."""
    out = []
    for i in range(len(posts)):
        rest = [p for j, p in enumerate(posts) if j != i]
        w = None if weights is None else [x for j, x in enumerate(weights) if j != i]
        out.append(log_pool(rest, w))
    return out


def dempster(masks, reliab):
    """masks: 각 기법이 지지하는 영역(불리언 지도), reliab: 신뢰도 r_i.
    질량함수 m_i(A_i)=r_i, m_i(전체)=1-r_i 를 Dempster 규칙으로 결합해 칸별 가능도(plausibility)를 낸다.
    반환: (plausibility 지도, 충돌량 K)"""
    n = len(masks)
    shape = masks[0].shape
    full = np.ones(shape, bool)
    # 부분집합 S ⊆ {1..n}: S에 든 기법은 자기 영역을 택하고 나머지는 전체를 택함. 질량 = Π r(S) Π (1-r(not S))
    pl = np.zeros(shape)
    K = 0.0
    for sel in itertools.product([0, 1], repeat=n):
        m = 1.0
        inter = full.copy()
        for i, s in enumerate(sel):
            if s:
                m *= reliab[i]
                inter &= masks[i]
            else:
                m *= (1 - reliab[i])
        if m == 0:
            continue
        if not inter.any():
            K += m
        else:
            pl += m * inter
    if K >= 1 - 1e-12:
        return np.zeros(shape), 1.0
    return pl / (1 - K), K


def credible_overlap(masks):
    """여러 기법의 신뢰 영역이 몇 개나 겹치는지 센 지도 (교차 지지도)"""
    return np.sum(np.stack(masks), axis=0)
