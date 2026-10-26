from lib import *
# C1: 郡東五十里 (가상)
base=(50*U_LO,50*U_HI)
rnd=(45*U_LO,55*U_HI)
def secA(r1,r2,w): return 0.5*math.radians(2*w)*(r2*r2-r1*r1)
c1=[("단위만",base,22.5),("반올림(45~55리)",rnd,22.5),("반올림, 16방위",rnd,11.25),("반올림, 4방위",rnd,45)]
c1res=[(n,r[0],r[1],r[1]-r[0],secA(r[0],r[1],w)) for n,r,w in c1]
# 참 위치(가상) 21.6 km 동쪽 약간 북 (거리 50리*0.42=21km)
true=(20.0,6.0); tr=math.hypot(*true); tb=brg(*true)
inside = (rnd[0]<=tr<=rnd[1]) and abs(tb-90)<=22.5
h=0.2; X,Y=grid(-5,40,-25,25,h)
m=ring(X,Y,(0,0),*rnd)&sector(X,Y,(0,0),67.5,112.5)
cx=X[m].mean(); cy=Y[m].mean()
err=math.hypot(cx-true[0],cy-true[1])
maxdist=max(math.hypot(x-true[0],y-true[1]) for x,y in zip(X[m][::50],Y[m][::50]))
# C2: 일정 서술
day_flat=(25,40); day_mtn=(15,25); det=(1.1,1.4)
def cvt(d_lo,d_hi,day,det): return (d_lo*day[0]/det[1], d_hi*day[1]/det[0])
c2=[]
for tn,day in (("평지길",day_flat),("산길",day_mtn)):
    for sn,(a,b) in (("사흘 길 (2.5~3.5일)",(2.5,3.5)),("이틀 길이 넘고 사흘 길이 못 됨 (2~3일)",(2,3)),("사흘 길이 채 못 됨 (0~3일)",(0,3))):
        lo,hi=cvt(a,b,day,det); c2.append((tn,sn,lo,hi,hi-lo))
# C3: 하천 + 나루
riv=np.array([(-45,14),(-30,10),(-14,5),(-8,0),(-14,-5),(-30,-10),(-45,-14)],float)
def dist_poly(X,Y,P):
    d=np.full(X.shape,1e9)
    for a,b in zip(P[:-1],P[1:]):
        ab=b-a; L2=(ab**2).sum()
        t=((X-a[0])*ab[0]+(Y-a[1])*ab[1])/L2; t=np.clip(t,0,1)
        px=a[0]+t*ab[0]; py=a[1]+t*ab[1]
        d=np.minimum(d,np.hypot(X-px,Y-py))
    return d
h3=0.1; X3,Y3=grid(-30,5,-30,30,h3)
r30=(27*U_LO,33*U_HI)
mr=ring(X3,Y3,(0,0),*r30)&sector(X3,Y3,(0,0),247.5,292.5)
near=dist_poly(X3,Y3,riv)<=2*U_HI      # 강가 = 2리 이내
mm=mr&near
lab,n=ndimage.label(mm)
sizes=[area(lab==i,h3) for i in range(1,n+1)]
a_ring=area(mr,h3); a_near=area(near&(dist(X3,Y3,0,0)<40),h3); a_both=area(mm,h3)
cent=[(X3[lab==i].mean(),Y3[lab==i].mean()) for i in range(1,n+1)]
if __name__=="__main__":
    print(base,rnd); [print(r) for r in c1res]; print(inside,cx,cy,err,maxdist,tr,tb)
    [print(r) for r in c2]
    print(r30,a_ring,a_near,a_both,n,sizes,cent)
