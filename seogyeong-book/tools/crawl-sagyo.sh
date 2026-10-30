#!/bin/bash
# z840에서 실행: bash crawl-sagyo.sh <라벨>  -> /data/safe/dball2/seogyeong_db/<라벨>/ 폴더를 먼저 만들고 크롤링 결과를 저장
L=${1:?라벨 필요}
D=/data/safe/dball2/seogyeong_db/$L
[ -e "$D" ] && { echo "이미 있음: $D"; exit 1; }
mkdir -p "$D" && echo "[1] 폴더 만듦: $D"
curl -fsSL https://raw.githubusercontent.com/LeeKJ717/water22/seogyeong-book/seogyeong-book/tools/crawl-sagyo.py -o "$D/crawl-sagyo.py" && echo "[2] 크롤러 받음"
python3 "$D/crawl-sagyo.py" "$D"
echo "[3] 끝: $(du -sh $D | cut -f1)"
