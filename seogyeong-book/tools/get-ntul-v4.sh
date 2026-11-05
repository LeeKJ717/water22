#!/bin/bash
# z840에서 실행. Commons의 NTUL v.4 (F01~F04) 스캔 PDF 4개를 받고, 쪽수·OCR 도구 현황을 점검한다.
# 저장: /data/safe/dball2/seogyeong_db/pyeongan-v1/raw  (폴더 먼저, 그 안에 자료)
# 자가 백그라운드 실행. 로그 ~/get-ntul-v4.log
if [ "$1" != "--run" ]; then
  setsid nohup bash "$0" --run > /dev/null 2>&1 < /dev/null &
  echo "백그라운드 시작. 진행: tail -f ~/get-ntul-v4.log"
  exit 0
fi
L=~/get-ntul-v4.log
UA="seogyeong-book-research/1.0 (contact@ssbook.kr)"
B=/data/safe/dball2/seogyeong_db
D=$B/pyeongan-v1
mkdir -p $D/raw $D/sample
echo "[$(date '+%F %T')] 시작 $D" > $L
BASE="https://upload.wikimedia.org/wikipedia/commons"
declare -A U
U[F01]="a/a8/NTUL-9910002605F01_%E6%96%B0%E5%A2%9E%E6%9D%B1%E5%9C%8B%E8%BC%BF%E5%9C%B0%E5%8B%9D%E8%A6%BD_%E4%BA%94%E5%8D%81%E4%BA%94%E5%8D%B7_v.4.pdf"
U[F02]="c/c0/NTUL-9910002605F02_%E6%96%B0%E5%A2%9E%E6%9D%B1%E5%9C%8B%E8%BC%BF%E5%9C%B0%E5%8B%9D%E8%A6%BD_%E4%BA%94%E5%8D%81%E4%BA%94%E5%8D%B7_v.4.pdf"
U[F03]="2/29/NTUL-9910002605F03_%E6%96%B0%E5%A2%9E%E6%9D%B1%E5%9C%8B%E8%BC%BF%E5%9C%B0%E5%8B%9D%E8%A6%BD_%E4%BA%94%E5%8D%81%E4%BA%94%E5%8D%B7_v.4.pdf"
U[F04]="6/68/NTUL-9910002605F04_%E6%96%B0%E5%A2%9E%E6%9D%B1%E5%9C%8B%E8%BC%BF%E5%9C%B0%E5%8B%9D%E8%A6%BD_%E4%BA%94%E5%8D%81%E4%BA%94%E5%8D%B7_v.4.pdf"
for K in F01 F02 F03 F04; do
  O=$D/raw/NTUL-9910002605${K}-v4.pdf
  curl -fsSL -C - -A "$UA" --retry 3 --retry-delay 10 -o "$O" "$BASE/${U[$K]}"
  R=$?
  echo "[$(date '+%F %T')] $K 다운로드 rc=$R $(du -m "$O" 2>/dev/null | cut -f1)MB" >> $L
  sleep 8
done
cd $D/raw && sha256sum *.pdf > ../SHA256SUMS && echo "SHA256SUMS 작성" >> $L
cat > $D/SOURCE.txt <<EOF
출처: Wikimedia Commons, File:NTUL-9910002605F01~F04 新增東國輿地勝覽 五十五卷 v.4.pdf
소장: 國立臺灣大學圖書館(NTUL). Commons 표기 라이선스: Public domain (파일별 extmetadata 확인값)
받은 날: $(date +%F). 상태: 스캔 PDF 원본. 텍스트는 OCR 예정이며 전부 "원문 대조 필요".
EOF
for f in $D/raw/*.pdf; do
  echo "--- $(basename $f)" >> $L
  pdfinfo "$f" 2>&1 | grep -E "Pages|Page size|Producer" >> $L
done
# 표본 쪽 렌더(저해상도): 각 파일의 1,2,3쪽
for f in $D/raw/*.pdf; do
  b=$(basename $f .pdf)
  pdftoppm -r 60 -f 1 -l 3 -png "$f" $D/sample/$b 2>> $L
done
echo "--- OCR 도구 점검" >> $L
{ which tesseract && tesseract --list-langs 2>&1 | grep -iE "chi_tra|chi_sim|jpn|osd"; } >> $L 2>&1
python3 - >> $L 2>&1 <<'PY'
for m in ("paddleocr","paddle","easyocr","torch","cv2","fitz"):
    try:
        mod=__import__(m); print(m,"OK",getattr(mod,"__version__",""))
    except Exception as e:
        print(m,"없음",type(e).__name__)
PY
nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader >> $L 2>&1
echo "[$(date '+%F %T')] DONE" >> $L
