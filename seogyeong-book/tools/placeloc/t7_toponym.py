"""t7_toponym.py - 기법 7: 지명 언어학적 추정 (한국 한자음 독음 원칙, 형태소 공간분포)"""
import numpy as np
from collections import Counter, defaultdict

try:
    import hanja as _hanja
except Exception:        # 한자 사전 라이브러리가 없으면 입력을 그대로 돌려준다(검사에서 경고)
    _hanja = None

_cache = {}


def reading_ko(han):
    """한국 한자음 독음(현대 표기). 병음은 쓰지 않는다. 두음법칙 등 표기 변이는 비교 시 별도 처리."""
    if han in _cache:
        return _cache[han]
    r = _hanja.translate(han, "substitution") if _hanja else han
    _cache[han] = r
    return r


def morph_density(grid, rows, morph, bw_km):
    """형태소(morph)를 포함한 지명들의 공간 핵밀도(가우시안). rows: [(이름, x, y)]"""
    pts = [(x, y) for n, x, y in rows if morph in n]
    d = np.zeros(grid.shape)
    for x, y in pts:
        d += np.exp(-0.5 * ((grid.X - x) ** 2 + (grid.Y - y) ** 2) / bw_km ** 2)
    return d, len(pts)


def morph_ratio(grid, rows, morph, bw_km, alpha=1.0):
    """칸 x에서 '지명 중 morph를 가진 비율'의 평활 추정 = (밀도_m + a·p)/(밀도_all + a)"""
    dm, n_m = morph_density(grid, rows, morph, bw_km)
    da = np.zeros(grid.shape)
    for _, x, y in rows:
        da += np.exp(-0.5 * ((grid.X - x) ** 2 + (grid.Y - y) ** 2) / bw_km ** 2)
    p = n_m / max(1, len(rows))
    return (dm + alpha * p) / (da + alpha), p


def location_likelihood(grid, rows, morphs, bw_km=60.0, alpha=1.0):
    """미지 지명이 가진 형태소들이 모두 관측될 우도 = Π (칸 x에서의 비율 / 전역 비율)  (나이브 베이즈)"""
    L = np.ones(grid.shape)
    for m in morphs:
        r, p = morph_ratio(grid, rows, m, bw_km, alpha)
        L *= r / max(p, 1e-9)
    return L


def learn_char_map(pairs):
    """pairs: [(이전 표기, 이후 표기)] 길이가 같은 쌍만 글자 단위로 정렬해 대응 빈도를 센다.
    예) 고구려계 원지명 → 통일신라 한자식 개명 쌍에서 글자 대응(買→水 등)을 학습하는 데 쓴다."""
    tab = defaultdict(Counter)
    for a, b in pairs:
        if len(a) == len(b):
            for ca, cb in zip(a, b):
                tab[ca][cb] += 1
    return {k: v.most_common() for k, v in tab.items()}


def translate_name(name, table):
    """학습된 대응표로 미지 지명을 개명 후보 문자열로 바꾼다(가장 많은 대응 우선, 없으면 그대로)"""
    out = []
    for c in name:
        out.append(table[c][0][0] if c in table else c)
    return "".join(out)
