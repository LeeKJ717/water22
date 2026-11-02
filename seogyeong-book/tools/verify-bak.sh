#!/bin/bash
# usage: bash verify-bak.sh label   (background; log ~/verify-LABEL.log)
L=$1; LOG=$HOME/verify-$L.log
if [ "$2" != "--run" ]; then
  setsid nohup bash "$0" "$L" --run > /dev/null 2>&1 < /dev/null &
  echo "백그라운드 시작. 결과: cat $LOG"; exit 0
fi
: > $LOG
for D in /mnt/nas/seogyeongdb/$L /data/safe/dball2/seogyeong_db/$L; do
  echo "== $D 시작" >> $LOG
  ( cd $D && sha256sum -c --quiet SHA256SUMS 2>&1 | head -20 >> $LOG )
  echo "== $D 끝" >> $LOG
done
echo DONE >> $LOG
