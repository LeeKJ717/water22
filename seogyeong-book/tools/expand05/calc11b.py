from lib import *
# B6 시기: E3 343, E6 586, E7 552~593, E1 1081
yrs={"E3 고국원왕 13년":343,"E7 착공":552,"E6 평원왕 28년 이거":586,"E7 북성 완성":593,"E1 문종 35년":1081}
gap=lambda a,b: b-a
g_E3_E7=552-343; g_E7s_E6=586-552; g_E6_E7e=593-586; g_E7e_E1=1081-593; g_E3_E1=1081-343; g_E6_E1=1081-586; g_E3_E6=586-343
dur=593-552; dur_incl=dur+1
# B7 km -> 리
tot=23.0
li=(tot/U_HI, tot/U_LO)
li_w=li[1]-li[0]
seg12=12
frac=(seg12/li[1], seg12/li[0])
# 둘레 / 면적
A=11.85
# 4~5 등분 확인
ns=[(n, 12*n) for n in (3,4,5,6)]
rel_w=(li[1]-li[0])/((li[0]+li[1])/2)
# 반대로 12리가 4.32~5.76 km, 총 23 km의 비
frac_km=(12*U_LO/tot, 12*U_HI/tot)
if __name__=="__main__":
    print(g_E3_E7,g_E7s_E6,g_E6_E7e,g_E7e_E1,g_E3_E1,g_E6_E1,g_E3_E6,dur,dur_incl)
    print(li,li_w,frac,rel_w,frac_km)
k12=(12*U_LO,12*U_HI)
n_rng=(tot/k12[1], tot/k12[0])
