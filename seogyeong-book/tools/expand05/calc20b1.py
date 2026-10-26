from lib import *
# 서경 작업지: 이 장의 입력으로 계산 가능한 값
g1=(LAT0,LON0)
t_xy=ll2xy(TLAT,TLON)
t_d=math.hypot(*t_xy); t_b=brg(*t_xy)
e1=(10*U_LO, 15*U_HI)       # 10여 리를 10~15리로 읽음 (사례 A1의 보통 읽기)
e1_hi_alt=(10*U_LO, 15*U_HI)
e8=(12*U_LO,12*U_HI)
e5_sum=25+130+300+730
e5_ratio=(25/e5_sum*100,130/e5_sum*100,300/e5_sum*100,730/e5_sum*100)
e7_dur=593-552+1
