#!/bin/bash
# z840에서 실행: 평안도(권51-55) 원문 소재 조사 (읽기 전용, robots 확인 후 API만 사용)
UA="seogyeong-book-research/1.0 (contact@ssbook.kr)"
OUT=$HOME/probe-pyeongan.log; : > $OUT
say(){ echo "$@" | tee -a $OUT; }
say "== robots.txt 확인"
for H in zh.wikisource.org ko.wikisource.org commons.wikimedia.org rmda.kulib.kyoto-u.ac.jp archive.org; do
  C=$(curl -s -m 20 -A "$UA" -o /tmp/rb.txt -w '%{http_code}' https://$H/robots.txt)
  say "$H robots http=$C disallow-root=$(grep -ci '^Disallow: /$' /tmp/rb.txt)"
done
say "== zh.wikisource 하위 페이지"
curl -s -m 30 -A "$UA" 'https://zh.wikisource.org/w/api.php?action=query&list=allpages&apprefix=%E6%96%B0%E5%A2%9E%E6%9D%B1%E5%9C%8B%E8%BC%BF%E5%9C%B0%E5%8B%9D%E8%A6%BD&aplimit=200&format=json' | python3 -c 'import sys,json;d=json.load(sys.stdin);print(len(d["query"]["allpages"]));[print(p["title"]) for p in d["query"]["allpages"]]' 2>&1 | tee -a $OUT | tail -70
say "== ko.wikisource 하위 페이지"
curl -s -m 30 -A "$UA" 'https://ko.wikisource.org/w/api.php?action=query&list=allpages&apprefix=%EC%8B%A0%EC%A6%9D%EB%8F%99%EA%B5%AD%EC%97%AC%EC%A7%80%EC%8A%B9%EB%9E%8C&aplimit=200&format=json' | python3 -c 'import sys,json;d=json.load(sys.stdin);print(len(d["query"]["allpages"]));[print(p["title"]) for p in d["query"]["allpages"]]' 2>&1 | tee -a $OUT | tail -40
say "== commons 파일 검색"
curl -s -m 30 -A "$UA" 'https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=%E6%96%B0%E5%A2%9E%E6%9D%B1%E5%9C%8B%E8%BC%BF%E5%9C%B0%E5%8B%9D%E8%A6%BD&srnamespace=6&srlimit=30&format=json' | python3 -c 'import sys,json;d=json.load(sys.stdin);[print(p["title"]) for p in d["query"]["search"]]' 2>&1 | tee -a $OUT
say "== 교토대 노드"
curl -s -m 30 -A "$UA" https://rmda.kulib.kyoto-u.ac.jp/node/16220 | sed 's/<[^>]*>/ /g' | tr -s ' \n' | head -c 1200 | tee -a $OUT
echo; echo "로그: $OUT"
