#!/bin/bash
# z840에서 실행. 매 단계마다: HDD에 단계 폴더를 만들고 -> 그 안에 DB를 만들고 -> 조판 자료 전체를 DB와 파일 트리로 보관한다.
# 사용: bash stage-db.sh <단계라벨>   예) bash stage-db.sh vol3-exec-v1
# 결과: /data/safe/dball2/seogyeong_db/<단계라벨>/{db,src,pdf,README.md,SHA256SUMS}
S=${1:?단계라벨 필요}; BASE=/data/safe/dball2/seogyeong_db; D=$BASE/$S
[ -d /data/safe/dball2 ] || { echo "FAIL: /data/safe/dball2 없음 (df -h 로 HDD 경로 확인)"; exit 1; }
[ -e $D ] && { echo "FAIL: $D 이미 있음. 다른 라벨을 쓰세요"; exit 1; }
mkdir -p $D/db $D/src $D/pdf || exit 1
echo "[1] 폴더 만듦: $D"
git clone -q --depth 1 -b seogyeong-book https://github.com/LeeKJ717/water22 $D/_w && echo "[2] GitHub 받기 OK $(git -C $D/_w rev-parse --short HEAD)" || { echo "FAIL clone"; exit 1; }
cp -a $D/_w/seogyeong-book/. $D/src/ && rm -rf $D/_w
echo "[3] DB 만들기 (폴더 안: $D/db)"
(cd $D/src && BOOK_VERSION=$S python3 tools/mk-db.py $D/db/seogyeong.sqlite 2>&1 | tail -20)
echo "[4] PDF는 $D/pdf 에 노트북에서 따로 넣는다(저장소가 공개라 PDF는 올리지 않음)"
cat > $D/README.md <<EOT
# seogyeong_db / $S
- db/seogyeong.sqlite : 원고·절·블록·표·그림·참고문헌·숫자·조판 파일 BLOB(book_typeset_file)·빌드 기록(book_build)
- src/ : 조판 전체 소스 트리(원고, tools, 그림, 표지, 참고문헌, buildlog). 복원 후 그대로 빌드 가능
- pdf/ : 완성 PDF (본문·표지 합본)
## 빌드 방법 (src/ 에서)
export LANG=C.UTF-8 LC_ALL=C.UTF-8; BOOK_VERSION=라벨 VOLUME=1|2|3|4 python3 tools/build.py color|bw
환경: src/buildlog/buildenv.txt (TeX Live 2023, pandoc 3.1.3, Python 3.13, Noto CJK 글꼴)
## DB에서 파일 복원
python3 -c "import sqlite3;d=sqlite3.connect('db/seogyeong.sqlite');[print(r) for r in d.execute('select path,bytes from book_typeset_file limit 5')]"
EOT
(cd $D && find db src -type f -print0 | xargs -0 sha256sum > SHA256SUMS; wc -l SHA256SUMS; du -sh $D)
echo "[5] 끝. 이어서 3중 백업: $D 를 z440, NAS로 복사"
