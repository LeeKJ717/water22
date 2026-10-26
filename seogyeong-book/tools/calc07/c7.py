from lib07 import *
import time
st=2.0
gx=np.arange(0,100.01,st); X,Y=np.meshgrid(gx,gx)
U9=np.linspace(0.36,0.48,9)
def world(rng,k=4,sig=0.10,utrue=None,eras=False,copy=False,near=False):
    t=rng.uniform(30,70,2)
    refs=[]
    while len(refs)<k:
        if near:
            a=rng.uniform(0,2*math.pi); rr=rng.uniform(3,12); r=t+rr*np.array([math.cos(a),math.sin(a)])
        else:
            r=rng.uniform(5,95,2)
        if near or math.hypot(*(r-t))>15: refs.append(r)
    refs=np.array(refs)
    ut=rng.uniform(0.38,0.46) if utrue is None else utrue
    d=np.hypot(*(refs-t).T)
    if eras:
        us=np.array([0.37,0.37,0.47,0.47][:k]); L=d/us*np.exp(sig*rng.normal(size=k))
    else:
        L=d/ut*np.exp(sig*rng.normal(size=k))
    L=np.maximum(np.round(L),1.0)
    if copy:
        refs=np.vstack([refs,refs[0]]); L=np.append(L,L[0])
    return t,refs,L
def like_terms(refs,L,sig,bug=False):
    out=[]
    for r,l in zip(refs,L):
        d=np.hypot(X-r[0],Y-r[1])
        out.append((d,l))
    return out
def post(refs,L,sig,mode="shared",bug=False,us=U9,weights=None,groups=None):
    terms=like_terms(refs,L,sig)
    if mode=="shared":
        tot=np.zeros_like(X)
        for u in us:
            v=np.ones_like(X)
            for i,(d,l) in enumerate(terms):
                f=zpdf(np.log(l)-np.log(np.maximum(d,1e-6)/u),sig)
                if bug: f=f/np.maximum(d,1e-6)
                w=1.0 if weights is None else weights[i]
                v=v*f**w
            tot+=v
        return norm(tot)
    if mode=="indep":
        v=np.ones_like(X)
        for (d,l) in terms:
            v=v*np.mean([zpdf(np.log(l)-np.log(np.maximum(d,1e-6)/u),sig) for u in us],axis=0)
        return norm(v)
    if mode=="groups":
        # separate u per group
        tot=np.zeros_like(X)
        gl=sorted(set(groups))
        import itertools
        for combo in itertools.product(us,repeat=len(gl)):
            v=np.ones_like(X)
            for (d,l),g in zip(terms,groups):
                u=combo[gl.index(g)]
                v=v*zpdf(np.log(l)-np.log(np.maximum(d,1e-6)/u),sig)
            tot+=v
        return norm(tot)
def cover(P,t,levels=(0.5,0.8,0.95)):
    ix=int(round(t[0]/st)); iy=int(round(t[1]/st))
    f=P.ravel(); idx=np.argsort(-f); c=np.cumsum(f[idx]); rank=np.empty(f.size,int); rank[idx]=np.arange(f.size)
    r=rank[iy*P.shape[1]+ix]; cr=c[r]-f[idx[r]]  # mass strictly above truth cell
    res=[]
    for lv in levels: res.append(cr<lv)
    areas=[(np.searchsorted(c,lv)+1)*st*st for lv in levels]
    return res,areas
def run(name,nw=300,seed=1,gen=None,model=None):
    rng=np.random.default_rng(seed); hits=np.zeros(3); ar=[]
    for _ in range(nw):
        t,refs,L=gen(rng); P=model(refs,L)
        h,a=cover(P,t); hits+=np.array(h); ar.append(a[2])
    hits/=nw
    put(f"C.{name}.h50",hits[0]*100); put(f"C.{name}.h80",hits[1]*100); put(f"C.{name}.h95",hits[2]*100); put(f"C.{name}.area",float(np.median(ar)))
    return hits,float(np.median(ar))
t0=time.time()
base=lambda rng: world(rng)
variants=[
 ("v1","기본: 옳은 $\\sigma=0.10$, 공유 단위",base,lambda r,L: post(r,L,0.10)),
 ("v2","$\\sigma$를 너무 작게 (0.05)",base,lambda r,L: post(r,L,0.05)),
 ("v3","$\\sigma$를 너무 크게 (0.20)",base,lambda r,L: post(r,L,0.20)),
 ("v10","단위를 증거마다 따로 뽑음",base,lambda r,L: post(r,L,0.10,mode="indep")),
 ("v9","우도에 $1/d$ 인자를 잘못 넣음",base,lambda r,L: post(r,L,0.10,bug=True)),
]
rows=[]
for key,name,g,m in variants:
    h,a=run(key,gen=g,model=m); rows.append([name,f"{h[0]*100:.1f}",f"{h[1]*100:.1f}",f"{h[2]*100:.1f}",f"{a:,.0f}"]); print(key,h,a,time.time()-t0,flush=True)
