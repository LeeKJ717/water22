import math
v=(60,90); t=10
walk=(t*v[0], t*v[1])
walk_ring=math.pi*(walk[1]**2-walk[0]**2)/1e6
t2=15; walk2=(t2*v[0], t2*v[1])
# 줄자
tape=(0.97,1.03)
ind=(10*tape[0]-8*tape[1], 10*tape[1]-8*tape[0]); sh=(2*tape[0],2*tape[1])
# 키
y0=(145,165); c0=(162,180); diff=(5,10)
c1=(max(c0[0],y0[0]+diff[0]), min(c0[1],y0[1]+diff[1]))
y1=(max(y0[0],c1[0]-diff[1]), min(y0[1],c1[1]-diff[0]))
# 용돈
allow=(8000,12000); weeks=(3,5)
tot=(allow[0]*weeks[0], allow[1]*weeks[1])
# 필름
areas=[400,300,250]
# 세 친구 이야기: 만난 시각
