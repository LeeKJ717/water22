from lib07 import *
import c4, c6, c7
from c0 import xs, f1
from c2 import post_u, ug, usum
# Ex1: 1D road, A at 0, B at 60; 'A에서 삼십 리', 'B에서 백이십 리'; u=0.40, sigma .25
u=0.40; s=0.25
la=lik_dist(30,xs,u,s); lb=lik_dist(120,60-xs,u,s)
pr=la*lb; post=norm(pr)
rows=[[f"{xs[k]:.0f}",f"{la[k]:.3f}",f"{lb[k]:.3f}",f"{pr[k]:.3f}",f"{post[k]*100:.1f}"] for k in range(len(xs))]
ptab("X1",["$x$ (km)","'A에서 삼십 리' 우도","'B에서 백이십 리' 우도","곱","사후(%)"],rows)
put("X1.map",xs[post.argmax()]); put("X1.pmap",post.max()*100); put("X1.mean",(post*xs).sum())
# check: 30 li*0.4=12 km from A -> x=12 ; 200 li*0.4=80 km from B -> 60-80 <0 no cell... 
# Ex2
put("X2.annulus",math.pi*(24**2-18**2)); put("X2.ring95",math.pi*(27.8**2-16.6**2))
# Ex4
put("X4.p",(1+3)/(2+3))
# Ex5
eps=0.2; fl=eps*WIDE; put("X5.floor",fl); put("X5.t",0.8*1e-5+fl); put("X5.g",0.8*0.02+fl); put("X5.naive_ratio",0.02/1e-5); put("X5.mix_ratio",(0.8*0.02+fl)/(0.8*1e-5+fl))
# Ex6
p=np.array([0.35,0.25,0.15,0.10,0.08,0.05,0.02]); c=np.cumsum(p)
put("X6.n50",int(np.searchsorted(c,0.5)+1)); put("X6.n80",int(np.searchsorted(c,0.8)+1)); put("X6.n95",int(np.searchsorted(c,0.95)+1))
put("X6.c4",c[3]); put("X6.c3",c[2]); put("X6.c6",c[5]); put("X6.c5",c[4])
# Ex7
put("X7.a",0.2/0.5)
# Ex10
put("X10.s",math.sqrt(0.01+(c4.c3.r_eq/5.0)**2) if hasattr(c4.c3,'r_eq') else math.sqrt(0.01+(R['J1.req']/5.0)**2)); put("X10.r",R['J1.req']/5.0)
# Ex11
put("X11.u",3.0/7); put("X11.lo",3.0/7*math.exp(-1.96*0.08)); put("X11.hi",3.0/7*math.exp(1.96*0.08))
# Ex12
n=300; k=270; ph=k/n; se=math.sqrt(0.95*0.05/n); put("X12.se",se*100); put("X12.z",(ph-0.95)/se); put("X12.sehat",math.sqrt(ph*(1-ph)/n)*100)
put("X12.lo",(ph-1.96*math.sqrt(ph*(1-ph)/n))*100); put("X12.hi",(ph+1.96*math.sqrt(ph*(1-ph)/n))*100)
put("C.se95",math.sqrt(0.95*0.05/300)*100); put("C.se50",math.sqrt(0.5*0.5/300)*100)
# Ex3 / bearing of north solution from A in L2
put("L2.bear_n2",math.degrees(math.atan2(30,R["L2.yoff"])))
put("X3.ulo",R["A.sep"]/40); put("X3.uhi",R["A.sep"]/20)
# extra: ratios for 12 li at posterior mean
put("E.len12",12*R["E.e8.m"])
if __name__=="__main__":
    print(TAB["X1"]); 
    for k,v in R.items():
        if k.startswith("X"): print(k,v)
