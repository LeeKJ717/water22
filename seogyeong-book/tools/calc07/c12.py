from lib07 import *
import c11
rows=[]
for nm,k in (("균등 사전","flat"),("능선 가중 사전","crest")):
    rows.append([nm,f"({R[f'J2.{k}.mx']:.1f}, {R[f'J2.{k}.my']:.1f})",f"({R[f'J2.{k}.mapx']:.1f}, {R[f'J2.{k}.mapy']:.1f})",f"{R[f'J2.{k}.a50']:.0f}",f"{R[f'J2.{k}.a95']:.0f}",f"{R[f'J2.{k}.oncrest']:.1f}"])
ptab("J2.tab",["사전","사후 평균 (km)","MAP (km)","50% 영역 (km²)","95% 영역 (km²)","능선 위의 사후질량(%)"],rows)
rows=[["물길을 따라 잰 거리 (옳은 읽기)",f"({R['J3.arc.x']:.1f}, {R['J3.arc.y']:.1f})",f"{R['J3.s_lo']:.1f}~{R['J3.s_hi']:.1f}",f"{R['J3.arc.chord']:.1f}"],
      ["두 점 사이 직선거리로 읽음 (잘못)",f"({R['J3.str.x']:.1f}, {R['J3.str.y']:.1f})","-","-"]]
ptab("J3.tab",["읽기","사후 평균 위치 (km)","물길 거리 95% 구간 (km)","평균 위치의 직선거리 (km)"],rows)
rows=[["군(첫 단계)",f"({R['J7.gun.mx']:.1f}, {R['J7.gun.my']:.1f})",f"{R['J7.gun.sx']:.1f}",f"{R['J7.gun.sy']:.1f}",f"{R['J7.gun.ell95']:,.0f}"],
      ["읍치, 단위를 공유",f"({R['J7.sh.mx']:.1f}, {R['J7.sh.my']:.1f})",f"{R['J7.sh.sx']:.1f}",f"{R['J7.sh.sy']:.1f}",f"{R['J7.sh.ell95']:,.0f}"],
      ["읍치, 단계마다 단위를 따로 뽑음 (잘못)",f"({R['J7.ind.mx']:.1f}, {R['J7.ind.my']:.1f})",f"{R['J7.ind.sx']:.1f}",f"{R['J7.ind.sy']:.1f}",f"{R['J7.ind.ell95']:,.0f}"]]
ptab("J7.tab",["대상","평균 (km)","$x$ 표준편차 (km)","$y$ 표준편차 (km)","95% 타원 넓이 (km²)"],rows)
rows=[["이틀+사흘 두 서술 (닫힌 길)",f"{R['J8.v_mean']:.1f} ± {R['J8.v_sd']:.1f}",f"{R['J8.s_mean']:.1f}",f"{R['J8.s_lo']:.1f}~{R['J8.s_hi']:.1f}",f"{R['J8.both.w']:.1f}"],
      ["이틀 서술 하나만",'-',"-",f"{R['J8.one.lo']:.1f}~{R['J8.one.hi']:.1f}",f"{R['J8.one.w']:.1f}"]]
ptab("J8.tab",["입력","$v$ (km/일)","길 위 위치 평균 (갑성에서 km)","95% 구간 (km)","구간 폭 (km)"],rows)
put("J7.sd_ratio",R["J7.sh.sx"]/R["J7.gun.sx"]); put("J7.area_ratio",R["J7.sh.ell95"]/R["J7.ind.ell95"])
put("J7.lastsd",R["J7.plug_sx"]); put("J7.latespan",R["J7.exp_mx"])
put("J2.dy",R["J2.crest.my"]-R["J2.flat.my"]); put("J2.off",100-R["J2.crest.oncrest"])
put("J3.chord_ratio",R["J3.arc.chord"]/(30*R["E.ok.m"]*0+12.6))
put("J8.pct",R["J8.v_mean"]/R["J8.v_exp"]*100)
if __name__=="__main__":
    for k in ("J2.tab","J3.tab","J7.tab","J8.tab"): print(TAB[k])
