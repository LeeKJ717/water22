#!/bin/bash
# z840에서 실행: bash fin-db2.sh <라벨>  -> README, SHA256SUMS 생성 후 NAS로 복사·검증 (z440·노트북 백업은 별도)
S=${1:?라벨 필요}; D=/data/safe/dball2/seogyeong_db/$S; N=/mnt/nas/seogyeongdb/$S
[ -d $D ] || { echo "FAIL: $D 없음"; exit 1; }
cat > $D/README.md <<EOF2
# seogyeong_db / $S  (2판·수정 작업용 통합 DB)
- db/seogyeong.sqlite : 원고(절·블록)·표·그림·참고문헌·논문·수치·조판 파일 BLOB + 확장표(book_volume, book_cite, book_flag, book_pdf, source_text, paper_fetch, crawl_*)
- src/ : 조판 소스 전체. pdf/ : 완성 PDF. crawl/ : 크롤 폴더(원본 raw 포함)
## 자주 쓰는 조회
sqlite3 db/seogyeong.sqlite 'select * from v_volume_toc;'
sqlite3 db/seogyeong.sqlite 'select * from v_flag_open limit 20;'
sqlite3 db/seogyeong.sqlite 'select * from v_cite_unmatched;'
sqlite3 db/seogyeong.sqlite 'select kind,count(*) from paper_fetch group by kind;'
EOF2
python3 - <<PY
import sqlite3
d=sqlite3.connect("$D/db/seogyeong.sqlite"); print("integrity:", d.execute("pragma integrity_check").fetchone()[0])
for t in ("book_volume","book_cite","book_flag","book_pdf","source_text","paper_fetch","paper","book_block","book_typeset_file"): print(t, d.execute("select count(*) from "+t).fetchone()[0])
print([r[0] for r in d.execute("select name from sqlite_master where name like 'crawl_%'")])
PY
(cd $D && find db src pdf crawl -type f -print0 | xargs -0 sha256sum > SHA256SUMS; wc -l SHA256SUMS; du -sh $D)
mkdir -p $N && rsync -rlt --no-g --no-p $D/ $N/; cd $N && sha256sum -c --quiet SHA256SUMS; echo NAS rc=$?
