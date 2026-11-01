#!/bin/bash
# z840에서 실행: bash crawl-archive.sh <라벨>  -> /data/safe/dball2/seogyeong_db/<라벨>/ 폴더를 먼저 만들고 archive.org 여지승람 항목의 메타데이터·OCR을 DB로 저장
L=${1:?라벨 필요}
D=/data/safe/dball2/seogyeong_db/$L
[ -e "$D" ] && { echo "FAIL: $D 이미 있음. 다른 라벨을 쓰세요"; exit 1; }
mkdir -p "$D" && echo "[1] 폴더: $D"
curl -fsSL https://raw.githubusercontent.com/LeeKJ717/water22/seogyeong-book/seogyeong-book/tools/crawl-archive.py -o "$D/crawl-archive.py" && echo "[2] 크롤러 받음"
python3 -u "$D/crawl-archive.py" "$D" 2>&1 | tee "$D/crawl.log" | tail -n 45
