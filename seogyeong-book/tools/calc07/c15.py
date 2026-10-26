from lib07 import *
import c14
from c1 import mk, US
# exact posterior mean of u for the mirror case (grid)
xs,ys,X,Y=mk(0,100,0,100,0.5)
A_=(20,50); B_=(80,50)
dA=np.hypot(X-A_[0],Y-A_[1]); dB=np.hypot(X-B_[0],Y-B_[1])
us=np.linspace(0.36,0.48,121); w=[]
for u in us:
    w.append((zpdf(np.log(100)-np.log(np.maximum(dA,1e-9)/u),0.10)*zpdf(np.log(100)-np.log(np.maximum(dB,1e-9)/u),0.10)).sum())
w=np.array(w); w/=w.sum(); put("M.u_exact",(w*us).sum()); put("M.u_sd",math.sqrt((w*us**2).sum()-(w*us).sum()**2))
put("M.u_prior",0.42); put("M.acc_target_lo",20); put("M.acc_target_hi",50)
for s in ("0.3","2","6","30"):
    put(f"M.s{s}.udiff",R[f"M.s{s}.umean"]-R["M.u_exact"])

put("C.k8.cells",R["C.k8.area"]/4.0)
