from lib import *
# C12: 읍성 (0,-17), 능선 y=0, 안장 x=-18,2,24 ; 사십 리 +-10% 
T=(0.0,-17.0)
r_lo=36*U_LO; r_hi=44*U_HI
sad=[(-18,0),(2,0),(24,0)]
rows=[]
for x,y in sad:
    d=math.hypot(x-T[0],y-T[1]); a=brg(x-T[0],y-T[1])
    n_ok = (a<=22.5 or a>=337.5)
    ne_ok = 22.5<=a<=67.5
    rows.append((x,d,a,r_lo<=d<=r_hi,n_ok,ne_ok))
h_ring=math.sqrt(max(r_hi**2-17**2,0))
h_sec=17*math.tan(math.radians(22.5))
seg_n=(-min(h_ring,h_sec),min(h_ring,h_sec)); seg_n_len=seg_n[1]-seg_n[0]
ne_lo=17*math.tan(math.radians(22.5)); ne_hi=min(17*math.tan(math.radians(67.5)),h_ring)
ne_len=max(ne_hi-ne_lo,0)
ring_lo_ok = r_lo<17     # 능선까지 최단거리 17이 아래끝보다 크다
passed=[r[0] for r in rows if r[3] and r[4]]
passed_ne=[r[0] for r in rows if r[3] and r[5]]
# C13
Lr=(12.5,20.0); c=(1.1,1.4)
r_in=Lr[0]/c[1]; r_out=Lr[1]/c[0]
a_in=math.pi*r_in**2; a_out=math.pi*r_out**2
a_in8=a_in/8; a_out8=a_out/8
# 후보 4곳(가상) 거리
cd=[("가", 6.0),("나", 12.0),("다", 17.0),("라", 21.0)]
c13=[(n,d,"확실" if d<=r_in else ("가능" if d<=r_out else "탈락")) for n,d in cd]
ratio=a_out/a_in
# C14 관청 터: 성 둘레 10리, 직사각형, 가로세로비 k, 서북 3분의 1 구획
P=(10*U_LO,10*U_HI)
def rect(p,k):
    a=p/2*k/(1+k); b=p/2/(1+k); return a,b
c14=[]
for k in (1.0,1.25,1.5):
    for p in P:
        a,b=rect(p,k); c14.append((k,p,a,b,a*b,a*b/9,a*b/9*100))
c14_wall=(min(r[4] for r in c14),max(r[4] for r in c14))
c14_reg=(min(r[5] for r in c14),max(r[5] for r in c14))
c14_ha=(c14_reg[0]*100,c14_reg[1]*100)
c14_ratio=c14_reg[1]/c14_reg[0]
# 성의 위치를 모르고 중심이 반지름 r_c km 원판 안에 있다고 할 때
rc=2.0; c14_disk=math.pi*rc**2
