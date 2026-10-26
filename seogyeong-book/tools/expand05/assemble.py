import re,sys
from render import render
orig=open('05-csp.orig.md',encoding='utf-8').read()
def R(n): 
    t=render(n).strip('\n')
    return t+"\n\n"
b=open('f20b.md',encoding='utf-8').read()
i=b.index("## 이 장의 요약")
open('f20b1.md','w',encoding='utf-8').write(b[:i]); open('f20b2.md','w',encoding='utf-8').write(b[i:])
open('calc20b1.py','w').write(open('calc20.py').read()); open('calc20b2.py','w').write("")
open('calc20a.py','w').write(open('calc20.py').read())
open('calc24.py','w').write(open('calc20.py').read())
open('calc23.py','w').write("from calc22 import *\n")
mid="".join(R(n) for n in ['03','04','05','06','07','08','08b','08c','09','10','11','11b','12','13','14','15','15b'])
tail="".join(R(n) for n in ['16','17','18','21','22','19','20a','23','20b1','24','20b2'])
def before(t,marker,ins):
    assert t.count(marker)==1,(marker,t.count(marker))
    return t.replace(marker,ins+marker)
t=orig
t=before(t,"## 직관적 소개",R('00'))
t=before(t,"## 이론 배경",R('01'))
t=before(t,"## 선행연구",R('02'))
t=before(t,"## 한계와 오차",mid)
t=before(t,"@@refs ch05@@",tail)
open(sys.argv[1],'w',encoding='utf-8').write(t)
print(len(orig),len(t),len(t)-len(orig))
