from lib07 import *
import c10
from c1 import mk, summ, US
st=0.5; xs,ys,X,Y=mk(0,100,0,100,st); ref=(50,50); d=np.hypot(X-ref[0],Y-ref[1])
def radial(P):
    idx=np.argsort(d.ravel()); c=np.cumsum(P.ravel()[idx]); dd=d.ravel()[idx]
    return dd[np.searchsorted(c,0.025)],dd[np.searchsorted(c,0.975)]
rows=[]
for nm,us,sg in (("$u$ 넓음(0.36~0.48), $\\sigma=0.10$",US,0.10),("$u$ 좁음(0.405~0.435), $\\sigma=0.10$",np.linspace(0.405,0.435,5),0.10),("$u$ 넓음, $\\sigma=0.03$",US,0.03),("$u$ 좁음, $\\sigma=0.03$",np.linspace(0.405,0.435,5),0.03)):
    tot=np.zeros_like(X)
    for u in us: tot+=zpdf(np.log(50)-np.log(np.maximum(d,1e-9)/u),sg)
    P=norm(tot); lo,hi=radial(P); a=summ(P,X,Y,st)["a95"]
    rows.append([nm,f"{lo:.1f}",f"{hi:.1f}",f"{hi-lo:.1f}",f"{a:,.0f}"])
    put("I1.w."+str(len(rows)),hi-lo); put("I1.a."+str(len(rows)),a)
ptab("I1.err",["입력","95% 반지름 하한 (km)","상한 (km)","폭 (km)","95% 영역 (km²)"],rows)
put("I1.sdlnu",(0.12/math.sqrt(12))/0.42); put("I1.comb",math.sqrt(R["I1.sdlnu"]**2+0.1**2))
put("I1.u_only_lo",50*0.36); put("I1.u_only_hi",50*0.48)
# I2 winding
put("I2.w80_lo",R["I2.r95lo"]*0.8); put("I2.w80_hi",R["I2.r95hi"]*0.8)
put("I2.ratio_to_li",R["I2.a95"]/R["I2.li25.a95"])
# I3 bits
put("I3.bits",math.log2(R["I3.a95"]/R["I1.ring.a95"]))
put("I3.share",R["I3.a95"]/100.0); put("I1.share",R["I1.ring.a95"]/100.0)
# I6 scale
put("I6.s15_a95",2*math.pi*15**2*math.log(20)); put("I6.ratio",9.0)
put("I4.east_ring",R["I4.eastshare"]); put("I4.ratio",R["I4.a95n"]/R["I4.a95"])
put("I5.ratio",R["I5.a95n"]/R["I5.a95"])
# I5 with band width 10
A_=(20,50); B_=(80,50); ds=np.abs(Y-50)  # segment is horizontal; points beyond ends ignored
dA=np.hypot(X-A_[0],Y-A_[1])
inseg=(X>=A_[0])&(X<=B_[0])
def dseg(X,Y):
    t=np.clip((X-20)/60.0,0,1); return np.hypot(X-(20+60*t),Y-50)
dd=dseg(X,Y)
for w in (3.0,10.0):
    band=np.exp(-dd**2/(2*w*w)); tot=np.zeros_like(X)
    for u in US: tot+=zpdf(np.log(30)-np.log(np.maximum(dA,1e-9)/u),0.10)*band
    put(f"I5.w{int(w)}.a95",summ(norm(tot),X,Y,st)["a95"])
put("I5.w_ratio",R["I5.w10.a95"]/R["I5.w3.a95"])
if __name__=="__main__":
    print(TAB["I1.err"])
    for k in ("I1.sdlnu","I1.comb","I2.w80_lo","I2.w80_hi","I2.ratio_to_li","I3.bits","I3.share","I1.share","I6.s15_a95","I4.ratio","I5.ratio"): print(k,R[k])
