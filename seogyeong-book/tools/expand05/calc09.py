from lib import *
L12=(12*U_LO,12*U_HI)                  # 성벽 길이 구간
WLO,WHI=1.0,1.3                        # 굽음 계수 (길이/직선거리) 가정
DEL=(L12[0]/WHI, L12[1]/WLO)           # 직선거리 구간
ring_area=math.pi*(DEL[1]**2-DEL[0]**2)
sec_area=0.5*(math.pi/4)*(DEL[1]**2-DEL[0]**2)
h=0.1; X,Y=grid(-8,8,-8,8,h)
m=ring(X,Y,(0,0),*DEL)&sector(X,Y,(0,0),67.5,112.5)
grid_sec=area(m,h)
# P가 가로세로 1km 정사각형(+-0.5) 안일 때의 Q 영역 (합집합)
X2,Y2=grid(-8,9,-8,8,h)
mm=np.zeros_like(X2,dtype=bool)
for px in np.linspace(-0.5,0.5,6):
    for py in np.linspace(-0.5,0.5,6):
        mm |= ring(X2,Y2,(px,py),*DEL)&sector(X2,Y2,(px,py),67.5,112.5)
union_area=area(mm,h)
# 1차원 전파
def inter(p,q):
    lo,hi=max(p[0],q[0]),min(p[1],q[1]); return (lo,hi)
P0=(0,2); Q0=(3,12)
Q1=inter(Q0,(P0[0]+DEL[0],P0[1]+DEL[1]))
P1=inter(P0,(Q1[0]-DEL[1],Q1[1]-DEL[0]))
Q2=inter(Q1,(P1[0]+DEL[0],P1[1]+DEL[1]))
# 단위 역산: 가상 실측 직선거리 4.8~5.0 km
meas=(4.8,5.0)
u_from=(meas[0]*WLO/12, meas[1]*WHI/12)
u_new=inter(u_from,(U_LO,U_HI))
width_before=U_HI-U_LO; width_after=u_new[1]-u_new[0]
# 굽음 계수를 1.0으로 고정(곧은 성벽)이라면
u_straight=(meas[0]/12,meas[1]/12)
if __name__=="__main__":
    print(L12,DEL,ring_area,sec_area,grid_sec,union_area,P1,Q1,Q2,u_from,u_new,width_before,width_after,u_straight)
