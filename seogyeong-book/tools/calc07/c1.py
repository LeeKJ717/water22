from lib07 import *
from scipy.stats import norm as N
US = np.linspace(0.36,0.48,15)
def mk(x0,x1,y0,y1,st):
    xs=np.arange(x0,x1+1e-9,st); ys=np.arange(y0,y1+1e-9,st)
    X,Y=np.meshgrid(xs,ys); return xs,ys,X,Y
def summ(P,X,Y,st):
    mx=(P*X).sum(); my=(P*Y).sum(); k=np.unravel_index(P.argmax(),P.shape)
    a50=hpd_mask(P,.5).sum()*st*st; a95=hpd_mask(P,.95).sum()*st*st
    return dict(mx=mx,my=my,mapx=X[k],mapy=Y[k],pmap=P.max(),a50=a50,a95=a95)
def phrase_ind(D, lo, hi, se):  # P('lo여' | true D li): smooth indicator on [lo,hi)
    return N.cdf((np.log(D)-np.log(lo))/se)-N.cdf((np.log(D)-np.log(hi))/se)
# ---------- Case A: E1 ----------
st=0.25
xs,ys,X,Y=mk(34,66,40,60,st)
PL=(54,50); PR=(45,51)
dL=np.hypot(PL[0]-X,PL[1]-Y); dR=np.hypot(PR[0]-X,PR[1]-Y)
bL=lik_dir(PL[0]-X,PL[1]-Y,90,6.5); bR=lik_dir(PR[0]-X,PR[1]-Y,270,6.5)
def runA(reading, swap=False, dirs=True):
    tot=np.zeros_like(X); pu=[]
    for u in US:
        if reading==1:
            a=lik_dist(10,dL,u,0.25); b=lik_dist(10,dR,u,0.25)
        else:
            a=phrase_ind(dL/u,10,20,0.1); b=phrase_ind(dR/u,10,20,0.1)
        v=a*b
        if dirs:
            v=v*((lik_dir(PL[0]-X,PL[1]-Y,270,6.5)*lik_dir(PR[0]-X,PR[1]-Y,90,6.5)) if swap else bL*bR)
        tot+=v; pu.append(v.sum())
    pu=np.array(pu); return norm(tot), pu/pu.sum()
sepA=math.hypot(PL[0]-PR[0],PL[1]-PR[1]); put("A.sep",sepA)
put("A.ulo",sepA/40); put("A.uhi",sepA/20)
for r in (1,2):
    P,pu=runA(r); s_=summ(P,X,Y,st)
    for k,v in s_.items(): put(f"A.r{r}.{k}",v)
    put(f"A.r{r}.umean",(pu*US).sum()); put(f"A.r{r}.usd",math.sqrt((pu*US**2).sum()-(pu*US).sum()**2))
    put(f"A.r{r}.u_lo",US[np.argmax(pu>0.01)]) 
    put(f"A.r{r}.pu_max",US[pu.argmax()])
    if r==1: PA1=P; pu1=pu
    else: PA2=P; pu2=pu
rows=[[f"{US[i]:.3f}",f"{pu1[i]*100:.1f}",f"{pu2[i]*100:.1f}"] for i in range(0,15,2)]
ptab("A.pu",["$u$ (km/리)","읽기 1: 10리 중심 (%)","읽기 2: 10~19리 (%)"],rows)
Ps,_=runA(1,swap=True); ss=summ(Ps,X,Y,st)
# total evidence for swapped vs right (marginal likelihood ratio)
def marg(reading,swap):
    tot=0
    for u in US:
        if reading==1: a=lik_dist(10,dL,u,0.25); b=lik_dist(10,dR,u,0.25)
        else: a=phrase_ind(dL/u,10,20,0.1); b=phrase_ind(dR/u,10,20,0.1)
        v=a*b*(bR*bL if swap else bL*bR) if False else None
    return None
