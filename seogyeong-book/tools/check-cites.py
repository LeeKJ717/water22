"""check-cites.py - 본문 인용(저자, 연도)이 장별 참고문헌에 있는지, 참고문헌이 본문에서 인용되는지 점검한다."""
import re, glob, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
bad = 0
for f in sorted(glob.glob(os.path.join(R, "원고", "[0-9]*.md"))):
    ch = "ch" + os.path.basename(f)[:2]
    t = open(f, encoding="utf-8").read()
    rp = os.path.join(R, "참고문헌", ch + ".txt")
    refs = [l.strip() for l in open(rp, encoding="utf-8") if l.strip() and not l.startswith("#")] if os.path.exists(rp) else []
    years = set(re.findall(r"\((?:[^()]*?)(\d{4})[a-z]?\)", t)) | set(re.findall(r"[A-Za-z&.\s]+\((\d{4})\)", t))
    cited = re.findall(r"([A-Z][A-Za-z'’\-]+)(?: et al\.| & [A-Z][A-Za-z'’\-]+)?[,\s]*\(?(\d{4})[a-z]?\)?", t)
    for name, y in set(cited):
        if not any(r.startswith(name) and f"({y}" in r for r in refs):
            print(f"[{ch}] 참고문헌에 없음: {name} {y}"); bad += 1
    for r in refs:
        n = re.split(r"[,.\s(]", r)[0]; m = re.search(r"\((\d{4})", r); y = m.group(1) if m else "n\\.d\\."
        if not re.search(re.escape(n) + r"[^\n]{0,40}" + y, t):
            print(f"[{ch}] 본문에서 인용되지 않음: {n} {y}"); bad += 1
print("불일치", bad)
