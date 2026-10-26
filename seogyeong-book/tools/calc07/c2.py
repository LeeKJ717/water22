from lib07 import *
from scipy.stats import norm as N
import c1
from c1 import mk, summ, phrase_ind, US
ug=np.linspace(0.30,0.55,251); du=ug[1]-ug[0]
def post_u(items, eps=0.0, prior=None):
    p=np.ones_like(ug) if prior is None else prior.copy()
    for (L,l,s) in items:
        z=np.log(L)-np.log(l/ug)
        p=p*((1-eps)*zpdf(z,s)+eps*WIDE)
    return p/p.sum()
def usum(p):
    m=(p*ug).sum(); sd=math.sqrt((p*ug**2).sum()-m*m); c=np.cumsum(p)
    lo=ug[np.searchsorted(c,0.025)]; hi=ug[np.searchsorted(c,0.975)]
    return m,sd,lo,hi
E8=(12,5.0,0.08); E10a=(10,4.1,0.08); E10b=(10,3.4,0.08)
rows=[]
def addrow(nm,p):
    m,sd,lo,hi=usum(p); rows.append([nm,f"{m:.4f}",f"{sd:.4f}",f"{lo:.3f}~{hi:.3f}"]); return m,sd,lo,hi
r=addrow("제2석만",post_u([E8])); 
for k,v in zip(("m","sd","lo","hi"),r): put(f"E.e8.{k}",v)
r=addrow("제2석 + 제1석(맞는 값)",post_u([E8,E10a]))
for k,v in zip(("m","sd","lo","hi"),r): put(f"E.ok.{k}",v)
r=addrow("제2석 + 제1석(어긋난 값), 순진한 우도",post_u([E8,E10b]))
for k,v in zip(("m","sd","lo","hi"),r): put(f"E.bad.{k}",v)
r=addrow("제2석 + 제1석(어긋난 값), 혼합 우도 $\\varepsilon=0.10$",post_u([E8,E10b],eps=0.1))
for k,v in zip(("m","sd","lo","hi"),r): put(f"E.mix.{k}",v)
ptab("E.sum",["입력","$u$ 사후 평균","표준편차","95% 구간 (km/리)"],rows)
# end-point uncertainty: sigma_total
E8w=(12,5.0,math.sqrt(0.08**2+0.10**2)); put("E.sigtot",E8w[2])
r=usum(post_u([E8w])); 
for k,v in zip(("m","sd","lo","hi"),r): put(f"E.wide.{k}",v)
# straight-line vs path
for eta in (0.9,0.8):
    r=usum(post_u([(12,5.0*eta,0.08)]))
    put(f"E.eta{int(eta*100)}.m",r[0]); put(f"E.eta{int(eta*100)}.drop",(1-r[0]/R["E.e8.m"])*100)
put("E.ratio",5.0/12)
# 12 li gives km of length at posterior mean
# F: probability that reading wrong vs mismatch
pE8=post_u([E8])
rows=[]
for l10 in (4.1,3.7,3.4,2.8,2.0):
    z=np.log(10)-np.log(l10/ug); m_ln=(pE8*zpdf(z,0.08)).sum()
    pw=0.1*WIDE/(0.9*m_ln+0.1*WIDE)
    zc=np.log(10)-np.log(l10/R["E.e8.m"])
    rows.append([f"{l10:.1f}",f"{10*R['E.e8.m']:.2f}",f"{zc:+.3f}",f"{m_ln:.4f}",f"{pw*100:.1f}"])
    put(f"F.pw{l10}",pw*100)
ptab("F.tab",["가상 실측 길이 (km)","10리의 기대 길이 (km)","$z$ (제2석의 $u$ 평균 기준)","LN 쪽 평균 밀도","\"읽기가 틀렸다\"의 사후확률(%)"],rows)
# G: beta-binomial
rows=[]
for nm,a,b in (("Beta(1,1): 아무것도 모름",1,1),("Beta(0.5,0.5): 극단을 선호",0.5,0.5),("Beta(2,2): 반반을 선호",2,2)):
    pm=(a+2)/(a+b+2); rows.append([nm,f"{a+2:g}, {b:g}",f"{pm:.3f}"])
    put(f"G.beta{a}",pm)
