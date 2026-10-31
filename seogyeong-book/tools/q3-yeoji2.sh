#!/bin/bash
# z840에서 실행: bash q3-yeoji2.sh  -> (A) 중복 제거 후 파일 규모 (B) 큰 파일 제목 (C) 평안도 관련 제목 (D) 다른 출처의 robots.txt (E) archive.org 검색
D=/data/safe/dball2/seogyeong_db/yeojiseungram-v2; DB=$D/db/yeoji2.sqlite
UA="seogyeong-book-research/1.0 (contact@ssbook.kr)"
echo "== A 중복 제거 후 (해시 기준) 파일 수|바이트"
sqlite3 $DB "select count(*), sum(size) from (select sha1,size from file group by sha1);"
echo "== B 고유 파일 중 큰 것 상위 30 (제목|바이트)"
sqlite3 $DB "select min(title), size from file group by sha1 order by size desc limit 30;"
echo "== C 평안도/권51~55 관련 파일 제목"
sqlite3 $DB "select min(title), size from file where title like '%平安%' or title like '%평안%' or title like '%平壤%' or title like '%평양%' or title like '%권51%' or title like '%권52%' or title like '%권53%' or title like '%권54%' or title like '%권55%' or title like '%卷五十%' group by sha1 limit 30;"
echo "== D 다른 출처 robots.txt (앞 8줄)"
for s in ctext.org db.history.go.kr kostma.aks.ac.kr; do echo "-- $s"; curl -s -m 20 -A "$UA" -w "\nHTTP %{http_code}\n" https://$s/robots.txt | head -n 9; done
echo "== E archive.org 검색 (식별자|제목)"
python3 - <<'PY'
import urllib.request, urllib.parse, json
UA = "seogyeong-book-research/1.0 (contact@ssbook.kr)"
for q in ("title:(新增東國輿地勝覽) OR title:(東國輿地勝覽) OR title:(신증동국여지승람) OR title:(Sinjung Tongguk yoji sungnam)",):
    url = "https://archive.org/advancedsearch.php?" + urllib.parse.urlencode({"q": q, "fl[]": ["identifier", "title"], "rows": 30, "output": "json"}, doseq=True)
    try:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60).read().decode())
        for x in d["response"]["docs"]: print(x.get("identifier"), "|", x.get("title"))
        print("건수", d["response"]["numFound"])
    except Exception as e:
        print("ERR", e)
PY
