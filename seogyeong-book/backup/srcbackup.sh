#!/bin/bash
# holymind에서 실행: GitHub seogyeong-book 브랜치 원본 -> z840 -> z440 -> NAS, SHA256 검증 (set -e 사용 안 함)
T=$(mktemp -d); N=srcv2; Z=z840@192.168.0.84; Y=z440@100.90.3.79
echo "[1] GitHub에서 받기"; git clone -q --depth 1 -b seogyeong-book https://github.com/LeeKJ717/water22 $T/w && echo "OK $(git -C $T/w rev-parse --short HEAD)" || { echo "FAIL clone"; exit 1; }
mkdir -p $T/p && tar czf $T/p/seogyeongsrcprepv2.tgz -C $T/w seogyeong-book && cp $T/w/seogyeong-book/인수인계/handoff-v14.md $T/p/seogyeonghandoffv1.md
(cd $T/p && sha256sum * > SHA256SUMS && cat SHA256SUMS)
echo "[2] 1차 z840"; ssh -n $Z "mkdir -p ~/seogyeongbackup/$N" && rsync -rlt $T/p/ $Z:seogyeongbackup/$N/ && ssh -n $Z "cd ~/seogyeongbackup/$N && sha256sum -c SHA256SUMS"
echo "[3] 2차 z440"; ssh -n $Z "ssh -n $Y 'mkdir -p ~/backup/seogyeong/$N' && rsync -rlt ~/seogyeongbackup/$N/ $Y:backup/seogyeong/$N/ && ssh -n $Y 'cd ~/backup/seogyeong/$N && sha256sum -c SHA256SUMS'"
echo "[4] 3차 NAS"; ssh -n $Z "mkdir -p /mnt/nas/seogyeong/$N && rsync -rlt --no-g --no-p ~/seogyeongbackup/$N/ /mnt/nas/seogyeong/$N/ ; cd /mnt/nas/seogyeong/$N && sha256sum -c SHA256SUMS"
echo "[5] 끝: FAILED 가 없으면 3곳 통과"; rm -rf $T
