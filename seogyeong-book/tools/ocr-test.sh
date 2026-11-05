#!/bin/bash
# z840에서 실행. OCR 환경(venv, pip만 사용)을 만들고 NTUL v.4 표본 쪽을 OCR해 품질·권 위치를 가늠한다.
# 읽기 전용 점검 + ~/ocrenv 설치. 로그 ~/ocr-test.log. 자가 백그라운드.
if [ "$1" != "--run" ]; then
  setsid nohup bash "$0" --run > /dev/null 2>&1 < /dev/null &
  echo "백그라운드 시작. 진행: tail -f ~/ocr-test.log"
  exit 0
fi
L=~/ocr-test.log
D=/data/safe/dball2/seogyeong_db/pyeongan-v1
mkdir -p $D/ocrtest
echo "[$(date '+%F %T')] 시작" > $L
if [ ! -x ~/ocrenv/bin/python ]; then
  python3 -m venv ~/ocrenv >> $L 2>&1; echo "venv rc=$?" >> $L
fi
~/ocrenv/bin/pip install -q --upgrade pip >> $L 2>&1
~/ocrenv/bin/pip install -q rapidocr-onnxruntime pymupdf pillow numpy >> $L 2>&1
echo "[$(date '+%F %T')] pip rc=$?" >> $L
~/ocrenv/bin/python - >> $L 2>&1 <<'PY'
import fitz, glob, os, time
import numpy as np
from rapidocr_onnxruntime import RapidOCR
ocr = RapidOCR()
D="/data/safe/dball2/seogyeong_db/pyeongan-v1"
for f in sorted(glob.glob(D+"/raw/*.pdf")):
    doc = fitz.open(f)
    n = len(doc)
    for p in [1,2,3,n//4,n//2,3*n//4,n]:
        pg = doc[p-1]
        pix = pg.get_pixmap(matrix=fitz.Matrix(1.5,1.5))
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        if pix.n==4: img = img[:,:,:3]
        t=time.time()
        res,_ = ocr(img)
        res = res or []
        # 세로쓰기: 오른쪽→왼쪽 열 순서로 정렬(박스 중심 x 내림차순, 같은 열은 y 오름차순)
        items=[]
        for box,txt,conf in res:
            cx=sum(b[0] for b in box)/4; cy=sum(b[1] for b in box)/4
            items.append((cx,cy,txt,float(conf)))
        items.sort(key=lambda r:(-round(r[0]/60), r[1]))
        s="".join(i[2] for i in items)
        print(f"== {os.path.basename(f)} p{p}/{n} 줄{len(items)} {time.time()-t:.1f}s")
        print(s[:260])
PY
echo "[$(date '+%F %T')] DONE" >> $L
