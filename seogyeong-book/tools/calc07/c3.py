from lib07 import *
from scipy.stats import norm as N
from scipy import ndimage
import c1
from c1 import mk, summ, US
# add the 2.8 row to E.sum and digit table ell=7.2 (patch into c2 results)
import c2
from c2 import post_u, ug, usum, zpdf
E8=(12,5.0,0.08); E10c=(10,2.8,0.08)
for nm,p in (("제2석 + 제1석(크게 어긋난 값 2.8 km), 순진한 우도",post_u([E8,E10c])),("제2석 + 제1석(크게 어긋난 값 2.8 km), 혼합 우도 $\\varepsilon=0.10$",post_u([E8,E10c],eps=0.1))):
    m,sd,lo,hi=usum(p)
    TAB["E.sum"]+=f"\n| {nm} | {m:.4f} | {sd:.4f} | {lo:.3f}~{hi:.3f} |"
    key="naive28" if "순진" in nm else "mix28"
    put(f"E.{key}.m",m); put(f"E.{key}.sd",sd); put(f"E.{key}.lo",lo); put(f"E.{key}.hi",hi)
pu=post_u([E8,(10,4.1,0.08)])
rows=[]
for l11 in (0.9,5.0,7.2,9.3):
    ls=[(pu*zpdf(np.log(c)-np.log(l11/ug),0.08)).sum() for c in (2,12,22)]
    ps=np.array(ls)/sum(ls); rows.append([f"{l11:.1f}"]+[f"{v*100:.1f}" for v in ps])
    for c,v in zip((2,12,22),ps): put(f"G.d{l11}.{c}",v*100)
    put(f"G.d{l11}.exp",l11/R["G.u_m"])
ptab("G.dig",["가상 실측 길이 (km)","길이 ÷ $u$ (리)","二里 (%)","十二里 (%)","卄二里 (%)"],[[r[0],f"{float(r[0])/R['G.u_m']:.1f}"]+r[1:] for r in rows])
# redo I4 with ref (42,50)
st=0.5; xs,ys,X,Y=mk(0,100,0,100,st)
def rx(y): return 50+6*np.sin(y/12)
refW=(42,50)
side=N.cdf((X-rx(Y))/0.4)
dW=np.hypot(X-refW[0],Y-refW[1])
tot=np.zeros_like(X); totn=np.zeros_like(X)
for u in US:
    base=zpdf(np.log(20)-np.log(np.maximum(dW,1e-9)/u),0.10); tot+=base*side; totn+=base
P=norm(tot); Pn=norm(totn); s5=summ(P,X,Y,st); s5n=summ(Pn,X,Y,st)
put("I4.a95",s5["a95"]); put("I4.a95n",s5n["a95"]); put("I4.mx",s5["mx"]); put("I4.my",s5["my"])
put("I4.eastshare",Pn[side>0.5].sum()*100)
side2=N.cdf((X-(rx(Y)+3))/0.4)
put("I4.lost",(P*(1-side2)).sum()*100)
put("I4.rx50",rx(50)); put("I4.rlo",20*0.36); put("I4.rhi",20*0.48)
# ---- J1 도읍: extent
area=(25+130+300+730)/100.0  # km2
r_eq=math.sqrt(area/math.pi); r_pe=23/(2*math.pi)
put("J1.area",area); put("J1.req",r_eq); put("J1.rpe",r_pe)
rows=[]
for Dkm in (4.0,6.0,8.0,12.0):
    se=r_eq/Dkm; sp=r_pe/Dkm
    rows.append([f"{Dkm:.0f}",f"{se:.3f}",f"{math.sqrt(0.1**2+se**2):.3f}",f"{sp:.3f}",f"{math.sqrt(0.1**2+sp**2):.3f}"])
    put(f"J1.s{int(Dkm)}",math.sqrt(0.01+se*se)); put(f"J1.sp{int(Dkm)}",math.sqrt(0.01+sp*sp))
ptab("J1.tab",["성 가운데에서 잰 거리 $D$ (km)","$r_{면적}/D$","합친 $\\sigma$ ($r_{면적}$)","$r_{둘레}/D$","합친 $\\sigma$ ($r_{둘레}$)"],rows)
# ring areas for D=4 km (10 li at u=0.4) and u fixed 0.40
refc=(50,50); d=np.hypot(X-refc[0],Y-refc[1])
for nm,sg in (("pt",0.10),("eq",math.sqrt(0.01+(r_eq/4.0)**2)),("pe",math.sqrt(0.01+(r_pe/4.0)**2))):
    P=norm(zpdf(np.log(10)-np.log(np.maximum(d,1e-9)/0.40),sg)); s_=summ(P,X,Y,st)
    put(f"J1.a95_{nm}",s_["a95"]); put(f"J1.a50_{nm}",s_["a50"])
