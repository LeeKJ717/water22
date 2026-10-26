from lib import *
# B2: E10 西向十日里 -- 읽기 갈래
def L(n): return (n*U_LO, n*U_HI)
WLO,WHI=1.0,1.3
def straight(n): l=L(n); return (l[0]/WHI, l[1]/WLO)
readA=L(10); readA_s=straight(10)
# 숫자 한 글자가 다른 숫자였다면: n=5..15
nvals=list(range(6,15))
tabn=[(n,)+L(n) for n in nvals]
# B3: E11 갈래
# 첫 표현 '卄一里': (a) 21리 거리, (b) 날짜 卄一日의 오기 (거리 없음)
# 둘째 '□二里': □ 한 글자가 없는 십단위 글자 (十=10, 卄=20, 卅=30) 또는 숫자 아님 -> 2, 12, 22, 32
first_opts={"21리":21,"거리 아님":0}
second_opts={"2리":2,"12리":12,"22리":22,"32리":32}
# E8 12리, E10 10리 는 읽기 확정 가정, E12 는 B4에서; 여기서는 E8+E10+E11 합
base=12+10
TOT=23.0   # E7 총길이 km (2층)
# 성벽 총길이 상한 제약: sum_L * u <= 23  (구간이 서로 겹치지 않는다는 가정)
rows=[]
for fn,fv in first_opts.items():
    for sn,sv in second_opts.items():
        s=base+fv+sv
        umax=TOT/s          # u의 상한
        feas=(U_LO<=umax)   # 단위 구간과 겹침 여부
        # 허용 단위 구간
        hi=min(U_HI,umax)
        txt = '아니오 (상한이 0.36보다 작음)' if not feas else ('예 (영향 없음)' if umax>=U_HI else '예 (단위 위끝이 %.3f로 내려감)'%umax)
        rows.append((fn,sn,s,umax,feas,hi,txt))
# 위 합에 E12의 □리(1~9) 포함 시 최대
smax=base+21+32+9
# 단위 구간 통과하는 경우 수
nfeas=sum(1 for r in rows if r[4])
nrows=len(rows)
# 합이 얼마를 넘으면 불가능: s*U_LO > 23 -> s > 23/0.36
s_limit=TOT/U_LO
if __name__=="__main__":
    print(readA,readA_s)
    for r in rows: print(r)
    print(smax,s_limit,nfeas,nrows)
# B2 보강: 갈래 b (十 뒤 한 자리 숫자 1~9 -> 11~19리)
bs=list(range(11,20))
b_lo,b_hi=11*U_LO, 19*U_HI
u_lo10,u_hi10=readA
union=(min(readA[0],b_lo), max(readA[1],b_hi))
def secA(r1,r2): return 0.5*(math.pi/4)*(r2*r2-r1*r1)
sa_a=secA(*readA); sa_u=secA(*union); sa_as=secA(*readA_s)
