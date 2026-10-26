from lib import *
# B4: E12 □里四尺
cands=list(range(1,11))+[20,30]
C_LO,C_HI=0.1,1.0          # 척의 길이 (m), 아주 넓은 가정
chi_lo,chi_hi=4*C_LO/1000, 4*C_HI/1000     # km
rows=[]
for n in cands:
    lo=n*U_LO; hi=n*U_HI
    rows.append((n,lo,hi,lo+chi_lo,hi+chi_hi,(hi+chi_hi)-(lo+chi_lo)-(hi-lo)))
frac_max = chi_hi/U_LO         # 4척 최대 / 1리 최소
frac_min = chi_lo/U_HI
# 척 가정에서 4척의 영향: 너비 증가량 m
width_add_m=(chi_hi-chi_lo)*1000
# n=1 에서의 상대 폭 증가
rel=( (U_HI+chi_hi)-(U_LO+chi_lo) )/(U_HI-U_LO)-1
# B5: 규모
A=11.85; P=23.0
Req=math.sqrt(A/math.pi); Dia=2*Req
Pc=2*math.pi*Req
shape=P*P/(4*math.pi*A)
r1=(3.6,7.2)
ratio_lo=r1[0]/Req; ratio_hi=r1[1]/Req
sec10=(10*U_LO,10*U_HI)
dia_ratio=(sec10[0]/Dia, sec10[1]/Dia)
# 조건부 표: 12리 구간이 성벽 총길이의 1/n 이라면
ntab=[]
for n in range(1,9):
    u=P/(12*n); ntab.append((n,u,U_LO<=u<=U_HI))
nin=[n for n,u,ok in ntab if ok]
# 장안성 면적 비율 검산
parts=[25,130,300,730]; tot=sum(parts)
if __name__=="__main__":
    for r in rows: print([round(x,4) for x in r])
    print(frac_max,frac_min,width_add_m,rel)
    print(Req,Dia,Pc,shape,ratio_lo,ratio_hi,dia_ratio,ntab,nin,tot)
