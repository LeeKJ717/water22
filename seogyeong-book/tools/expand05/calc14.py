from lib import *
# C7: 두 읍에서 각각 40리 -> 두 개의 렌즈 (대칭)
h=0.1; X,Y=grid(-25,50,-25,25,h)
A=(0,0); B=(26,0)
rr=(38*U_LO,42*U_HI)          # 반올림 38~42리
m1=ring(X,Y,A,*rr); m2=ring(X,Y,B,*rr)
both=m1&m2
a1,a2,a12=area(m1,h),area(m2,h),area(both,h)
lab,nc=ndimage.label(both)
sizes=[area(lab==i,h) for i in range(1,nc+1)]
cents=[(X[lab==i].mean(),Y[lab==i].mean()) for i in range(1,nc+1)]
north=both&(Y>0); a_north=area(north,h)
# 공유 단위: 어떤 u에 대해 d1,d2 모두 40u*[0.95,1.05] (+-5%) 를 만족
def shared_area(rec=0.05):
    d1=dist(X,Y,*A); d2=dist(X,Y,*B)
    ok=np.zeros_like(X,dtype=bool)
    for u in np.linspace(U_LO,U_HI,97):
        lo,hi=40*u*(1-rec),40*u*(1+rec)
        ok |= (d1>=lo)&(d1<=hi)&(d2>=lo)&(d2<=hi)
    return area(ok,h)
sh=shared_area(0.05)
ind=area(ring(X,Y,A,40*U_LO*0.95,40*U_HI*1.05)&ring(X,Y,B,40*U_LO*0.95,40*U_HI*1.05),h)
# 렌즈 이론: 두 원 교점 (r=평균)
rm=40*(U_LO+U_HI)/2
d=26.0
ycross=math.sqrt(rm**2-(d/2)**2)
# C8: 역참 chain, A=0, D=33
hop=(27*U_LO,33*U_HI)
Dpos=33.0
def inter(p,q): return (max(p[0],q[0]),min(p[1],q[1]))
def add(p,q): return (p[0]+q[0],p[1]+q[1])
def sub(p,q): return (p[0]-q[1],p[1]-q[0])
B0=hop; C0=sub((Dpos,Dpos),hop)
hist=[("처음",B0,C0)]
Bc,Cc=B0,C0
for it in range(5):
    Cn=inter(Cc,add(Bc,hop)); Bn=inter(Bc,sub(Cn,hop))
    if (Bn,Cn)==(Bc,Cc): break
    Bc,Cc=Bn,Cn; hist.append((f"{it+1}회",Bc,Cc))
Bfin,Cfin=Bc,Cc
# 공유 단위 + 반올림 (r_i in [0.9,1.1])
us=np.linspace(U_LO,U_HI,481)
Bs=[];Cs=[];Uok=[]
rg=np.linspace(0.9,1.1,81)
for u in us:
    for r1 in rg:
        for r2 in rg:
            r3=1.1/u - r1 - r2   # 30u(r1+r2+r3)=33
            if 0.9-1e-9<=r3<=1.1+1e-9:
                Bs.append(30*u*r1); Cs.append(30*u*(r1+r2)); Uok.append(u)
Bsh=(min(Bs),max(Bs)); Csh=(min(Cs),max(Cs)); Ush=(min(Uok),max(Uok))
# 단순 확인: 처음 범위 폭 vs 마지막
wB0=B0[1]-B0[0]; wBf=Bfin[1]-Bfin[0]; wBs=Bsh[1]-Bsh[0]
wC0=C0[1]-C0[0]; wCf=Cfin[1]-Cfin[0]; wCs=Csh[1]-Csh[0]
# 누적 폭 (끝점 모를 때)
cum=[(k,k*hop[0],k*hop[1],k*(hop[1]-hop[0])) for k in range(1,6)]
# C9: 세 문헌
T=(21.0,5.0)
Aa=(0,0); Bb=(10,-30); Cc_=(30,40)
def lay(X,Y,h):
    mA=ring(X,Y,Aa,45*U_LO,55*U_HI)&sector(X,Y,Aa,67.5,112.5)
    mB=ring(X,Y,Bb,85*U_LO,95*U_HI)&sector(X,Y,Bb,-22.5,22.5)
    mC=ring(X,Y,Cc_,35*U_LO,45*U_HI)&sector(X,Y,Cc_,112.5,157.5)
    return mA,mB,mC
h9=0.1; X9,Y9=grid(-10,60,-45,60,h9)
mA,mB,mC=lay(X9,Y9,h9)
score=mA.astype(int)+mB+mC
areas={k:area(score==k,h9) for k in (0,1,2,3)}
aA,aB,aC=area(mA,h9),area(mB,h9),area(mC,h9)
aAB,aAC,aBC,aABC=area(mA&mB,h9),area(mA&mC,h9),area(mB&mC,h9),area(mA&mB&mC,h9)
tA=(dist(np.array([T[0]]),np.array([T[1]]),*Aa)[0], brg(T[0]-Aa[0],T[1]-Aa[1]))
tB=(math.hypot(T[0]-Bb[0],T[1]-Bb[1]), brg(T[0]-Bb[0],T[1]-Bb[1]))
tC=(math.hypot(T[0]-Cc_[0],T[1]-Cc_[1]), brg(T[0]-Cc_[0],T[1]-Cc_[1]))
# T가 각 제약 만족?
def ok_at(P):
    x,y=P; X1=np.array([[x]]);Y1=np.array([[y]]); a,b,c=lay(X1,Y1,0.1); return bool(a[0,0]),bool(b[0,0]),bool(c[0,0])
tok=ok_at(T)
# 2점 이상 만족하는 영역 중 T 포함?
if __name__=="__main__":
    print(rr,a1,a2,a12,nc,sizes,cents,a_north,sh,ind,ycross)
    print(hist,Bfin,Cfin,Bsh,Csh,Ush,wB0,wBf,wBs,wC0,wCf,wCs)
    print(cum)
    print(areas,aA,aB,aC,aAB,aAC,aBC,aABC,tA,tB,tC,tok)
