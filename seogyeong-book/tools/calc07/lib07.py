import numpy as np, math, re
from scipy.special import i0
WIDE = 1/math.log(40)
R = {}
TAB = {}
def zpdf(z, s): return np.exp(-0.5*(z/s)**2)/(s*math.sqrt(2*math.pi))
def lik_dist(L, d, u, s):
    d = np.maximum(d, 1e-9)
    return zpdf(np.log(L)-np.log(d/u), s)
def lik_mix(L, d, u, s, eps):
    return (1-eps)*lik_dist(L, d, u, s)+eps*WIDE
def bearing(dx, dy):  # compass: north=0, east=90 (radians)
    return np.arctan2(dx, dy)
def vm(theta, phi, kappa):
    return np.exp(kappa*(np.cos(theta-phi)-1))/(2*np.pi*i0(kappa)*np.exp(-kappa))
def lik_dir(dx, dy, deg, kappa):
    return vm(bearing(dx, dy), math.radians(deg), kappa)
def hpd_mask(P, level):
    f = P.ravel(); idx = np.argsort(-f); c = np.cumsum(f[idx]); n = int(np.searchsorted(c, level))+1
    m = np.zeros(f.size, bool); m[idx[:n]] = True
    return m.reshape(P.shape)
def norm(P): return P/P.sum()
def fmt_tab(head, rows, align=None):
    out = ["| "+" | ".join(head)+" |", "|"+"|".join(["---"]*len(head))+"|"]
    for r in rows: out.append("| "+" | ".join(str(c) for c in r)+" |")
    return "\n".join(out)
def put(k, v): R[k] = v
def ptab(k, head, rows): TAB[k] = fmt_tab(head, rows)
def render(text):
    def t(m): return TAB[m.group(1)]
    text = re.sub(r"\[\[T:([A-Za-z0-9_.]+)\]\]", t, text)
    def f(m):
        key, spec = m.group(1), m.group(2)
        v = R[key]
        return format(v, spec) if spec else str(v)
    return re.sub(r"\[\[([A-Za-z0-9_.\u3131-\u318e\uac00-\ud7a3]+)(?::([^\]]+))?\]\]", f, text)
