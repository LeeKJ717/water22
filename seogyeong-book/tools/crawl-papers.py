"""crawl-papers.py - 참고문헌 논문의 전문(공개 PDF·웹 문서)을 수집해 폴더 안 sqlite에 저장한다.
사용: python3 -u crawl-papers.py <출력폴더> <원본DB(seogyeong.sqlite)>           수집(중단 후 재실행하면 이어받음)
      python3 -u crawl-papers.py --merge <출력폴더> <대상DB>                       수집 결과를 대상 DB의 paper 표(fulltext, pdf_blob, pdf_sha256)와 paper_fetch 에 반영
수집 순서: DOI -> Unpaywall(공개 PDF 위치) -> OpenAlex(공개 위치) / DOI 없음 -> OpenAlex 제목 검색(제목 유사도 0.9 이상만 채택) / 웹 주소 -> robots.txt 허용 시에만 내려받음
저장: <폴더>/db/papers.sqlite (fetch, log), <폴더>/raw/<paper_id>.pdf|html, <폴더>/SHA256SUMS. 표준 라이브러리 + pdftotext(있으면)"""
import sys, os, re, json, time, hashlib, sqlite3, subprocess, difflib, datetime, urllib.request, urllib.parse, urllib.robotparser, html
if sys.argv[1] == "--merge":
    OUT, TGT = sys.argv[2], sys.argv[3]
    s = sqlite3.connect(os.path.join(OUT, "db", "papers.sqlite")); t = sqlite3.connect(TGT); n = 0
    for pid, st, src, url, sha, raw, text, at in s.execute("SELECT paper_id,status,source,url,sha256,rawfile,text,fetched_at FROM fetch WHERE status IN ('pdf','html')").fetchall():
        blob = open(os.path.join(OUT, raw), "rb").read() if raw and raw.endswith(".pdf") and os.path.exists(os.path.join(OUT, raw)) else None
        t.execute("UPDATE paper SET fulltext=COALESCE(?,fulltext), pdf_blob=COALESCE(?,pdf_blob), pdf_sha256=COALESCE(?,pdf_sha256) WHERE paper_id=?", (text, blob, sha if blob else None, pid))
        t.execute("UPDATE paper_fetch SET status=?, pdf_sha256=?, fetched_at=?, note=? WHERE paper_id=?", ("done-" + st, sha, at, src + " " + (url or ""), pid)); n += 1
    t.commit(); print("병합", n, "건"); sys.exit()
OUT, SRC = sys.argv[1], sys.argv[2]
RAW = os.path.join(OUT, "raw"); DBD = os.path.join(OUT, "db")
for p in (RAW, DBD): os.makedirs(p, exist_ok=True)
UA = "seogyeong-book-research/1.0 (contact@ssbook.kr)"; MAIL = "contact@ssbook.kr"
db = sqlite3.connect(os.path.join(DBD, "papers.sqlite"))
db.executescript("""CREATE TABLE IF NOT EXISTS fetch(paper_id INTEGER PRIMARY KEY, status TEXT, source TEXT, url TEXT, bytes INTEGER, sha256 TEXT, rawfile TEXT, text TEXT, fetched_at TEXT, note TEXT);
CREATE TABLE IF NOT EXISTS log(lid INTEGER PRIMARY KEY, at TEXT, paper_id INTEGER, action TEXT, status TEXT, detail TEXT);""")
def now(): return datetime.datetime.now().isoformat(timespec="seconds")
def log(pid, a, s, d=""):
    db.execute("INSERT INTO log(at,paper_id,action,status,detail) VALUES(?,?,?,?,?)", (now(), pid, a, s, str(d)[:300])); db.commit()
def get(url, timeout=60, binary=True):
    time.sleep(1.5)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"}), timeout=timeout) as r:
        b = r.read(40_000_000); return b if binary else b.decode("utf-8", "replace")
def js(url): return json.loads(get(url, binary=False))
_rp = {}
def allowed(url):
    h = urllib.parse.urlparse(url); base = f"{h.scheme}://{h.netloc}"
    if base not in _rp:
        rp = urllib.robotparser.RobotFileParser(); rp.set_url(base + "/robots.txt")
        try: rp.read()
        except Exception: rp = None
        _rp[base] = rp
    rp = _rp[base]
    return True if rp is None else rp.can_fetch(UA, url)
def norm(s): return re.sub(r"[^0-9a-z가-힣]", "", (s or "").lower())
def pdf_text(path):
    try: return subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, timeout=180).stdout.decode("utf-8", "replace")
    except Exception: return ""
