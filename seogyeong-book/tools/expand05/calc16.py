from lib import *
h=0.1; X,Y=grid(-30,30,-30,30,h)
win=40*40
def ua(box):
    m=np.zeros_like(X,dtype=bool)
    pts=[(0,0)] if box==0 else [(sx,sy) for sx in np.linspace(-box,box,9) for sy in np.linspace(-box,box,9)]
    for c in pts: m|=ring(X,Y,c,3.6,7.2)&sector(X,Y,c,67.5,112.5)
    return area(m,h)
res=[(b,ua(b)) for b in (0,2,5,10)]
frac=[(b,a,a/win*100) for b,a in res]
if __name__=="__main__":
    print(frac)