def marg2(reading,swap):
    tot=0
    for u in US:
        if reading==1: a=lik_dist(10,dL,u,0.25); b=lik_dist(10,dR,u,0.25)
        else: a=phrase_ind(dL/u,10,20,0.1); b=phrase_ind(dR/u,10,20,0.1)
        d_=(bL*bR) if not swap else (lik_dir(PL[0]-X,PL[1]-Y,270,6.5)*lik_dir(PR[0]-X,PR[1]-Y,90,6.5))
        tot+=(a*b*d_).sum()*st*st
    return tot/len(US)
for r in (1,2):
    put(f"A.r{r}.bf_swap",marg2(r,False)/marg2(r,True))
put("A.r1.cx",0.5*(PL[0]+PR[0])); put("A.r1.cy",0.5*(PL[1]+PR[1]))
# no-direction run
P0,_=runA(1,dirs=False); s0=summ(P0,X,Y,st)
put("A.nodir.a95",s0["a95"]); put("A.nodir.mx",s0["mx"]); put("A.nodir.my",s0["my"])
# distances at posterior mean for readings
put("A.r1.dL",math.hypot(PL[0]-R["A.r1.mx"],PL[1]-R["A.r1.my"]))
put("A.r1.dR",math.hypot(PR[0]-R["A.r1.mx"],PR[1]-R["A.r1.my"]))
rows=[]
for name,r,sw in (("읽기 1, 방위 반영",1,False),("읽기 2, 방위 반영",2,False),("읽기 1, 방위 없음",1,None)):
    if sw is None: P=P0
    else: P,_=runA(r,swap=sw)
    s_=summ(P,X,Y,st)
    rows.append([name,f"({s_['mx']:.2f}, {s_['my']:.2f})",f"({s_['mapx']:.2f}, {s_['mapy']:.2f})",f"{s_['a50']:.1f}",f"{s_['a95']:.1f}"])
P_,_=runA(1,swap=True); s_=summ(P_,X,Y,st)
rows.append(["읽기 1, 좌우를 바꿔 넣음",f"({s_['mx']:.2f}, {s_['my']:.2f})",f"({s_['mapx']:.2f}, {s_['mapy']:.2f})",f"{s_['a50']:.1f}",f"{s_['a95']:.1f}"])
ptab("A.sum",["계산","사후 평균 (km)","MAP (km)","50% 영역 (km²)","95% 영역 (km²)"],rows)
# ---------- Case B: E3 ----------
Ms=[(70,52),(62,38),(80,66)]
tests=[("가",(55,52)),("나",(55,40)),("다",(75,60)),("라",(40,30))]
rows=[]; 
for nm,(tx,ty) in tests:
    ls=[float(lik_dir(m[0]-tx,m[1]-ty,90,6.5)) for m in Ms]
    bs=[math.degrees(float(bearing(m[0]-tx,m[1]-ty)))%360 for m in Ms]
    mixv=sum(ls)/3
    rows.append([f"{nm} ({tx},{ty})"]+[f"{b:.0f}°" for b in bs]+[f"{l:.3f}" for l in ls]+[f"{mixv:.3f}"])
ptab("B.tests",["시험 칸","M1 방위","M2 방위","M3 방위","M1 우도","M2 우도","M3 우도","평균(가중 1/3씩)"],rows)
xsB,ysB,XB,YB=mk(0,100,0,100,1.0)
def postB(w):
    v=sum(wi*lik_dir(m[0]-XB,m[1]-YB,90,6.5) for wi,m in zip(w,Ms)); return norm(v)
for nm,w in (("eq",(1/3,1/3,1/3)),("sk",(0.6,0.3,0.1)),("one",(1,0,0))):
    P=postB(w); s_=summ(P,XB,YB,1.0)
    put(f"B.{nm}.a95",s_["a95"]); put(f"B.{nm}.a50",s_["a50"]); put(f"B.{nm}.mx",s_["mx"]); put(f"B.{nm}.my",s_["my"])
    # mass west of x=62 etc
    put(f"B.{nm}.west50",P[XB<50].sum()*100)
    put(f"B.{nm}.east_of_M1",P[XB>70].sum()*100)
