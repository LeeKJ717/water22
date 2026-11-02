#!/bin/bash
# z840에서 실행: bash merge-papers.sh <새라벨> <이전단계라벨> <논문수집폴더라벨>   예) bash merge-papers.sh series-all-v3 series-all-v2 paperfetch-v1
# 새 폴더를 먼저 만들고 -> 이전 단계를 복사(db·src는 실복사, pdf·crawl은 하드링크) -> 논문 수집 폴더를 crawl 에 넣고 -> 확장표 갱신 -> 논문 전문 병합 -> README·해시·NAS
S=${1:?새라벨}; P=${2:?이전단계라벨}; Q=${3:?논문수집폴더라벨}; B=/data/safe/dball2/seogyeong_db; D=$B/$S; O=$B/$P
[ -d $O ] && [ -d $B/$Q/db ] || { echo "FAIL: $O 또는 $B/$Q 없음"; exit 1; }
[ -e $D ] && { echo "FAIL: $D 이미 있음. 다른 라벨을 쓰세요"; exit 1; }
mkdir -p $D/db $D || exit 1; echo "[1] 폴더: $D"
cp -a $O/db/seogyeong.sqlite $D/db/ && cp -a $O/src $D/src && cp -al $O/pdf $D/pdf && cp -al $O/crawl $D/crawl && echo "[2] 이전 단계 복사"
mkdir -p $D/crawl/$Q && cp -al $B/$Q/db $B/$Q/raw $D/crawl/$Q/ && cp -a $B/$Q/crawl-papers.py $D/crawl/$Q/ && echo "[3] 논문 수집 폴더 포함 $(ls $D/crawl/$Q/raw | wc -l)개 원본"
for F in mk-db-ext.py crawl-papers.py; do curl -fsSL https://raw.githubusercontent.com/LeeKJ717/water22/seogyeong-book/seogyeong-book/tools/$F -o $D/src/tools/$F; done; echo "[4] 최신 도구"
echo "[5] 확장표 갱신"; (cd $D/src && python3 tools/mk-db-ext.py $D/db/seogyeong.sqlite --root . --pdf-dir $D/pdf --crawl-dir $D/crawl 2>&1 | tail -16)
echo "[6] 논문 전문 병합"; (cd $D/src && python3 tools/crawl-papers.py --merge $D/crawl/$Q $D/db/seogyeong.sqlite)
python3 - <<PY
import sqlite3
d = sqlite3.connect("$D/db/seogyeong.sqlite")
print("paper_fetch 상태:", d.execute("select status,count(*) from paper_fetch group by status").fetchall())
print("전문 있음", d.execute("select count(*) from paper where fulltext is not null and fulltext!=''").fetchone()[0], "/ PDF BLOB", d.execute("select count(*) from paper where pdf_blob is not null").fetchone()[0])
PY
curl -fsSL https://raw.githubusercontent.com/LeeKJ717/water22/seogyeong-book/seogyeong-book/tools/fin-db2.sh -o ~/fin-db2.sh; bash ~/fin-db2.sh $S
