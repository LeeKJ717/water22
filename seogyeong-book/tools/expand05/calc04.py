from lib import *
# E1 "10여 리" 세 가지 읽기 x 두 가지 단위 가정
readings = {"좁게": (10,13), "보통": (10,15), "넓게": (10,19)}
units = {"이 장의 구간": (0.36,0.48), "넓은 가정": (0.30,0.50)}
tab = {}
for rn,(a,b) in readings.items():
    for un,(ul,uh) in units.items():
        lo, hi = a*ul, b*uh
        tab[(rn,un)] = (lo,hi,hi-lo, math.pi*(hi**2-lo**2), 0.5*math.radians(45)*(hi**2-lo**2))
def T(r,u,i): return tab[(r,u)][i]
# 추가 기록 오차 +-10%
e_lo, e_hi = 10*0.36*0.9, 15*0.48*1.1
# 평양 점에서 동쪽 끝의 경도
lon_e_lo = LON0 + T("보통","이 장의 구간",0)/KLON
lon_e_hi = LON0 + T("보통","이 장의 구간",1)/KLON
lon_w_lo = LON0 - T("보통","이 장의 구간",0)/KLON
lon_w_hi = LON0 - T("보통","이 장의 구간",1)/KLON
# 격자 확인
h=0.1
X,Y = grid(-12,12,-12,12,h)
c=(0,0)
m = ring(X,Y,c,3.6,7.2)&sector(X,Y,c,67.5,112.5)
grid_area = area(m,h)
wid_ratio = T("넓게","이 장의 구간",2)/T("좁게","이 장의 구간",2)
if __name__=="__main__":
    for k,v in tab.items(): print(k,[round(x,2) for x in v])
    print(e_lo,e_hi,lon_e_lo,lon_e_hi,lon_w_lo,lon_w_hi,grid_area,wid_ratio,KLON)
