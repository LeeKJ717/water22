#!/usr/bin/env python3
"""실례-삽입안.md의 초안을 원고의 가상 문장 단락 바로 아래에 '추가만' 한다 (idempotent, 마커 기반)."""
import re,glob,sys,os
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src=open(f'{root}/원고/실례-삽입안.md',encoding='utf-8').read()
secs=re.split(r'\n(?=### 삽입 \d+\.)',src)
files={os.path.basename(p)[:2]:p for p in glob.glob(f'{root}/원고/[0-9][0-9]-*.md')}
def filekey(sec,head):
    m=re.search(r'^## (\d\d)-',sec,re.M)
    return None
cur=None;items=[]
# 파일 헤더(## NN-...) 추적
parts=re.split(r'\n(?=## |### 삽입)',src)
curfile=None
for p in parts:
    m=re.match(r'## (\d\d)-',p)
    if m: curfile=[m.group(1)]; continue
    if p.startswith('## 16~19'): curfile=['16','17','18','19']; continue
    m=re.match(r'### 삽입 (\d+)\.',p)
    if not m or not curfile: continue
    n=int(m.group(1))
    # 앵커와 블록
    toks=re.split(r'(▼ 삽입 시작[^\n]*\n|▲ 삽입 끝)',p)
    anchor=None;i=0;pre=toks[0]
    def anchors(t):
        a=re.findall(r'`([^`\n]{8,})`',t)
        return a[-1] if a else None
    a0=anchors(pre)
    j=1;lasttext=pre
    while j<len(toks)-1:
        if toks[j].startswith('▼'):
            body=toks[j+1].strip('\n'); 
            a=anchors(lasttext) or a0
            items.append((n,curfile,a,body,lasttext))
            lasttext=toks[j+2] if j+2<len(toks) else ''
            j+=3
        else: j+=1
def norm(s): return re.sub(r'[\s*`_\\]','',s)
rep=[]
for n,fl,a,body,last in items:
    if n==25 and '해로' in last: a='이동에 해로가 포함될 수 있다'
    if not a or not body.strip(): rep.append((n,'앵커/본문 없음'));continue
    key=norm(a.split('…')[0])[:24]
    for k in fl:
        path=files.get(k)
        txt=open(path,encoding='utf-8').read()
        mark=f'<!-- real-example:{n}:{k}:{hash(body)%10**6 if False else len(body)} -->'
        if f'<!-- real-example:{n}:{k}:' in txt and (n!=2 and n!=25 and n!=1 and n!=6 and n!=7 and n!=14 and n!=17 and n!=5 and n!=8 and n!=9 and n!=4):
            rep.append((n,k,'이미 삽입')); continue
        if mark in txt: rep.append((n,k,'이미 삽입')); continue
        paras=re.split(r'(\n\s*\n)',txt)
        hit=None
        for idx in range(0,len(paras),2):
            if key and key in norm(paras[idx]) and 'real-example' not in paras[idx]:
                hit=idx;break
        if hit is None: rep.append((n,k,'앵커 못 찾음: '+key));continue
        ins=f'\n\n{mark}\n{body.strip()}\n<!-- /real-example -->'
        paras[hit]=paras[hit]+ins
        open(path,'w',encoding='utf-8').write(''.join(paras))
        rep.append((n,k,'삽입'))
for r in rep: print(*r)
