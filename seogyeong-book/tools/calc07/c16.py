from lib07 import *
import c15
put("X2.ann30",math.pi*(14.4**2-10.8**2)); put("X2.r_lo",30*0.36); put("X2.r_hi",30*0.48)
put("X12b.shrink",1/math.sqrt(2)); put("X12b.narrow",(1-1/math.sqrt(2))*100)
a=[0.2,0.6,0.2]; b=[0.5,0.3,0.2]
put("X13.right",np.mean([x*y for x,y in zip(a,b)])); put("X13.wrong",np.mean(a)*np.mean(b)); put("X13.ratio",R["X13.right"]/R["X13.wrong"])
put("X4b.p",(1+1)/(2+2))
put("X9.pw",0.1*WIDE/(0.9*0.5+0.1*WIDE))
# beta for 5 of 5
put("X4c.p",(1+5)/(2+5))
# lognormal mean shift: ln(480/12)...
put("X14.bf",R["J4.bf12"])
# expected radius ring for 50 li
put("X15.hand_z",math.log(40)-math.log(60/0.40))
put("X15.f",float(zpdf(math.log(40)-math.log(60/0.40),0.25)))
put("X16.s",float(math.sqrt(0.0825**2+0.10**2)))
# prior sd of u (uniform .36-.48)
put("X17.sd",0.12/math.sqrt(12))
