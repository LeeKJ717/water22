from lib07 import *
from scipy import ndimage
import c3
from c1 import mk, summ, US
from c2 import post_u, ug, usum, zpdf
# J3 arc interval
# --- recompute arclength interval for ferry
yy=c3.yy; xx=c3.xx; arc=c3.arc; iT=c3.iT
s_rel=arc-arc[iT]; down=s_rel>=0
tot=np.zeros_like(yy)
for u in US: tot+=np.where(down,zpdf(np.log(30)-np.log(np.maximum(s_rel,1e-9)/u),0.10),0)
p=tot/tot.sum(); c=np.cumsum(p)
put("J3.s_lo",s_rel[np.searchsorted(c,0.025)]); put("J3.s_hi",s_rel[np.searchsorted(c,0.975)])
# ---- K: disagreement between sources
st=0.5; xs,ys,X,Y=mk(0,100,0,100,st); AREA=100*100
Dm=(40,40)
W=np.nan_to_num(lik_dir(X-Dm[0],Y-Dm[1],45,6.5)); W=W/(W.sum()*st*st)       # density over the domain
scen={"a":(52,52),"b":(62,32),"c":(15,70)}
tau=1.5
res={}
for nm,K in scen.items():
    Pk=np.exp(-((X-K[0])**2+(Y-K[1])**2)/(2*tau**2)); Pk=Pk/(Pk.sum()*st*st)
    m_naive=(W*Pk).sum()*st*st
    eps=0.15
    f1=(1-eps)*W+eps/AREA; f2=(1-eps)*Pk+eps/AREA
    m_mix=(f1*f2).sum()*st*st
    # latent combos
    combos={"둘 다 맞음":(1-eps)**2*(W*Pk).sum()*st*st,"승람만 틀림":eps*(1-eps)*(1/AREA*Pk).sum()*st*st,"해동역사만 틀림":(1-eps)*eps*(W/AREA).sum()*st*st,"둘 다 틀림":eps*eps/AREA}
    tot=sum(combos.values()); pc={k:v/tot for k,v in combos.items()}
    Pn=norm(W*Pk); Pm=norm(f1*f2)
    sn=summ(Pn,X,Y,st); sm=summ(Pm,X,Y,st)
    labn,ncn=ndimage.label(hpd_mask(Pn,.95)); labm,ncm=ndimage.label(hpd_mask(Pm,.95))
    d_=math.hypot(K[0]-Dm[0],K[1]-Dm[1]); b=math.degrees(math.atan2(K[0]-Dm[0],K[1]-Dm[1]))%360
    res[nm]=dict(d=d_,b=b,m=m_naive,mm=m_mix,pc=pc,sn=sn,sm=sm,ncn=ncn,ncm=ncm)
    put(f"K.{nm}.d",d_); put(f"K.{nm}.b",b); put(f"K.{nm}.logm",math.log10(m_naive*AREA)); put(f"K.{nm}.logmm",math.log10(m_mix*AREA))
    for k,v in pc.items(): put(f"K.{nm}.pc.{k}",v*100)
    put(f"K.{nm}.n_a95",sn["a95"]); put(f"K.{nm}.m_a95",sm["a95"])
    put(f"K.{nm}.n_mx",sn["mx"]); put(f"K.{nm}.n_my",sn["my"]); put(f"K.{nm}.m_mx",sm["mx"]); put(f"K.{nm}.m_my",sm["my"])
    put(f"K.{nm}.ncn",ncn); put(f"K.{nm}.ncm",ncm)
    put(f"K.{nm}.dd",abs((b-45+180)%360-180))
rows=[]
for nm in "abc":
    r=res[nm]; rows.append([nm,f"{r['d']:.1f}",f"{r['b']:.0f}°",f"{R[f'K.{nm}.dd']:.0f}°",f"{R[f'K.{nm}.logm']:+.2f}",f"{R[f'K.{nm}.logmm']:+.2f}"])
ptab("K.scen",["경우","구룡산(가상)-대성산(가상) 거리 (km)","방위","45°와의 차","순진한 곱의 $\\log_{10}$(증거/균등)","혼합의 $\\log_{10}$(증거/균등)"],rows)
rows=[]
for nm in "abc":
    pc=res[nm]["pc"]; rows.append([nm]+[f"{pc[k]*100:.1f}" for k in ("둘 다 맞음","승람만 틀림","해동역사만 틀림","둘 다 틀림")])
ptab("K.latent",["경우","둘 다 맞음 (%)","승람만 틀림 (%)","해동역사만 틀림 (%)","둘 다 틀림 (%)"],rows)
rows=[]
for nm in "abc":
    r=res[nm]
    rows.append([nm,f"({r['sn']['mx']:.1f}, {r['sn']['my']:.1f})",f"{r['sn']['a95']:.0f}",f"{r['ncn']}",f"({r['sm']['mx']:.1f}, {r['sm']['my']:.1f})",f"{r['sm']['a95']:.0f}",f"{r['ncm']}"])
