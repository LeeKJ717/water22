from lib07 import *
import c12
put("J1.eq_over_pt",R["J1.a95_eq"]/R["J1.a95_pt"]); put("J1.pe_over_pt",R["J1.a95_pe"]/R["J1.a95_pt"])
put("J6.nsa_dir",0.148)
put("J7.ind_over_sh",100*R["J7.ind.ell95"]/R["J7.sh.ell95"])

for nm in "abc":
    pc={k.split(".pc.")[1]:v for k,v in R.items() if k.startswith(f"K.{nm}.pc.")}
    put(f"K.{nm}.pboth",pc["둘 다 맞음"]); put(f"K.{nm}.pone1",pc["승람만 틀림"]); put(f"K.{nm}.pone2",pc["해동역사만 틀림"]); put(f"K.{nm}.pnone",pc["둘 다 틀림"])
    put(f"K.{nm}.sumone",pc["승람만 틀림"]+pc["해동역사만 틀림"])

put("J5.da",R["J5.다섬"]); put("J5.ma",R["J5.마섬"]); put("J5.o.da",R["J5.o.다섬"]); put("J5.o.ma",R["J5.o.마섬"])
