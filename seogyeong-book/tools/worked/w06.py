"""6장 완전 풀이 예제: 닮음변환 최소제곱, 아핀, 하나 빼고 맞추기 RMSE, 부트스트랩. 가상 통제점."""
import numpy as np, math

def fm(v, n=2):
    return f"{v:.{n}f}"

def md():
    # 옛 지도 좌표(cm 단위 임의), 현대 좌표(km). 가상: 참 변환은 s=40 km/cm, 회전 12도, 이동(100,50), 통제점 위치 오차 포함
    p = np.array([[2.0, 1.0], [8.0, 2.0], [7.0, 7.0], [1.5, 6.0], [4.5, 4.0]])
    rng = np.random.default_rng(6)
    th0 = math.radians(12); R0 = np.array([[math.cos(th0), -math.sin(th0)], [math.sin(th0), math.cos(th0)]])
    q_true = 40*(p@R0.T)+np.array([100, 50])
    noise = np.array([[2.0, -1.5], [-1.0, 2.5], [1.5, 1.0], [-2.5, -1.0], [1.0, -2.0]])
    q = np.round(q_true+noise, 1)
    n = len(p)
    out = []; P = out.append
    P("### 완전 풀이 예제 1: 닮음변환을 손으로 구하기")
    P("")
    P("가상의 옛 지도에서 통제점 5개를 잡았다. 옛 지도의 좌표 $\\mathbf{p}_i$는 cm이고, 현대 좌표 $\\mathbf{q}_i$는 km이다. 서경의 값이 아니라 계산 과정을 보이기 위한 숫자이다.")
    P("")
    P("| 번호 $i$ | 옛 지도 $\\mathbf{p}_i$ (cm) | 현대 $\\mathbf{q}_i$ (km) |")
    P("|---|---|---|")
    for i in range(n):
        P(f"| {i+1} | ({p[i,0]:.1f}, {p[i,1]:.1f}) | ({q[i,0]:.1f}, {q[i,1]:.1f}) |")
    P("")
    pc, qc = p.mean(0), q.mean(0)
    P("**1단계: 무게중심을 맞춘다.** 닮음변환은 \"돌리고, 키우고, 밀기\"이다. 밀기는 마지막에 정하면 되므로, 먼저 두 점 묶음의 평균(무게중심)을 원점으로 옮긴다.")
    P("")
    P(f"- 옛 지도의 평균: $\\bar{{\\mathbf{{p}}}}=(\\,({'+'.join(f'{v:.1f}' for v in p[:,0])})/5,\\ ({'+'.join(f'{v:.1f}' for v in p[:,1])})/5\\,)=({pc[0]:.2f},\\ {pc[1]:.2f})$")
    P(f"- 현대의 평균: $\\bar{{\\mathbf{{q}}}}=({qc[0]:.2f},\\ {qc[1]:.2f})$")
    P("")
    pd_, qd_ = p-pc, q-qc
    P("평균을 뺀 좌표(편차)는 다음과 같다.")
    P("")
    P("| $i$ | $\\mathbf{p}_i-\\bar{\\mathbf{p}}$ | $\\mathbf{q}_i-\\bar{\\mathbf{q}}$ |")
    P("|---|---|---|")
    for i in range(n):
        P(f"| {i+1} | ({pd_[i,0]:.2f}, {pd_[i,1]:.2f}) | ({qd_[i,0]:.2f}, {qd_[i,1]:.2f}) |")
    P("")
    # complex closed form
    zp = pd_[:, 0]+1j*pd_[:, 1]; zq = qd_[:, 0]+1j*qd_[:, 1]
    num = np.sum(np.conj(zp)*zq); den = np.sum(np.abs(zp)**2)
    c = num/den
    s = abs(c); th = math.degrees(math.atan2(c.imag, c.real))
    P("**2단계: 배율과 회전각을 한꺼번에 구한다.** 평면의 점을 복소수 $z=x+iy$로 적으면 \"돌리고 키우기\"는 복소수 $c=s\\,e^{i\\theta}$ 하나를 곱하는 일이 된다. 오차 제곱합을 가장 작게 하는 $c$는 다음 식으로 닫힌 형태로 구해진다.")
    P("")
    P("$$c=\\frac{\\sum_i \\overline{z_{p,i}}\\,z_{q,i}}{\\sum_i |z_{p,i}|^2}$$")
    P("")
    P("위 줄은 \"옛 좌표 편차의 켤레복소수에 현대 편차를 곱해 모두 더한 값\"을 \"옛 좌표 편차의 크기 제곱의 합\"으로 나눈다는 뜻이다. 켤레복소수는 허수부의 부호만 바꾼 수이다(예: $\\overline{3+2i}=3-2i$).")
    P("")
    P(f"- 분모: $\\sum|z_p|^2=$ " + " + ".join(f"{abs(z)**2:.2f}" for z in zp) + f" $={den:.2f}$")
    P(f"- 분자: 실수부 ${num.real:.2f}$, 허수부 ${num.imag:.2f}$ (각 항은 $\\overline{{z_p}}z_q$의 합)")
    P(f"- $c=({num.real:.2f}+{num.imag:.2f}i)/{den:.2f}={c.real:.3f}+{c.imag:.3f}i$")
    P(f"- 배율 $s=|c|=\\sqrt{{{c.real:.3f}^2+{c.imag:.3f}^2}}={s:.3f}$ km/cm. 곧 옛 지도 1 cm가 현실의 약 {s:.1f} km에 해당한다.")
    P(f"- 회전각 $\\theta=\\arctan({c.imag:.3f}/{c.real:.3f})={th:.2f}^\\circ$ (반시계 방향)")
    t = qc - c*(pc[0]+1j*pc[1]) if False else None
    tz = (qc[0]+1j*qc[1]) - c*(pc[0]+1j*pc[1])
    P("")
    P(f"**3단계: 이동량.** $\\mathbf{{t}}=\\bar{{\\mathbf{{q}}}}-sR\\bar{{\\mathbf{{p}}}}$. 복소수로 $t=\\bar q-c\\,\\bar p=({qc[0]:.2f}+{qc[1]:.2f}i)-({c.real:.3f}+{c.imag:.3f}i)({pc[0]:.2f}+{pc[1]:.2f}i)=({tz.real:.2f},\\ {tz.imag:.2f})$ km.")
    P("")
    fit = c*(p[:, 0]+1j*p[:, 1])+tz
    res = np.array([fit.real, fit.imag]).T - q
    rr = np.hypot(res[:, 0], res[:, 1])
    P("**4단계: 맞춤 잔차를 본다.** 구한 변환으로 통제점을 옮기고 현대 좌표와의 차이를 잰다.")
    P("")
    P("| $i$ | 변환 결과 (km) | 현대 좌표 (km) | 거리 차이 (km) |")
    P("|---|---|---|---|")
    for i in range(n):
        P(f"| {i+1} | ({fit[i].real:.1f}, {fit[i].imag:.1f}) | ({q[i,0]:.1f}, {q[i,1]:.1f}) | {rr[i]:.2f} |")
    P("")
    P(f"맞춤 RMSE는 $\\sqrt{{(" + "+".join(f"{x:.2f}^2" for x in rr) + f")/5}}={math.sqrt(np.mean(rr**2)):.2f}$ km이다. 다만 이 값은 **같은 점으로 맞추고 같은 점으로 쟀기 때문에 낙관적**이다. 이어서 정직한 값을 구한다.")
    P("")
    # LOOCV
    def fit_sim(pp, qq):
        pc_, qc_ = pp.mean(0), qq.mean(0)
        zp_ = (pp-pc_)[:, 0]+1j*(pp-pc_)[:, 1]; zq_ = (qq-qc_)[:, 0]+1j*(qq-qc_)[:, 1]
        c_ = np.sum(np.conj(zp_)*zq_)/np.sum(np.abs(zp_)**2)
        t_ = (qc_[0]+1j*qc_[1])-c_*(pc_[0]+1j*pc_[1])
        return c_, t_
    P("### 완전 풀이 예제 2: 하나 빼고 맞추기(LOOCV)")
    P("")
    P("점 하나를 빼고 나머지 4개로 변환을 다시 구한 뒤, 뺀 점을 옮겨서 오차를 잰다. 5번 반복한다.")
    P("")
    P("| 뺀 점 | $s$ (km/cm) | $\\theta$ (도) | 뺀 점 예측 (km) | 실제 (km) | 오차 $e_i$ (km) |")
    P("|---|---|---|---|---|---|")
    es = []
    for i in range(n):
        m = np.arange(n) != i
        c_, t_ = fit_sim(p[m], q[m])
        z = c_*(p[i, 0]+1j*p[i, 1])+t_
        e = math.hypot(z.real-q[i, 0], z.imag-q[i, 1]); es.append(e)
        P(f"| {i+1} | {abs(c_):.3f} | {math.degrees(math.atan2(c_.imag, c_.real)):.2f} | ({z.real:.1f}, {z.imag:.1f}) | ({q[i,0]:.1f}, {q[i,1]:.1f}) | {e:.2f} |")
    es = np.array(es)
    P("")
    P(f"$\\mathrm{{RMSE}}_{{\\text{{LOO}}}}=\\sqrt{{(" + "+".join(f"{x:.2f}^2" for x in es) + f")/5}}=\\sqrt{{{np.mean(es**2):.2f}}}={math.sqrt(np.mean(es**2)):.2f}$ km")
    P("")
    P(f"맞춤 RMSE({math.sqrt(np.mean(rr**2)):.2f} km)보다 LOO RMSE({math.sqrt(np.mean(es**2)):.2f} km)가 크다. 후자가 \"처음 보는 점에서 기대할 오차\"이다. 서경에 적용할 때 영역의 반지름은 맞춤 오차가 아니라 이 값을 기준으로 잡아야 한다.")
    P("")
    # affine
    Aa = np.hstack([p, np.ones((n, 1))])
    sol, *_ = np.linalg.lstsq(Aa, q, rcond=None)
    P("### 완전 풀이 예제 3: 아핀변환의 연립방정식")
    P("")
    P("아핀변환은 미지수가 여섯 개($a,b,c,d,t_x,t_y$)이다. $x'=ax+by+t_x$, $y'=cx+dy+t_y$를 통제점 다섯 개에 적으면 식이 열 개다. 열 개의 식으로 미지수 여섯을 구하므로 오차 제곱합이 가장 작게 되는 값을 고른다(최소제곱). 가로축 식과 세로축 식은 서로 독립이므로 따로 푼다.")
    P("")
    P("행렬로 쓰면 $\\begin{pmatrix}x_1&y_1&1\\\\\\vdots&\\vdots&\\vdots\\\\x_5&y_5&1\\end{pmatrix}\\begin{pmatrix}a\\\\b\\\\t_x\\end{pmatrix}\\approx\\begin{pmatrix}x'_1\\\\\\vdots\\\\x'_5\\end{pmatrix}$이다. 정규방정식 $(M^{\\mathsf T}M)\\,\\mathbf{w}=M^{\\mathsf T}\\mathbf{x}'$의 좌변 행렬은 다음과 같다.")
    P("")
    MtM = Aa.T@Aa
    P("$$M^{\\mathsf T}M=\\begin{pmatrix}" + "\\\\".join("&".join(f"{v:.2f}" for v in row) for row in MtM) + "\\end{pmatrix}$$")
    P("")
    P(f"풀면 $a={sol[0,0]:.3f},\\ b={sol[1,0]:.3f},\\ t_x={sol[2,0]:.2f}$, $c={sol[0,1]:.3f},\\ d={sol[1,1]:.3f},\\ t_y={sol[2,1]:.2f}$이다. 닮음변환이라면 $a=d$, $b=-c$여야 하는데 결과는 $a-d={sol[0,0]-sol[1,1]:.3f}$, $b+c={sol[1,0]+sol[0,1]:.3f}$로 조금 어긋난다. 이 차이는 통제점의 오차가 만든 것이다.")
    P("")
    J = np.array([[sol[0, 0], sol[1, 0]], [sol[0, 1], sol[1, 1]]])
    det = np.linalg.det(J)
    P(f"행렬식 $ad-bc={sol[0,0]:.3f}\\times{sol[1,1]:.3f}-({sol[1,0]:.3f})\\times({sol[0,1]:.3f})={det:.2f}$이므로 넓이는 {det:.0f}배, 길이는 평균 $\\sqrt{{{det:.0f}}}\\approx{math.sqrt(det):.1f}$ km/cm이다. 닮음변환의 배율 {s:.1f}과 거의 같다.")
    # LOO affine
    esA = []
    for i in range(n):
        m = np.arange(n) != i
        Ai = np.hstack([p[m], np.ones((n-1, 1))])
        so, *_ = np.linalg.lstsq(Ai, q[m], rcond=None)
        z = np.array([p[i, 0], p[i, 1], 1])@so
        esA.append(math.hypot(z[0]-q[i, 0], z[1]-q[i, 1]))
    esA = np.array(esA)
    P("")
    P(f"아핀변환의 LOO 오차는 " + ", ".join(f"{x:.2f}" for x in esA) + f" km, RMSE는 ${math.sqrt(np.mean(esA**2)):.2f}$ km이다. 닮음({math.sqrt(np.mean(es**2)):.2f} km)과 비교하여 작은 쪽을 고른다. 아핀은 미지수가 6개로 많아 통제점이 적을 때 LOO에서 불리해지는 경우가 많다. 이번 예에서는 " + ("닮음이" if math.sqrt(np.mean(es**2)) <= math.sqrt(np.mean(esA**2)) else "아핀이") + " 낫다.")
    P("")
    # TPS 4 pts small? skip; bootstrap
    P("### 완전 풀이 예제 4: 부트스트랩으로 구름 만들기")
    P("")
    P("통제점 5개에서 같은 점이 다시 뽑힐 수 있게 5번 뽑아 새 표본을 만든다. 번호 뽑기는 난수로 하며, 예로 6개의 표본을 직접 적는다. 목표 지명의 옛 지도 좌표는 $(5.0,\\,3.0)$ cm라고 하자. 표본마다 닮음변환을 구해 목표를 옮기면 위치가 나온다.")
    P("")
    P("| 표본 | 뽑힌 통제점 번호 | 서로 다른 점 수 | 목표 예측 (km) |")
    P("|---|---|---|---|")
    rb = np.random.default_rng(66)
    tgt = 5.0+3.0j
    preds = []
    shown = 0
    allpred = []
    for b in range(1000):
        idx = rb.integers(0, n, n)
        if len(set(idx)) < 3:
            continue
        c_, t_ = fit_sim(p[idx], q[idx])
        z = c_*tgt+t_
        allpred.append((z.real, z.imag))
        if shown < 6:
            P(f"| {shown+1} | {', '.join(str(i+1) for i in idx)} | {len(set(idx))} | ({z.real:.1f}, {z.imag:.1f}) |")
            shown += 1
    ap = np.array(allpred)
    c0, t0 = fit_sim(p, q); z0 = c0*tgt+t0
    P("")
    P(f"같은 방식으로 1000개의 표본을 만들었다(서로 다른 점이 3개 미만인 표본은 버렸다). 전체 표본 {len(ap)}개에서 목표 예측의 평균은 $({ap[:,0].mean():.1f},\\ {ap[:,1].mean():.1f})$ km, 표준편차는 동서 {ap[:,0].std():.1f} km, 남북 {ap[:,1].std():.1f} km이다. 모든 점을 쓴 원래 변환의 예측은 $({z0.real:.1f},\\ {z0.imag:.1f})$ km이다.")
    d = np.hypot(ap[:, 0]-z0.real, ap[:, 1]-z0.imag)
    P("")
    P(f"원래 예측에서 각 표본 예측까지 거리의 중앙값은 {np.median(d):.1f} km, 90번째 백분위수는 {np.percentile(d,90):.1f} km이다. 따라서 \"통제점이 옳다면 90%의 표본이 원래 예측에서 {np.percentile(d,90):.1f} km 이내에 든다\"고 말할 수 있다. 그런데 이 폭은 하나 빼고 맞추기 오차({math.sqrt(np.mean(es**2)):.2f} km)보다 훨씬 작다. 부트스트랩은 \"어떤 통제점이 뽑혔는가\"의 흔들림만 보여 줄 뿐 \"변환의 모양 자체가 틀렸을 가능성\"은 반영하지 못하기 때문이다. 실제 보고에서는 두 값 중 큰 쪽을 영역의 반지름으로 삼는 것이 안전하다. 이 구름은 **통제점이 옳다는 가정** 아래의 폭이다. 통제점 자체가 학설에 따라 틀렸다면 구름 밖에 참이 있을 수 있다.")

    # ---- TPS
    def phi(r):
        return 0.0 if r == 0 else r*r*math.log(r)
    def tps_fit(pp, qq, lam):
        m = len(pp)
        K = np.array([[phi(math.hypot(*(pp[i]-pp[j]))) for j in range(m)] for i in range(m)])+lam*np.eye(m)
        Pm = np.hstack([np.ones((m, 1)), pp])
        Lm = np.zeros((m+3, m+3)); Lm[:m, :m] = K; Lm[:m, m:] = Pm; Lm[m:, :m] = Pm.T
        rhs = np.vstack([qq, np.zeros((3, 2))])
        sol = np.linalg.solve(Lm, rhs)
        return sol[:m], sol[m:], K
    def tps_eval(x, pp, w, a):
        v = a[0]+a[1]*x[0]+a[2]*x[1]
        for i in range(len(pp)):
            v = v+w[i]*phi(math.hypot(*(x-pp[i])))
        return v
    P("")
    P("### 완전 풀이 예제 5: 박판스플라인을 작은 연립방정식으로 풀기")
    P("")
    P("박판스플라인은 \"아핀변환 + 통제점마다의 비틀림\"이다. 통제점이 $m$개이면 미지수는 비틀림 가중치 $\\mathbf{w}_1,\\dots,\\mathbf{w}_m$과 아핀 계수 세 쌍($a_0,a_x,a_y$)이다. 식은 통제점마다 $f(\\mathbf{p}_i)=\\mathbf{q}_i$로 $m$개, 여기에 \"비틀림이 큰 흐름을 바꾸지 못하게\" 하는 조건 3개를 더하여 $m+3$개이다. 위 통제점 가운데 앞의 4개를 써서 직접 구성한다.")
    pp = p[:4]; qq = q[:4]
    w_, a_, K_ = tps_fit(pp, qq, 0.0)
    P("")
    P("**1단계: 거리와 $\\varphi(r)=r^2\\ln r$ 표.** 통제점 사이의 거리 $r_{ij}$(cm)와 $\\varphi$의 값은 다음과 같다. 대각선은 거리 0이므로 0이다.")
    P("")
    P("| $\\varphi(r_{ij})$ | 점 1 | 점 2 | 점 3 | 점 4 |")
    P("|---|---|---|---|---|")
    for i in range(4):
        P(f"| 점 {i+1} | " + " | ".join(f"{K_[i,j]:.3f}" for j in range(4)) + " |")
    P("")
    r12 = math.hypot(*(pp[0]-pp[1]))
    P(f"예를 들어 점 1과 점 2의 거리는 $\\sqrt{{(2-8)^2+(1-2)^2}}={r12:.3f}$이고 $\\varphi={r12:.3f}^2\\ln{r12:.3f}={phi(r12):.3f}$이다.")
    P("")
    P("**2단계: 연립방정식을 세워 푼다.** $7\\times7$ 행렬 방정식 $\\begin{pmatrix}K&P\\\\P^{\\mathsf T}&0\\end{pmatrix}\\begin{pmatrix}W\\\\A\\end{pmatrix}=\\begin{pmatrix}Q\\\\0\\end{pmatrix}$를 푼다. $K$는 위의 표, $P$는 각 통제점의 $(1,x,y)$를 쌓은 행렬이다. 풀이 결과는 다음과 같다(동서 방향 성분과 남북 방향 성분).")
    P("")
    P("| 항 | 동서 성분 | 남북 성분 |")
    P("|---|---|---|")
    for i in range(4):
        P(f"| 가중치 $\\mathbf{{w}}_{i+1}$ | {w_[i,0]:.3f} | {w_[i,1]:.3f} |")
    P(f"| 아핀 $a_0$ (이동) | {a_[0,0]:.2f} | {a_[0,1]:.2f} |")
    P(f"| 아핀 $a_x$ | {a_[1,0]:.3f} | {a_[1,1]:.3f} |")
    P(f"| 아핀 $a_y$ | {a_[2,0]:.3f} | {a_[2,1]:.3f} |")
    P("")
    z1 = tps_eval(pp[0], pp, w_, a_)
    P(f"**3단계: 검산.** $\\lambda=0$이면 통제점을 정확히 지나가야 한다. 점 1을 넣으면 $({z1[0]:.2f},\\ {z1[1]:.2f})$로 현대 좌표 $({qq[0,0]:.1f},\\ {qq[0,1]:.1f})$와 같다. 가중치의 합이 0이고($\\sum w={w_[:,0].sum():.4f}$), 이것이 위에서 말한 \"큰 흐름을 바꾸지 않는다\"는 조건의 한 부분이다.")
    P("")
    tg = np.array([5.0, 3.0])
    zt = tps_eval(tg, pp, w_, a_)
    c_, t_ = fit_sim(p, q); zs_ = c_*(tg[0]+1j*tg[1])+t_
    P("**4단계: 목표 지명에 적용하고 다른 변환과 비교.** 목표의 옛 좌표 $(5.0,\\,3.0)$을 넣는다.")
    P("")
    P(f"- 박판스플라인($\\lambda=0$, 점 4개): $({zt[0]:.1f},\\ {zt[1]:.1f})$ km")
    P(f"- 닮음변환(점 5개 모두): $({zs_.real:.1f},\\ {zs_.imag:.1f})$ km")
    P(f"- 둘의 거리: {math.hypot(zt[0]-zs_.real, zt[1]-zs_.imag):.1f} km")
    P("")
    P("**5단계: $\\lambda$를 키우면.** $\\lambda$는 $K$의 대각선에 더해지는 값이다. 값이 커질수록 통제점을 정확히 지나가는 일을 포기하고 아핀변환에 가까워진다.")
    P("")
    P("| $\\lambda$ | 점 1 맞춤 오차 (km) | 목표 예측 (km) |")
    P("|---|---|---|")
    for lam in (0.0, 1.0, 10.0, 100.0):
        w2, a2, _ = tps_fit(pp, qq, lam)
        z1 = tps_eval(pp[0], pp, w2, a2); zt2 = tps_eval(tg, pp, w2, a2)
        P(f"| {lam:g} | {math.hypot(z1[0]-qq[0,0], z1[1]-qq[0,1]):.2f} | ({zt2[0]:.1f}, {zt2[1]:.1f}) |")
    P("")
    # LOO TPS
    es_t = {}
    for lam in (0.0, 10.0):
        e_ = []
        for i in range(n):
            m_ = np.arange(n) != i
            w2, a2, _ = tps_fit(p[m_], q[m_], lam)
            z = tps_eval(p[i], p[m_], w2, a2)
            e_.append(math.hypot(z[0]-q[i, 0], z[1]-q[i, 1]))
        es_t[lam] = math.sqrt(np.mean(np.array(e_)**2))
    P(f"하나 빼고 맞추기로 비교하면 $\\lambda=0$일 때 RMSE ${es_t[0.0]:.2f}$ km, $\\lambda=10$일 때 ${es_t[10.0]:.2f}$ km이다. 닮음변환의 {math.sqrt(np.mean(es**2)):.2f} km, 아핀변환의 {math.sqrt(np.mean(esA**2)):.2f} km와 한 표에 놓고 가장 작은 것을 택한다. 통제점이 5개뿐일 때는 복잡한 변환이 정직한 오차에서 오히려 불리한 경우가 많다.")
    return "\n".join(out)

if __name__ == "__main__":
    print(md())
