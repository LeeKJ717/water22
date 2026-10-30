"""crawl-yeoji.py - 『신증동국여지승람』 전권을 위키문헌(MediaWiki API)에서 받아 폴더 안 sqlite에 저장한다.
사용: python3 crawl-yeoji.py <출력폴더>   (z840에서 실행, 표준 라이브러리만 사용)
방식: allpages로 '新增東國輿地勝覽' 접두 문서 목록을 먼저 확보한 뒤 각 문서의 wikitext 전체를 저장한다.
저장: <폴더>/raw/<해시>.txt, <폴더>/db/yeoji.sqlite (page, entry, log), <폴더>/SHA256SUMS
이미 받은 문서는 건너뛰므로 중단 후 재실행 가능."""
import sys, os, re, json, time, hashlib, sqlite3, urllib.request, urllib.parse, datetime, subprocess
OUT = sys.argv[1]; RAW = os.path.join(OUT, "raw"); DBD = os.path.join(OUT, "db")
os.makedirs(RAW, exist_ok=True); os.makedirs(DBD, exist_ok=True)
API = "https://zh.wikisource.org/w/api.php"; UA = "seogyeong-book-research/1.0 (contact@ssbook.kr)"
PREFIX = "新增東國輿地勝覽"
db = sqlite3.connect(os.path.join(DBD, "yeoji.sqlite"))
db.executescript("""CREATE TABLE IF NOT EXISTS page(pid INTEGER PRIMARY KEY, title TEXT UNIQUE, url TEXT, fetched_at TEXT, bytes INTEGER, sha256 TEXT, rawfile TEXT, text TEXT);
CREATE TABLE IF NOT EXISTS entry(eid INTEGER PRIMARY KEY, pid INTEGER, seq INTEGER, level INTEGER, heading TEXT, body TEXT);
CREATE TABLE IF NOT EXISTS log(lid INTEGER PRIMARY KEY, at TEXT, action TEXT, status TEXT, detail TEXT);""")
def now(): return datetime.datetime.now().isoformat(timespec="seconds")
def log(a, s, d=""):
    db.execute("INSERT INTO log(at,action,status,detail) VALUES(?,?,?,?)", (now(), a, s, str(d)[:300])); db.commit(); print(f"[{s}] {a} {str(d)[:80]}")
def api(**p):
    p["format"] = "json"; url = API + "?" + urllib.parse.urlencode(p)
    time.sleep(1.2)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
        return json.loads(r.read().decode("utf-8")), url
titles = [PREFIX]; cont = None
while True:
    p = dict(action="query", list="allpages", apprefix=PREFIX + "/", aplimit=500, apnamespace=0)
    if cont: p["apcontinue"] = cont
    try:
        d, _ = api(**p)
    except Exception as e:
        log("allpages", "ERR", e); break
    titles += [x["title"] for x in d["query"]["allpages"]]
    cont = d.get("continue", {}).get("apcontinue")
    if not cont: break
titles = sorted(set(titles)); log("allpages", "OK", f"{len(titles)}개 문서")
for t in titles:
    if db.execute("SELECT 1 FROM page WHERE title=?", (t,)).fetchone(): continue
    try:
        d, url = api(action="query", prop="revisions", rvprop="content", rvslots="main", titles=t, redirects=1)
        pg = list(d["query"]["pages"].values())[0]
        if "missing" in pg: log("fetch " + t, "MISSING"); continue
        text = pg["revisions"][0]["slots"]["main"]["*"]
    except Exception as e:
        log("fetch " + t, "ERR", e); continue
    b = text.encode("utf-8"); h = hashlib.sha256(b).hexdigest(); fn = f"yeoji-{h[:12]}.txt"
    open(os.path.join(RAW, fn), "wb").write(b)
    cur = db.execute("INSERT INTO page(title,url,fetched_at,bytes,sha256,rawfile,text) VALUES(?,?,?,?,?,?,?)",
                     (t, "https://zh.wikisource.org/wiki/" + urllib.parse.quote(t), now(), len(b), h, "raw/" + fn, text)); pid = cur.lastrowid
    seq = 0; head = "(앞머리)"; lvl = 0; buf = []
    def flush():
        global seq
        body = "\n".join(buf).strip()
        if body or head != "(앞머리)":
            seq += 1; db.execute("INSERT INTO entry(pid,seq,level,heading,body) VALUES(?,?,?,?,?)", (pid, seq, lvl, head, body))
    for line in text.split("\n"):
        m = re.match(r"^(=+)\s*(.+?)\s*\1\s*$", line)
        if m: flush(); head = m.group(2); lvl = len(m.group(1)); buf = []
        else: buf.append(line)
    flush(); db.commit(); log("fetch " + t, "OK", f"{len(b)}B entries={seq}")
print("page", db.execute("SELECT count(*), sum(bytes) FROM page").fetchone(), "entry", db.execute("SELECT count(*) FROM entry").fetchone())
db.close()
subprocess.run("cd '%s' && find . -type f ! -name SHA256SUMS -print0 | xargs -0 sha256sum > SHA256SUMS" % OUT, shell=True)