ptab("K.post",["경우","순진한 곱: 평균","95% 영역 (km²)","조각 수","혼합: 평균","95% 영역 (km²)","조각 수"],rows)
# tempering in scenario a
Pk=np.exp(-((X-52)**2+(Y-52)**2)/(2*tau**2)); 
Wr=np.nan_to_num(lik_dir(X-Dm[0],Y-Dm[1],45,6.5))
P1=norm(Wr*Pk); P5=norm((Wr**0.5)*(Pk**0.5))
put("K.temp.a95_1",summ(P1,X,Y,st)["a95"]); put("K.temp.a95_5",summ(P5,X,Y,st)["a95"])
put("K.temp.ratio",R["K.temp.a95_5"]/R["K.temp.a95_1"])
# ---- L: counterexamples
# L1 ring: mean at centre
ref=(50,50); d=np.hypot(X-ref[0],Y-ref[1])
tot=np.zeros_like(X)
for u in US: tot+=zpdf(np.log(50)-np.log(np.maximum(d,1e-9)/u),0.10)
P=norm(tot); s_=summ(P,X,Y,st)
put("L1.mx",s_["mx"]); put("L1.my",s_["my"]); put("L1.pmean",P[int(round(s_["my"]/st)),int(round(s_["mx"]/st))])
put("L1.pmax",P.max()); put("L1.mapd",math.hypot(s_["mapx"]-50,s_["mapy"]-50)); put("L1.a95",s_["a95"]); put("L1.ratio",R["L1.pmean"]/P.max())
put("L1.ringarea",math.pi*(27.8**2-16.6**2))
lab,nc=ndimage.label(hpd_mask(P,.95)); put("L1.nc",nc)
inside=(hpd_mask(P,.95)); put("L1.mean_in",bool(inside[int(round(s_["my"]/st)),int(round(s_["mx"]/st))]))
# L2 mirror bimodal
A_=(20,50); B_=(80,50)
dA=np.hypot(X-A_[0],Y-A_[1]); dB=np.hypot(X-B_[0],Y-B_[1])
# L chosen so that d~35 km at u=.42 => 83 li
LA=100; LB=100
tot=np.zeros_like(X)
for u in US: tot+=zpdf(np.log(LA)-np.log(np.maximum(dA,1e-9)/u),0.10)*zpdf(np.log(LB)-np.log(np.maximum(dB,1e-9)/u),0.10)
P=norm(tot); s_=summ(P,X,Y,st); lab,nc=ndimage.label(hpd_mask(P,.95))
put("L2.nc",nc); put("L2.mx",s_["mx"]); put("L2.my",s_["my"]); put("L2.a95",s_["a95"]); put("L2.pmax",P.max())
put("L2.pmean",P[int(round(s_["my"]/st)),int(round(s_["mx"]/st))]); put("L2.ratio",R["L2.pmean"]/R["L2.pmax"])
put("L2.north",P[Y>50].sum()*100); put("L2.yoff",math.sqrt(0.42**2*LA**2-30**2)); put("L2.d",0.42*LA)
# third evidence: bearing from A "북동"
C_=np.nan_to_num(lik_dir(X-A_[0],Y-A_[1],45,6.5))
P2=norm(tot*C_); s2=summ(P2,X,Y,st); lab,nc2=ndimage.label(hpd_mask(P2,.95))
put("L2b.north",P2[Y>50].sum()*100); put("L2b.nc",nc2); put("L2b.a95",s2["a95"]); put("L2b.mx",s2["mx"]); put("L2b.my",s2["my"])
# the bearing of the north solution from A
put("L2.bear_n",math.degrees(math.atan2(50-20,68-50))%360 if False else math.degrees(math.atan2(30,18)))
# L5 prior-dominated: single weak direction evidence
Wk=np.nan_to_num(lik_dir(X-Dm[0],Y-Dm[1],45,2.0)); P=norm(Wk); s_=summ(P,X,Y,st)
put("L5.a95",s_["a95"]); put("L5.share",s_["a95"]/AREA*100)
# prior sensitivity: prior 3x in NE quadrant and 3x in SW
pri=np.where((X>50)&(Y>50),3.0,1.0); P3=norm(Wk*pri); put("L5.mass_ne_flat",P[(X>50)&(Y>50)].sum()*100); put("L5.mass_ne_pri",P3[(X>50)&(Y>50)].sum()*100)
# --- era Bayes factor
lu=np.ones_like(ug)
for (L,l,s) in [(12,5.0,0.08),(10,4.1,0.08)]:
    lu=lu*zpdf(np.log(L)-np.log(l/ug),s)
ha=(ug>=0.36)&(ug<0.42); hb=(ug>=0.42)&(ug<=0.48)
put("era.bf",lu[ha].mean()/lu[hb].mean()); put("era.pa",lu[ha].mean()/(lu[ha].mean()+lu[hb].mean())*100)
if __name__=="__main__":
    for k,v in R.items():
        if k[0] in "KL" or k.startswith("era") or k.startswith("J3.s_"): print(k, round(v,4) if isinstance(v,float) else v)
    for k in ("K.scen","K.latent","K.post"): print(TAB[k])
