from lib import *
# 개념1,2
a30=(30*U_LO,30*U_HI)
inv=(a30[0]/U_HI, a30[1]/U_LO)         # 구간으로 나눠 리 수 복원 시도
# 개념3
rel_w=(a30[1]-a30[0])/((a30[0]+a30[1])/2)
inner=(10.8,12.0)    # 입력 구간이 좁아지면
outer_in=(inner[0]*1.0, inner[1]*1.0)
# 개념5: 칸 크기와 넓이
exact=math.pi*(7.2**2-3.6**2)
gtab=[]
for h in (2.5,1.0,0.5,0.1):
    X,Y=grid(-8,8,-8,8,h)
    m=ring(X,Y,(0,0),3.6,7.2)
    gtab.append((h,area(m,h),(area(m,h)-exact)/exact*100))
# 개념6: 7x7 ascii
def amap(mask,xs,ys,ch='#'):
    rows=[]
    for j in range(len(ys)-1,-1,-1):
        rows.append(''.join(ch if mask[j,i] else '.' for i in range(len(xs))))
    return '\n'.join(rows)
xs=np.arange(-6,7); ys=np.arange(-6,7)
XX,YY=np.meshgrid(xs,ys)
m1=ring(XX,YY,(0,0),3.0,5.5)
m2=sector(XX,YY,(0,0),45,135)
m3=(YY<=1)
mall=m1&m2&m3
ascii1=amap(m1,xs,ys); ascii2=amap(m2,xs,ys); ascii3=amap(m3,xs,ys); ascii_all=amap(mall,xs,ys,'@')
n1,n2,n3,nall=int(m1.sum()),int(m2.sum()),int(m3.sum()),int(mall.sum())
n12=int((m1&m2).sum())
# 개념7: 작은 전파 예
def inter(p,q): return (max(p[0],q[0]),min(p[1],q[1]))
Xr=(0,10); Yr=(5,8); dr=(3,4)
h=[("처음",Xr,Yr)]
for k in range(4):
    Y1=inter(Yr,(Xr[0]+dr[0],Xr[1]+dr[1])); X1=inter(Xr,(Y1[0]-dr[1],Y1[1]-dr[0]))
    if (X1,Y1)==(Xr,Yr): break
    Xr,Yr=X1,Y1; h.append((f"{k+1}회",Xr,Yr))
prop=h
# 개념8: 점수
w=[1,1,1,0.5]
# 개념9: 공유
d1,d2=60,90
ind_diff=(d2*U_LO-d1*U_HI, d2*U_HI-d1*U_LO); sh_diff=((d2-d1)*U_LO,(d2-d1)*U_HI)
if __name__=="__main__":
    print(a30,inv,rel_w,exact,gtab,n1,n2,n3,nall,n12,prop,ind_diff,sh_diff)
    print(ascii1);print();print(ascii2);print();print(ascii3);print();print(ascii_all)
def side(a,b,la,lb):
    A=a.split('\n'); B=b.split('\n')
    out=[f"{la:<17}{lb}"]
    for x,y in zip(A,B): out.append(f"{x}    {y}")
    return '\n'.join(out)
ascii_ab=side(ascii1,ascii2,"(A) %d cells"%n1,"(B) %d cells"%n2)
ascii_cd=side(ascii3,ascii_all,"(C) %d cells"%n3,"(D) %d cells"%nall)