ptab("G.beta",["사전분포","사후분포의 두 모수","E11의 해당 글자가 '日'일 확률"],rows)
# G2 missing digit
pu=post_u([E8,E10a]); put("G.u_m",(pu*ug).sum())
cands=[2,12,22]
rows=[]
for l11 in (0.9,5.0,9.3):
    ls=[ (pu*zpdf(np.log(c)-np.log(l11/ug),0.08)).sum() for c in cands]
    ps=np.array(ls)/sum(ls)
    rows.append([f"{l11:.1f}"]+[f"{v*100:.1f}" for v in ps])
    put(f"G.c{l11}.2",ps[0]*100); put(f"G.c{l11}.12",ps[1]*100); put(f"G.c{l11}.22",ps[2]*100)
ptab("G.dig",["가상 실측 길이 (km)","二里 (%)","十二里 (%)","卄二里 (%)"],rows)
# H: N prediction
l12=6.4
Ns=np.arange(1,41)
def predN(pu_,l):
    return np.array([ (pu_*zpdf(np.log(n)-np.log(l/ug),0.08)).sum() for n in Ns])
pn=predN(pu,l12); pn=pn/pn.sum()
flat=np.ones_like(ug)/len(ug); pn0=predN(flat,l12); pn0=pn0/pn0.sum()
rows=[[f"{n}",f"{pn[n-1]*100:.1f}",f"{pn0[n-1]*100:.1f}"] for n in range(12,20)]
ptab("H.N",["빠진 숫자 $N$ (리)","$u$를 다른 돌에서 알 때 (%)","$u$를 모를 때 (%)"],rows)
for n in (14,15,16,17): put(f"H.p{n}",pn[n-1]*100)
put("H.top",int(Ns[pn.argmax()])); put("H.top_p",pn.max()*100); put("H.top0",int(Ns[pn0.argmax()]))
c=np.cumsum(pn0); put("H.r0_lo",int(Ns[np.searchsorted(c,0.025)])); put("H.r0_hi",int(Ns[np.searchsorted(c,0.975)]))
c=np.cumsum(pn); put("H.r_lo",int(Ns[np.searchsorted(c,0.025)])); put("H.r_hi",int(Ns[np.searchsorted(c,0.975)]))
put("H.n95_0",int(Ns[pn0>0.0]) if False else 0)
um=R["G.u_m"]; put("H.expect",l12/um)
rows=[]
for rho in (100,300,600):
    li=4/rho; m=li*um*1000
    rows.append([f"{rho}",f"{li:.4f}",f"{m:.1f}"])
    put(f"H.rho{rho}.m",m)
ptab("H.chok",["가정한 1리의 척 수 $\\rho$","4척은 몇 리","그 길이 (m, $u=$ 사후 평균)"],rows)
put("H.sigm",0.08*l12*1000)
# ---------------- I cases ----------------
st=0.5
xs,ys,X,Y=mk(0,100,0,100,st)
def ringpost(refs, L, extra=None, s=0.10, us=US, dirdeg=None, kap=6.5, speed=False):
    tot=np.zeros_like(X)
    for u in us:
        d=np.hypot(X-refs[0],Y-refs[1]); v=lik_dist(L,d,u,s)
        if dirdeg is not None: v=v*np.nan_to_num(lik_dir(X-refs[0],Y-refs[1],dirdeg,kap))
        if extra is not None: v=v*extra
        tot+=v
    return norm(tot)
ref=(50,50)
Pr=ringpost(ref,50); s1=summ(Pr,X,Y,st)
Pd=ringpost(ref,50,dirdeg=90); s2=summ(Pd,X,Y,st)
put("I1.ring.a95",s1["a95"]); put("I1.dir.a95",s2["a95"]); put("I1.dir.a50",s2["a50"])
put("I1.dir.mx",s2["mx"]); put("I1.dir.my",s2["my"]); put("I1.ring.a50",s1["a50"])
put("I1.dist_mean",math.hypot(s2["mx"]-50,s2["my"]-50)); put("I1.r_lo",50*0.36); put("I1.r_hi",50*0.48)
put("I1.ratio",s1["a95"]/s2["a95"])
# MAP location
put("I1.mapx",s2["mapx"]); put("I1.mapy",s2["mapy"])
# I2: three-day road, speed v km/day
vs=np.linspace(20,35,16)
tot=np.zeros_like(X)
d=np.hypot(X-ref[0],Y-ref[1])
for v_ in vs: tot+=lik_dist(3,d,v_ ,0.25) if False else zpdf(np.log(3)-np.log(d/v_),0.25)
P=norm(tot); s3=summ(P,X,Y,st)
put("I2.a95",s3["a95"]); put("I2.a50",s3["a50"]); put("I2.rlo",3*20); put("I2.rhi",3*35)
# compare: 오십 리 with sigma .25, same u grid
P=ringpost(ref,50,s=0.25); s3b=summ(P,X,Y,st); put("I2.li25.a95",s3b["a95"])
# radial 95% interval
def radial(P,center):
    d=np.hypot(X-center[0],Y-center[1]); idx=np.argsort(d.ravel()); c=np.cumsum(P.ravel()[idx]); dd=d.ravel()[idx]
    return dd[np.searchsorted(c,0.025)],dd[np.searchsorted(c,0.975)]
