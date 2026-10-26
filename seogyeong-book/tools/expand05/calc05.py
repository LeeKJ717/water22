from lib import *
def I(a,b): return (a,b)
def inter(p,q): 
    lo,hi=max(p[0],q[0]),min(p[1],q[1]); return (lo,hi) if lo<=hi else None
def add(p,q): return (p[0]+q[0],p[1]+q[1])
def sub(p,q): return (p[0]-q[1],p[1]-q[0])
D=(3.6,7.2)
S0=(-20,20); L0=(5,7); R0=(-7,-3)
def run_indep():
    S,L,R=S0,L0,R0; hist=[(S,L,R)]
    for it in range(10):
        S1=inter(inter(S,sub(L,D)),add(R,D))
        L1=inter(L,add(S1,D)); R1=inter(R,sub(S1,D))
        if (S1,L1,R1)==(S,L,R): break
        S,L,R=S1,L1,R1; hist.append((S,L,R))
    return hist
hi=run_indep()
def run_sym():
    S,L,R,d=S0,L0,R0,D; hist=[(S,L,R,d)]
    for it in range(20):
        # L=S+d, R=S-d, S=(L+R)/2, d=(L-R)/2
        L1=inter(L,add(S,d)); R1=inter(R,sub(S,d))
        S1=inter(S,(( L1[0]+R1[0])/2,(L1[1]+R1[1])/2))
        S1=inter(S1,sub(L1,d)); S1=inter(S1,add(R1,d))
        d1=inter(d,((L1[0]-R1[1])/2,(L1[1]-R1[0])/2))
        d1=inter(d1,sub(L1,S1)); d1=inter(d1,sub(S1,R1))
        new=(S1,L1,R1,d1)
        if new==(S,L,R,d): break
        S,L,R,d=new; hist.append(new)
    return hist
hs=run_sym()
wi=hi[-1][0][1]-hi[-1][0][0]; ws=hs[-1][0][1]-hs[-1][0][0]
w0=S0[1]-S0[0]
# 비대칭: 동쪽 10여 리, 서쪽 10리 미만 -> 변형
if __name__=="__main__":
    print(hi); print(hs); print(wi,ws)
