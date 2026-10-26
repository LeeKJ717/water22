from lib import *
tx,ty = ll2xy(TLAT,TLON)       # 대성산 (G1 원점 기준 km)
tdist = math.hypot(tx,ty); tbrg = brg(tx,ty)
# 대성산 -> 북동 부채꼴(8방위 22.5~67.5), 창 반지름 5,10,20
def sa(w,R): return 0.5*math.radians(2*w)*R*R
SA={ (w,R):sa(w,R) for w in (22.5,45) for R in (5,10,20)}
# 기준이 점이 아니라 산체(반지름 rho)일 때: 꼭짓점이 원판 안 -> 합집합 면적 (창 R=10 안쪽 측정 위해 큰 창에서 측정 후 거리 제한 대신 '꼭짓점에서 R 이내' 합집합)
h=0.1
X,Y = grid(-30,40,-30,40,h)
def union_area(rho, R, w=22.5):
    # 점 p가 해: 어떤 꼭짓점 c (|c-T|<=rho)에 대해 p가 c에서 NE 부채꼴이고 |p-c|<=R
    # 원판 위 꼭짓점을 이산 표본으로
    m=np.zeros_like(X,dtype=bool)
    if rho==0: pts=[(tx,ty)]
    else:
        pts=[]
        for dx in np.arange(-rho,rho+0.01,rho/6):
            for dy in np.arange(-rho,rho+0.01,rho/6):
                if dx*dx+dy*dy<=rho*rho+1e-9: pts.append((tx+dx,ty+dy))
    for c in pts:
        m |= sector(X,Y,c,45-w,45+w) & (dist(X,Y,*c)<=R)
    return area(m,h)
UN={rho:union_area(rho,10) for rho in (0,2,4)}
# "성 가운데 안학궁 옛터": 장안성 크기 11.85 km2 -> 등가원 반지름
A_total=(25+130+300+730)/100.0
Req=math.sqrt(A_total/math.pi)
# 규모 눈금: 부채꼴 반지름 10km 영역 대비 성 면적
frac=A_total/SA[(22.5,10)]
# E1 보통읽기 최대 7.2 km 대비
if __name__=="__main__":
    print(tx,ty,tdist,tbrg,SA,UN,A_total,Req,frac)
