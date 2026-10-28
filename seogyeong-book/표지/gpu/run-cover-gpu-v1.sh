#!/bin/bash
# z840에서 실행: 서경 책 표지 그림 후보 생성 (프롬프트 4개 x 시드 4 = 16장, 약 10분)
set -e
P=~/bookz840/seogyeong-cover; mkdir -p $P/cand; cd $P
cp ~/mdfile/cover_kit/photo_gen_v1.py ~/mdfile/cover_kit/style_cover_v4.txt ~/mdfile/cover_kit/noboost.json . 
cp "$(dirname "$0")/prompts-seogyeong-v1.json" .
bash ~/mdfile/cover_kit/start_comfy_v1.sh
until curl -s -m 2 localhost:8188/system_stats >/dev/null && curl -s -m 2 localhost:8189/system_stats >/dev/null; do sleep 3; done
~/imggen/ComfyUI/.venv/bin/python photo_gen_v1.py prompts-seogyeong-v1.json --seeds 4 --out cand --style style_cover_v4.txt --boost noboost.json > gen.log 2>&1
tail -1 gen.log
ls cand/*/ | head -30
tar czf seogyeong-cover-cand-v1.tar.gz cand && echo "묶음: $P/seogyeong-cover-cand-v1.tar.gz"
