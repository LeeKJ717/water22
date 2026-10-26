"""collect-coords.py - Wikidata에서 지명의 좌표(P625)를 찾아 place/coord에 넣는다(basis='gazetteer', 식별자·URL·조회 시각 기록).
사용: python collect-coords.py 평양 "Pyongyang" ...      후보가 여럿이면 모두 넣고 note에 후보 순위를 적는다. 연구자가 하나를 확정한다."""
import sys
from common import *
con = db()
for name in sys.argv[1:]:
    r = get("https://www.wikidata.org/w/api.php", {"action": "wbsearchentities", "search": name, "language": "ko", "uselang": "ko", "limit": 5, "format": "json"})
    for rank, c in enumerate(r.get("search", [])):
        e = get("https://www.wikidata.org/w/api.php", {"action": "wbgetentities", "ids": c["id"], "props": "claims", "format": "json"})
        cl = e["entities"][c["id"]]["claims"].get("P625")
        if not cl:
            continue
        v = cl[0]["mainsnak"]["datavalue"]["value"]
        pid = con.execute("insert into place(name_han,name_ko,note) values(?,?,?)", (name, name, f"Wikidata 후보 {rank+1}: {c.get('description','')}")).lastrowid
        con.execute("insert into coord(place_id,lon,lat,sigma_km,basis,gazetteer,gazetteer_id,url,retrieved_at) values(?,?,?,?,?,?,?,?,?)",
                    (pid, v["longitude"], v["latitude"], None, "gazetteer", "Wikidata", c["id"], "https://www.wikidata.org/wiki/" + c["id"], now()))
        print(name, c["id"], v["latitude"], v["longitude"], c.get("description", ""))
    time.sleep(0.3)
con.commit()
