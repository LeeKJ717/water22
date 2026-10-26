"""과학과영성출판사 최종 로고 SVG 생성 (글자는 Noto Sans CJK KR Bold 곡선화). 사용: python3 ssp-logo-final-build-v1.py 출력폴더"""
import math,sys
from fontTools.ttLib import TTCollection
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
IN='#1F2F6B';SA='#F2A33A';JA='#2FA38F';CO='#E9674B';CR='#FBF4E4'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
col=TTCollection(FONT); f=[x for x in col.fonts if 'KR' in x['name'].getDebugName(1)][0]
gs=f.getGlyphSet(); cmap=f.getBestCmap()
def text_path(s,x,base,fs,track):
    d='';cx=x
    for ch in s:
        pen=SVGPathPen(gs); k=fs/1000
        gs[cmap[ord(ch)]].draw(TransformPen(pen,(k,0,0,-k,cx,base)))
        d+=pen.getCommands(); cx+=gs[cmap[ord(ch)]].width*k+track
    return d,cx
def dots(cx,cy,sc):
    o=''
    for i in range(12):
        a=math.radians(i*30); x=cx+78*sc*math.cos(a); y=cy+78*sc*math.sin(a); big=i%3==0
        o+=f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{(7.5 if big else 5.5)*sc:.2f}" fill="{SA if big else CO}"/>'
    return o
def symbol(cx,cy,H,disc,s):
    sc=H/200; t=f'translate({cx-100*sc:.2f},{cy-100*sc:.2f}) scale({sc})'
    return (f'<g transform="{t}"><circle cx="100" cy="100" r="62" fill="{disc}"/>'
            f'<path d="M114.85,64.15 A21,21 0 1 0 100,100 A21,21 0 1 1 85.15,135.85" fill="none" stroke="{s}" stroke-width="14" stroke-linecap="round"/>'
            +dots(100,100,1)+'</g>')
def ssp(x,cy,H,c1):
    sc=H/150; w=215*sc; t=f'translate({x-28*sc:.2f},{cy-92*sc:.2f}) scale({sc})'
    return (f'<g transform="{t}" fill="none" stroke-linecap="round" stroke-width="14">'
            f'<path d="M76.85,56.15 A21,21 0 1 0 62,92 A21,21 0 1 1 47.15,127.85" stroke="{c1}"/>'
            f'<path d="M144.85,56.15 A21,21 0 1 0 130,92 A21,21 0 1 1 115.15,127.85" stroke="{JA}"/>'
            f'<path d="M190,52 L190,132 M190,52 L208,52 A21,21 0 0 1 208,94 L190,94" stroke="{SA}"/></g>'),x+w
def lockup(dark,text=True,fs=36):
    c=CR if dark else IN; H=120; cy=60
    parts=[symbol(60,cy,H,CR if dark else IN, IN if dark else CR)]
    s,x=ssp(124,cy,95,c); parts.append(s)
    w=x
    if text:
        d,w=text_path('과학과영성출판사',x+16,cy+0.36*fs+0.55*fs/36,fs,fs*0.06)
        parts.append(f'<path d="{d}" fill="{c}"/>')
    return ''.join(parts),w
def write(path,dark,text=True,fs=36,pad=6):
    body,w=lockup(dark,text,fs)
    end=w-(fs*0.06 if text else 0); x0=8.7-pad; W=end+pad-x0
    open(path,'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.1f} {-pad} {W:.1f} {120+pad*2}"><title>과학과영성출판사</title>{body}</svg>')
    return W+0
if __name__=='__main__':
    o=sys.argv[1]
    write(f'{o}/ssp-logo-h-light-v1.svg',False)           # 밝은 바탕용
    write(f'{o}/ssp-logo-h-dark-v1.svg',True)             # 어두운 바탕용
    write(f'{o}/ssp-logo-h-web-v1.svg',False,True,64)     # 웹 헤더용(글자 크게)
    write(f'{o}/ssp-logo-h-notext-light-v1.svg',False,False)
    write(f'{o}/ssp-logo-h-notext-dark-v1.svg',True,False)
    open(f'{o}/ssp-symbol-v1.svg','w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><title>과학과영성출판사</title>'+symbol(60,60,120,IN,CR)+'</svg>')
    open(f'{o}/ssp-symbol-dark-v1.svg','w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><title>과학과영성출판사</title>'+symbol(60,60,120,CR,IN)+'</svg>')