# coverage test: truth is city boundary at distance 4.0±r from center; point-center model with sg=.1 : does 95% region cover points at 4.0 - r_eq?
for nm in ("pt","eq"):
    sg=0.10 if nm=="pt" else math.sqrt(0.01+(r_eq/4.0)**2)
    P=norm(zpdf(np.log(10)-np.log(np.maximum(d,1e-9)/0.40),sg)); m=hpd_mask(P,.95)
    # radial extent of 95% region
    put(f"J1.rmin_{nm}",d[m].min()); put(f"J1.rmax_{nm}",d[m].max())
# ---- J2 ridge fortress
def elev(X,Y): return 300*np.exp(-((Y-60-0.3*(X-50))**2)/(2*4.0**2))
H=elev(X,Y); crest=(H>=150)
refF=(80,58); dF=np.hypot(X-refF[0],Y-refF[1])
def runF(prior_crest):
    tot=np.zeros_like(X)
    for u in US:
        v=zpdf(np.log(40)-np.log(np.maximum(dF,1e-9)/u),0.10)*np.nan_to_num(lik_dir(X-refF[0],Y-refF[1],270,6.5))
        tot+=v
    pr=np.where(crest,1.0,0.05) if prior_crest else np.ones_like(X)
    return norm(tot*pr)
for nm,flag in (("flat",False),("crest",True)):
    P=runF(flag); s_=summ(P,X,Y,st)
    lab,nc=ndimage.label(hpd_mask(P,.95))
    put(f"J2.{nm}.a95",s_["a95"]); put(f"J2.{nm}.a50",s_["a50"]); put(f"J2.{nm}.mx",s_["mx"]); put(f"J2.{nm}.my",s_["my"])
    put(f"J2.{nm}.mapx",s_["mapx"]); put(f"J2.{nm}.mapy",s_["mapy"])
    put(f"J2.{nm}.oncrest",P[crest].sum()*100)
put("J2.crest_share",crest.mean()*100); put("J2.rlo",40*0.36); put("J2.rhi",40*0.48)
# ---- J3 ferry on a river (arclength)
def rx2(y): return 50+12*np.sin(y/5)
yy=np.linspace(100,0,4001); xx=rx2(yy)
seg=np.hypot(np.diff(xx),np.diff(yy)); arc=np.concatenate([[0],np.cumsum(seg)])
put("J3.total",arc[-1]); put("J3.sin",arc[-1]/100.0)
iT=int(np.argmin(np.abs(yy-76))); town=(xx[iT],yy[iT]); put("J3.tx",town[0]); put("J3.ty",town[1])
s_rel=arc-arc[iT]; down=s_rel>=0
dstr=np.hypot(xx-town[0],yy-town[1])
def river_post(model):
    tot=np.zeros_like(yy)
    for u in US:
        dd=s_rel if model=="arc" else dstr
        v=zpdf(np.log(30)-np.log(np.maximum(dd,1e-9)/u),0.10)
        tot+=np.where(down,v,0)
    return tot/tot.sum()
for nm in ("arc","str"):
    p=river_post(nm); m=(p*yy).sum(); c=np.cumsum(p)
    ylo=yy[np.searchsorted(c,0.025)]; yhi=yy[np.searchsorted(c,0.975)]
    # downstream: y decreasing so c increases as y decreases; 
    put(f"J3.{nm}.y",m); put(f"J3.{nm}.ya",yy[np.searchsorted(c,0.025)]); put(f"J3.{nm}.yb",yy[np.searchsorted(c,0.975)])
    put(f"J3.{nm}.x",(p*xx).sum())
