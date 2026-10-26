from lib07 import *
import c9
rows=[]; prods=[]
us=[0.36,0.39,0.42,0.45,0.48]
for u in us:
    z8=math.log(12)-math.log(5.0/u); z10=math.log(10)-math.log(4.1/u)
    f8=float(zpdf(z8,0.08)); f10=float(zpdf(z10,0.08)); prods.append(f8*f10)
    rows.append([f"{u:.2f}",f"{5.0/u:.2f}",f"{z8:+.3f}",f"{f8:.3f}",f"{4.1/u:.2f}",f"{z10:+.3f}",f"{f10:.3f}",f"{f8*f10:.3f}"])
prods=np.array(prods); post=prods/prods.sum()
for r,p in zip(rows,post): r.append(f"{p*100:.1f}")
ptab("E.hand",["$u$","제2석: 5.0 km ÷ $u$ (리)","$z$","$f(z)$","제1석: 4.1 km ÷ $u$ (리)","$z$","$f(z)$","곱","5칸 안에서 정규화(%)"],rows)
put("E.hand.f8_42",float(zpdf(math.log(12)-math.log(5.0/0.42),0.08)))
put("E.hand.norm",1/(0.08*math.sqrt(2*math.pi)))
put("E.sd_prior",0.25/math.sqrt(12))
put("E.sd_drop",(1-R["E.ok.sd"]/R["E.e8.sd"])*100)
put("E.bad_shift",(1-R["E.bad.m"]/R["E.ok.m"])*100)
put("E.len10",10*R["E.ok.m"])
put("E.mismatch34",(10*R["E.ok.m"]-3.4)/(10*R["E.ok.m"])*100)
put("E.mismatch28",(10*R["E.ok.m"]-2.8)/(10*R["E.ok.m"])*100)
put("G.eps_from_beta",(1-R["G.beta1"])*100)
if __name__=="__main__":
    print(TAB["E.hand"])
    for k in ("E.hand.f8_42","E.sd_prior","E.sd_drop","E.bad_shift","E.len10","E.mismatch34","E.mismatch28","E.eta90.m","E.eta90.drop","E.eta80.drop","E.wide.sd","E.wide.m"): print(k,R[k])
