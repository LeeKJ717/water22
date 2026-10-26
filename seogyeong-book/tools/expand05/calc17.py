from lib import *
# Q 단위를 좁히는 효과
u_wide=(0.30,0.50); u_this=(U_LO,U_HI)
r10_wide=(10*u_wide[0],15*u_wide[1]); r10_this=(10*U_LO,15*U_HI)
w_ratio=(r10_wide[1]-r10_wide[0])/(r10_this[1]-r10_this[0])
# 방위 반폭
half8=360/16
# 영역 넓이 vs 폭 : 폭 6 -> 3 이면 넓이?
def ringA(r,R): return math.pi*(R*R-r*r)
a_base=ringA(18,24); a_half=ringA(19.5,22.5)
# 칸 크기 0.1 칸 수
cells_per_km2=1/0.01
# 확률 vs 구간: 균일 vs 중심 가중 예

import calc12
c2_lo=min(r[2] for r in calc12.c2 if r[1].startswith('사흘 길 ('))
c2_hi=max(r[3] for r in calc12.c2)
c1_err=calc12.err; c1_max=calc12.maxdist
