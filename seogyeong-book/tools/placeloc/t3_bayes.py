"""t3_bayes.py - 기법 3: 베이즈 추론과 몬테카를로 (격자 사후분포 + 단위 길이 불확실성 주변화)"""
import numpy as np
from .geo import ang_diff


def normalize(w):
    s = w.sum()
    assert s > 0, "사후분포 전체가 0"
    return w / s


def prior_uniform(grid, mask=None):
    w = np.ones(grid.shape) if mask is None else np.asarray(mask, float)
    return normalize(w)


def prior_gaussian(grid, x0, y0, sigma):
    return normalize(np.exp(-0.5 * ((grid.X - x0) ** 2 + (grid.Y - y0) ** 2) / sigma ** 2))


def lik_distance(grid, x, y, d_obs, rel_sigma, unit_samples=None):
    """관측 거리 d_obs(원문 수치×단위)에 대한 로그정규 우도. 관측 log d_obs = log d(x) - log u + 오차 이므로 x에 대한 우도에는 1/d 항이 없다.
    unit_samples(단위 길이 표본, km/단위)를 주면 d_obs가 '원문 수치'이고 단위를 주변화한다."""
    d = grid.dist(x, y) + 1e-9
    if unit_samples is None:
        mu = np.log(d_obs)
        return np.exp(-0.5 * ((np.log(d) - mu) / rel_sigma) ** 2)
    L = np.zeros(grid.shape)
    for u in unit_samples:
        mu = np.log(d_obs * u)
        L += np.exp(-0.5 * ((np.log(d) - mu) / rel_sigma) ** 2)
    return L / len(unit_samples)


def lik_interval(grid, x, y, lo, hi, soft=0.1):
    """'~리 이상 ~리 이내'처럼 구간으로 주어진 거리: 경계가 soft(상대폭)만큼 흐린 상자 우도"""
    d = grid.dist(x, y)
    def sig(z):
        return 1.0 / (1.0 + np.exp(-z))
    s_lo = max(soft * lo, 1e-6)
    s_hi = max(soft * hi, 1e-6)
    return sig((d - lo) / s_lo) * sig((hi - d) / s_hi)


def lik_bearing(grid, x, y, az_obs, kappa):
    """방위 관측에 대한 폰 미제스 우도 (kappa: 집중도, 8방위 서술이면 약 8~15)"""
    a = np.radians(ang_diff(grid.azimuth(x, y), az_obs))
    return np.exp(kappa * (np.cos(a) - 1.0))


def posterior(prior, liks):
    p = prior.copy()
    for L in liks:
        p = p * (L + 1e-300)
        p = p / p.sum()
    return normalize(p)


def hpd_mask(post, level=0.95):
    """최고사후밀도(HPD) 영역: 확률이 큰 칸부터 level이 될 때까지"""
    flat = post.ravel()
    order = np.argsort(flat)[::-1]
    c = np.cumsum(flat[order])
    k = int(np.searchsorted(c, level)) + 1
    m = np.zeros(flat.shape, bool)
    m[order[:k]] = True
    return m.reshape(post.shape)


def summarize(grid, post, levels=(0.5, 0.95)):
    iy, ix = np.unravel_index(np.argmax(post), post.shape)
    mean = grid.centroid(post)
    out = dict(map_xy=(float(grid.xs[ix]), float(grid.ys[iy])), mean_xy=(float(mean[0]), float(mean[1])))
    for lv in levels:
        out[f"hpd{int(lv*100)}_km2"] = grid.area(hpd_mask(post, lv))
    return out


def metropolis(logpost, x0, n=20000, step=5.0, seed=0):
    """랜덤워크 메트로폴리스(Metropolis et al., 1953). 격자 사후분포 검산용."""
    rng = np.random.default_rng(seed)
    x = np.array(x0, float)
    lp = logpost(x)
    out, acc = [], 0
    for _ in range(n):
        y = x + rng.normal(0, step, 2)
        lq = logpost(y)
        if np.log(rng.random()) < lq - lp:
            x, lp = y, lq
            acc += 1
        out.append(x.copy())
    return np.array(out), acc / n


def posterior_shared_unit(grid, prior, dists, rel_sigma, units, extra=None):
    """거리 서술들이 '하나의 단위 길이'를 공유할 때의 사후분포.
    p(x|증거) ∝ prior(x) · Σ_u p(u) Π_k LN(log d_k(x) | log(원문수치_k · u), σ)  -- u는 증거마다 따로 뽑지 않고 함께 뽑는다.
    dists: [(x, y, 원문수치)], units: 단위 길이 후보(균등 사전), extra: 곱해 줄 추가 우도(예: 하천 근접)"""
    logs = []
    for u in units:
        ll = np.zeros(grid.shape)
        for (x, y, dobs) in dists:
            d = grid.dist(x, y) + 1e-9
            ll += -0.5 * ((np.log(d) - np.log(dobs * u)) / rel_sigma) ** 2
        logs.append(ll)
    logs = np.array(logs)
    lik = np.exp(logs - logs.max()).sum(axis=0)       # 전체 최댓값으로 규격화해 언더플로 방지(상수배는 정규화에서 사라짐)
    post = prior * lik
    if extra is not None:
        post = post * extra
    return normalize(post)


def posterior_shared_unit_robust(grid, prior, dists, rel_sigma, units, eps=0.1, d_range_li=1000.0, extra=None):
    """필사·판각 오류에 견디는 사후분포: 각 거리 서술이 확률 eps로 '아무 값이나'(균등, 범위 d_range_li 리)일 수 있다고 본다.
    증거 k의 우도 = (1-eps)·LN(원문수치|x,u) + eps/d_range_li  (원문수치 공간에서 정규화된 밀도). 단위 길이 u는 공유."""
    logs = []
    for u in units:
        ll = np.zeros(grid.shape)
        for (x, y, dobs) in dists:
            d = grid.dist(x, y) + 1e-9
            # 관측 log(dobs) ~ N(log(d/u), sigma)  →  dobs의 밀도 = N(log dobs; log(d/u), s)/(dobs)
            dens = np.exp(-0.5 * ((np.log(dobs) - np.log(d / u)) / rel_sigma) ** 2) / (rel_sigma * np.sqrt(2 * np.pi) * dobs)
            ll += np.log((1 - eps) * dens + eps / d_range_li)
        logs.append(ll)
    logs = np.array(logs)
    lik = np.exp(logs - logs.max()).sum(axis=0)
    post = prior * lik
    if extra is not None:
        post = post * extra
    return normalize(post)