put("J3.shift",math.hypot(R["J3.arc.x"]-R["J3.str.x"],R["J3.arc.y"]-R["J3.str.y"]))
put("J3.arc.len",R["J3.arc.ya"]-R["J3.arc.yb"])
parc=river_post("arc"); mask=hpd_mask(parc.reshape(1,-1),.95)[0]; 
put("J3.arc.chord",math.hypot(R["J3.arc.x"]-town[0],R["J3.arc.y"]-town[1])); put("J3.rlo",30*0.36); put("J3.rhi",30*0.48)
# ---- J4 pass candidates
refP=(50,50); cands=[("P1",(60,60)),("P2",(64,52)),("P3",(58,67)),("P4",(38,62))]
rows=[]; ml=[]
for nm,(cx,cy) in cands:
    d_=math.hypot(cx-refP[0],cy-refP[1]); b=math.degrees(math.atan2(cx-refP[0],cy-refP[1]))%360
    dirl=float(lik_dir(cx-refP[0],cy-refP[1],45,6.5))
    dl=np.mean([zpdf(math.log(40)-math.log(d_/u),0.10) for u in US])
    ml.append(dl*dirl); rows.append([nm,f"({cx},{cy})",f"{d_:.1f}",f"{d_/0.42:.0f}",f"{b:.0f}°",f"{dl:.3f}",f"{dirl:.3f}",f"{dl*dirl:.4f}"])
ml=np.array(ml); post=ml/ml.sum()
for r,pp in zip(rows,post): r.append(f"{pp*100:.1f}")
ptab("J4.tab",["후보","좌표 (km)","거리 (km)","$u=0.42$일 때 리","방위","거리 우도 ($u$ 평균)","방위 우도","곱","사후(%)"],rows)
for (nm,_),pp in zip(cands,post): put(f"J4.{nm}",pp*100)
put("J4.bf12",ml[0]/ml[1]); put("J4.bf13",ml[0]/ml[2]); 
# sensitivity: kappa=2
ml2=[]
for nm,(cx,cy) in cands:
    d_=math.hypot(cx-refP[0],cy-refP[1]); dirl=float(lik_dir(cx-refP[0],cy-refP[1],45,2.0))
    ml2.append(np.mean([zpdf(math.log(40)-math.log(d_/u),0.10) for u in US])*dirl)
ml2=np.array(ml2); p2=ml2/ml2.sum()
for (nm,_),pp in zip(cands,p2): put(f"J4.k2.{nm}",pp*100)
# sigma .25
ml3=[]
for nm,(cx,cy) in cands:
    d_=math.hypot(cx-refP[0],cy-refP[1]); dirl=float(lik_dir(cx-refP[0],cy-refP[1],45,6.5))
    ml3.append(np.mean([zpdf(math.log(40)-math.log(d_/u),0.25) for u in US])*dirl)
ml3=np.array(ml3); p3=ml3/ml3.sum()
for (nm,_),pp in zip(cands,p3): put(f"J4.s25.{nm}",pp*100)
# ---- J5 islands
refH=(20,50)
isl=[("가섬",(52,38),12.0),("나섬",(60,62),30.0),("다섬",(75,45),55.0),("라섬",(45,20),6.0),("마섬",(88,70),20.0)]
# '큰 섬' -> prior proportional to area (assumption); evidence: 'two days by boat', speed v in 40..60 km/day, sigma .25, direction ESE(112.5deg)
vs=np.linspace(40,60,11)
rows=[]; priors=np.array([a for _,_,a in isl]); priors=priors/priors.sum(); L_=[]
for (nm,(cx,cy),a),pr in zip(isl,priors):
    d_=math.hypot(cx-refH[0],cy-refH[1]); b=math.degrees(math.atan2(cx-refH[0],cy-refH[1]))%360
    dl=np.mean([zpdf(math.log(2)-math.log(d_/v),0.25) for v in vs]); dirl=float(lik_dir(cx-refH[0],cy-refH[1],90,6.5))
    L_.append(dl*dirl); rows.append([nm,f"({cx},{cy})",f"{a:.0f}",f"{pr*100:.1f}",f"{d_:.1f}",f"{b:.0f}°",f"{dl:.3f}",f"{dirl:.3f}"])
