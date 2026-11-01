#!/bin/bash
# z840에서 실행: bash crawl-papers.sh <라벨> <원본단계라벨>   예) bash crawl-papers.sh paperfetch-v1 series-all-v2
# 폴더를 먼저 만들고 -> 수집기를 받아 -> 백그라운드로 돌린다(로그: <폴더>/crawl.log)
L=${1:?라벨 필요}; P=${2:?원본단계라벨 필요}; B=/data/safe/dball2/seogyeong_db; D=$B/$L
[ -f $B/$P/db/seogyeong.sqlite ] || { echo "FAIL: $B/$P/db/seogyeong.sqlite 없음"; exit 1; }
[ -e "$D" ] && { echo "FAIL: $D 이미 있음. 다른 라벨을 쓰세요"; exit 1; }
mkdir -p "$D" && echo "[1] 폴더: $D"
curl -fsSL https://raw.githubusercontent.com/LeeKJ717/water22/seogyeong-book/seogyeong-book/tools/crawl-papers.py -o "$D/crawl-papers.py" && echo "[2] 수집기 받음"
command -v pdftotext >/dev/null && echo "[3] pdftotext 있음" || echo "[3] pdftotext 없음: PDF는 저장만 되고 본문 추출은 빈칸"
cd "$D" && nohup python3 -u crawl-papers.py "$D" $B/$P/db/seogyeong.sqlite > crawl.log 2>&1 &
sleep 8; echo "[4] 백그라운드 시작"; tail -n 5 "$D/crawl.log"
