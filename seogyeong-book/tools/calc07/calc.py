import warnings, pickle; warnings.filterwarnings("ignore")
import lib07, c0, c8, c9, c10, c11, c12, c13, c14, c15, c16
pickle.dump((lib07.R,lib07.TAB),open("RT.pkl","wb"))
with open("keys.txt","w") as f:
    for k,v in lib07.R.items(): f.write(f"{k}\t{v}\n")
print(len(lib07.R),len(lib07.TAB))
