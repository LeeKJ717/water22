"""t2_georef.py - 기법 2: 고지도·고문헌 기준점의 기하 보간(닮음·아핀·박판스플라인)"""
import numpy as np


def fit_similarity(src, dst):
    """Helmert 닮음변환(회전·균등 축척·이동). 복소수 선형 최소제곱."""
    s = src[:, 0] + 1j * src[:, 1]
    d = dst[:, 0] + 1j * dst[:, 1]
    A = np.c_[s, np.ones(len(s))]
    (a, b), *_ = np.linalg.lstsq(A, d, rcond=None)
    def f(p):
        z = p[:, 0] + 1j * p[:, 1]
        w = a * z + b
        return np.c_[w.real, w.imag]
    return f


def fit_affine(src, dst):
    A = np.c_[src, np.ones(len(src))]
    M, *_ = np.linalg.lstsq(A, dst, rcond=None)
    return lambda p: np.c_[p, np.ones(len(p))] @ M


def _U(r2):
    with np.errstate(divide="ignore", invalid="ignore"):
        u = np.where(r2 == 0, 0.0, 0.5 * r2 * np.log(r2))   # r^2 log r
    return u


def fit_tps(src, dst, lam=0.0):
    """박판스플라인(Bookstein, 1989). lam>0이면 정칙화(기준점 오차를 흡수).
    lam은 핵행렬 비대각 원소의 평균 크기에 대한 상대값이므로 자료의 단위와 무관하게 비교할 수 있다."""
    n = len(src)
    d2 = ((src[:, None, :] - src[None, :, :]) ** 2).sum(-1)
    K0 = _U(d2)
    scale = float(np.abs(K0[np.triu_indices(n, 1)]).mean())
    K = K0 + lam * scale * np.eye(n)
    P = np.c_[np.ones(n), src]
    L = np.zeros((n + 3, n + 3))
    L[:n, :n], L[:n, n:], L[n:, :n] = K, P, P.T
    Y = np.zeros((n + 3, 2))
    Y[:n] = dst
    W = np.linalg.solve(L + 1e-12 * np.eye(n + 3), Y)

    def f(p):
        p = np.atleast_2d(p)
        d2p = ((p[:, None, :] - src[None, :, :]) ** 2).sum(-1)
        return _U(d2p) @ W[:n] + np.c_[np.ones(len(p)), p] @ W[n:]
    return f


def loocv(fitter, src, dst, **kw):
    """기준점 하나씩 빼고 적합 → 뺀 점의 예측 잔차(km). 모형 선택의 기준."""
    res = []
    for i in range(len(src)):
        m = np.ones(len(src), bool)
        m[i] = False
        f = fitter(src[m], dst[m], **kw)
        res.append(f(src[i:i + 1])[0] - dst[i])
    res = np.array(res)
    return res, float(np.sqrt((res ** 2).sum(1).mean()))


def bootstrap_target(fitter, src, dst, target_src, n=500, seed=0, **kw):
    """기준점 재표집으로 목표 지점 좌표의 분포를 얻는다."""
    rng = np.random.default_rng(seed)
    out = []
    N = len(src)
    for _ in range(n):
        idx = np.unique(rng.integers(0, N, N))     # 중복 기준점은 박판스플라인 행렬을 특이하게 만들므로 제거
        if len(idx) < 6:
            continue
        try:
            f = fitter(src[idx], dst[idx], **kw)
            out.append(f(target_src[None, :])[0])
        except np.linalg.LinAlgError:
            continue
    return np.array(out)


def grid_distortion(f, xlim, ylim, n=11):
    """격자 왜곡도 - 일정한 격자가 변환 뒤 어떻게 휘는지(그림용)"""
    gx = np.linspace(*xlim, n)
    gy = np.linspace(*ylim, n)
    lines = []
    for x in gx:
        lines.append(f(np.c_[np.full(n * 5, x), np.linspace(*ylim, n * 5)]))
    for y in gy:
        lines.append(f(np.c_[np.linspace(*xlim, n * 5), np.full(n * 5, y)]))
    return lines
