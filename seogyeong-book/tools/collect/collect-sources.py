"""collect-sources.py - 위키문헌(ko/zh)에서 지정한 문서를 가져와 source_text에 verified=0으로 넣는다.
사용: python collect-sources.py titles.txt --lang zh      (titles.txt: 한 줄에 문서 제목 하나, 예: 高麗史/卷五十八)
      python collect-sources.py --search "西京 平壤" --lang zh --limit 20   (제목 후보 검색만 출력)
저본은 위키문헌 문서의 판본 정보를 edition에 적는다. 인용은 인쇄본·공인 전자 원문과 대조해 verified=1로 바꾼 뒤에만 한다."""
import argparse, re
from common import *
ap = argparse.ArgumentParser()
ap.add_argument("titles", nargs="?"); ap.add_argument("--lang", default="zh"); ap.add_argument("--search"); ap.add_argument("--limit", type=int, default=20)
a = ap.parse_args()
api = f"https://{a.lang}.wikisource.org/w/api.php"
if a.search:
    r = get(api, {"action": "query", "list": "search", "srsearch": a.search, "srlimit": a.limit, "format": "json"})
    for x in r["query"]["search"]:
        print(x["title"])
    raise SystemExit
con = db()
for t in [l.strip() for l in open(a.titles, encoding="utf-8") if l.strip()]:
    r = get(api, {"action": "query", "prop": "revisions", "rvprop": "content|ids", "rvslots": "main", "titles": t, "format": "json", "formatversion": 2})
    pg = r["query"]["pages"][0]
    if "revisions" not in pg:
        print("없음:", t); continue
    rev = pg["revisions"][0]; txt = rev["slots"]["main"]["content"]
    work = t.split("/")[0]
    con.execute("insert into source_text(work,juan,passage,original,edition,verified,verified_note) values(?,?,?,?,?,0,?)",
                (work, t, t, txt, f"{a.lang}.wikisource rev {rev['revid']} ({now()})", "자동 수집, 원문 대조 전"))
    print("적재:", t, len(txt), "자"); time.sleep(0.5)
con.commit()
