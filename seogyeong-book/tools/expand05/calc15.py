from lib import *
# C10: 거리 크기별 폭
Ls=[10,30,50,100,200,490]
c10=[]
for L in Ls:
    a=(L*U_LO,L*U_HI); b=(L*U_LO*0.9,L*U_HI*1.1)
    wa=a[1]-a[0]; wb=b[1]-b[0]
    rela=wa/((a[0]+a[1])/2); relb=wb/((b[0]+b[1])/2)
    ring_b=math.pi*(b[1]**2-b[0]**2)
    c10.append((L,a,wa,rela,b,wb,relb,ring_b,ring_b/160000))
# 한 기록 +-25% (장 앞부분 값) 490리
b25=(490*U_LO*0.75,490*U_HI*1.25)
# C11 (가) 순환
D=(20*U_LO,20*U_HI)
sum3=(3*D[0],3*D[1])
# (나) 기준점 어긋남 Monte Carlo
rng=np.random.default_rng(12345)
N=200000
ang=rng.uniform(0,2*np.pi,N); rad=rng.uniform(18.0,24.0,N)
tx=rad*np.cos(ang); ty=rad*np.sin(ang)
shift_tab=[]
for s in (0,1,2,3,5,8):
    d2=np.hypot(tx-s,ty)
    keep=((d2>=18.0)&(d2<=24.0)).mean()
    shift_tab.append((s,keep))
# (다) 근처
near=[]
for L in (5,10,20):
    lo,hi=L*U_LO,L*U_HI
    near.append((L,hi,math.pi*hi*hi))
# (라) 공유 오류
h=0.1; X,Y=grid(-45,60,-20,70,h)
Aa=(0,0); Bb=(-30,10); Cc=(-5,55); Dd=(25,45)
T=(21.0,5.0); W=(-5.0,25.0)
mA=ring(X,Y,Aa,45*U_LO,55*U_HI)&sector(X,Y,Aa,67.5,112.5)
mB=ring(X,Y,Bb,65*U_LO,75*U_HI)&sector(X,Y,Bb,22.5,67.5)
mC=ring(X,Y,Cc,65*U_LO,75*U_HI)&sector(X,Y,Cc,157.5,202.5)
mD=ring(X,Y,Dd,80*U_LO,90*U_HI)&sector(X,Y,Dd,213.5,258.5)
sc=mA.astype(int)+mB+mC+mD
a3=area(sc==3,h); a4=area(sc==4,h); a1=area(sc==1,h); a2=area(sc==2,h)
def at(P):
    x,y=P; i=np.argmin(abs(Y[:,0]-y)); j=np.argmin(abs(X[0,:]-x)); return int(sc[i,j]), (bool(mA[i,j]),bool(mB[i,j]),bool(mC[i,j]),bool(mD[i,j]))
sT=at(T); sW=at(W)
# 가중: B,C,D 는 한 출처 -> 각 1/3
wsc=mA*1.0+(mB*1.0+mC*1.0+mD*1.0)/3
wmax=wsc.max()
a_wmax=area(wsc>=wmax-1e-9,h)
wT=wsc[np.argmin(abs(Y[:,0]-T[1])),np.argmin(abs(X[0,:]-T[0]))]
wW=wsc[np.argmin(abs(Y[:,0]-W[1])),np.argmin(abs(X[0,:]-W[0]))]
if __name__=="__main__":
    for r in c10: print([round(x,2) if not isinstance(x,tuple) else tuple(round(y,2) for y in x) for x in r])
    print(b25,D,sum3,shift_tab,near)
    print(a1,a2,a3,a4,sT,sW,wmax,a_wmax,wT,wW)
