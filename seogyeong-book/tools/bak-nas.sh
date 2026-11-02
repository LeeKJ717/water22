#!/bin/bash
# usage: bash bak-nas.sh label1 label2 ...   (z840 -> NAS, background, log ~/bak-nas.log)
B=/data/safe/dball2/seogyeong_db
LOG=$HOME/bak-nas.log
if [ "$1" != "--run" ]; then
  setsid nohup bash "$0" --run "$@" > /dev/null 2>&1 < /dev/null &
  echo "백그라운드 시작. 진행: tail -5 $LOG"; exit 0
fi
shift
: > $LOG
for L in "$@"; do
  echo "[$(date +%T)] $L rsync 시작" >> $LOG
  mkdir -p /mnt/nas/seogyeongdb/$L
  rsync -rltH --no-g --no-p $B/$L/ /mnt/nas/seogyeongdb/$L/ >> $LOG 2>&1
  echo "[$(date +%T)] $L rsync rc=$?" >> $LOG
  ( cd /mnt/nas/seogyeongdb/$L && sha256sum -c --quiet SHA256SUMS >> $LOG 2>&1; echo "[$(date +%T)] $L NAS 검증 rc=$?" >> $LOG; du -sh . >> $LOG )
done
echo "DONE" >> $LOG
