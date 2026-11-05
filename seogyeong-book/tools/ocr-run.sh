#!/bin/bash
# z840에서 실행. NTUL v.4 F03·F04(평안도 권51~55가 들어 있는 구간) 전 쪽을 OCR해 DB에 저장한다.
# DB: /data/safe/dball2/seogyeong_db/pyeongan-v1/db/pyeongan.sqlite  (폴더 먼저, DB는 그 안)
# 전부 verified=0 (원문 대조 필요). CPU만 사용(GPU는 다른 작업 중). 자가 백그라운드. 로그 ~/ocr-run.log
if [ "$1" != "--run" ]; then
  setsid nohup bash "$0" --run > /dev/null 2>&1 < /dev/null &
  echo "백그라운드 시작. 진행: tail -f ~/ocr-run.log"
  exit 0
fi
L=~/ocr-run.log
D=/data/safe/dball2/seogyeong_db/pyeongan-v1
mkdir -p $D/db
echo "[$(date '+%F %T')] 시작" > $L
OMP_NUM_THREADS=4 ~/ocrenv/bin/python - >> $L 2>&1 <<'PY'
import fitz, glob, os, re, sqlite3, time, json, hashlib
import numpy as np
from rapidocr_onnxruntime import RapidOCR
D="/data/safe/dball2/seogyeong_db/pyeongan-v1"
con=sqlite3.connect(D+"/db/pyeongan.sqlite")
con.executescript("""
CREATE TABLE IF NOT EXISTS sources(file TEXT PRIMARY KEY, sha256 TEXT, pages INT, origin TEXT, license TEXT, note TEXT);
CREATE TABLE IF NOT EXISTS pages(file TEXT, page INT, header TEXT, vol_header INT, vol_carry INT, text TEXT,
  ocr_engine TEXT, scale REAL, nlines INT, verified INT DEFAULT 0, note TEXT DEFAULT '원문 대조 필요', created TEXT,
  PRIMARY KEY(file,page));
CREATE TABLE IF NOT EXISTS boxes(file TEXT, page INT, idx INT, x0 REAL, y0 REAL, x1 REAL, y1 REAL, text TEXT, conf REAL,
  PRIMARY KEY(file,page,idx));
""")
NUM={'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9}
def cn(s):
    s=s.strip()
    if s.startswith('十'): return 10+NUM.get(s[1:2],0)
    if '十' in s:
        a,b=s.split('十'); return NUM.get(a,0)*10+NUM.get(b[:1],0)
    return None
pat=re.compile(r"卷之?([二三四五六]十[一二三四五六七八九]?)")
ocr=RapidOCR()
SC=1.5
files=[f for f in sorted(glob.glob(D+"/raw/*.pdf")) if ("F03" in f or "F04" in f)]
sums={l.split()[1]:l.split()[0] for l in open(D+"/SHA256SUMS")}
for f in files:
    b=os.path.basename(f)
    doc=fitz.open(f); n=len(doc)
    con.execute("INSERT OR REPLACE INTO sources VALUES(?,?,?,?,?,?)",(b,sums.get(b),n,
      "Wikimedia Commons File:NTUL-9910002605F0x 新增東國輿地勝覽 五十五卷 v.4.pdf (國立臺灣大學圖書館 소장본)","Public domain (Commons 표기)","스캔 PDF. OCR 텍스트는 원문 대조 필요"))
    carry=None
    for p in range(1,n+1):
        if con.execute("SELECT 1 FROM pages WHERE file=? AND page=?",(b,p)).fetchone():
            continue
        pg=doc[p-1]
        pix=pg.get_pixmap(matrix=fitz.Matrix(SC,SC))
        img=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.h,pix.w,pix.n)
        if pix.n==4: img=img[:,:,:3]
        res,_=ocr(img); res=res or []
        items=[]
        for box,txt,conf in res:
            xs=[q[0] for q in box]; ys=[q[1] for q in box]
            items.append((min(xs),min(ys),max(xs),max(ys),txt,float(conf)))
        # 세로쓰기: 오른쪽→왼쪽, 같은 열은 위→아래
        items.sort(key=lambda r:(-(r[0]+r[2])/2, r[1]))
        text="".join(i[4] for i in items)
        head="".join(i[4] for i in items if i[1]<pix.h*0.12)
        m=pat.search(head) or pat.search(text[:60])
        vh=cn(m.group(1)) if m else None
        if vh: carry=vh
        con.execute("INSERT OR REPLACE INTO pages VALUES(?,?,?,?,?,?,?,?,?,0,'원문 대조 필요',datetime('now'))",
                    (b,p,head[:60],vh,carry,text,"rapidocr-onnxruntime(ch)",SC,len(items)))
        for k,i in enumerate(items):
            con.execute("INSERT OR REPLACE INTO boxes VALUES(?,?,?,?,?,?,?,?,?)",(b,p,k,i[0]/SC,i[1]/SC,i[2]/SC,i[3]/SC,i[4],i[5]))
        if p%10==0:
            con.commit(); print(time.strftime("%F %T"),b,p,"/",n,flush=True)
    con.commit()
print("권 범위 요약(헤더 인식 기준)")
for r in con.execute("SELECT vol_header,MIN(file||' p'||page),MAX(file||' p'||page),COUNT(*) FROM pages WHERE vol_header IS NOT NULL GROUP BY vol_header ORDER BY 1"):
    print(r)
print("헤더 미인식 쪽 수:",con.execute("SELECT COUNT(*) FROM pages WHERE vol_header IS NULL").fetchone()[0])
PY
cd $D && sha256sum db/pyeongan.sqlite > db/SHA256SUMS-db && echo "DB 해시 작성" >> $L
echo "[$(date '+%F %T')] DONE" >> $L
