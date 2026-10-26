from lib07 import *
import c13, c7
from c7 import *
import c7 as C7
# grid resolution experiment: near-world, correct likelihood, step 2 vs 0.5
res={}
for stp in (2.0,0.5):
    C7.st=stp; C7.gx=np.arange(0,100.01,stp); C7.X,C7.Y=np.meshgrid(C7.gx,C7.gx)
    X,Y=C7.X,C7.Y
    import c7 as m
    m.X,m.Y=X,Y; m.st=stp
    h,a=m.run(f"g{stp}",nw=200,seed=3,gen=lambda rng: m.world(rng,near=True),model=lambda r,L: m.post(r,L,0.10))
    res[stp]=(h,a)
    put(f"GR.{stp}.h50",h[0]*100); put(f"GR.{stp}.h80",h[1]*100); put(f"GR.{stp}.h95",h[2]*100); put(f"GR.{stp}.area",a)
m.st=2.0; m.gx=np.arange(0,100.01,2.0); m.X,m.Y=np.meshgrid(m.gx,m.gx)
rows=[[f"{s_:g}",f"{res[s_][0][0]*100:.1f}",f"{res[s_][0][1]*100:.1f}",f"{res[s_][0][2]*100:.1f}",f"{res[s_][1]:,.0f}"] for s_ in (2.0,0.5)]
ptab("GR.tab",["격자 간격 (km)","50% 영역 적중(%)","80%","95%","95% 영역 면적 중앙값 (km²)"],rows)
put("GR.cells2",R["GR.2.0.area"]/4.0); put("GR.cells05",R["GR.0.5.area"]/0.25)
if __name__=="__main__":
    print(TAB["GR.tab"]); print(R["GR.cells2"],R["GR.cells05"])
