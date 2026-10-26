from lib import *
def inter(p,q): return (max(p[0],q[0]),min(p[1],q[1]))
def add(p,q): return (p[0]+q[0],p[1]+q[1])
def sub(p,q): return (p[0]-q[1],p[1]-q[0])
# P1 남쪽으로 30여 리 (30~36리), 단위 이 장
p1=(30*U_LO,36*U_HI); p1_w=p1[1]-p1[0]
p1_sec=0.5*(math.pi/4)*(p1[1]**2-p1[0]**2)
p1_ring=math.pi*(p1[1]**2-p1[0]**2)
# P2 사슬
Xr=(10,25); Yr=(-1e9,1e9); Zr=(30,34); dXY=(8,12); dYZ=(5,9)
Yr=add(Xr,dXY)               # 처음 Y = X+dXY
Yr=inter(Yr,sub(Zr,dYZ))
hist=[("처음",Xr,Yr,Zr)]
for it in range(6):
    Y1=inter(Yr,add(Xr,dXY)); Y1=inter(Y1,sub(Zr,dYZ))
    X1=inter(Xr,sub(Y1,dXY)); Z1=inter(Zr,add(Y1,dYZ))
    Y2=inter(Y1,add(X1,dXY)); Y2=inter(Y2,sub(Z1,dYZ))
    new=(X1,Y2,Z1)
    if new==(Xr,Yr,Zr): break
    Xr,Yr,Zr=new; hist.append((f"{it+1}회",Xr,Yr,Zr))
p2=hist[-1]
# P3 가상 석: 서쪽으로 돌아 15리, 굽음 [1.0,1.3], 실측 직선 5.8~6.0
L15=(15*U_LO,15*U_HI); DEL15=(L15[0]/1.3,L15[1]/1.0)
meas=(5.8,6.0); u3=(meas[0]*1.0/15, meas[1]*1.3/15); u3n=inter(u3,(U_LO,U_HI))
# P4 80리,50리 차이
ind4=(80*U_LO-50*U_HI, 80*U_HI-50*U_LO); sh4=(30*U_LO,30*U_HI)
# P5 이틀 반 길
p5=(2.5*25/1.4, 2.5*40/1.1)
# P6 최대 CSP
h=0.1; X,Y=grid(-25,60,-25,60,h)
mA=ring(X,Y,(0,0),20,26); mB=ring(X,Y,(30,0),20,26); mC=ring(X,Y,(15,40),10,14)
sc=mA.astype(int)+mB+mC
p6={k:area(sc==k,h) for k in (0,1,2,3)}
p6_ab=area(mA&mB,h); p6_ac=area(mA&mC,h); p6_bc=area(mB&mC,h)
# P8 평양 점에서 동 5리, 북 8리
dx=(5*U_LO,5*U_HI); dy=(8*U_LO,8*U_HI)
lon8=(LON0+dx[0]/KLON, LON0+dx[1]/KLON); lat8=(LAT0+dy[0]/KLAT, LAT0+dy[1]/KLAT)
# P9 □三里
p9=[(n,n*U_LO,n*U_HI) for n in (3,13,23,33)]
# P10 후보 산
cands=[("갑산",6,3,1.5),("을산",-8,2,2.0),("병산",12,-1,2.5),("정산",9,9,2.0),("무산",3,-10,1.5)]
p10=[]
for n,x,y,r in cands:
    d=math.hypot(x,y); a=brg(x,y); half=math.degrees(math.asin(min(1,r/d)))
    diff=abs((a-90+180)%360-180); p10.append((n,x,y,r,d,a,half,diff,diff<=22.5+half and d<=15))
if __name__=="__main__":
    print(p1,p1_w,p1_sec,p1_ring); print(hist); print(L15,DEL15,u3,u3n); print(ind4,sh4,p5); print(p6,p6_ab,p6_ac,p6_bc)
    print(lon8,lat8,p9); [print(r) for r in p10]
# P7 시간
p7_in=586-552; p7_left=593-586; p7_incl=593-552+1
p6_win=85*85
p4_ratio=((ind4[1]-ind4[0])/(sh4[1]-sh4[0]))
p2_chk=(inter(add(Xr,dXY),sub(Zr,dYZ)))