ptab("C.tab1",["모형","50% 영역 적중(%)","80% 영역 적중(%)","95% 영역 적중(%)","95% 영역 면적 중앙값 (km²)"],rows)
# eras
rows=[]
g=lambda rng: world(rng,eras=True)
h,a=run("v4",gen=g,model=lambda r,L: post(r,L,0.10)); rows.append(["단위를 하나로 묶음 (옳지 않은 가정)",f"{h[0]*100:.1f}",f"{h[1]*100:.1f}",f"{h[2]*100:.1f}",f"{a:,.0f}"])
h,a=run("v5",gen=g,model=lambda r,L: post(r,L,0.10,mode="groups",groups=[0,0,1,1])); rows.append(["시대마다 단위를 따로 둠",f"{h[0]*100:.1f}",f"{h[1]*100:.1f}",f"{h[2]*100:.1f}",f"{a:,.0f}"])
ptab("C.tab2",["모형 (두 시대의 단위가 0.37과 0.47인 세계)","50%","80%","95%","95% 영역 면적 중앙값 (km²)"],rows); print("eras",time.time()-t0,flush=True)
# copies
rows=[]
g=lambda rng: world(rng,k=3,copy=True)
h,a=run("v6",gen=g,model=lambda r,L: post(r,L,0.10)); rows.append(["복사본을 독립 증거로 셈",f"{h[0]*100:.1f}",f"{h[1]*100:.1f}",f"{h[2]*100:.1f}",f"{a:,.0f}"])
h,a=run("v7",gen=g,model=lambda r,L: post(r,L,0.10,weights=[0.5,1,1,0.5])); rows.append(["원본과 복사본에 지수 1/2씩",f"{h[0]*100:.1f}",f"{h[1]*100:.1f}",f"{h[2]*100:.1f}",f"{a:,.0f}"])
g3=lambda rng: world(rng,k=3)
h,a=run("v7b",gen=g3,model=lambda r,L: post(r,L,0.10)); rows.append(["(참고) 복사본 없이 독립 증거 3개",f"{h[0]*100:.1f}",f"{h[1]*100:.1f}",f"{h[2]*100:.1f}",f"{a:,.0f}"])
ptab("C.tab3",["모형 (증거 3개 + 첫 증거의 복사본 1개)","50%","80%","95%","95% 영역 면적 중앙값 (km²)"],rows); print("copy",time.time()-t0,flush=True)
# number of evidence
rows=[]
for k in (2,3,4,8):
    h,a=run(f"k{k}",nw=300,gen=lambda rng,k=k: world(rng,k=k),model=lambda r,L: post(r,L,0.10)); rows.append([k,f"{h[0]*100:.1f}",f"{h[1]*100:.1f}",f"{h[2]*100:.1f}",f"{a:,.0f}"])
ptab("C.tab4",["증거 수","50%","80%","95%","95% 영역 면적 중앙값 (km²)"],rows); print("k",time.time()-t0,flush=True)
st=0.5; gx=np.arange(0,100.01,st); X,Y=np.meshgrid(gx,gx)
rows=[]
gn=lambda rng: world(rng,near=True)
h,a=run("v1n",nw=200,gen=gn,model=lambda r,L: post(r,L,0.10)); rows.append(["옳은 우도",f"{h[0]*100:.1f}",f"{h[1]*100:.1f}",f"{h[2]*100:.1f}",f"{a:,.0f}"])
h,a=run("v9n",nw=200,gen=gn,model=lambda r,L: post(r,L,0.10,bug=True)); rows.append(["$1/d$ 인자를 잘못 넣음",f"{h[0]*100:.1f}",f"{h[1]*100:.1f}",f"{h[2]*100:.1f}",f"{a:,.0f}"])
ptab("C.tab5",["모형 (기준점이 참 위치에서 3~12 km 안에 있는 세계)","50%","80%","95%","95% 영역 면적 중앙값 (km²)"],rows)
st=2.0; gx=np.arange(0,100.01,st); X,Y=np.meshgrid(gx,gx)
# u misspecified range (truth .50)
g=lambda rng: world(rng,utrue=0.50)
h,a=run("v11",gen=g,model=lambda r,L: post(r,L,0.10)); 
put("C.v11.note",0)
if __name__=="__main__":
    for k in ("C.tab5",): print(TAB[k])
    print(R["C.v11.h95"],R["C.v11.area"])