put("B.total",100*100)
# sector hard vs soft: share of domain with lik >= half max for one M
L1=lik_dir(Ms[0][0]-XB,Ms[0][1]-YB,90,6.5); put("B.half_share",(L1>=0.5*L1[np.isfinite(L1)].max()).mean()*100)
# ---------- Case C: E6 ----------
D=(40,40)
tests=[("a",(60,60)),("b",(60,45)),("c",(45,60)),("d",(20,60)),("e",(60,20))]
rows=[]
for nm,(tx,ty) in tests:
    b=math.degrees(float(bearing(tx-D[0],ty-D[1])))%360
    l65=float(lik_dir(tx-D[0],ty-D[1],45,6.5)); l2=float(lik_dir(tx-D[0],ty-D[1],45,2.0))
    dd=abs((b-45+180)%360-180)
    rows.append([f"{nm} ({tx},{ty})",f"{b:.0f}°",f"{dd:.0f}°",f"{l65:.3f}",f"{l2:.3f}","통과" if dd<=22.5 else "탈락"])
ptab("C.tests",["시험 칸","대성산에서 본 방위","45°와의 차","우도 ($\\kappa=6.5$)","우도 ($\\kappa=2$)","8방위 칸막이(±22.5°)"],rows)
Lc65=lik_dir(XB-D[0],YB-D[1],45,6.5); Lc2=lik_dir(XB-D[0],YB-D[1],45,2.0)
for nm,L in (("k65",Lc65),("k2",Lc2)):
    L=np.nan_to_num(L); P=norm(L); s_=summ(P,XB,YB,1.0)
    put(f"C.{nm}.a50",s_["a50"]); put(f"C.{nm}.a95",s_["a95"])
    put(f"C.{nm}.max",L.max())
dd=np.abs((np.degrees(bearing(XB-D[0],YB-D[1]))-45+180)%360-180)
hard=(dd<=22.5); hard[(XB==D[0])&(YB==D[1])]=False
put("C.hard_share",hard.mean()*100); put("C.hard_area",hard.sum())
# ---------- Case D: E9 ----------
Ks=[(30,70),(66,22)]
xsD,ysD,XD,YD=mk(0,100,0,100,0.5)
for tau in (1.5,4.0):
    v=sum(0.5*np.exp(-((XD-k[0])**2+(YD-k[1])**2)/(2*tau**2)) for k in Ks)
    P=norm(v); s_=summ(P,XD,YD,0.5)
    put(f"D.t{tau}.a50",s_["a50"]); put(f"D.t{tau}.a95",s_["a95"])
    # ratio of 95% area to circle pi*(2 tau)^2? 
    left=P[XD<50].sum()*100; put(f"D.t{tau}.left",left)
# weights 0.9/0.1
v=0.9*np.exp(-((XD-Ks[0][0])**2+(YD-Ks[0][1])**2)/(2*1.5**2))+0.1*np.exp(-((XD-Ks[1][0])**2+(YD-Ks[1][1])**2)/(2*1.5**2))
P=norm(v); put("D.w9.left",P[XD<50].sum()*100)
put("D.circ95_1.5",math.pi*(1.5**2)*5.991)  # 2D gaussian 95%: r^2=2*tau^2*ln(20) -> area=2*pi*tau^2*ln20
put("D.g95_1.5",2*math.pi*1.5**2*math.log(20)); put("D.g95_4",2*math.pi*4**2*math.log(20))
put("D.g50_1.5",2*math.pi*1.5**2*math.log(2))
if __name__=="__main__":
    for k,v in R.items(): print(k, round(v,4) if isinstance(v,float) else v)
    for k in TAB: print(k); print(TAB[k])
