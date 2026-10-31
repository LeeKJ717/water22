"""crawl-yeoji2.py - 『신증동국여지승람』 평안도(권51~55 평양부 등)를 찾기 위한 확장 크롤러.
사용: python3 -u crawl-yeoji2.py <출력폴더>   (z840에서 실행, 표준 라이브러리만 사용)
대상: 한국어 위키문헌(ko), 중문 위키문헌(zh), 위키미디어 공용(commons)
방식: ① 네임스페이스 번호 확인 ② 접두어 목록(allpages)과 검색(search)으로 후보 문서·파일 전부 수집
      ③ 본문/페이지/색인 문서는 wikitext 전체 저장 ④ 스캔 파일(PDF 등)은 메타데이터 기록 후 내려받기
저장: <폴더>/db/yeoji2.sqlite (found, page, entry, file, log), <폴더>/raw/ (본문 원본), <폴더>/raw/files/ (스캔 파일), <폴더>/SHA256SUMS
중단 후 재실행하면 이어받는다. 이미 받은 중문 '新增東國輿地勝覽/…' 권1~33 문서는 건너뛴다(yeojiseungram-v1에 있음)."""
import sys, os, re, json, time, hashlib, sqlite3, urllib.request, urllib.parse, datetime, subprocess
OUT = sys.argv[1]; RAW = os.path.join(OUT, "raw"); FILES = os.path.join(RAW, "files"); DBD = os.path.join(OUT, "db")
for p in (RAW, FILES, DBD): os.makedirs(p, exist_ok=True)
SITES = {"ko": "https://ko.wikisource.org/w/api.php", "zh": "https://zh.wikisource.org/w/api.php",
         "commons": "https://commons.wikimedia.org/w/api.php"}
UA = "seogyeong-book-research/1.0 (contact@ssbook.kr)"
PREFIXES = ["신증동국여지승람", "新增東國輿地勝覽", "東國輿地勝覽", "동국여지승람"]
SEARCHES = ["신증동국여지승람", "新增東國輿地勝覽", "東國輿地勝覽 平壤府", "신증동국여지승람 평양부", "新增東國輿地勝覽 平安道"]
KEYS = ("신증동국여지승람", "新增東國輿地勝覽", "東國輿地勝覽", "동국여지승람", "여지승람")
MAXFILE = 400 * 1024 * 1024
db = sqlite3.connect(os.path.join(DBD, "yeoji2.sqlite"))
db.executescript("""CREATE TABLE IF NOT EXISTS found(fid INTEGER PRIMARY KEY, site TEXT, ns INTEGER, title TEXT, via TEXT, UNIQUE(site,title));
CREATE TABLE IF NOT EXISTS page(pid INTEGER PRIMARY KEY, site TEXT, ns INTEGER, title TEXT, url TEXT, fetched_at TEXT, bytes INTEGER, sha256 TEXT, rawfile TEXT, text TEXT, UNIQUE(site,title));
CREATE TABLE IF NOT EXISTS entry(eid INTEGER PRIMARY KEY, pid INTEGER, seq INTEGER, level INTEGER, heading TEXT, body TEXT);
CREATE TABLE IF NOT EXISTS file(fid INTEGER PRIMARY KEY, site TEXT, title TEXT, url TEXT, size INTEGER, mime TEXT, sha1 TEXT, sha256 TEXT, path TEXT, status TEXT, UNIQUE(site,title));
CREATE TABLE IF NOT EXISTS log(lid INTEGER PRIMARY KEY, at TEXT, action TEXT, status TEXT, detail TEXT);""")
def now(): return datetime.datetime.now().isoformat(timespec="seconds")
def log(a, s, d=""):
    db.execute("INSERT INTO log(at,action,status,detail) VALUES(?,?,?,?)", (now(), a, s, str(d)[:300])); db.commit()
    print(f"[{s}] {a} {str(d)[:100]}", flush=True)
def api(site, **p):
    p["format"] = "json"; url = SITES[site] + "?" + urllib.parse.urlencode(p)
    time.sleep(1.2)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))
def addfound(site, ns, title, via):
    db.execute("INSERT OR IGNORE INTO found(site,ns,title,via) VALUES(?,?,?,?)", (site, ns, title, via))
