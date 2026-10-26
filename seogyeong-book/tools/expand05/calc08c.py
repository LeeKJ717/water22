from lib import *
units={"좁게":(0.40,0.44),"이 장":(U_LO,U_HI),"넓게":(0.30,0.60)}
rows=[]
for k,(lo,hi) in units.items():
    r=(10*lo,15*hi)          # E1: 10~15리
    e8=(12*lo,12*hi)         # E8: 12리
    n=(23/(12*hi),23/(12*lo))  # E7/E8 비
    ring=math.pi*(r[1]**2)   # 원판 넓이 (0~R)
    rows.append((k,lo,hi,r,r[1]-r[0],e8,e8[1]-e8[0],n,ring))
base=rows[1]
rel=[(k,(x[4]/base[4]),(x[8]/base[8])) for k,x in zip(units,rows)]
