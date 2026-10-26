import os, sqlite3, time, json, hashlib, urllib.request, urllib.parse

DB = os.environ.get("PLACELOC_DB", "placeloc.sqlite")
UA = "placeloc-book/1.0 (mailto:%s)" % os.environ.get("PLACELOC_MAIL", "sanbada136@gmail.com")

def db():
    new = not os.path.exists(DB)
    con = sqlite3.connect(DB)
    if new:
        con.executescript(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "placeloc-schema-v1.sql"), encoding="utf-8").read())
    return con

def get(url, params=None, binary=False, tries=3):
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            return data if binary else json.loads(data.decode("utf-8"))
        except Exception as e:
            if k == tries - 1:
                raise
            time.sleep(2 * (k + 1))

def sha256(b):
    return hashlib.sha256(b).hexdigest()

def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")
