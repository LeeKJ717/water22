#!/bin/bash
# z840에서 실행: bash stage-db2.sh <새라벨> <이전단계라벨>   예) bash stage-db2.sh series-all-v2 series-all-v1
# 새 폴더를 먼저 만들고 -> 최신 GitHub 소스로 DB 생성(mk-db.py) -> 확장(mk-db-ext.py: 권·인용·표시문장·PDF·크롤·사료·논문수집목록) -> 이전 단계의 pdf/crawl 을 하드링크로 가져온다.
S=${1:?새라벨 필요}; P=${2:?이전단계라벨 필요}; BASE=/data/safe/dball2/seogyeong_db; D=$BASE/$S; O=$BASE/$P
[ -d $O ] || { echo "FAIL: $O 없음"; exit 1; }
[ -e $D ] && { echo "FAIL: $D 이미 있음. 다른 라벨을 쓰세요"; exit 1; }
mkdir -p $D/db $D/src $D/pdf $D/crawl || exit 1; echo "[1] 폴더: $D"
git clone -q --depth 1 -b seogyeong-book https://github.com/LeeKJ717/water22 $D/_w && echo "[2] GitHub $(git -C $D/_w rev-parse --short HEAD)" || { echo "FAIL clone"; exit 1; }
cp -a $D/_w/seogyeong-book/. $D/src/ && rm -rf $D/_w
[ -d $O/pdf ] && cp -al $O/pdf/. $D/pdf/ && echo "[3] pdf $(ls $D/pdf | wc -l)개 (하드링크)"
[ -d $O/crawl ] && cp -al $O/crawl/. $D/crawl/ && echo "[4] crawl 폴더 $(ls $D/crawl | wc -l)개 (하드링크)"
for X in yeojiseungram-v1 yeojiseungram-v2 yeojiarchive-v1 sagyocrawl-v1 sagyocrawl-v2; do [ -d $D/crawl/$X ] || { [ -d $BASE/$X/db ] && mkdir -p $D/crawl/$X/db && cp -al $BASE/$X/db/. $D/crawl/$X/db/ ; }; done
echo "[5] DB 만들기"
(cd $D/src && BOOK_VERSION=$S python3 tools/mk-db.py $D/db/seogyeong.sqlite 2>&1 | tail -5)
python3 -c "import pypdf" 2>/dev/null || pip install -q --user pypdf 2>&1 | tail -1
echo "[6] 확장"
(cd $D/src && python3 tools/mk-db-ext.py $D/db/seogyeong.sqlite --root . --pdf-dir $D/pdf --crawl-dir $D/crawl 2>&1 | tail -30)
cat > $D/README.md <<EOF2
# seogyeong_db / $S  (2판·수정 작업용 통합 DB)
- db/seogyeong.sqlite : 원고(절·블록)·표·그림·참고문헌·논문·수치·조판 파일 BLOB + 확장표(book_volume, book_cite, book_flag, book_pdf, source_text, paper_fetch, crawl_*)
- src/ : 조판 소스 전체. pdf/ : 완성 PDF. crawl/ : 크롤 폴더(원본 raw 포함)
## 자주 쓰는 조회
sqlite3 db/seogyeong.sqlite 'select * from v_volume_toc;'      권별 목차
sqlite3 db/seogyeong.sqlite 'select * from v_flag_open limit 20;'  2판에서 처리할 표시 문장
sqlite3 db/seogyeong.sqlite 'select * from v_cite_unmatched;'   참고문헌에 연결 안 된 인용
sqlite3 db/seogyeong.sqlite 'select kind,count(*) from paper_fetch group by kind;'  논문 전문 수집 대기
EOF2
(cd $D && find db src pdf crawl -type f -print0 | xargs -0 sha256sum > SHA256SUMS; wc -l SHA256SUMS; du -sh $D)
echo "[7] 끝. 이어서 3중 백업"
