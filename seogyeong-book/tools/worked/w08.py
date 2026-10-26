"""8장 완전 풀이 예제: 하이킹 함수, 칸 비용, 데이크스트라, 이동시간 우도. 가상 지형(7x7, 칸 5 km)."""
import numpy as np, math, heapq

CELL = 3.0
def elev():
    E = np.zeros((7, 7))
    for j in range(7):
        for i in range(7):
            ridge = 1600*math.exp(-((i-3.0)/0.8)**2)*(1-0.82*math.exp(-((j-5.0)/0.8)**2))
            E[j, i] = round((60+ridge+8*j)/10)*10
    return E
def vel(S):
    return 6*math.exp(-3.5*abs(S+0.05))

def md():
    E = elev()
    out = []; P = out.append
    P("### 완전 풀이 예제 1: 경사에서 시간까지")
    P("")
    P("가상의 지형 $7\\times7$칸(한 칸 3 km)의 고도(m)가 다음과 같다. 행은 북(위)에서 남(아래) 순이고 열은 서(왼쪽)에서 동 순이다. 가운데 열(3열)을 따라 남북으로 높은 산줄기가 뻗어 있고, 남쪽 5행 부근만 고개(안부)로 낮아진다.")
    P("")
    P("| 행＼열 | 0 | 1 | 2 | 3 | 4 | 5 | 6 |")
    P("|---|---|---|---|---|---|---|---|")
    for j in range(7):
        P(f"| {j} | " + " | ".join(f"{int(E[j,i])}" for i in range(7)) + " |")
    P("")
    P("출발점은 서쪽 가장자리의 $(0,3)$ 칸(열 0, 행 3), 고도 " + f"{int(E[3,0])} m" + "이다.")
    P("")
    P("**1단계: 두 칸 사이의 경사.** $S=\\Delta h/(\\text{수평 거리})$. 상하좌우 이웃은 거리 3 km, 대각선 이웃은 $3\\sqrt2=4.24$ km이다. 몇 개의 간선을 계산해 본다.")
    P("")
    P("| 간선 | $\\Delta h$ (m) | 거리 (km) | $S$ | $v(S)$ (km/h) | 시간 (h) |")
    P("|---|---|---|---|---|---|")
    def edge(a, b):
        (i1, j1), (i2, j2) = a, b
        dh = E[j2, i2]-E[j1, i1]
        dist = CELL*math.hypot(i2-i1, j2-j1)
        S = dh/(dist*1000)
        v = vel(S)
        return dh, dist, S, v, dist/v
    for a, b in [((0, 3), (1, 3)), ((1, 3), (0, 3)), ((2, 3), (3, 3)), ((3, 3), (2, 3)), ((2, 3), (3, 2)), ((3, 3), (4, 3))]:
        dh, dist, S, v, t = edge(a, b)
        P(f"| ({a[0]},{a[1]})→({b[0]},{b[1]}) | {dh:+.0f} | {dist:.2f} | {S:+.4f} | {v:.2f} | {t:.3f} |")
    P("")
    P("고도 차 $\\Delta h$는 m이고 거리는 km이므로 $S=\\Delta h/(\\text{거리}\\times1000)$이다. 가는 방향과 오는 방향에서 $S$의 부호가 반대이므로 시간이 다르다(위 표의 첫 두 줄).")
    P("")
    # example detailed
    dh, dist, S, v, t = edge((2, 3), (3, 3))
    P(f"**2단계: 한 간선의 계산을 끝까지 따라가기.** $(2,3)\\to(3,3)$: $\\Delta h={dh:+.0f}$ m이므로 $S={dh:+.0f}/(3\\times1000)={S:+.4f}$. 이를 $v(S)=6\\exp(-3.5|S+0.05|)$에 넣으면 $|S+0.05|=|{S+0.05:+.4f}|={abs(S+0.05):.4f}$, 지수 $=-3.5\\times{abs(S+0.05):.4f}={-3.5*abs(S+0.05):.4f}$, $e^{{{-3.5*abs(S+0.05):.4f}}}={math.exp(-3.5*abs(S+0.05)):.4f}$, $v=6\\times{math.exp(-3.5*abs(S+0.05)):.4f}={v:.2f}$ km/h이다. 시간은 $3/{v:.2f}={t:.3f}$ h이다.")
    P("")
    # Dijkstra
    start = (0, 3)
    T = {start: 0.0}; prev = {}; done = set(); pq = [(0.0, start)]
    order = []
    while pq:
        d, u = heapq.heappop(pq)
        if u in done: continue
        done.add(u); order.append((u, d))
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di == 0 and dj == 0: continue
                w = (u[0]+di, u[1]+dj)
                if not (0 <= w[0] < 7 and 0 <= w[1] < 7): continue
                t_ = d+edge(u, w)[4]
                if t_ < T.get(w, 1e9):
                    T[w] = t_; prev[w] = u; heapq.heappush(pq, (t_, w))
    P("### 완전 풀이 예제 2: 데이크스트라로 최소 시간 지도 만들기")
    P("")
    P("출발점에서 가까운(시간이 적게 걸리는) 칸부터 차례로 \"확정\"한다. 확정할 때마다 이웃 칸의 후보 시간을 $T_{\\text{확정}}+\\text{간선 시간}$으로 갱신하되 더 작을 때만 바꾼다. 처음 여덟 번의 확정 과정은 다음과 같다.")
    P("")
    P("| 순서 | 확정된 칸 | 최소 시간 (h) | 직전 칸(길을 거슬러 올라가는 표시) |")
    P("|---|---|---|---|")
    for k, (u, d) in enumerate(order[:8], 1):
        pv = prev.get(u)
        P(f"| {k} | ({u[0]},{u[1]}) | {d:.3f} | " + (f"({pv[0]},{pv[1]})" if pv else "출발") + " |")
    P("")
    P("49칸 모두를 확정하면 최소 시간 지도 $T$가 완성된다(시간, h).")
    P("")
    P("| 행＼열 | 0 | 1 | 2 | 3 | 4 | 5 | 6 |")
    P("|---|---|---|---|---|---|---|---|")
    for j in range(7):
        P(f"| {j} | " + " | ".join(f"{T[(i,j)]:.1f}" for i in range(7)) + " |")
    P("")
    # path to (6,3)
    tgt = (6, 3)
    path = [tgt]
    while path[-1] != start:
        path.append(prev[path[-1]])
    path.reverse()
    P("**길 거슬러 올라가기.** 동쪽 가장자리 $(6,3)$까지의 길은 \"직전 칸\"을 거꾸로 따라가면 얻는다: " + " → ".join(f"({a},{b})" for a, b in path) + f". 총 {T[tgt]:.2f}시간이다. 고도표와 대조하면 길이 산줄기를 곧장 넘지 않고 남쪽의 낮은 고개(5행 부근)로 돌아가는지 볼 수 있다.")
    straight = sum(edge((i, 3), (i+1, 3))[4] for i in range(6))
    P(f"비교: 행 3을 곧장 가로지르는 길(직선 18 km)의 시간은 {straight:.2f}시간이다. 최소 시간 길은 이보다 {straight-T[tgt]:.2f}시간 짧다. 지형이 길을 휘게 만든다는 것은 이렇게 숫자로 확인된다.")
    P("")
    # likelihood
    P("### 완전 풀이 예제 3: \"반나절 길\"을 우도로 바꾸기")
    P("")
    P("사료에 \"출발 지명에서 반나절 길\"이라고 적혀 있고 반나절을 4시간으로 읽는다고 하자(구간 3~5시간으로 두는 변형도 아래에서 본다). 관측값 $T_{\\text{obs}}=4$시간, $\\sigma_T=0.15$이다. 칸마다 $z=\\ln(4/T)/0.15$, 상대 우도 $=\\exp(-z^2/2)$를 구한다.")
    P("")
    def rel(Tv, obs=4.0, sg=0.15):
        if Tv <= 0: return 0.0
        z = math.log(obs/Tv)/sg
        return math.exp(-0.5*z*z)
    P("| 행＼열 | 0 | 1 | 2 | 3 | 4 | 5 | 6 |")
    P("|---|---|---|---|---|---|---|---|")
    for j in range(7):
        P(f"| {j} | " + " | ".join(f"{rel(T[(i,j)]):.2f}" for i in range(7)) + " |")
    P("")
    best = max(T, key=lambda c: rel(T[c]))
    hi = [c for c in T if rel(T[c]) >= 0.5]
    P(f"상대 우도가 0.5 이상인 칸은 {len(hi)}개이다. 이 칸들이 출발점에서 이동시간이 대략 4시간인 \"등시선\" 띠를 이룬다. 산줄기를 넘는 쪽에서는 같은 직선 거리라도 시간이 더 걸리므로 띠가 출발점 가까이로 오그라든다.")
    P("")
    P("**반나절을 3~5시간 구간으로 두면** 관측값 $T_{\\text{obs}}$를 3, 4, 5로 바꿔 세 번 계산하고 결과를 비교한다. 아래는 각 경우에 상대 우도 0.5 이상인 칸의 수이다.")
    P("")
    P("| $T_{obs}$ (h) | 0.5 이상인 칸 수 | 가장 우도가 높은 칸 |")
    P("|---|---|---|")
    for ob in (3.0, 4.0, 5.0):
        c = [k for k in T if rel(T[k], ob) >= 0.5]
        bb = max(T, key=lambda k: rel(T[k], ob))
        P(f"| {ob:.0f} | {len(c)} | ({bb[0]},{bb[1]}) |")
    P("")
    P("관측값을 바꾸면 띠가 안팎으로 이동한다. 반나절의 걷는 시간이 불확실한 만큼 이 띠도 불확실하다. 그래서 결과를 하나의 값이 아니라 구간으로 비교하라고 한 것이다.")
    # grid bias
    P("")
    P("### 완전 풀이 예제 4: 격자 크기를 바꾸면 결과가 얼마나 달라지는가")
    P("")
    P("위 $7\\times7$ 고도표의 위쪽 $6\\times6$ 칸만 떼어 $2\\times2$씩 평균하면 $3\\times3$ 격자(한 칸 6 km)가 된다. 산줄기의 봉우리가 평균에 섞여 낮아지고 비탈이 완만해진다.")
    P("")
    E6 = E[:6, :6]; Ec = E6.reshape(3, 2, 3, 2).mean(axis=(1, 3))
    P(f"- 최고 고도: 원래 {int(E6.max())} m → 평균 후 {int(round(Ec.max()))} m.")
    def mean_speed(Eg, cell, st, tg):
        n = Eg.shape[0]
        def ed(a, b):
            (i1, j1), (i2, j2) = a, b
            dh = Eg[j2, i2]-Eg[j1, i1]; dist = cell*math.hypot(i2-i1, j2-j1)
            S = dh/(dist*1000); return dist/vel(S)
        Tm = {st: 0.0}; pq = [(0.0, st)]; dn = set()
        while pq:
            d, u = heapq.heappop(pq)
            if u in dn: continue
            dn.add(u)
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if di == 0 and dj == 0: continue
                    w = (u[0]+di, u[1]+dj)
                    if not (0 <= w[0] < n and 0 <= w[1] < n): continue
                    t_ = d+ed(u, w)
                    if t_ < Tm.get(w, 1e9): Tm[w] = t_; heapq.heappush(pq, (t_, w))
        dist = cell*math.hypot(tg[0]-st[0], tg[1]-st[1])
        return Tm[tg], dist
    tf_, df_ = mean_speed(E6, 3.0, (0, 3), (5, 3)); tc_, dc_ = mean_speed(Ec, 6.0, (0, 1), (2, 1))
    P(f"- 서쪽 가장자리 중간 칸에서 산줄기를 넘어 동쪽 가장자리 칸까지의 최소 시간, 직선 거리, 평균 속도(거리÷시간): 원래 격자 {tf_:.2f} h, {df_:.1f} km, **{df_/tf_:.2f} km/h**. 거친 격자 {tc_:.2f} h, {dc_:.1f} km, **{dc_/tc_:.2f} km/h**.")
    P("- 두 격자의 칸 중심이 정확히 같은 점이 아니므로 시간 자체보다 평균 속도로 견준다. 거친 쪽의 평균 속도가 " + ("더 빠르면" if dc_/tc_ > df_/tf_ else "비슷하거나 느리면") + " 평균에 의한 편향이 " + ("보이는 것이다." if dc_/tc_ > df_/tf_ else "이번 예에서는 뚜렷하지 않은 것이다.") + " 이 편향의 크기는 지형마다 다르므로 서경 적용에서는 격자 크기를 바꿔 같은 계산을 되풀이하고 결과의 차이를 보고한다.")

    P("")
    P("### 완전 풀이 예제 5: 하이킹 함수 표와 왕복 시간")
    P("")
    P("경사별 속도와 10 km를 가는 시간을 표로 만들면 하이킹 함수의 성격이 한눈에 보인다. 오르막과 내리막의 시간이 어떻게 다른지, 왕복하면 얼마나 걸리는지도 함께 본다.")
    P("")
    P("| 경사 $S$ | 각도 (도) | 속도 $v$ (km/h) | 10 km 가는 시간 (h) |")
    P("|---|---|---|---|")
    for Sv in (-0.30, -0.20, -0.10, -0.05, 0.0, 0.05, 0.10, 0.20, 0.30):
        P(f"| {Sv:+.2f} | {math.degrees(math.atan(Sv)):+.1f} | {vel(Sv):.2f} | {10/vel(Sv):.2f} |")
    P("")
    P("**왕복 계산.** 평균 경사 $S=+0.10$인 10 km 길을 올라갔다가 같은 길로 내려온다고 하자. 올라갈 때 $S=+0.10$이므로 $v={:.2f}$ km/h, 시간 ${:.2f}$ h. 내려올 때 $S=-0.10$이므로 $v={:.2f}$ km/h, 시간 ${:.2f}$ h. 왕복 {:.2f} h이다. 평지로 20 km를 가는 시간 {:.2f} h({:.2f} km/h)보다 {:.2f} h 더 걸린다. 오르막이 느려진 만큼을 내리막이 다 되찾아 주지는 못한다는 뜻이다.".format(vel(0.10), 10/vel(0.10), vel(-0.10), 10/vel(-0.10), 10/vel(0.10)+10/vel(-0.10), 20/vel(0.0), vel(0.0), 10/vel(0.10)+10/vel(-0.10)-20/vel(0.0)))
    P("")
    P("**최고 속도가 $S=-0.05$에서 나오는 이유.** $|S+0.05|$가 0이 되는 경사, 곧 약 $-2.9^\\circ$의 완만한 내리막에서 가장 빠르고, 그보다 가파른 내리막에서는 다시 느려지는 것이 이 함수의 모양이다. 우리는 이 모양이 옛사람에게도 맞는지 모른다. 그러므로 서경 적용에서는 계수를 바꾼 대안(예: 최고 속도 5 km/h, 민감도 3.0)도 함께 계산해 결과가 얼마나 달라지는지 비교한다. 이 대안 하나만 바꾸어도 위 표의 모든 숫자가 움직인다.")
    return "\n".join(out)

if __name__ == "__main__":
    print(md())
