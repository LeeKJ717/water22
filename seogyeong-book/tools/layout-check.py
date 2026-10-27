"""layout-check.py - PDF 레이아웃 점검: 좌우 넘침, 하단 넘침, 쪽 맨 아래에 홀로 남은 제목. 사용: python3 tools/layout-check.py book.pdf"""
import sys, pymupdf
MM = 72 / 25.4
doc = pymupdf.open(sys.argv[1])
W, H = doc[0].rect.width, doc[0].rect.height
L_OK, R_OK = 19 * MM, 168 * MM      # 표·그림 허용 범위(왼쪽 21mm, 오른쪽 167mm 기준 ±)
BOT = H - 22 * MM                   # 본문 하단 한계(쪽번호 제외)
rep = {"side": [], "bottom": [], "strand": [], "heading-near-bottom": [], "gap": []}
for pn, page in enumerate(doc, 1):
    d = page.get_text("dict")
    lines = []
    for b in d["blocks"]:
        if b["type"] != 0: continue
        for ln in b["lines"]:
            txt = "".join(s["text"] for s in ln["spans"]).strip()
            if not txt: continue
            sz = max(s["size"] for s in ln["spans"])
            lines.append((ln["bbox"], sz, txt))
    body = [l for l in lines if l[0][3] < H - 20 * MM]   # 쪽번호 줄 제외
    if not body: continue
    x0 = min(l[0][0] for l in body); x1 = max(l[0][2] for l in body); y1 = max(l[0][3] for l in body)
    gx0, gx1 = x0, x1
    for dr in page.get_drawings():
        r = dr["rect"]
        if r.width > W * 0.98 or r.height > H * 0.98: continue
        if r.y1 > H - 18 * MM: continue
        if dr.get('fill') == (1.0, 1.0, 1.0) and not dr.get('color'): continue   # 보이지 않는 흰 바탕 사각형
        gx0 = min(gx0, r.x0); gx1 = max(gx1, r.x1)
    for im in page.get_image_info():
        gx0 = min(gx0, im["bbox"][0]); gx1 = max(gx1, im["bbox"][2])
    if gx0 < L_OK or gx1 > R_OK:
        rep["side"].append((pn, round(gx0 / MM, 1), round(gx1 / MM, 1)))
    if y1 > BOT:
        rep["bottom"].append((pn, round(y1 / MM, 1)))
    sb = sorted(body, key=lambda l: l[0][3])
    for idx, l in enumerate(sb):
        if 11.4 <= l[1] < 20 and len(l[2]) < 70 and idx >= len(sb) - 2 and idx < len(sb) - 1 + 1:
            below = [m for m in sb[idx + 1:] if m[1] < 11.4]
            if len(below) < 2 and idx != len(sb) - 1:
                rep["heading-near-bottom"].append((pn, l[2][:40], len(below)))
    if y1 < 150 * MM and not any("이 장의 차례" in l[2] for l in body) and pn > 12:
        rep["gap"].append((pn, round(y1 / MM)))
    last = sb[-1]
    if last[1] >= 11.4 and len(last[2]) < 60:
        rep["strand"].append((pn, last[2][:40], round(last[1], 1)))
for k, v in rep.items():
    print(k, len(v)); [print("  ", x) for x in v[:60]]