# ① 네임스페이스 확인 (Page/Index/File 번호는 사이트마다 다를 수 있음)
NS = {}
for s in SITES:
    try:
        d = api(s, action="query", meta="siteinfo", siprop="namespaces")
        ids = {}
        for k, v in d["query"]["namespaces"].items():
            c = v.get("canonical", "")
            if c in ("File", "Page", "Index"): ids[c] = int(k)
        NS[s] = ids; log("namespaces " + s, "OK", ids)
    except Exception as e:
        NS[s] = {"File": 6}; log("namespaces " + s, "ERR", e)
# ② 후보 수집: 접두어 목록 + 검색
for s in SITES:
    nss = [0] + [NS[s][c] for c in ("File", "Page", "Index") if c in NS[s]]
    if s == "commons": nss = [NS[s].get("File", 6)]
    for ns in nss:
        for pre in PREFIXES:
            cont = None
            while True:
                p = dict(action="query", list="allpages", apprefix=pre, aplimit=500, apnamespace=ns)
                if cont: p["apcontinue"] = cont
                try: d = api(s, **p)
                except Exception as e: log(f"allpages {s} ns{ns} {pre}", "ERR", e); break
                for x in d["query"]["allpages"]: addfound(s, ns, x["title"], "prefix:" + pre)
                cont = d.get("continue", {}).get("apcontinue")
                if not cont: break
        db.commit()
    for q in SEARCHES:
        off = 0
        while off < 500:
            try:
                d = api(s, action="query", list="search", srsearch=q, srnamespace="|".join(map(str, nss)), srlimit=50, sroffset=off)
            except Exception as e: log(f"search {s} {q}", "ERR", e); break
            for x in d["query"]["search"]:
                if any(k in x["title"] for k in KEYS) or "平壤" in q or "평양" in q:
                    addfound(s, x["ns"], x["title"], "search:" + q)
            nxt = d.get("continue", {}).get("sroffset")
            if nxt is None: break
            off = nxt
        db.commit()
    log("discover " + s, "OK", db.execute("SELECT ns,count(*) FROM found WHERE site=? GROUP BY ns", (s,)).fetchall())
log("discover", "OK", db.execute("SELECT site,ns,count(*) FROM found GROUP BY site,ns").fetchall())
# ③ 본문 계열 문서 wikitext 저장 (파일 네임스페이스 제외)
filens = {s: NS[s].get("File", 6) for s in SITES}
todo = [(s, ns, t) for s, ns, t in db.execute("SELECT site,ns,title FROM found ORDER BY site,ns,title")
        if ns != filens[s] and not (s == "zh" and t.startswith("新增東國輿地勝覽/"))
        and not db.execute("SELECT 1 FROM page WHERE site=? AND title=?", (s, t)).fetchone()]
log("pages todo", "OK", len(todo))
def split_entries(pid, text):
    seq = 0; head = "(앞머리)"; lvl = 0; buf = []
    def flush():
        nonlocal seq
        body = "\n".join(buf).strip()
        if body or head != "(앞머리)":
            seq += 1; db.execute("INSERT INTO entry(pid,seq,level,heading,body) VALUES(?,?,?,?,?)", (pid, seq, lvl, head, body))
    for line in text.split("\n"):
        m = re.match(r"^(=+)\s*(.+?)\s*\1\s*$", line)
        if m: flush(); head = m.group(2); lvl = len(m.group(1)); buf = []
        else: buf.append(line)
    flush(); return seq
