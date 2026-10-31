#!/bin/bash
# z840에서 실행: bash crawl-yeoji2.sh <라벨>  -> /data/safe/dball2/seogyeong_db/<라벨>/ 폴더를 먼저 만들고 여지승람 평안도 후보(ko·zh 위키문헌, 공용 스캔)를 DB로 저장
L=${1:?라벨 필요}
D=/data/safe/dball2/seogyeong_db/$L
[ -e "$D" ] && { echo "FAIL: $D 이미 있음. 다른 라벨을 쓰세요"; exit 1; }
mkdir -p "$D" && echo "[1] 폴더: $D"
curl -fsSL https://raw.githubusercontent.com/LeeKJ717/water22/seogyeong-book/seogyeong-book/tools/crawl-yeoji2.py -o "$D/crawl-yeoji2.py" && echo "[2] 크롤러 받음"
nohup python3 -u "$D/crawl-yeoji2.py" "$D" > "$D/crawl.log" 2>&1 &
echo "[3] 백그라운드 실행 시작. 진행: tail -n 8 $D/crawl.log"
