import pickle, re, sys, glob
sys.path.insert(0,'.')
import lib07
R,TAB=pickle.load(open("RT.pkl","rb")); lib07.R.update(R); lib07.TAB.update(TAB)
def rendered(path):
    return lib07.render(open(path,encoding="utf-8").read())
if __name__=="__main__":
    for p in sorted(glob.glob("chunk*.md")):
        t=rendered(p); print(p,len(t))
