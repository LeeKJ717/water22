#!/bin/bash
# z840에서 실행(읽기 전용). pyeongan.sqlite에서 머리글의 고을 이름(괄호 안)을 따라 쪽 구간을 요약한다.
python3 - <<'PY'
import sqlite3, re
con=sqlite3.connect("/data/safe/dball2/seogyeong_db/pyeongan-v1/db/pyeongan.sqlite")
print("쪽 수:",con.execute("select count(*) from pages").fetchone()[0], " 상자 수:",con.execute("select count(*) from boxes").fetchone()[0])
pat=re.compile(r"卷[之宝]?([二三四五六]?十?[一二三四五六七八九]?)[（(]([^）)]{1,3})[）)]")
rows=con.execute("select file,page,header,text from pages order by file,page").fetchall()
runs=[];cur=None
for f,p,h,t in rows:
    m=pat.search(h or "") or pat.search((t or "")[:40])
    key=(m.group(1),m.group(2)) if m else None
    tag=f[-12:-7]
    if key and (cur is None or cur[0]!=key):
        cur=[key,tag,p,p,1]; runs.append(cur)
    elif cur is not None:
        cur[3]=p
        if key: cur[4]+=1
print("머리글 고을 구간 (권표기, 고을, 파일, 시작쪽~끝쪽, 머리글 인식 쪽수):")
for k,tag,a,b,c in runs: print(f"  {k[0] or '?'} {k[1]}  {tag}  p{a}~p{b}  ({c})")
print("키워드 첫 출현(본문 OCR):")
for kw in ["平壤","順安","義州","江界","慈城","昌城","寧邊","安州","定州","龍川","鐵山","宣川","郭山","嘉山","博川","熙川","碧潼","理山","朔州","楚山","渭原","雲山","孟山","成川","江東","价川","肅川","永柔","咸從","龍岡","三和","中和","祥原","江西","甑山","三登","順川","慈山","殷山","德川","寧遠","泰川","定遠"]:
    r=con.execute("select file,page from pages where text like ? order by file,page limit 1",("%"+kw+"%",)).fetchone()
    if r: print(f"  {kw}: {r[0][-12:-7]} p{r[1]}")
PY
