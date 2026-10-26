from lib07 import *
import c4
A_=(20,50); B_=(80,50); LA=LB=100
def logpost(x,y,u):
    if not (0<=x<=100 and 0<=y<=100 and 0.36<=u<=0.48): return -np.inf
    dA=math.hypot(x-A_[0],y-A_[1]); dB=math.hypot(x-B_[0],y-B_[1])
    if dA<1e-6 or dB<1e-6: return -np.inf
    zA=math.log(LA)-math.log(dA/u); zB=math.log(LB)-math.log(dB/u)
    return -0.5*(zA/0.1)**2-0.5*(zB/0.1)**2
def chain(start,s,n,rng,su=0.01):
    x,y,u=start; lp=logpost(x,y,u); out=np.zeros((n,3)); acc=0
    for i in range(n):
        xn=x+s*rng.normal(); yn=y+s*rng.normal(); un=u+su*rng.normal()
        lpn=logpost(xn,yn,un)
        if lpn-lp>=0 or rng.random()<math.exp(lpn-lp): x,y,u,lp=xn,yn,un,lpn; acc+=1
        out[i]=(x,y,u)
    return out,acc/n
def ess(v):
    v=v-v.mean(); n=len(v); f=np.fft.rfft(v,2*n); ac=np.fft.irfft(f*np.conj(f))[:n]; ac/=ac[0]
    t=1.0
    for k in range(1,n):
        if ac[k]<0: break
        t+=2*ac[k]
    return n/t
starts=[(50,79,0.42),(50,21,0.42),(60,50,0.42),(90,10,0.40)]
rows=[]; N=20000; burn=2000
for s in (0.3,2.0,6.0,30.0):
    rng=np.random.default_rng(int(s*10)+11)
    ch=[]; accs=[]
    for st_ in starts:
        o,a=chain(st_,s,N,rng); ch.append(o[burn:]); accs.append(a)
    ys=np.array([c[:,1] for c in ch]); n=ys.shape[1]; m=ys.mean(1); W=ys.var(1,ddof=1).mean(); B=n*m.var(ddof=1)
    varp=(n-1)/n*W+B/n; rhat=math.sqrt(varp/W)
    north=[(c[:,1]>50).mean() for c in ch]
    ess_y=np.mean([ess(c[:,1]) for c in ch])
    allc=np.concatenate(ch)
    rows.append([f"{s:g}",f"{np.mean(accs)*100:.1f}",", ".join(f"{v*100:.0f}" for v in north),f"{rhat:.2f}",f"{ess_y:.0f}",f"{(allc[:,1]>50).mean()*100:.1f}"])
    put(f"M.s{s:g}.acc",np.mean(accs)*100); put(f"M.s{s:g}.rhat",rhat); put(f"M.s{s:g}.ess",ess_y); put(f"M.s{s:g}.north",(allc[:,1]>50).mean()*100)
    put(f"M.s{s:g}.umean",allc[:,2].mean())
    for i,v in enumerate(north): put(f"M.s{s:g}.n{i}",v*100)
ptab("M.tab",["제안 폭 $s$ (km)","채택률(%)","네 사슬이 북쪽에 머문 비율(%)","$\\hat R$ ($y$)","유효 표본 수(평균, $y$)","네 사슬을 합친 북쪽 비율(%)"],rows)
# burn-in trace from corner
rng=np.random.default_rng(5)
o,a=chain((95,5,0.40),2.0,3000,rng)
tr=[]; 
# distance to nearest mode
modes=[(50,50+29.39),(50,50-29.39)]
rows=[]
for k in (0,10,50,100,200,500,1000,2000):
    p=o[k]; dm=min(math.hypot(p[0]-m[0],p[1]-m[1]) for m in modes)
    rows.append([k,f"({p[0]:.1f}, {p[1]:.1f})",f"{p[2]:.3f}",f"{dm:.1f}"])
    put(f"M.b{k}.d",dm)
ptab("M.burn",["걸음","위치 $(x,y)$","$u$","가까운 봉우리까지 거리 (km)"],rows)
if __name__=="__main__":
    print(TAB["M.tab"]); print(TAB["M.burn"])
