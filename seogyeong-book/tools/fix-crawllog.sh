#!/bin/bash
# usage: bash fix-crawllog.sh label ...  : refresh stale ./crawl.log hash line in source and NAS SHA256SUMS
for L in "$@"; do
  S=/data/safe/dball2/seogyeong_db/$L; N=/mnt/nas/seogyeongdb/$L
  echo "== $L"
  if pgrep -f "crawl-" >/dev/null; then echo "경고: crawl 프로세스 실행 중 (로그가 더 바뀔 수 있음)"; fi
  cmp -s $S/crawl.log $N/crawl.log || { echo "crawl.log 다름 -> NAS로 재복사"; cp -f $S/crawl.log $N/crawl.log; }
  H=$(sha256sum $S/crawl.log | cut -d' ' -f1)
  for D in $S $N; do
    cp -f $D/SHA256SUMS $D/SHA256SUMS.old
    sed -i "s|^[0-9a-f]\{64\}  \./crawl\.log\$|$H  ./crawl.log|" $D/SHA256SUMS
    ( cd $D; grep '  \./crawl\.log$' SHA256SUMS | sha256sum -c - ; wc -l < SHA256SUMS )
  done
done
