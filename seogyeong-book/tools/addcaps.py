#!/usr/bin/env python3
"""캡션 없는 마크다운 표 앞에 'Table: 캡션'을 추가한다(idempotent). 캡션은 바로 위 단락의 첫 문장(굵은 머리말 우선)."""
import re,glob,sys
for f in sorted(glob.glob('원고/*.md')):
    L=open(f,encoding='utf-8').read().split('\n'); out=[]; n=0; i=0
    while i<len(L):
        l=L[i]
        if l.startswith('|') and (i==0 or not L[i-1].startswith('|')) and i+1<len(L) and re.match(r'^\|[-: |]+\|$',L[i+1]):
            has = i>=2 and L[i-1].strip()=='' and L[i-2].startswith('Table:')
            if not has:
                j=i-1
                while j>=0 and L[j].strip()=='': j-=1
                p=L[j] if j>=0 else ''
                p=re.sub(r'<!--.*?-->','',p)
                m=re.match(r'\*\*(.+?)\*\*',p)
                cap=m.group(1) if m else re.split(r'(?<=[.다요])\s',p.strip())[0]
                cap=re.sub(r'[*`]','',cap).strip().rstrip('.:')
                if len(cap)>60: cap=cap[:58]+'…'
                if not cap or cap.startswith('|') : cap='계산표'
                out+=[f'Table: {cap}','']; n+=1
        out.append(l); i+=1
    if n: open(f,'w',encoding='utf-8').write('\n'.join(out)); print(f,n)
