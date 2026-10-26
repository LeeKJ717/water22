from lib import *
def km(a,b): return (a*U_LO, b*U_HI)
def ringA(r): return math.pi*(r[1]**2-r[0]**2)
def secA(r,half): return 0.5*math.radians(2*half)*(r[1]**2-r[0]**2)
s1=km(50,50); s2=km(20,25); s3=km(63,77); s4=km(40,50); s5=km(0,100)
s7=km(30,30); s8=km(40,40)
s9=(2*25/1.4, 2*40/1.1)
A1=ringA(s1); A1s=secA(s1,22.5)
A2=ringA(s2); A2s=secA(s2,22.5)
A3=ringA(s3); A3s=secA(s3,22.5)
A4=ringA(s4); A4s=secA(s4,22.5)
A5=math.pi*s5[1]**2
A7=ringA(s7); A7s=secA(s7,22.5)
A9=ringA(s9)
# 작성 예: 가상 문장 "읍성에서 동쪽으로 열다섯 리 가면 산이 있다"
w=km(15,15); wA=ringA(w); wAs=secA(w,22.5)
w2=km(15*0.9,15*1.1); w2A=ringA(w2); w2As=secA(w2,22.5)
wide=km(10,15); wideA=ringA(wide); wideAs=secA(wide,22.5)
