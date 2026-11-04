#!/bin/bash
# z840: Commons의 新增東國輿地勝覽 스캔 PDF 목록과 쪽수/크기/설명/라이선스 조회 (읽기 전용, API만)
UA="seogyeong-book-research/1.0 (contact@ssbook.kr)"
OUT=$HOME/probe-commons.log
python3 - "$UA" <<'PY' 2>&1 | tee $OUT
import sys, json, urllib.request, urllib.parse
UA = sys.argv[1]
API = "https://commons.wikimedia.org/w/api.php"
def get(params):
    url = API + "?" + urllib.parse.urlencode(params)
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40))
# robots: '*' 그룹 요약
try:
    r = urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/robots.txt", headers={"User-Agent": UA}), timeout=20).read().decode()
    grp = r.split("User-agent: *")[1].split("User-agent:")[0] if "User-agent: *" in r else ""
    print("[robots * 그룹 Disallow 줄 수]", sum(1 for l in grp.splitlines() if l.startswith("Disallow")), " /w/api.php 차단:", "/w/api.php" in grp)
except Exception as e:
    print("robots 오류", e)
titles = []
for q in ["新增東國輿地勝覽", "東國輿地勝覽 NTUL", "東國輿地勝覽 NCL", "東國輿地勝覽 CNTS"]:
    d = get({"action": "query", "list": "search", "srsearch": q, "srnamespace": 6, "srlimit": 60, "format": "json"})
    titles += [p["title"] for p in d["query"]["search"]]
titles = sorted(set(t for t in titles if "輿地勝覽" in t and t.lower().endswith(".pdf")))
print("PDF 파일 수:", len(titles))
for i in range(0, len(titles), 15):
    d = get({"action": "query", "titles": "|".join(titles[i:i+15]), "prop": "imageinfo", "iiprop": "size|url|extmetadata", "format": "json"})
    for p in d["query"]["pages"].values():
        ii = (p.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata", {})
        desc = (em.get("ImageDescription", {}).get("value", "") or "").replace("\n", " ")[:160]
        lic = em.get("LicenseShortName", {}).get("value", "")
        print(f'{p["title"]} | {round(ii.get("size",0)/1048576,1)}MB | {ii.get("pagecount","?")}쪽 | {lic} | {desc}')
        print("   ", ii.get("url", ""))
PY
echo "로그: $OUT"
