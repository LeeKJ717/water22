#!/bin/bash
# usage (on z440): bash bak-z440.sh label ...   NAS -> /data/backup/seogyeongdb, background, log ~/bak-z440.log
LOG=$HOME/bak-z440.log
if [ "$1" != "--run" ]; then
  setsid nohup bash "$0" --run "$@" > /dev/null 2>&1 < /dev/null &
  echo "백그라운드 시작. 진행: tail -5 $LOG"; exit 0
fi
shift
: > $LOG
for L in "$@"; do
  S=/mnt/nas/seogyeongdb/$L; D=/data/backup/seogyeongdb/$L
  mkdir -p $D
  echo "[$(date +%T)] $L rsync 시작" >> $LOG
  rsync -rltH $S/ $D/ >> $LOG 2>&1; R=$?
  echo "[$(date +%T)] $L rsync rc=$R" >> $LOG
  ( cd $D; sha256sum -c --quiet SHA256SUMS >> $LOG 2>&1; V=$?; echo "[$(date +%T)] $L 검증 rc=$V (0이면 전체 일치)" >> $LOG; du -sh . >> $LOG )
done
echo DONE >> $LOG