L_=np.array(L_); post=priors*L_/ (priors*L_).sum()
for r,pp in zip(rows,post): r.append(f"{pp*100:.1f}")
ptab("J5.tab",["섬","좌표 (km)","면적 (km²)","사전(%)","거리 (km)","방위","거리 우도","방위 우도","사후(%)"],rows)
for (nm,_,_),pp in zip(isl,post): put(f"J5.{nm}",pp*100)
# open-world: add catch-all with weight .10, its likelihood = average likelihood over open-sea cells region (mean of the lik of a broad region)
xs2,ys2,X2,Y2=mk(0,100,0,100,1.0)
tot=0; 
d2=np.hypot(X2-refH[0],Y2-refH[1])
lik_sea=np.mean([np.nan_to_num(zpdf(np.log(2)-np.log(np.maximum(d2,1e-9)/v),0.25)*lik_dir(X2-refH[0],Y2-refH[1],90,6.5)) for v in vs])
put("J5.lik_sea",lik_sea)
w0=0.10; pri=np.concatenate([(1-w0)*priors,[w0]]); Ls=np.concatenate([L_,[lik_sea]]); post2=pri*Ls/(pri*Ls).sum()
for (nm,_,_),pp in zip(isl,post2[:-1]): put(f"J5.o.{nm}",pp*100)
put("J5.o.unk",post2[-1]*100)
# ---- J6 temple, gazetteer prior
refT=(50,50); T=[("가사",(44,51)),("나사",(45,45)),("다사",(43,56))]
def tp(w, L=15, deg=270):
    out=[]
    for (nm,(cx,cy)),wi in zip(T,w):
        d_=math.hypot(cx-refT[0],cy-refT[1]); dl=np.mean([zpdf(math.log(L)-math.log(d_/u),0.15) for u in US]); dirl=float(lik_dir(cx-refT[0],cy-refT[1],deg,6.5))
        out.append(wi*dl*dirl)
    out=np.array(out); return out/out.sum()
rows=[]
for nm,(cx,cy) in T:
    d_=math.hypot(cx-refT[0],cy-refT[1]); b=math.degrees(math.atan2(cx-refT[0],cy-refT[1]))%360
    dl=np.mean([zpdf(math.log(15)-math.log(d_/u),0.15) for u in US]); dirl=float(lik_dir(cx-refT[0],cy-refT[1],270,6.5))
    rows.append([nm,f"({cx},{cy})",f"{d_:.1f}",f"{b:.0f}°",f"{dl:.3f}",f"{dirl:.3f}",f"{dl*dirl:.3f}"])
ptab("J6.lik",["후보","좌표 (km)","거리 (km)","방위","거리 우도","방위 우도","곱"],rows)
rowsb=[]
for nm_,w in (("이름 일치 사전 (0.2, 0.3, 0.5)",(0.2,0.3,0.5)),("균등 (1/3씩)",(1/3,1/3,1/3)),("이름 일치 사전 (0.1, 0.1, 0.8)",(0.1,0.1,0.8)),("이름 일치 사전 (0.8, 0.1, 0.1)",(0.8,0.1,0.1))):
    p=tp(w); rowsb.append([nm_]+[f"{v*100:.1f}" for v in p])
    put(f"J6.{w[0]:.1f}.{w[2]:.1f}.a",p[0]*100); put(f"J6.{w[0]:.1f}.{w[2]:.1f}.b",p[1]*100); put(f"J6.{w[0]:.1f}.{w[2]:.1f}.c",p[2]*100)
ptab("J6.post",["사전","가사 (%)","나사 (%)","다사 (%)"],rowsb)
# ---- J7 chain propagation (two hops east, shared u)
xs3,ys3,X3,Y3=mk(10,110,20,80,0.5)
A0=(10,50)
tot_u={}; w1=[]
for u in US:
    d=np.hypot(X3-A0[0],Y3-A0[1]); v=zpdf(np.log(100)-np.log(np.maximum(d,1e-9)/u),0.10)*np.nan_to_num(lik_dir(X3-A0[0],Y3-A0[1],90,6.5))
    tot_u[u]=v; w1.append(v.sum())
# displacement kernel for hop 2
dxs=np.arange(0,100.01,0.5); dys=np.arange(-40,40.01,0.5); DX,DY=np.meshgrid(dxs,dys)
K={}; w2=[]
for u in US:
    k=zpdf(np.log(100)-np.log(np.maximum(np.hypot(DX,DY),1e-9)/u),0.10)*np.nan_to_num(lik_dir(DX,DY,90,6.5)); K[u]=k; w2.append(k.sum())
w=np.array(w1)*np.array(w2); pu_=w/w.sum(); pu1=np.array(w1)/sum(w1)
put("J7.pu1_mean",(pu1*US).sum()); put("J7.pu2_mean",(pu_*US).sum())
put("J7.pu1_sd",math.sqrt((pu1*US**2).sum()-(pu1*US).sum()**2)); put("J7.pu2_sd",math.sqrt((pu_*US**2).sum()-(pu_*US).sum()**2))
rng=np.random.default_rng(20261023); nS=60000
uidx=rng.choice(len(US),size=nS,p=pu_)
flatXY=np.stack([X3.ravel(),Y3.ravel()],1); flatD=np.stack([DX.ravel(),DY.ravel()],1)
g1=np.zeros((nS,2)); g2=np.zeros((nS,2)); g2i=np.zeros((nS,2))
uidx_i=rng.choice(len(US),size=nS,p=pu_)  # independent u for hop 2
for i,u in enumerate(US):
    m=uidx==i; n_=m.sum()
    if n_:
        p=norm(tot_u[u]).ravel(); ch=rng.choice(len(p),size=n_,p=p); g1[m]=flatXY[ch]
        pk=norm(K[u]).ravel(); ch=rng.choice(len(pk),size=n_,p=pk); g2[m]=flatD[ch]
    m2=uidx_i==i; n2=m2.sum()
    if n2:
        pk=norm(K[u]).ravel(); ch=rng.choice(len(pk),size=n2,p=pk); g2i[m2]=flatD[ch]
