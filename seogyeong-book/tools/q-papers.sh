#!/bin/bash
# z840에서 실행: bash q-papers.sh [라벨]  -> 논문 수집 진행 상황(읽기 전용)
L=${1:-paperfetch-v1}; D=/data/safe/dball2/seogyeong_db/$L
echo "== 프로세스"; ps -eo pid,etime,cmd | grep crawl-papers | grep -v grep
echo "== 로그 끝"; tail -n 6 $D/crawl.log
python3 - <<PY
import sqlite3
d = sqlite3.connect("file:$D/db/papers.sqlite?mode=ro", uri=True)
print("== 상태별 (상태, 건수, 바이트)")
for r in d.execute("select status,count(*),sum(bytes) from fetch group by status"): print(r)
print("== 출처별 (출처, 건수)")
for r in d.execute("select source,count(*) from fetch group by source"): print(r)
print("전체 처리", d.execute("select count(*) from fetch").fetchone()[0], "/ 358")
PY
du -sh $D
