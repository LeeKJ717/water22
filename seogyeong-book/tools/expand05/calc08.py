from lib import *
tx,ty = ll2xy(TLAT,TLON)
h=0.1
X,Y=grid(-60,60,-40,80,h)
sec_T = sector(X,Y,(tx,ty),22.5,67.5)          # E6: 대성산 NE
def secN(c, w=22.5): return sector(X,Y,c,-w,w)
W40=dist(X,Y,0,0)<=40
def ov(c=(0,0), wN=22.5):
    b=sec_T&secN(c,wN)&W40
    return area(b,h), (dist(X,Y,0,0)[b].min() if b.any() else None)
base=ov()
tab_w={w:ov((0,0),w) for w in (22.5,25,30,35,45)}
tab_s={d:ov((d,0),22.5) for d in (0,3,4,5,6,8)}
# 이론 값: 경계선 x = tan(22.5) y + c , 대성산 경계 c_T
t22=math.tan(math.radians(22.5)); cT=tx-t22*ty
def inter_dist(wN):
    tw=math.tan(math.radians(wN))
    # T boundary: x = t22*y + cT ; N boundary: x = tw*y -> y=cT/(tw-t22)
    if tw<=t22: return None
    y=cT/(tw-t22); x=tw*y; return math.hypot(x,y)
d30=inter_dist(30); d45=inter_dist(45)
# 대성산이 평양 점의 북쪽 부채꼴 밖임 (방위 47.7도)
bT=brg(tx,ty)
# 조합: 8방위 읽기 동북/북 사이에서 벗어나는 각
if __name__=="__main__":
    print(base, tab_w, tab_s, cT, d30, d45, bT)
W20=dist(X,Y,0,0)<=20
a_T20=area(sec_T&W20,h); a_N20=area(secN((0,0))&W20,h); a_both20=area(sec_T&secN((0,0))&W20,h)
perp=cT*math.cos(math.radians(22.5))