gun=g1; yup=g1+g2; yup_i=g1+g2i
for nm,arr in (("gun",gun),("sh",yup),("ind",yup_i)):
    put(f"J7.{nm}.mx",arr[:,0].mean()); put(f"J7.{nm}.my",arr[:,1].mean()); put(f"J7.{nm}.sx",arr[:,0].std()); put(f"J7.{nm}.sy",arr[:,1].std())
for nm,arr in (("gun",gun),("sh",yup),("ind",yup_i)):
    cov=np.cov(arr.T); put(f"J7.{nm}.ell95",math.pi*5.991*math.sqrt(np.linalg.det(cov)))
# plug-in: MAP of gun then displacement with MAP u only? use gun mean and the displacement distribution's mean per-u
put("J7.plug_sx",g2[:,0].std()); put("J7.plug_note",0)
put("J7.corr12",np.corrcoef(g1[:,0],g2[:,0])[0,1])
put("J7.exp_mx",A0[0]+200*R["J7.pu2_mean"]); 
put("J7.sx_ratio",R["J7.sh.sx"]/R["J7.ind.sx"])
# ---- J8 route
route=np.array([(10,10),(40,12),(45,40),(75,45),(90,70)],float)
seg=np.hypot(*np.diff(route,axis=0).T); cum=np.concatenate([[0],np.cumsum(seg)]); Ltot=cum[-1]; put("J8.total",Ltot)
put("J8.chord",math.hypot(80,60)); 
s=np.linspace(0,Ltot,2001)
def pos(sv): return np.array([np.interp(sv,cum,route[:,0]),np.interp(sv,cum,route[:,1])])
vv=np.linspace(15,40,126)
# evidence: A to node 2 days; node to B 3 days
post=np.zeros((len(vv),len(s)))
for i,v in enumerate(vv):
    post[i]=zpdf(np.log(2)-np.log(s/v+1e-9),0.2)*zpdf(np.log(3)-np.log((Ltot-s)/v+1e-9),0.2)
post[:,0]=0;post[:,-1]=0
pv=post.sum(1); pv/=pv.sum(); ps=post.sum(0); ps/=ps.sum()
put("J8.v_mean",(pv*vv).sum()); put("J8.v_sd",math.sqrt((pv*vv**2).sum()-(pv*vv).sum()**2)); put("J8.v_exp",Ltot/5)
put("J8.s_mean",(ps*s).sum()); put("J8.s_exp",Ltot*2/5)
c=np.cumsum(ps); put("J8.s_lo",s[np.searchsorted(c,.025)]); put("J8.s_hi",s[np.searchsorted(c,.975)])
pp=pos(R["J8.s_mean"]); put("J8.px",pp[0]); put("J8.py",pp[1])
# straight-line version ignoring route: circle around A radius 2 days *v and around B 3 days: intersection
# v prior alone: no info -> ps if only A evidence with v unknown flat: wide
post1=np.zeros((len(vv),len(s)))
for i,v in enumerate(vv): post1[i]=zpdf(np.log(2)-np.log(s/v+1e-9),0.2)
post1[:,0]=0
ps1=post1.sum(0); ps1/=ps1.sum(); c1_=np.cumsum(ps1)
put("J8.one.lo",s[np.searchsorted(c1_,.025)]); put("J8.one.hi",s[np.searchsorted(c1_,.975)])
put("J8.both.w",R["J8.s_hi"]-R["J8.s_lo"]); put("J8.one.w",R["J8.one.hi"]-R["J8.one.lo"])
if __name__=="__main__":
    for k,v in R.items():
        if k[0] in "IJ" or k.startswith("E.naive28") or k.startswith("E.mix28") or k.startswith("G.d"):
            print(k, round(v,4) if isinstance(v,float) else v)
    for k in TAB:
        if k[0] in "JG" or k=="E.sum": print(k); print(TAB[k])
