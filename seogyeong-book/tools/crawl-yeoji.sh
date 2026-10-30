#!/bin/bash
# z840에서 실행: bash crawl-yeoji.sh <라벨>  -> /data/safe/dball2/seogyeong_db/<라벨>/ 폴더를 먼저 만들고 여지승람 전권을 DB로 저장(중단 후 재실행하면 이어받음)
L=${1:?라벨 필요}
D=/data/safe/dball2/seogyeong_db/$L
mkdir -p "$D" && echo "[1] 폴더: $D"
curl -fsSL https://raw.githubusercontent.com/LeeKJ717/water22/seogyeong-book/seogyeong-book/tools/crawl-yeoji.py -o "$D/crawl-yeoji.py" && echo "[2] 크롤러 받음"
nohup python3 "$D/crawl-yeoji.py" "$D" > "$D/crawl.log" 2>&1 &
echo "[3] 백그라운드 실행 시작. 진행: tail -n 5 $D/crawl.log"
