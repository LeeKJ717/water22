"""9장 완전 풀이 예제: 스트레스 최소화(기울기 하강), 잭나이프, 매개중심성. 가상 세계."""
import numpy as np, math
from scipy.optimize import minimize

ANC = {"A": (0, 0), "B": (100, 0), "C": (50, 80), "D": (100, 80)}
DREC = {"A": 70.0, "B": 48.0, "C": 51.0, "D": 66.0}
W = {"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0}

def stress(z, ks, dd=None, w=None):
    dd = dd or DREC; w = w or W
    s = 0.0
    for k in ks:
        a = ANC[k]; r = math.hypot(z[0]-a[0], z[1]-a[1])
        s += w[k]*(r-dd[k])**2
    return s

def grad(z, ks, dd=None):
    dd = dd or DREC
    g = np.zeros(2)
    for k in ks:
        a = ANC[k]; v = np.array([z[0]-a[0], z[1]-a[1]]); r = np.linalg.norm(v)
        g += 2*W[k]*(r-dd[k])*v/r
    return g

def solve(ks, dd=None, z0=(50, 40)):
    r = minimize(lambda z: stress(z, ks, dd), z0, method="Nelder-Mead", options={"xatol": 1e-6, "fatol": 1e-9})
    return r.x, r.fun

def bc_table():
    # 6개 지명의 그물: 간선 목록
    E = [("가", "나"), ("나", "다"), ("나", "라"), ("다", "마"), ("라", "마"), ("마", "바")]
    nodes = sorted({n for e in E for n in e})
    adj = {n: set() for n in nodes}
    for a, b in E:
        adj[a].add(b); adj[b].add(a)
    def paths(s, t):
        # 모든 최단 경로
        from collections import deque
        dist = {s: 0}; q = deque([s]); pre = {s: []}
        while q:
            u = q.popleft()
            for w in sorted(adj[u]):
                if w not in dist:
                    dist[w] = dist[u]+1; pre[w] = [u]; q.append(w)
                elif dist[w] == dist[u]+1:
                    pre[w].append(u)
        res = []
        def back(v, path):
            if v == s:
                res.append([s]+path[::-1]); return
            for p in pre[v]:
                back(p, path+[v])
        back(t, [])
        return [list(reversed(r)) if False else r for r in res]
    return E, nodes, adj, paths

def md():
    out = []; P = out.append
    P("### 완전 풀이 예제 1: 스트레스를 줄여 가며 미지 지명 놓기")
    P("")
    P("앵커 네 곳(위치를 아는 지명)과 미지 지명 $Z$가 있다. 앵커는 $A=(0,0)$, $B=(100,0)$, $C=(50,80)$, $D=(100,80)$ km이고, 사료에서 환산한 거리는 $d_{AZ}=70$, $d_{BZ}=48$, $d_{CZ}=51$, $d_{DZ}=66$ km이다. 가중치는 모두 1이다(참 위치는 $(62,31)$로 정해 두었지만 계산하는 사람은 모른다).")
    P("")
    P("스트레스 $=\\sum_k w_k(\\lVert\\mathbf{z}-\\mathbf{a}_k\\rVert-d_k)^2$. 먼저 처음 추측 $\\mathbf{z}_0=(50,40)$의 값을 구한다.")
    P("")
    z = np.array([50.0, 40.0])
    ks = ["A", "B", "C", "D"]
    P("| 앵커 | 지도에서 잰 거리 | 사료 거리 | 어긋남 | 어긋남² |")
    P("|---|---|---|---|---|")
    tot = 0
    for k in ks:
        a = ANC[k]; r = math.hypot(z[0]-a[0], z[1]-a[1]); e = r-DREC[k]; tot += e*e
        P(f"| {k} | {r:.2f} | {DREC[k]:.0f} | {e:+.2f} | {e*e:.2f} |")
    P("")
    P(f"스트레스 $={tot:.2f}$이다. 이제 내려가는 방향을 찾는다. 스트레스를 $\\mathbf{{z}}$로 미분한 기울기(그래디언트)는 $\\nabla=\\sum_k 2w_k(r_k-d_k)\\,(\\mathbf{{z}}-\\mathbf{{a}}_k)/r_k$이고, 기울기의 **반대 방향**으로 조금(보폭 $\\eta=0.1$) 움직인다. 세 번 되풀이한 결과이다.")
    P("")
    P("| 회 | $\\mathbf{z}$ | 스트레스 | 기울기 $\\nabla$ | 다음 $\\mathbf{z}=\\mathbf{z}-0.1\\nabla$ |")
    P("|---|---|---|---|---|")
    for it in range(1, 4):
        g = grad(z, ks); s_ = stress(z, ks); zn = z-0.1*g
        P(f"| {it} | ({z[0]:.2f}, {z[1]:.2f}) | {s_:.2f} | ({g[0]:.1f}, {g[1]:.1f}) | ({zn[0]:.2f}, {zn[1]:.2f}) |")
        z = zn
    P(f"")
    zs, fs = solve(ks)
    P(f"3회 후 스트레스는 {stress(z, ks):.2f}로 처음의 {tot:.2f}에서 크게 줄었다. 컴퓨터로 끝까지 내리면 $\\mathbf{{z}}^*=({zs[0]:.1f},\\ {zs[1]:.1f})$, 스트레스 ${fs:.2f}$에서 멈춘다. 참 위치 $(62,31)$와의 거리는 {math.hypot(zs[0]-62, zs[1]-31):.1f} km이다. 스트레스가 0이 아닌 까닭은 사료의 거리 넷이 서로 정확히 맞지 않기 때문이다. 남은 스트레스가 클수록 증거들 사이의 모순이 크다.")
    P("")
    P("**앵커가 둘뿐이면** 어떻게 되는지 보자. $A$와 $B$의 거리만 쓰면 두 원이 만나는 점이 둘이다. 컴퓨터로 시작점을 위쪽 $(50,40)$과 아래쪽 $(50,-40)$에서 각각 출발시키면 닿는 곳이 다르다.")
    P("")
    za, fa = solve(["A", "B"], z0=(50, 40)); zb, fb = solve(["A", "B"], z0=(50, -40))
    P(f"- 위에서 출발: $({za[0]:.1f},\\ {za[1]:.1f})$, 스트레스 {fa:.4f}")
    P(f"- 아래에서 출발: $({zb[0]:.1f},\\ {zb[1]:.1f})$, 스트레스 {fb:.4f}")
    P("- 두 해의 스트레스가 모두 0에 가깝다. 앵커 둘은 거울상을 구별하지 못한다. 앵커를 셋 이상 쓰고 한 직선에 놓지 않는 이유이다.")
    P("")
    P("### 완전 풀이 예제 2: 잭나이프로 의심스러운 증거 찾기")
    P("")
    P("간선(거리 서술) 네 개 중 하나를 빼고 나머지 셋으로 다시 풀어 전체 해 $\\mathbf{z}^*$에서 얼마나 움직이는지 본다. 먼저 모든 증거가 정상일 때이다.")
    P("")
    P("| 뺀 간선 | 새 위치 | 전체 해에서의 이동 (km) |")
    P("|---|---|---|")
    for k in ks:
        kk = [x for x in ks if x != k]
        zz, _ = solve(kk)
        P(f"| {k} | ({zz[0]:.1f}, {zz[1]:.1f}) | {math.hypot(zz[0]-zs[0], zz[1]-zs[1]):.1f} |")
    P("")
    P("이동이 모두 몇 km 안이면 어느 한 증거에 크게 기대지 않는다는 뜻이다. 이번에는 D의 서술이 필사 오류로 66이 아니라 **110**으로 적혔다고 하자.")
    dd2 = dict(DREC); dd2["D"] = 110.0
    zs2, fs2 = solve(ks, dd2)
    P("")
    P(f"전체 해는 $({zs2[0]:.1f},\\ {zs2[1]:.1f})$, 스트레스 {fs2:.1f}로 참에서 {math.hypot(zs2[0]-62, zs2[1]-31):.1f} km 떨어진다(오류가 없을 때의 스트레스 {fs:.1f}). 잭나이프는 다음과 같다.")
    P("")
    P("| 뺀 간선 | 새 위치 | 이동 (km) | 참과의 거리 (km) | 남은 스트레스 |")
    P("|---|---|---|---|---|")
    res2 = {}
    for k in ks:
        kk = [x for x in ks if x != k]
        zz, ff = solve(kk, dd2)
        res2[k] = (zz, ff, math.hypot(zz[0]-zs2[0], zz[1]-zs2[1]))
        P(f"| {k} | ({zz[0]:.1f}, {zz[1]:.1f}) | {res2[k][2]:.1f} | {math.hypot(zz[0]-62, zz[1]-31):.1f} | {ff:.2f} |")
    kmove = max(res2, key=lambda k: res2[k][2]); kstress = min(res2, key=lambda k: res2[k][1])
    P("")
    P(f"표를 읽는 법이 중요하다. **이동 크기**만 보면 가장 큰 것은 {kmove}를 뺄 때({res2[kmove][2]:.1f} km)이다. 그러나 이것은 그 증거가 틀렸다는 뜻이 아니라, 그 증거를 빼면 나머지 셋의 기하가 불안정해진다는 뜻일 수 있다. 반대로 **남은 스트레스**가 가장 크게 줄어드는 것은 {kstress}를 뺄 때({res2[kstress][1]:.2f})이고 그때 위치는 참에서 {math.hypot(res2[kstress][0][0]-62, res2[kstress][0][1]-31):.1f} km 안으로 돌아온다. 나머지 셋이 서로 잘 맞는데 {kstress} 하나만 어긋난다는 신호이므로 {kstress}가 가장 의심스러운 증거이다. 그래도 이것은 **의심**일 뿐이다. 원문과 대조해 확인하기 전에는 틀렸다고 단정하지 않는다. 또 틀린 증거가 둘 이상이면 하나씩 빼는 방법으로는 찾기 어렵다.")
    P("")
    P("### 완전 풀이 예제 3: 매개중심성을 손으로 세기")
    P("")
    E, nodes, adj, paths = bc_table()
    P("여섯 지명 가, 나, 다, 라, 마, 바의 그물이 있고 간선은 " + ", ".join(f"{a}–{b}" for a, b in E) + "이다. 점 \"나\"의 매개중심성 $B(\\text{나})=\\sum\\sigma_{st}(\\text{나})/\\sigma_{st}$를 모든 쌍 $(s,t)$에 대해 센다(나 자신이 시작이나 끝인 쌍은 제외, 쌍은 순서 없이 한 번씩).")
    P("")
    P("| 쌍 $(s,t)$ | 최단 경로(개수) | 나를 지나는 경로 | 기여 |")
    P("|---|---|---|---|")
    def bc(v):
        tot = 0.0; rows = []
        others = [n for n in nodes if n != v]
        for i, s in enumerate(others):
            for t in others[i+1:]:
                ps = paths(s, t)
                thr = [p for p in ps if v in p[1:-1]]
                rows.append((s, t, ps, thr))
                tot += len(thr)/len(ps)
        return tot, rows
    tn, rows = bc("나")
    for s, t, ps, thr in rows:
        if len(thr) == 0: continue
        P(f"| ({s},{t}) | {len(ps)}개: " + ", ".join("".join(p) for p in ps) + f" | {len(thr)}개 | {len(thr)}/{len(ps)} |")
    P("")
    P(f"나를 지나는 쌍의 기여를 모두 더하면 $B(\\text{{나}})={tn:.2f}$이다. 같은 방법으로 모든 점의 값은 다음과 같다.")
    P("")
    P("| 지명 | " + " | ".join(nodes) + " |")
    P("|---|" + "---|"*len(nodes))
    vals = [bc(n)[0] for n in nodes]
    P("| $B(v)$ | " + " | ".join(f"{v:.2f}" for v in vals) + " |")
    top = nodes[int(np.argmax(vals))]
    P("")
    P(f"가장 큰 값은 \"{top}\"이다. 이 지명의 위치가 틀리면 그 지명을 거치는 많은 서술이 함께 틀어지므로 독립 증거로 먼저 확인할 대상이다. 가운데 다리 역할을 하지 않는 가장자리 지명(여기서는 \"가\"와 \"바\")은 값이 0이다.")

    P("")
    P("### 완전 풀이 예제 4: 구간으로 적힌 서술의 스트레스")
    P("")
    P("사료가 \"5~7\"처럼 구간으로 말하면, 지도 위 거리가 구간 안에 있으면 벌이 0이고 밖으로 벗어난 만큼만 벌을 준다: 벌 $=(\\max(0,\\ \\ell-r,\\ r-u))^2$, 단 $[\\ell,u]$는 사료의 구간, $r$은 지도에서 잰 거리이다. 예제 1의 앵커 네 곳을 그대로 쓰되 거리 서술을 구간으로 바꾼다: $A:[62,76]$, $B:[44,54]$, $C:[46,56]$, $D:[58,72]$ km.")
    P("")
    INT = {"A": (62, 76), "B": (44, 54), "C": (46, 56), "D": (58, 72)}
    def stress_int(z):
        t = 0
        for k in ks:
            a = ANC[k]; r = math.hypot(z[0]-a[0], z[1]-a[1]); lo, hi = INT[k]
            e = max(0.0, lo-r, r-hi); t += e*e
        return t
    P("먼저 두 후보 위치의 스트레스를 비교한다.")
    P("")
    P("| 후보 | A까지 | B까지 | C까지 | D까지 | 스트레스 |")
    P("|---|---|---|---|---|---|")
    for nm, zz in (("(62, 31)", (62, 31)), ("(50, 40)", (50, 40)), ("(75, 20)", (75, 20))):
        cells = []
        for k in ks:
            a = ANC[k]; r = math.hypot(zz[0]-a[0], zz[1]-a[1]); lo, hi = INT[k]
            e = max(0.0, lo-r, r-hi)
            cells.append(f"{r:.1f}" + ("" if e == 0 else f" (벗어남 {e:.1f})"))
        P(f"| {nm} | " + " | ".join(cells) + f" | {stress_int(zz):.2f} |")
    P("")
    xs_ = np.arange(40, 90.1, 1.0); ys_ = np.arange(10, 60.1, 1.0)
    ok = [(x, y) for x in xs_ for y in ys_ if stress_int((x, y)) == 0.0]
    P(f"격자(1 km 간격, 동 40~90, 북 10~60)에서 스트레스가 정확히 0인 점을 세면 {len(ok)}개이다. 넓이로는 약 {len(ok)} km²이다. 점 하나가 아니라 **영역**이 해이고 구간이 좁을수록 영역이 줄어든다. 이 영역은 동쪽으로 {min(p[0] for p in ok):.0f}~{max(p[0] for p in ok):.0f} km, 북쪽으로 {min(p[1] for p in ok):.0f}~{max(p[1] for p in ok):.0f} km의 범위에 놓인다." if ok else "격자에서 스트레스 0인 점이 없다. 구간들이 서로 모순되는 것이다.")
    P("")
    P("점 방식의 해(예제 1)가 한 점이었던 것과 달리 구간 방식은 해의 모양으로 불확실성을 보여 준다. 구간을 만들 때의 폭 선택(여기서는 각각 7~15% 안팎)이 곧 영역의 크기를 정하므로 그 근거를 DB에 적어야 한다.")
    return "\n".join(out)

if __name__ == "__main__":
    print(md())
