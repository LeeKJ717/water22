#!/bin/bash
# z840에서 실행: bash retry-papers.sh <라벨> <원본단계라벨>  -> robots-blocked 건만 고친 판정(우리 UA로 robots.txt 직접 조회)으로 다시 수집(백그라운드)
L=${1:?라벨 필요}; P=${2:?원본단계라벨 필요}; B=/data/safe/dball2/seogyeong_db; D=$B/$L
[ -d "$D" ] || { echo "FAIL: $D 없음"; exit 1; }
curl -fsSL https://raw.githubusercontent.com/LeeKJ717/water22/seogyeong-book/seogyeong-book/tools/crawl-papers.py -o "$D/crawl-papers.py" && echo "[1] 수집기 갱신"
cd "$D" && nohup python3 -u crawl-papers.py "$D" $B/$P/db/seogyeong.sqlite --retry-blocked > crawl-retry.log 2>&1 &
sleep 10; echo "[2] 백그라운드 시작"; tail -n 5 "$D/crawl-retry.log"