def html_text(b):
    t = b.decode("utf-8", "replace"); t = re.sub(r"(?is)<(script|style|noscript|nav|footer|header)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t); t = html.unescape(t); return re.sub(r"\s+", " ", t).strip()
def save(pid, status, source, url, b=None, ext="", note=""):
    sha = rel = text = None
    if b is not None:
        sha = hashlib.sha256(b).hexdigest(); rel = f"raw/{pid}.{ext}"; open(os.path.join(OUT, rel), "wb").write(b)
        text = pdf_text(os.path.join(OUT, rel)) if ext == "pdf" else html_text(b)
    db.execute("INSERT OR REPLACE INTO fetch VALUES(?,?,?,?,?,?,?,?,?,?)", (pid, status, source, url, len(b) if b else 0, sha, rel, text, now(), note)); db.commit()
    log(pid, "save", status, f"{source} {url} {len(b) if b else 0}B")
def try_pdf(pid, url, source):
    try:
        b = get(url, timeout=120)
        if b[:5] == b"%PDF-": save(pid, "pdf", source, url, b, "pdf"); return True
        log(pid, "pdf-check", "NOTPDF", url)
    except Exception as e: log(pid, "pdf-get", "ERR", f"{url} {e}")
    return False
src = sqlite3.connect(SRC)
rows = src.execute("SELECT f.paper_id,f.doi,f.url,f.kind,p.title FROM paper_fetch f JOIN paper p ON p.paper_id=f.paper_id ORDER BY f.paper_id").fetchall()
print("대상", len(rows), "건", flush=True)
for pid, doi, url, kind, title in rows:
    if db.execute("SELECT 1 FROM fetch WHERE paper_id=?", (pid,)).fetchone(): continue
    ok = False
    try:
        if not doi and title and kind != "web":
            q = js("https://api.openalex.org/works?per-page=1&mailto=%s&search=%s" % (MAIL, urllib.parse.quote(title)))
            r = (q.get("results") or [None])[0]
            if r and difflib.SequenceMatcher(None, norm(r.get("title")), norm(title)).ratio() >= 0.9:
                doi = (r.get("doi") or "").replace("https://doi.org/", "") or None
                log(pid, "title-match", "OK", f"{doi} {r.get('title')}")
        if doi:
            try:
                u = js("https://api.unpaywall.org/v2/%s?email=%s" % (urllib.parse.quote(doi), MAIL))
                locs = [u.get("best_oa_location")] + (u.get("oa_locations") or [])
                for l in locs:
                    if l and l.get("url_for_pdf") and try_pdf(pid, l["url_for_pdf"], "unpaywall"): ok = True; break
            except Exception as e: log(pid, "unpaywall", "ERR", e)
            if not ok:
                try:
                    w = js("https://api.openalex.org/works/doi:%s?mailto=%s" % (urllib.parse.quote(doi), MAIL))
                    for l in [w.get("best_oa_location")] + (w.get("locations") or []):
                        if l and l.get("pdf_url") and try_pdf(pid, l["pdf_url"], "openalex"): ok = True; break
                    if not ok and w.get("abstract_inverted_index"):
                        ai = w["abstract_inverted_index"]; ws = sorted((p, k) for k, v in ai.items() for p in v)
                        save(pid, "abstract", "openalex", w.get("id"), (" ".join(k for _, k in ws)).encode(), "html", "초록만 확보(전문 아님)")
                        ok = True
                except Exception as e: log(pid, "openalex", "ERR", e)
        if not ok and url and kind == "web":
            if not allowed(url): save(pid, "robots-blocked", "web", url, note="robots.txt 불허: 내려받지 않음"); continue
            b = get(url, timeout=60)
            if b[:5] == b"%PDF-": save(pid, "pdf", "web", url, b, "pdf")
            else: save(pid, "html", "web", url, b, "html")
            ok = True
    except Exception as e: log(pid, "paper", "ERR", e)
    if not ok and not db.execute("SELECT 1 FROM fetch WHERE paper_id=?", (pid,)).fetchone(): save(pid, "none", "-", doi or url, note="공개 전문 없음 또는 접근 실패")
    print(pid, db.execute("SELECT status FROM fetch WHERE paper_id=?", (pid,)).fetchone()[0], flush=True)
print("==== 요약", flush=True)
for st, n, by in db.execute("SELECT status,count(*),sum(bytes) FROM fetch GROUP BY status").fetchall(): print(st, n, by, flush=True)
db.close()
subprocess.run("cd '%s' && find . -type f ! -name SHA256SUMS -print0 | xargs -0 sha256sum > SHA256SUMS" % OUT, shell=True)
print("DONE", flush=True)
