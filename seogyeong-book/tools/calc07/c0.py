from lib07 import *
xs = np.arange(5, 60, 5.0); u = 0.40; s = 0.25
d1 = xs; d2 = 60-xs
def f1(x,L,ref,u=u,s=s): return lik_dist(L, abs(x-ref), u, s)
l1 = f1(xs,50,0); l2 = f1(xs,100,60)
n=len(xs); uni = np.ones(n)/n
w = np.where((xs>=25)&(xs<=40),3.0,1.0); flat = w/w.sum()
# table road1
rows=[]
for k in range(n):
    z=math.log(50)-math.log(xs[k]/u)
    rows.append([f"{xs[k]:.0f}", f"{xs[k]/u:.1f}", f"{z:+.3f}", f"{l1[k]:.3f}"])
ptab("road1",["후보 칸 $x$ (km)","$d/u$ (리)","$z=\\ln 50-\\ln(d/u)$","우도 $f(z)$"],rows)
put("road.norm", 1/(s*math.sqrt(2*math.pi)))
# table road2: both evidence
prod = l1*l2; post=norm(prod*uni); postf=norm(prod*flat); post1=norm(l1*uni)
rows=[[f"{xs[k]:.0f}",f"{l1[k]:.3f}",f"{l2[k]:.3f}",f"{prod[k]:.3f}",f"{post[k]*100:.1f}"] for k in range(n)]
ptab("road2",["$x$ (km)","증거 1 우도","증거 2 우도","곱","사후확률(%), 균등 사전"],rows)
put("road.prodsum",prod.sum()); put("road.mean",(post*xs).sum()); put("road.map",xs[post.argmax()])
put("road.post_map",post.max()*100)
rows=[[f"{xs[k]:.0f}",f"{uni[k]*100:.1f}",f"{flat[k]*100:.1f}",f"{post[k]*100:.1f}",f"{postf[k]*100:.1f}"] for k in range(n)]
ptab("road3",["$x$ (km)","균등 사전(%)","평지 3배 사전(%)","사후(균등 사전, %)","사후(평지 사전, %)"],rows)
put("road.flat_mean",(postf*xs).sum()); put("road.flat_map",xs[postf.argmax()]); put("road.flat_pmap",postf.max()*100)
put("road.flat_prior20",flat[3]*100); put("road.flat_prior25",flat[4]*100)
put("road.post1_mean",(post1*xs).sum()); put("road.post1_20",post1[3]*100); put("road.post_20",post[3]*100)
# only e1 summary
# HPD
def hp(P,level):
    idx=np.argsort(-P); c=np.cumsum(P[idx]); k=int(np.searchsorted(c,level))+1; return sorted(xs[idx[:k]]), c[k-1]
h50,c50=hp(post,0.5); h95,c95=hp(post,0.95)
put("road.h50",", ".join(f"{v:.0f}" for v in h50)); put("road.c50",c50*100)
put("road.h95",", ".join(f"{v:.0f}" for v in h95)); put("road.c95",c95*100); put("road.n95",len(h95))
# unit example, cell x=20 and x=25, three units
us=[0.35,0.40,0.45]
for cell in (20,25):
    a=[float(f1(cell,50,0,uu)) for uu in us]; b=[float(f1(cell,100,60,uu)) for uu in us]
    produ=[a[i]*b[i] for i in range(3)]
    put(f"unit{cell}.right",np.mean(produ)); put(f"unit{cell}.wrong",np.mean(a)*np.mean(b))
    put(f"unit{cell}.ratio",np.mean(produ)/(np.mean(a)*np.mean(b)))
    rows=[[f"{us[i]:.2f}",f"{a[i]:.3f}",f"{b[i]:.3f}",f"{produ[i]:.3f}"] for i in range(3)]
    ptab(f"unit{cell}",["$u$ (km/리)","증거 1 우도","증거 2 우도","곱"],rows)
    put(f"unit{cell}.ma",np.mean(a)); put(f"unit{cell}.mb",np.mean(b))