tot=np.zeros_like(X)
for v_ in vs: tot+=zpdf(np.log(3)-np.log(d/v_),0.25)
P2=norm(tot); lo,hi=radial(P2,ref); put("I2.r95lo",lo); put("I2.r95hi",hi)
P1=ringpost(ref,50); lo,hi=radial(P1,ref); put("I1.r95lo",lo); put("I1.r95hi",hi)
# I3: 수십 리
tot=np.zeros_like(X)
for u in US:
    tot+=phrase_ind(np.maximum(d,1e-6)/u,20,100,0.1)
P3=norm(tot); s4=summ(P3,X,Y,st); put("I3.a95",s4["a95"]); put("I3.a50",s4["a50"])
lo,hi=radial(P3,ref); put("I3.r95lo",lo); put("I3.r95hi",hi)
put("I3.area_ratio",s4["a95"]/s1["a95"])
put("I3.dom",100*100)
# I4: river
def rx(y): return 50+6*np.sin(y/12)
refW=(30,50)
side=N.cdf((X-rx(Y))/0.4)
tot=np.zeros_like(X); totn=np.zeros_like(X)
dW=np.hypot(X-refW[0],Y-refW[1])
for u in US:
    base=lik_dist(20,dW,u,0.10); tot+=base*side; totn+=base
P=norm(tot); Pn=norm(totn); s5=summ(P,X,Y,st); s5n=summ(Pn,X,Y,st)
put("I4.a95",s5["a95"]); put("I4.a95n",s5n["a95"]); put("I4.mx",s5["mx"]); put("I4.my",s5["my"])
put("I4.mxn",s5n["mx"]); put("I4.eastshare",Pn[side>0.5].sum()*100)
put("I4.rlo",20*0.36); put("I4.rhi",20*0.48)
# river moved: truth side computed with shifted river x+3
side2=N.cdf((X-(rx(Y)+3))/0.4)
put("I4.lost",(P*(1-side2)).sum()*100)
# I5: between A and B plus 30 li from A
A_=(20,50); B_=(80,50)
def dseg(X,Y,A,B):
    ax,ay=A; bx,by=B; vx,vy=bx-ax,by-ay; t=np.clip(((X-ax)*vx+(Y-ay)*vy)/(vx*vx+vy*vy),0,1)
    return np.hypot(X-(ax+t*vx),Y-(ay+t*vy))
ds=dseg(X,Y,A_,B_)
between=np.exp(-ds**2/(2*3.0**2))
tot=np.zeros_like(X); dA=np.hypot(X-A_[0],Y-A_[1])
for u in US: tot+=lik_dist(30,dA,u,0.10)*between
P=norm(tot); s6=summ(P,X,Y,st); put("I5.a95",s6["a95"]); put("I5.mx",s6["mx"]); put("I5.my",s6["my"])
tot=np.zeros_like(X)
for u in US: tot+=lik_dist(30,dA,u,0.10)
Pn=norm(tot); s6n=summ(Pn,X,Y,st); put("I5.a95n",s6n["a95"])
put("I5.lo",30*0.36); put("I5.hi",30*0.48)
put("I5.ymax_between",float(np.abs(Y[P>1e-9]-50).max()))
# compare mass off-line (|y-50|>3)
put("I5.off",Pn[np.abs(Y-50)>3].sum()*100)
# I6: not far (half normal)
tot=np.exp(-dA**2/(2*5.0**2)); P=norm(tot); s7=summ(P,X,Y,st); put("I6.a95",s7["a95"]); put("I6.a50",s7["a50"])
put("I6.g95",2*math.pi*25*math.log(20)); put("I6.g50",2*math.pi*25*math.log(2))
if __name__=="__main__":
    for k,v in R.items():
        if k.split('.')[0] in "EFGHI" or k[0] in "EFGHI": print(k, round(v,4) if isinstance(v,float) else v)
    for k in TAB:
        if k[0] in "EFGH": print(k); print(TAB[k])
