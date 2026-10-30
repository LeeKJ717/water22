"""crawl-sagyo.py - 서경(西京) 관련 원사료를 위키문헌(MediaWiki API)에서 수집해 폴더 안 sqlite에 저장한다.
사용: python3 crawl-sagyo.py <출력폴더>   (z840에서 실행. 표준 라이브러리만 사용)
저장: <폴더>/raw/*.txt (원문 wikitext), <폴더>/db/sagyocrawl.sqlite (page, hit, log), <폴더>/SHA256SUMS
원칙: 접속 실패·미발견은 log에 그대로 남긴다. 본문은 가공하지 않고 저장한다."""
import sys, os, re, json, time, hashlib, sqlite3, urllib.request, urllib.parse, datetime
OUT = sys.argv[1]
RAW = os.path.join(OUT, "raw"); DBD = os.path.join(OUT, "db")
os.makedirs(RAW, exist_ok=True); os.makedirs(DBD, exist_ok=True)
UA = "seogyeong-book-research/1.0 (contact@ssbook.kr)"
SITES = {"zh": "https://zh.wikisource.org/w/api.php", "ko": "https://ko.wikisource.org/w/api.php"}
# (표시명, 사이트, 직접 제목 후보들, 검색어)
TARGETS = [
 ("고려사 권58 지리3 서경유수관", "zh", ["高麗史/卷五十八", "高麗史/卷058"], "高麗史 地理三 西京留守官 平壤府"),
 ("고려사 권57 지리2", "zh", ["高麗史/卷五十七", "高麗史/卷057"], "高麗史 地理二 楊廣道"),
 ("신증동국여지승람 권51 평양부", "zh", ["新增東國輿地勝覽/卷五十一", "新增東國輿地勝覽/卷51"], "新增東國輿地勝覽 平壤府 建置沿革"),
 ("삼국사기 권19 평원왕", "zh", ["三國史記/卷第十九", "三國史記/卷十九"], "三國史記 平原王 長安城 移都"),
 ("삼국사기 권37 지리4", "zh", ["三國史記/卷第三十七", "三國史記/卷三十七"], "三國史記 地理四 平壤"),
 ("세종실록지리지 평안도 평양부", "zh", ["世宗實錄地理志/平安道", "世宗實錄/地理志/平安道"], "世宗實錄地理志 平安道 平壤府"),
 ("고려사 서경 검색", "ko", [], "서경 평양 유수관"),
 ("고려사절요 서경 검색", "zh", [], "高麗史節要 西京 平壤 重營"),
]
KEYS = ["西京", "平壤", "鴨綠", "浿水", "大同江", "遼東", "里"]
db = sqlite3.connect(os.path.join(DBD, "sagyocrawl.sqlite"))
db.executescript("""CREATE TABLE IF NOT EXISTS page(pid INTEGER PRIMARY KEY, target TEXT, site TEXT, title TEXT, url TEXT, fetched_at TEXT, bytes INTEGER, sha256 TEXT, rawfile TEXT, text TEXT);
CREATE TABLE IF NOT EXISTS hit(hid INTEGER PRIMARY KEY, pid INTEGER, keyword TEXT, context TEXT);
CREATE TABLE IF NOT EXISTS log(lid INTEGER PRIMARY KEY, at TEXT, target TEXT, action TEXT, status TEXT, detail TEXT);""")
def now(): return datetime.datetime.now().isoformat(timespec="seconds")
def log(t, a, s, d=""):
    db.execute("INSERT INTO log(at,target,action,status,detail) VALUES(?,?,?,?,?)", (now(), t, a, s, str(d)[:500])); db.commit()
    print(f"[{s}] {t} {a} {str(d)[:100]}")
def api(site, **p):
    p["format"] = "json"
    url = SITES[site] + "?" + urllib.parse.urlencode(p)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    time.sleep(1.5)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8")), url
def get_text(site, title):
    d, url = api(site, action="query", prop="revisions", rvprop="content", rvslots="main", titles=title, redirects=1)
    for pg in d.get("query", {}).get("pages", {}).values():
        if "missing" in pg: return None, url
        return pg["revisions"][0]["slots"]["main"]["*"], url
    return None, url
def save(target, site, title, url, text):
    b = text.encode("utf-8"); h = hashlib.sha256(b).hexdigest()
    fn = re.sub(r"[^0-9A-Za-z가-힣]+", "-", f"{site}-{title}")[:80] + ".txt"
    open(os.path.join(RAW, fn), "wb").write(b)
    cur = db.execute("INSERT INTO page(target,site,title,url,fetched_at,bytes,sha256,rawfile,text) VALUES(?,?,?,?,?,?,?,?,?)",
                     (target, site, title, url, now(), len(b), h, "raw/" + fn, text)); pid = cur.lastrowid
    n = 0
    for line in re.split(r"\n+", text):
        for k in KEYS[:6]:
            if k in line:
                db.execute("INSERT INTO hit(pid,keyword,context) VALUES(?,?,?)", (pid, k, line.strip()[:600])); n += 1; break
    db.commit(); return pid, len(b), n
for target, site, titles, query in TARGETS:
    got = False
    for t in titles:
        try:
            text, url = get_text(site, t)
        except Exception as e:
            log(target, "fetch " + t, "ERR", e); continue
        if text:
            pid, nb, nh = save(target, site, t, url, text); log(target, "fetch " + t, "OK", f"{nb}B hit={nh}"); got = True; break
        log(target, "fetch " + t, "MISSING")
    if got: continue
    try:
        d, url = api(site, action="query", list="search", srsearch=query, srlimit=5)
        res = d.get("query", {}).get("search", [])
        log(target, "search", "OK", [r["title"] for r in res])
    except Exception as e:
        log(target, "search", "ERR", e); continue
    for r in res[:3]:
        try:
            text, url = get_text(site, r["title"])
            if text:
                pid, nb, nh = save(target, site, r["title"], url, text); log(target, "fetch " + r["title"], "OK", f"{nb}B hit={nh}")
        except Exception as e:
            log(target, "fetch " + r["title"], "ERR", e)
print("page", db.execute("SELECT count(*) FROM page").fetchone(), "hit", db.execute("SELECT count(*) FROM hit").fetchone())
db.close()
import subprocess
subprocess.run("cd '%s' && find . -type f ! -name SHA256SUMS -print0 | xargs -0 sha256sum > SHA256SUMS" % OUT, shell=True)
