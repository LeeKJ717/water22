import re, sys, importlib, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PAT = re.compile(r"⟪([^⟫]+?)⟫")
def render(name):
    ns = {}
    py = f"calc{name}.py"
    if os.path.exists(py):
        mod = importlib.import_module(f"calc{name}"); ns = dict(vars(mod))
    ns["math"] = math
    t = open(f"f{name}.md", encoding="utf-8").read()
    def rep(m):
        s = m.group(1)
        if "|" in s: expr, spec = s.split("|", 1)
        else: expr, spec = s, ""
        v = eval(expr.strip(), ns)
        return format(v, spec) if spec else str(v)
    out = PAT.sub(rep, t)
    out = re.sub(r'(?m)^- \[ \] ', '- ', out)
    return out
if __name__ == "__main__":
    for n in sys.argv[1:]:
        print(render(n))