# shared-u posterior along road vs wrong
def shared(xs,Ls_refs,us,s=s,eps=0.0):
    out=np.zeros(len(xs))
    for uu in us:
        v=np.ones(len(xs))
        for (L,r) in Ls_refs:
            v=v*((1-eps)*lik_dist(L,abs(xs-r),uu,s)+eps*WIDE)
        out+=v
    return out/len(us)
def indep(xs,Ls_refs,us,s=s):
    v=np.ones(len(xs))
    for (L,r) in Ls_refs:
        v=v*np.mean([lik_dist(L,abs(xs-r),uu,s) for uu in us],axis=0)
    return v
ev=[(50,0),(100,60)]
ps=norm(shared(xs,ev,us)); pi_=norm(indep(xs,ev,us))
sd=lambda P: math.sqrt((P*xs**2).sum()-(P*xs).sum()**2)
put("unit.sd_sh",sd(ps)); put("unit.sd_in",sd(pi_)); put("unit.mean_sh",(ps*xs).sum()); put("unit.mean_in",(pi_*xs).sum())
rows=[[f"{xs[k]:.0f}",f"{ps[k]*100:.1f}",f"{pi_[k]*100:.1f}"] for k in range(n)]
ptab("unit.post",["$x$ (km)","곱 먼저(올바른 방법), %","따로 평균(잘못된 방법), %"],rows)
# mixture: add wrong evidence 3 "A에서 십 리"(true cell 20)
ev3=ev+[(10,0)]
naive=norm(shared(xs,ev3,[0.40]));mix=norm(shared(xs,ev3,[0.40],eps=0.1))
rows=[[f"{xs[k]:.0f}",f"{f1(xs[k],10,0):.5f}",f"{0.9*f1(xs[k],10,0)+0.1*WIDE:.4f}",f"{naive[k]*100:.1f}",f"{mix[k]*100:.1f}"] for k in range(n)]
ptab("mix.tab",["$x$ (km)","잘못된 증거의 LN 밀도","혼합 우도 ($\\varepsilon=0.1$)","사후(순진, %)","사후(혼합, %)"],rows)
put("mix.wide",WIDE); put("mix.floor",0.1*WIDE)
put("mix.naive_map",xs[naive.argmax()]); put("mix.naive_pmap",naive.max()*100); put("mix.naive_p20",naive[3]*100)
put("mix.mix_map",xs[mix.argmax()]); put("mix.mix_pmap",mix.max()*100); put("mix.mix_p20",mix[3]*100)
put("mix.l_true",f1(20,10,0)); put("mix.lm_true",0.9*f1(20,10,0)+0.1*WIDE)
put("mix.z20",math.log(10)-math.log(20/0.4))
# metropolis 1D tiny: use post as pi, steps with fixed random numbers
rng=np.random.default_rng(7)
pos=0; path=[]; rows=[]
pi=post/post.max()
cur=9 # index of x=50
rs=[(+1,0.42),(-1,0.88),(-1,0.17),(-1,0.64),(-1,0.05),(-1,0.77),(+1,0.31),(-1,0.5),(-1,0.2),(-1,0.9)]
cur=8
for i,(dir_,r) in enumerate(rs,1):
    prop=cur+dir_
    if prop<0 or prop>=n: rows.append([i,f"{xs[cur]:.0f}","범위 밖","","","",f"{r:.2f}","제자리"]); continue
    a=min(1,pi[prop]/pi[cur]) if pi[cur]>0 else 1
    mv= r<a
    rows.append([i,f"{xs[cur]:.0f}",f"{xs[prop]:.0f}",f"{pi[cur]:.4f}",f"{pi[prop]:.4f}",f"{a:.3f}",f"{r:.2f}","예" if mv else "아니오"])
    if mv: cur=prop
ptab("mh1d",["걸음","현재 $x$","제안 $x$","$\\pi_{old}$","$\\pi_{new}$","이동 확률","난수","이동?"],rows)
if __name__=="__main__":
    for k,v in R.items(): print(k, v if not isinstance(v,float) else round(v,4))
    for k in ("road1","road2","road3","unit20","unit25","unit.post","mix.tab","mh1d"): print(k); print(TAB[k])
