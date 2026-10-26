from lib07 import *
import c8, c1
from c1 import *
from scipy.stats import norm as N
# case 1 extras
u=0.42; dL=R["A.r1.dL"]; D=dL/u
put("A.u42.D",D); z=math.log(10)-math.log(D); put("A.u42.z1",z); f=float(zpdf(z,0.25)); put("A.u42.f1",f); put("A.u42.f1sq",f*f)
ind=float(N.cdf((math.log(D)-math.log(10))/0.1)-N.cdf((math.log(D)-math.log(20))/0.1)); put("A.u42.ind",ind); put("A.u42.indsq",ind*ind)
s=(49.5,50.5); PL=(54,50); PR=(45,51)
bL=math.degrees(float(bearing(PL[0]-s[0],PL[1]-s[1])))%360; bR=math.degrees(float(bearing(PR[0]-s[0],PR[1]-s[1])))%360
put("A.bL",bL); put("A.bR",bR); put("A.dL90",abs(bL-90)); put("A.dR270",abs(bR-270))
put("A.dirLl",float(lik_dir(PL[0]-s[0],PL[1]-s[1],90,6.5))); put("A.dirRl",float(lik_dir(PR[0]-s[0],PR[1]-s[1],270,6.5)))
put("A.prior_sd",0.12/math.sqrt(12)); put("A.sum_swap_a95",170.7)
put("A.r1.logbf",math.log10(R["A.r1.bf_swap"])); put("A.r2.logbf",math.log10(R["A.r2.bf_swap"]))
# case 2 extras
tests={"t1":(55,52),"t3":(75,60)}
Ms=[(70,52),(62,38),(80,66)]
for k,(tx,ty) in tests.items():
    ls=[float(lik_dir(m[0]-tx,m[1]-ty,90,6.5)) for m in Ms]
    for i,l in enumerate(ls,1): put(f"B.{k}.l{i}",l)
    put(f"B.{k}.mix",sum(ls)/3)
put("B.t3.ratio",R["B.t1.mix"]/R["B.t3.mix"])
put("B.eq_over_one",(R["B.eq.a95"]/R["B.one.a95"]-1)*100)
# case 3 extras
D0=(40,40)
def l(tx,ty,k): return float(lik_dir(tx-D0[0],ty-D0[1],45,k))
put("C.t_a_k2",l(60,60,2.0)); put("C.t_b_k65",l(60,45,6.5)); put("C.t_b_k2",l(60,45,2.0)); put("C.t_d_k65",l(20,60,6.5)); put("C.t_d_k2",l(20,60,2.0))
put("C.k_ratio",R["C.k2.a95"]/R["C.k65.a95"])
for d_ in (3,10,30): put(f"C.off{d_}",math.degrees(math.atan(3/d_)))
# case 4 extras
H=(50,40); K1=(30,70); K2=(66,22)
b1=math.degrees(float(bearing(K1[0]-H[0],K1[1]-H[1])))%360; b2=math.degrees(float(bearing(K2[0]-H[0],K2[1]-H[1])))%360
put("D.bK1",b1); put("D.bK2",b2); put("D.dK1",min(b1,360-b1))
l1=float(lik_dir(K1[0]-H[0],K1[1]-H[1],0,6.5)); l2=float(lik_dir(K2[0]-H[0],K2[1]-H[1],0,6.5))
put("D.lK1",l1); put("D.lK2",l2); put("D.w1",l1/(l1+l2)*100); put("D.w2",l2/(l1+l2)*100)
xs,ys,X,Y=mk(0,100,0,100,0.5)
v=(l1/(l1+l2))*np.exp(-((X-K1[0])**2+(Y-K1[1])**2)/(2*1.5**2))+(l2/(l1+l2))*np.exp(-((X-K2[0])**2+(Y-K2[1])**2)/(2*1.5**2))
put("D.dir.a95",summ(norm(v),X,Y,0.5)["a95"])
put("D.g95_1.5x2",2*R["D.g95_1.5"]); put("D.tau_ratio",R["D.t4.0.a95"]/R["D.t1.5.a95"])
if __name__=="__main__":
    for k in ("A.u42.D","A.u42.z1","A.u42.f1","A.u42.ind","A.bL","A.bR","A.dirLl","B.t1.l1","B.t3.l3","B.t3.ratio","B.eq_over_one","C.t_a_k2","C.k_ratio","C.off3","C.off10","C.off30","D.bK1","D.bK2","D.lK1","D.lK2","D.w1","D.w2","D.dir.a95","D.tau_ratio"): print(k,R[k])
