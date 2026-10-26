from lib import *
# C4: 합수머리에서 상류 20리 (하천을 따라)
P=np.array([(0,0),(4,2),(6,5),(3,8),(5,12),(10,13),(13,10),(17,9),(20,13)],float)
seg=np.hypot(*(P[1:]-P[:-1]).T); cum=np.concatenate([[0],np.cumsum(seg)])
def at(s):
    i=np.searchsorted(cum,s)-1; i=max(0,min(i,len(seg)-1)); t=(s-cum[i])/seg[i]; return P[i]+t*(P[i+1]-P[i])
S20=(20*U_LO,20*U_HI); S20r=(18*U_LO,22*U_HI)
a1,b1=at(S20[0]),at(S20[1]); a2,b2=at(S20r[0]),at(S20r[1])
chord1=float(np.hypot(*(b1-a1))); chord2=float(np.hypot(*(b2-a2)))
len1=S20[1]-S20[0]; len2=S20r[1]-S20r[0]
total_len=cum[-1]; straight_total=float(np.hypot(*(P[-1]-P[0])))
sinu=total_len/straight_total
# 직선 고리로 잘못 읽은 경우의 넓이 vs 강 띠
ring_wrong=math.pi*(S20[1]**2-S20[0]**2)
band=len1*2*(2*U_HI)    # 양쪽 2리
# 직선거리 대 경로거리: 두 구간 끝점의 직선거리
d_end_lo=float(np.hypot(*a1)); d_end_hi=float(np.hypot(*b1))
# C5: 섬 (바닷길 70리, 북동쪽, 육지 제외)
SEA=(70*U_LO,70*U_HI); WIND=(1.0,1.25)
sea_st=(SEA[0]/WIND[1],SEA[1]/WIND[0])
h=0.1; X,Y=grid(-5,60,-5,60,h)
base=ring(X,Y,(0,0),*sea_st)&sector(X,Y,(0,0),22.5,67.5)
land=(X<0)|(dist(X,Y,24,26)<=12)
sea_only=base&~land
a_base=area(base,h); a_sea=area(sea_only,h)
# C6: 사찰 : 산 남쪽 기슭, 샘 곁
Hk=900.0; Rm=12.0
def hgt(r): return np.clip(Hk*(1-r/Rm),0,None)
r=dist(X,Y,0,0) # reuse grid? need centered at peak: use new grid
X6,Y6=grid(-14,14,-14,14,0.05)
r6=dist(X6,Y6,0,0); H6=np.clip(Hk*(1-r6/Rm),0,None)
foot=(H6>=0.10*Hk)&(H6<=0.35*Hk)
south=sector(X6,Y6,(0,0),135,225)
band6=foot&south
a_band=area(band6,0.05)
springs=[(-2.0,-9.0),(3.0,-8.5),(7.0,3.0)]
near=np.zeros_like(X6,dtype=bool)
sp_info=[]
for sx,sy in springs:
    nm=dist(X6,Y6,sx,sy)<=0.5
    inb=area(nm&band6,0.05)
    sp_info.append((sx,sy,float(np.hypot(sx,sy)),brg(sx,sy),inb))
    near|=nm
a_final=area(near&band6,0.05)
rlo,rhi=Rm*(1-0.35),Rm*(1-0.10)
if __name__=="__main__":
    print(cum,S20,len1,chord1,chord2,len2,sinu,ring_wrong,band,d_end_lo,d_end_hi)
    print(sea_st,a_base,a_sea,a_base-a_sea)
    print(a_band,rlo,rhi,sp_info,a_final)
