"""7장 완전 풀이 예제: 격자 베이즈. 가상 세계(5장과 같은 기준점 3개)."""
import numpy as np, math

A, B, C = (0, 0), (300, 0), (150, 300)
REFS = [("A", A), ("B", B), ("C", C)]
LOBS = [510, 570, 310]
SIG = 0.10
US = [0.36, 0.42, 0.48]
XS = [90, 110, 130, 150, 170]
YS = [130, 150, 170, 190, 210]
WIDE = 1/math.log(2000/50)   # 로그 눈금 위의 평평한 분포 밀도

def nd(z, sig):
    return math.exp(-0.5*(z/sig)**2)/(sig*math.sqrt(2*math.pi))

def lik_u(x, y, u, ks=(0, 1, 2), eps=0.0, Ls=None):
    Ls = Ls or LOBS
    v = 1.0
    for k in ks:
        r = REFS[k][1]; d = math.hypot(x-r[0], y-r[1])
        z = math.log(Ls[k]) - math.log(d/u)
        f = nd(z, SIG)
        if eps:
            f = (1-eps)*f + eps*WIDE
        v *= f
    return v

def lik(x, y, **kw):
    return sum(lik_u(x, y, u, **kw) for u in US)/len(US)

def md():
    out = []; P = out.append
    P("### 완전 풀이 예제 1: 한 칸의 우도를 끝까지 계산하기")
    P("")
    P(f"5장의 가상 세계를 그대로 쓴다(기준 $A=(0,0)$, $B=(300,0)$, $C=(150,300)$ km, 사료 수치 510리, 570리, 310리). 이번에는 구간 대신 확률로 계산한다. 오차의 표준편차는 $\\sigma={SIG:.2f}$(로그 눈금)로 두고, 단위 $u$는 $0.36,\\ 0.42,\\ 0.48$ km/리 세 값을 각각 확률 $1/3$로 둔다. 후보 칸 하나, $\\mathbf{{p}}=(130,170)$을 먼저 계산한다.")
    P("")
    x, y = 130, 170
    P("**1단계: 칸에서 기준까지의 실제 거리.** $d_k=\\sqrt{(x-x_k)^2+(y-y_k)^2}$이다.")
    P("")
    ds = []
    for nm, r in REFS:
        d = math.hypot(x-r[0], y-r[1]); ds.append(d)
        P(f"- $d_{nm}=\\sqrt{{({x}-{r[0]})^2+({y}-{r[1]})^2}}=\\sqrt{{{(x-r[0])**2}+{(y-r[1])**2}}}={d:.1f}$ km")
    P("")
    P("**2단계: $u$가 하나로 정해졌다고 보고 증거마다 점수를 매긴다.** 로그 눈금에서 $z_k=\\ln L_k-\\ln(d_k/u)$를 구하고 정규 밀도 $f(z)=\\dfrac{1}{\\sigma\\sqrt{2\\pi}}e^{-z^2/(2\\sigma^2)}$에 넣는다. $\\sigma=0.10$이므로 $\\sigma\\sqrt{2\\pi}=0.2507$이다. $f(z)$는 확률이 아니라 **밀도**라서 1보다 클 수 있다. 칸끼리 비교할 때는 크기의 비만 쓰므로 문제가 없다.")
    P("")
    P("| $u$ | 증거 | $d/u$ (리) | $z$ | $f(z)$ |")
    P("|---|---|---|---|---|")
    prods = []
    for u in US:
        pr = 1.0
        for k, (nm, r) in enumerate(REFS):
            d = ds[k]; z = math.log(LOBS[k])-math.log(d/u); f = nd(z, SIG); pr *= f
            P(f"| {u} | {nm} ({LOBS[k]}리) | {d/u:.1f} | {z:+.3f} | {f:.3f} |")
        prods.append(pr)
    P("")
    P("**3단계: 같은 $u$로 세 증거를 먼저 곱한다.** (곱이 적분 안쪽)")
    P("")
    for u, pr in zip(US, prods):
        P(f"- $u={u}$: 곱 $={pr:.4f}$")
    avg = sum(prods)/3
    P("")
    P(f"**4단계: $u$에 대해 평균한다.** $({' + '.join(f'{p:.4f}' for p in prods)})/3={avg:.4f}$. 이 값이 이 칸의 우도 $P(D\\mid\\mathbf{{p}})$이다. $u=0.42$ 근처에서 곱이 가장 크다는 점에 주목하자. 참 단위가 $0.42$였으므로 방법이 그 값을 알아본 것이다.")
    # wrong way: separate integrals
    sep = 1.0
    for k in range(3):
        s_ = 0
        for u in US:
            r = REFS[k][1]; d = ds[k]; z = math.log(LOBS[k])-math.log(d/u); s_ += nd(z, SIG)
        sep *= s_/3
    P("")
    P(f"- 비교: 증거마다 $u$를 따로 평균하는 잘못된 방법은 $\\prod_k(\\text{{평균}})={sep:.4f}$이다. 올바른 값 {avg:.4f}의 {sep/avg*100:.0f}%이다. 두 증거가 같은 $u$를 요구한다는 정보를 잃기 때문이다.")
    P("")
    P("### 완전 풀이 예제 2: 격자 전체의 사후확률")
    P("")
    P("같은 계산을 $5\\times5=25$개 칸(간격 20 km)에 되풀이한다. 사전분포는 균등(칸마다 $1/25$)이므로 사후는 우도의 비율이다. 첫 표는 우도에 1000을 곱해 적은 값이고(칸끼리의 상대 크기만 의미가 있다), 둘째 표는 이를 정규화한 사후확률(%)이다.")
    L = np.array([[lik(xx, yy) for xx in XS] for yy in YS])
    post = L/L.sum()
    P("")
    P("| 북 \\ 동 (km) | " + " | ".join(str(xx) for xx in XS) + " |")
    P("|---|" + "---|"*len(XS))
    for j in range(len(YS)-1, -1, -1):
        P(f"| **{YS[j]}** | " + " | ".join(f"{L[j,i]*1000:.2f}" for i in range(len(XS))) + " |")
    P("")
    P(f"25칸의 합은 {L.sum()*1000:,.0f}이다. 정규화는 각 칸의 값을 이 합으로 나누는 것이다. 예를 들어 (130,170) 칸은 {L[2,2]*1000:,.0f}/{L.sum()*1000:,.0f}$={L[2,2]/L.sum()*100:.1f}\\%$이다.")
    P("")
    P("| 북 \\ 동 (km) | " + " | ".join(str(xx) for xx in XS) + " |")
    P("|---|" + "---|"*len(XS))
    for j in range(len(YS)-1, -1, -1):
        P(f"| **{YS[j]}** | " + " | ".join(f"{post[j,i]*100:.1f}" for i in range(len(XS))) + " |")
    P("")
    jm, im = np.unravel_index(np.argmax(post), post.shape)
    P(f"- **MAP**: 사후확률이 가장 큰 칸은 $({XS[im]},{YS[jm]})$, 확률 {post[jm,im]*100:.1f}%이다.")
    px = sum(post[j, i]*XS[i] for j in range(5) for i in range(5)); py = sum(post[j, i]*YS[j] for j in range(5) for i in range(5))
    P(f"- **사후 평균**: $\\bar x=\\sum P\\cdot x={px:.1f}$, $\\bar y=\\sum P\\cdot y={py:.1f}$ km. 평균은 칸의 중심이 아니어도 된다.")
    order = np.argsort(-post.ravel()); cum = 0; hpd = []
    for idx in order:
        hpd.append(idx); cum += post.ravel()[idx]
        if cum >= 0.90: break
    P(f"- **90% HPD**: 확률이 큰 칸부터 담으면 {len(hpd)}개 칸에서 합이 {cum*100:.1f}%가 되어 90%를 넘는다. 넓이는 {len(hpd)}칸 × 400 km² $={len(hpd)*400}$ km²이다.")
    hpd50 = []; cum = 0
    for idx in order:
        hpd50.append(idx); cum += post.ravel()[idx]
        if cum >= 0.50: break
    P(f"- 50% HPD는 {len(hpd50)}칸이다. 같은 자료로 \"가운데 절반\"과 \"거의 전부\"의 넓이가 이렇게 다르다.")
    P("")
    P("### 완전 풀이 예제 3: 틀린 증거를 섞어 보기(혼합 우도)")
    P("")
    bad = [510, 570, 310]
    P("네 번째 기준 $D=(300,300)$을 더하고 사료에 \"180리\"라고 적혀 있다고 하자(참 거리는 약 214 km로 510리쯤이어야 한다). 이 서술은 필사 오류이다.")
    global REFS_BAK
    REFS.append(("D", (300, 300)))
    Ls4 = [510, 570, 310, 180]
    ks = (0, 1, 2, 3)
    Lp = np.array([[lik(xx, yy, ks=ks, Ls=Ls4) for xx in XS] for yy in YS])
    Lm = np.array([[lik(xx, yy, ks=ks, Ls=Ls4, eps=0.1) for xx in XS] for yy in YS])
    pp = Lp/Lp.sum(); pm = Lm/Lm.sum()
    jt, it = 2, 2
    P("")
    P(f"- 순진한 우도($\\varepsilon=0$): 참 위치 칸(130,170)의 우도 {Lp[jt,it]:.3e}, 사후확률 {pp[jt,it]*100:.2f}%. 가장 높은 칸은 {XS[np.unravel_index(np.argmax(pp),pp.shape)[1]]},{YS[np.unravel_index(np.argmax(pp),pp.shape)[0]]}로 참에서 {math.hypot(XS[np.unravel_index(np.argmax(pp),pp.shape)[1]]-130, YS[np.unravel_index(np.argmax(pp),pp.shape)[0]]-170):.0f} km 떨어져 있다.")
    P(f"- 혼합 우도($\\varepsilon=0.1$, 평평한 분포 밀도 ${WIDE:.3f}$): 참 위치 칸 우도 {Lm[jt,it]:.3e}, 사후확률 {pm[jt,it]*100:.2f}%. 가장 높은 칸은 {XS[np.unravel_index(np.argmax(pm),pm.shape)[1]]},{YS[np.unravel_index(np.argmax(pm),pm.shape)[0]]}이다.")
    P(f"- 두 방법의 참 위치 우도 비는 약 {Lm[jt,it]/Lp[jt,it]:.1e}배이다. 틀린 증거 하나가 곱셈 때문에 참 위치를 사실상 지워 버렸다가 혼합 우도로 되살아난 것이다.")
    z4 = math.log(180)-math.log(math.hypot(130-300, 170-300)/0.42)
    P(f"- 이유: 참 위치에서 네 번째 증거의 $z=\\ln180-\\ln(214.0/0.42)={z4:.2f}$로 $\\sigma=0.10$의 {abs(z4)/SIG:.0f}배 떨어져 정규 밀도가 거의 0이다. 혼합 우도는 이때 $0.1\\times{WIDE:.3f}={0.1*WIDE:.4f}$라는 바닥을 깔아 준다. 나머지 세 증거는 그대로이다.")
    REFS.pop()
    P("")
    P("### 완전 풀이 예제 4: 메트로폴리스로 사후분포 걷기")
    P("")
    P("격자를 다 계산할 수 없을 만큼 칸이 많을 때 쓰는 방법이다. 위의 25칸 사후(예제 2)를 \"비례값\" $\\pi$로 쓰고 8걸음을 걸어 보자. 규칙은 (1) 상하좌우 이웃 중 하나를 제안, (2) $\\pi_{new}/\\pi_{old}$가 1 이상이면 이동, (3) 아니면 그 비율을 확률로 이동, 이다. 난수는 미리 정한 값을 쓴다.")
    P("")
    rng = np.random.default_rng(7)
    pos = [0, 0]  # index (i,j) start at corner (90,130)
    P("| 걸음 | 현재 칸 | 제안 칸 | $\\pi_{old}$ | $\\pi_{new}$ | 비율 | 난수 | 이동? |")
    P("|---|---|---|---|---|---|---|---|")
    Lg = L/L.max()
    cur = (0, 0)
    for st in range(1, 9):
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        dx, dy = dirs[rng.integers(0, 4)]
        nx, ny = cur[0]+dx, cur[1]+dy
        if not (0 <= nx < 5 and 0 <= ny < 5):
            P(f"| {st} | ({XS[cur[0]]},{YS[cur[1]]}) | 격자 밖 | | | | | 제자리 |")
            continue
        po, pn = Lg[cur[1], cur[0]], Lg[ny, nx]
        r = pn/po; u_ = rng.random()
        mv = (r >= 1) or (u_ < r)
        P(f"| {st} | ({XS[cur[0]]},{YS[cur[1]]}) | ({XS[nx]},{YS[ny]}) | {po:.4f} | {pn:.4f} | {r:.3f} | {u_:.2f} | {'예' if mv else '아니오'} |")
        if mv:
            cur = (nx, ny)
    P("")
    P("비례값 $\\pi$는 최대 우도를 1로 맞춘 값이다. 처음에는 우도가 낮은 모서리에서 출발하므로 곧바로 높은 칸으로 올라가고, 높은 곳에서는 낮은 이웃으로의 제안을 대부분 거절한다. 오래 걸을수록 각 칸에 머문 횟수의 비율이 사후확률에 가까워진다. 8걸음은 설명용이고 실제로는 수만 걸음 이상 걷고 앞부분(번인)을 버린다.")

    P("")
    P("### 완전 풀이 예제 5: 사전분포를 바꾸면 결과가 얼마나 움직이는가")
    P("")
    P("예제 2에서는 모든 칸의 사전확률을 같게(균등) 두었다. 이번에는 어떤 학설이 \"서경은 동쪽(동 150 km 이상)에 있었다\"고 주장한다고 하자. 이 학설을 사전으로 옮기는 두 가지 방법을 비교한다. (가) 동쪽 칸에 3배의 가중, (나) 동쪽 칸에 10배의 가중이다. 사후 $\\propto$ 우도 $\\times$ 사전이므로 각 칸의 우도에 가중을 곱하고 다시 정규화하면 된다.")
    P("")
    def post_with(wf):
        pr = np.array([[wf if XS[i] >= 150 else 1.0 for i in range(5)] for j in range(5)])
        q_ = L*pr
        return q_/q_.sum()
    rows = [("균등(1배)", post_with(1.0)), ("동쪽 3배", post_with(3.0)), ("동쪽 10배", post_with(10.0))]
    P("| 사전 | MAP 칸 | MAP 확률(%) | 동쪽(동 150 이상) 칸의 사후확률 합(%) | 사후 평균 동 (km) |")
    P("|---|---|---|---|---|")
    for nm, pq in rows:
        jm_, im_ = np.unravel_index(np.argmax(pq), pq.shape)
        east = sum(pq[j, i] for j in range(5) for i in range(5) if XS[i] >= 150)
        mx = sum(pq[j, i]*XS[i] for j in range(5) for i in range(5))
        P(f"| {nm} | ({XS[im_]},{YS[jm_]}) | {pq[jm_,im_]*100:.1f} | {east*100:.1f} | {mx:.1f} |")
    P("")
    P("사전의 동쪽 가중을 올릴수록 동쪽 칸의 사후확률 합과 사후 평균의 동쪽 위치가 함께 올라간다. 증거(우도) 자체는 하나도 바뀌지 않았다. 학설이 결과를 움직인 만큼은 \"증거가 말한 것\"이 아니라 \"학설이 넣은 것\"이므로, 이 책에서는 사전을 바꿀 때마다 결과를 따로 표시한다. 균등 사전의 결과와 나란히 놓는 것이 정직한 보고이다.")
    P("")
    P("### 완전 풀이 예제 6: 단위 $u$ 자체에 대한 사후분포")
    P("")
    P("예제 1에서 한 칸의 우도는 $u$별로 따로 계산한 뒤 평균했다. 같은 계산을 25칸 모두에서 하고 $u$별로 합하면 \"증거가 $u$에 대해 말하는 것\"을 얻는다. $P(u\\mid D)\\propto p(u)\\sum_{\\mathbf{p}}P(D\\mid\\mathbf{p},u)\\,P(\\mathbf{p})$이다.")
    P("")
    tot_u = []
    for u in US:
        tot_u.append(sum(lik_u(xx, yy, u) for xx in XS for yy in YS))
    tu = np.array(tot_u)/sum(tot_u)
    P("| $u$ (km/리) | 25칸 합 (1000배) | 사후확률(%) |")
    P("|---|---|---|")
    for u, a, b in zip(US, tot_u, tu):
        P(f"| {u} | {a*1000:,.0f} | {b*100:.1f} |")
    P("")
    P(f"단위의 사후확률이 {US[int(np.argmax(tu))]}에서 가장 높고({tu.max()*100:.0f}%) 사전의 $1/3$씩에서 크게 움직였다. 서술 세 개가 서로 맞는 단위를 골라 준 것이다. 이처럼 7장의 방법은 위치만이 아니라 단위의 값도 함께 추정한다. 사료에서 단위를 독립적으로 알 수 없을 때 이 결과를 책의 단위 해석(리의 길이)에 대한 증거로 쓸 수 있다. 단, 이는 세 서술이 같은 단위로 적혔다는 가정 아래의 이야기이다.")
    return "\n".join(out)

if __name__ == "__main__":
    print(md())
