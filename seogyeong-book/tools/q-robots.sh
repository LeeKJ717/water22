#!/bin/bash
# z840에서 실행: bash q-robots.sh [라벨]  -> robots-blocked 로 기록된 호스트별로 robots.txt 응답코드와 실제 불허 여부를 조회(읽기 전용, 본문은 내려받지 않음)
L=${1:-paperfetch-v1}; D=/data/safe/dball2/seogyeong_db/$L
python3 - <<PY
import sqlite3, urllib.request, urllib.parse, urllib.robotparser, urllib.error, collections
UA = "seogyeong-book-research/1.0 (contact@ssbook.kr)"
d = sqlite3.connect("file:$D/db/papers.sqlite?mode=ro", uri=True)
urls = [r[0] for r in d.execute("select url from fetch where status='robots-blocked'")]
by = collections.defaultdict(list)
for u in urls: by[urllib.parse.urlparse(u).netloc].append(u)
print("호스트 수", len(by), "/ 건수", len(urls))
for h, us in sorted(by.items(), key=lambda x: -len(x[1])):
    code = None; verdict = "?"
    try:
        r = urllib.request.urlopen(urllib.request.Request("https://%s/robots.txt" % h, headers={"User-Agent": UA}), timeout=20)
        code = r.status; body = r.read(500000).decode("utf-8", "replace")
        rp = urllib.robotparser.RobotFileParser(); rp.parse(body.splitlines())
        ok = sum(rp.can_fetch(UA, u) for u in us)
        verdict = "실제 불허 %d건 / 허용 %d건" % (len(us) - ok, ok)
    except urllib.error.HTTPError as e: code = e.code; verdict = "robots.txt 응답 %d (불허 판정이 아니라 접근 거부일 수 있음)" % e.code
    except Exception as e: verdict = "조회 실패 %s" % str(e)[:60]
    print(len(us), h, code, verdict)
PY
