"""t6_gazetteer.py - 기법 6: 시공간 지명 사전(gazetteer) 정합"""
from dataclasses import dataclass, field
import numpy as np
from scipy.optimize import linear_sum_assignment
from .t7_toponym import reading_ko


@dataclass
class Record:
    rid: str
    name_han: str
    era_from: float          # 연도(음수=기원전)
    era_to: float
    x: float = np.nan        # km 평면 좌표 (또는 위경도에서 변환한 값)
    y: float = np.nan
    sigma_km: float = 0.0
    kind: str = ""
    source: str = ""
    variants: tuple = field(default_factory=tuple)


@dataclass
class Mention:
    mid: str
    name_han: str
    year_from: float
    year_to: float
    hint_xy: tuple = None    # 본문이 알려 주는 대략 위치(있을 때)
    hint_sigma_km: float = 200.0


def time_overlap(a0, a1, b0, b1):
    lo, hi = max(a0, b0), min(a1, b1)
    span = max(a1 - a0, 1e-9)
    return max(0.0, hi - lo) / span if a1 > a0 else (1.0 if b0 <= a0 <= b1 else 0.0)


def name_sim(m, r):
    if m.name_han == r.name_han or m.name_han in r.variants:
        return 1.0
    if reading_ko(m.name_han) == reading_ko(r.name_han):      # 같은 한국 한자음(이표기)
        return 0.8
    sa, sb = set(m.name_han), set(r.name_han)
    j = len(sa & sb) / max(1, len(sa | sb))
    return 0.5 * j


def score(m, r, w=(0.5, 0.3, 0.2)):
    sn = name_sim(m, r)
    st = time_overlap(m.year_from, m.year_to, r.era_from, r.era_to)
    if m.hint_xy is None or np.isnan(r.x):
        ss = 1.0
    else:
        d = np.hypot(m.hint_xy[0] - r.x, m.hint_xy[1] - r.y)
        ss = float(np.exp(-0.5 * (d / np.hypot(m.hint_sigma_km, r.sigma_km + 1e-9)) ** 2))
    return w[0] * sn + w[1] * st + w[2] * ss, (sn, st, ss)


def candidates(m, gaz, top=5):
    sc = [(score(m, r)[0], r, score(m, r)[1]) for r in gaz]
    sc.sort(key=lambda t: -t[0])
    return sc[:top]


def ambiguity(name_han, year, gaz):
    """같은 시기(year)에 같은 이름을 가진 서로 다른 지점의 수 - 동명이지 위험도"""
    return [r for r in gaz if r.name_han == name_han and r.era_from <= year <= r.era_to]


def align(mentions, gaz, min_score=0.45):
    """언급-사전 일대일 정합(헝가리 알고리즘). 점수 미만은 '정합 실패'로 둔다."""
    S = np.array([[score(m, r)[0] for r in gaz] for m in mentions])
    ri, ci = linear_sum_assignment(-S)
    res = {}
    for i, j in zip(ri, ci):
        res[mentions[i].mid] = (gaz[j], S[i, j]) if S[i, j] >= min_score else (None, S[i, j])
    return res
