from lib import *
def sec_area(w_half, R): return 0.5*math.radians(2*w_half)*R*R
WS=[11.25,22.5,45.0]; RS=[10,20,30]
SA={(w,R):sec_area(w,R) for w in WS for R in RS}
DISK={R:math.pi*R*R for R in RS}
# 격자 확인
h=0.1; X,Y=grid(-31,31,-31,31,h)
m=sector(X,Y,(0,0),67.5,112.5)&(dist(X,Y,0,0)<=30)
grid30=area(m,h)
cands=[("목멱산(갑)",13,4,2.5),("목멱산(을)",-11,-3,3.0),("목면산",8,-1,2.0),("백운산",10,12,3.0),("용악산",27,-2,4.0),("마천산",4,-14,2.0)]
rows=[]
for n,x,y,r in cands:
    d=math.hypot(x,y); a=brg(x,y); half=math.degrees(math.asin(min(1,r/d)))
    diff=abs((a-90+180)%360-180)
    ok = diff <= 22.5+half
    rows.append((n,x,y,r,d,a,half,diff,ok))
dpl = [r for r in rows if r[8]]
mtn_area=math.pi*2.5**2
ratio=mtn_area/SA[(22.5,30)]
ratio10=mtn_area/SA[(22.5,10)]
if __name__=="__main__":
    print({k:round(v,1) for k,v in SA.items()}, grid30)
    for r in rows: print([round(x,1) if not isinstance(x,(str,bool)) else x for x in r])
    print(mtn_area,ratio,ratio10)
