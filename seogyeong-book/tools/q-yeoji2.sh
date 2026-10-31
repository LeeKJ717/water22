#!/bin/bash
# z840에서 실행: bash q-yeoji2.sh  -> yeojiseungram-v2 DB 요약(읽기 전용)
D=/data/safe/dball2/seogyeong_db/yeojiseungram-v2; DB=$D/db/yeoji2.sqlite
echo "== 1 페이지 분포 (사이트|네임스페이스|건수|바이트)"
sqlite3 $DB "select site,ns,count(*),sum(bytes) from page group by site,ns;"
echo "== 2 평안도/평양 관련 제목 후보"
sqlite3 $DB "select site,ns,title,bytes from page where title like '%卷五十%' or title like '%권51%' or title like '%권52%' or title like '%권53%' or title like '%권54%' or title like '%권55%' or title like '%平安%' or title like '%평안%' or title like '%平壤%' or title like '%평양%' order by site,title limit 40;"
echo "== 3 본문에 平壤府가 많이 나오는 문서 상위"
sqlite3 $DB "select site,ns,title,bytes,(length(text)-length(replace(text,'平壤府','')))/3 as n from page where text like '%平壤府%' order by n desc limit 15;"
echo "== 4 한국어 위키문헌 본문(ns0) 제목"
sqlite3 $DB "select title,bytes from page where site='ko' and ns=0 order by title limit 70;"
echo "== 5 파일 분포 (사이트|상태|건수|바이트)"
sqlite3 $DB "select site,status,count(*),sum(size) from file group by site,status;"
echo "== 6 파일명에 K2-4182 가 든 것 (번호순)"
sqlite3 $DB "select title,size from file where title like '%K2-4182%' order by title;"
echo "== 7 디스크 실제 크기와 DB 크기 대조"
python3 - <<'PY'
import sqlite3, os
D = "/data/safe/dball2/seogyeong_db/yeojiseungram-v2"
db = sqlite3.connect(D + "/db/yeoji2.sqlite")
tot_db = tot_disk = bad = miss = 0
for t, size, path in db.execute("select title,size,path from file where status='OK'"):
    p = os.path.join(D, path or "")
    if not path or not os.path.exists(p): miss += 1; continue
    s = os.path.getsize(p); tot_db += size; tot_disk += s
    if s != size: bad += 1
print("DB 합계", tot_db, "디스크 합계", tot_disk, "크기 불일치", bad, "파일 없음", miss)
PY
