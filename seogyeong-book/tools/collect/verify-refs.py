"""verify-refs.py - 장별 참고문헌(참고문헌/chNN.txt)을 Crossref에 조회해 실재 여부와 서지 일치도를 CSV로 낸다.
사용: python verify-refs.py ../../참고문헌 > verify-report.csv
판정: title 유사도 0.85 이상이고 연도가 같으면 OK, 아니면 CHECK(손으로 확인). 책·기술보고서는 Crossref에 없을 수 있어 NOTFOUND가 나오며 별도 확인이 필요하다."""
import sys, glob, os, re, csv, difflib
from common import *

def title_of(ref):
    m = re.search(r"\(\d{4}[a-z]?\)\.\s*(.+?)\.\s", ref)
    return m.group(1) if m else ref

root = sys.argv[1] if len(sys.argv) > 1 else "../../참고문헌"
w = csv.writer(sys.stdout); w.writerow(["file", "reference", "status", "score", "crossref_title", "crossref_year", "doi"])
for f in sorted(glob.glob(os.path.join(root, "ch*.txt"))):
    for l in open(f, encoding="utf-8"):
        l = l.strip()
        if not l or l.startswith("#"):
            continue
        y = re.search(r"\((\d{4})", l); y = y.group(1) if y else ""
        t = title_of(l)
        try:
            r = get("https://api.crossref.org/works", {"query.bibliographic": t + " " + l.split("(")[0], "rows": 3, "mailto": os.environ.get("PLACELOC_MAIL", "")})
            items = r["message"]["items"]
        except Exception as e:
            w.writerow([os.path.basename(f), l, "ERROR " + str(e)[:40], "", "", "", ""]); continue
        best = None
        for it in items:
            ct = (it.get("title") or [""])[0]
            sc = difflib.SequenceMatcher(None, t.lower(), ct.lower()).ratio()
            yr = str((it.get("issued", {}).get("date-parts") or [[""]])[0][0])
            if best is None or sc > best[0]:
                best = (sc, ct, yr, it.get("DOI", ""))
        if best and best[0] >= 0.85 and best[2] == y:
            st = "OK"
        elif best and best[0] >= 0.6:
            st = "CHECK"
        else:
            st = "NOTFOUND"
        w.writerow([os.path.basename(f), l, st, f"{best[0]:.2f}" if best else "", best[1] if best else "", best[2] if best else "", best[3] if best else ""])
        time.sleep(0.1)