BATCH = 15
for i in range(0, len(todo), BATCH):
    chunk = todo[i:i + BATCH]
    for s in {c[0] for c in chunk}:
        sub = [c for c in chunk if c[0] == s]
        try:
            d = api(s, action="query", prop="revisions", rvprop="content", rvslots="main", titles="|".join(c[2] for c in sub))
        except Exception as e:
            log(f"fetch {s} batch{i}", "ERR", e); continue
        nsmap = {c[2]: c[1] for c in sub}
        for pg in d["query"]["pages"].values():
            t = pg.get("title")
            if "missing" in pg or "revisions" not in pg: log("fetch " + str(t), "MISSING"); continue
            text = pg["revisions"][0]["slots"]["main"]["*"]; b = text.encode("utf-8"); h = hashlib.sha256(b).hexdigest()
            fn = f"{s}-{h[:12]}.txt"; open(os.path.join(RAW, fn), "wb").write(b)
            ns = nsmap.get(t, pg.get("ns", 0))
            cur = db.execute("INSERT OR IGNORE INTO page(site,ns,title,url,fetched_at,bytes,sha256,rawfile,text) VALUES(?,?,?,?,?,?,?,?,?)",
                (s, ns, t, SITES[s].replace("/w/api.php", "/wiki/") + urllib.parse.quote(t), now(), len(b), h, "raw/" + fn, text))
            if cur.rowcount and ns == 0: split_entries(cur.lastrowid, text)
        db.commit()
    if (i // BATCH) % 10 == 0: log("pages progress", "OK", f"{min(i + BATCH, len(todo))}/{len(todo)}")
log("pages", "OK", db.execute("SELECT site,ns,count(*),sum(bytes) FROM page GROUP BY site,ns").fetchall())
# ④ 스캔 파일: 메타데이터 기록 후 내려받기
ftodo = [(s, t) for s, ns, t in db.execute("SELECT site,ns,title FROM found") if ns == filens[s]
         and any(k in t for k in KEYS) and not db.execute("SELECT 1 FROM file WHERE site=? AND title=? AND status='OK'", (s, t)).fetchone()]
log("files todo", "OK", len(ftodo))
for i in range(0, len(ftodo), 20):
    chunk = ftodo[i:i + 20]
    for s in {c[0] for c in chunk}:
        sub = [c[1] for c in chunk if c[0] == s]
        try: d = api(s, action="query", prop="imageinfo", iiprop="url|size|sha1|mime", titles="|".join(sub))
        except Exception as e: log(f"imageinfo {s}", "ERR", e); continue
        for pg in d["query"]["pages"].values():
            ii = (pg.get("imageinfo") or [None])[0]
            if not ii: log("imageinfo " + str(pg.get("title")), "MISSING"); continue
            db.execute("INSERT OR REPLACE INTO file(site,title,url,size,mime,sha1,status) VALUES(?,?,?,?,?,?,?)",
                       (s, pg["title"], ii["url"], ii["size"], ii["mime"], ii["sha1"], "META"))
        db.commit()
for fid, s, t, url, size in db.execute("SELECT fid,site,title,url,size FROM file WHERE status!='OK' ORDER BY title").fetchall():
    if size and size > MAXFILE: db.execute("UPDATE file SET status='TOOBIG' WHERE fid=?", (fid,)); db.commit(); log("download " + t, "SKIP", f"{size}B"); continue
    fn = re.sub(r"[^0-9A-Za-z.\-]", "", hashlib.sha1(t.encode()).hexdigest()[:10]) + "-" + re.sub(r"[^0-9A-Za-z.]", "", os.path.basename(urllib.parse.urlparse(url).path)[-40:] or "f.bin")
    path = os.path.join(FILES, fn)
    try:
        time.sleep(3)
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=300) as r, open(path, "wb") as f:
            h = hashlib.sha256()
            while True:
                c = r.read(1 << 20)
                if not c: break
                f.write(c); h.update(c)
        db.execute("UPDATE file SET sha256=?, path=?, status='OK' WHERE fid=?", (h.hexdigest(), "raw/files/" + fn, fid)); db.commit()
        log("download " + t, "OK", f"{os.path.getsize(path)}B")
    except Exception as e:
        db.execute("UPDATE file SET status='ERR' WHERE fid=?", (fid,)); db.commit(); log("download " + t, "ERR", e)
print("found", db.execute("SELECT site,ns,count(*) FROM found GROUP BY site,ns").fetchall(), flush=True)
print("page", db.execute("SELECT count(*), sum(bytes) FROM page").fetchone(), "file", db.execute("SELECT status,count(*),sum(size) FROM file GROUP BY status").fetchall(), flush=True)
db.close()
subprocess.run("cd '%s' && find . -type f ! -name SHA256SUMS -print0 | xargs -0 sha256sum > SHA256SUMS" % OUT, shell=True)
print("DONE", flush=True)
