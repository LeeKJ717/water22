"""collect-papers.py - OpenAlex에서 선행 논문을 모아 paper 표에 넣는다(메타데이터, 초록, 공개 PDF가 있으면 PDF 해시와 본문).
사용: python collect-papers.py "검색어" --technique 1 --region 한반도 --max 500
      (PDF를 받으려면 --pdf, 본문 추출에는 pip install pypdf)
OpenAlex는 무료이며 이메일을 UA에 넣으면 빠른 풀을 쓴다(PLACELOC_MAIL 환경변수)."""
import argparse, io
from common import *

def abstract(inv):
    if not inv:
        return None
    pos = {}
    for w, ps in inv.items():
        for p in ps:
            pos[p] = w
    return " ".join(pos[k] for k in sorted(pos))

def apa7(w):
    au = [a["author"]["display_name"] for a in w.get("authorships", [])]
    def fmt(n):
        p = n.split()
        return f"{p[-1]}, " + " ".join(x[0] + "." for x in p[:-1]) if len(p) > 1 else n
    a = ", ".join(fmt(x) for x in au[:20]) if au else ""
    src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
    bi = w.get("biblio") or {}
    pg = f", {bi['first_page']}–{bi['last_page']}" if bi.get("first_page") and bi.get("last_page") else ""
    vol = f", {bi['volume']}" if bi.get("volume") else ""
    doi = ("https://doi.org/" + w["doi"].split("doi.org/")[-1]) if w.get("doi") else ""
    return f"{a} ({w.get('publication_year')}). {w.get('title')}. {src}{vol}{pg}. {doi}".strip()

ap = argparse.ArgumentParser()
ap.add_argument("query"); ap.add_argument("--technique", default=""); ap.add_argument("--region", default="")
ap.add_argument("--max", type=int, default=200); ap.add_argument("--pdf", action="store_true")
a = ap.parse_args()
con = db(); cur = "*"; n = 0
while n < a.max and cur:
    r = get("https://api.openalex.org/works", {"search": a.query, "per-page": 100, "cursor": cur})
    for w in r["results"]:
        if n >= a.max:
            break
        doi = w.get("doi")
        if doi and con.execute("select 1 from paper where doi=?", (doi,)).fetchone():
            continue
        blob = full = h = None
        loc = w.get("best_oa_location") or {}
        if a.pdf and loc.get("pdf_url"):
            try:
                blob = get(loc["pdf_url"], binary=True); h = sha256(blob)
                try:
                    from pypdf import PdfReader
                    full = "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(blob)).pages)
                except Exception:
                    full = None
            except Exception:
                blob = None
        con.execute("insert into paper(doi,title,authors,year,journal,abstract,fulltext,pdf_blob,pdf_sha256,source,technique,region,apa7) values(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (doi, w.get("title"), "; ".join(x["author"]["display_name"] for x in w.get("authorships", [])), w.get("publication_year"),
                     ((w.get("primary_location") or {}).get("source") or {}).get("display_name"), abstract(w.get("abstract_inverted_index")),
                     full, blob, h, "OpenAlex " + now(), a.technique, a.region, apa7(w)))
        n += 1
    con.commit(); cur = r["meta"].get("next_cursor"); time.sleep(0.2)
print("적재", n, "편 ->", DB)
