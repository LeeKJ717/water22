#!/bin/bash
# z840에서 실행. (1) 권·고을 색인표 vol_index를 DB에 추가 (2) 평양부(권51) 텍스트를 쪽 표시 붙여 txt로 내보냄
# (3) 西京 출현 구절과 평양부 建置沿革·四至 구절을 화면에 출력. 모든 텍스트는 OCR 원자료 = 원문 대조 필요.
python3 - <<'PY'
import sqlite3, re, os
D="/data/safe/dball2/seogyeong_db/pyeongan-v1"
con=sqlite3.connect(D+"/db/pyeongan.sqlite")
con.executescript("""
DROP TABLE IF EXISTS vol_index;
CREATE TABLE vol_index(vol INT, section TEXT, file TEXT, p_start INT, p_end INT, method TEXT, verified INT DEFAULT 0);
""")
# 2026-11-05 q-pyeongan 출력 기준(머리글 인식 + 이어받기). 경계 쪽은 원문 대조 필요.
F3="NTUL-9910002605F03-v4.pdf"; F4="NTUL-9910002605F04-v4.pdf"
rows=[(51,"平壤府",F3,43,83),(52,"中和~永柔",F3,84,126),(53,"義州~郭山",F3,127,128),(53,"義州~郭山",F4,1,48),
      (54,"雲山~慈山",F4,49,75),(55,"祥原~(말미)",F4,76,124)]
con.executemany("INSERT INTO vol_index VALUES(?,?,?,?,?,'머리글 고을 구간(OCR)',0)",rows)
con.commit()
# 평양부 내보내기
out=D+"/db/pyeongyang-F03-p43-83.txt"
with open(out,"w",encoding="utf-8") as fo:
    fo.write("# 新增東國輿地勝覽 권51 平壤府 (NTUL v.4 F03 p43~83) OCR 원자료 — 원문 대조 필요\n")
    for p,t in con.execute("select page,text from pages where file=? and page between 43 and 83 order by page",(F3,)):
        fo.write(f"\n=== F03 p{p} ===\n{t}\n")
print("내보냄:",out,os.path.getsize(out),"bytes")
print("\n[西京 출현 구절 — 전 쪽]")
for f,p,t in con.execute("select file,page,text from pages order by file,page"):
    for m in re.finditer("西京",t):
        s=max(0,m.start()-40); print(f"  {f[-12:-7]} p{p}: …{t[s:m.end()+60]}…")
print("\n[平壤府 建置沿革·四至]")
for f,p,t in con.execute("select file,page,text from pages where file=? and page between 43 and 50 order by page",(F3,)):
    for kw in ("建置沿革","距京都","四至","東，至","東至"):
        i=t.find(kw)
        if i>=0: print(f"  p{p} [{kw}]: {t[max(0,i-20):i+260]}"); break
PY
cd /data/safe/dball2/seogyeong_db/pyeongan-v1/db && sha256sum pyeongan.sqlite pyeongyang-F03-p43-83.txt > SHA256SUMS-db && echo "해시 갱신 완료"
