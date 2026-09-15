# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import math, os, random, json

OUT = "D:/github profile/assets"
os.makedirs(OUT, exist_ok=True)
UP=(38,166,154); DOWN=(239,83,80); ACC=(41,98,255); GOLD=(247,166,0)
DARK=dict(bg=(19,23,34),panel=(30,34,43),txt=(209,212,220),mut=(120,123,134),grid=(30,34,43),border=(42,46,57))
LIGHT=dict(bg=(246,248,250),panel=(227,231,236),txt=(36,41,46),mut=(87,96,106),grid=(225,228,232),border=(208,215,222))

def font(sz,bold=False):
    for name in (("consolab.ttf" if bold else "consola.ttf"),"courbd.ttf","cour.ttf","arial.ttf"):
        try: return ImageFont.truetype(name,sz)
        except: pass
    return ImageFont.load_default()

def save(frames,path,dur):
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=dur,loop=0,optimize=True)

def star(d,cx,cy,r,col):
    pts=[]
    for i in range(10):
        a=-math.pi/2+i*math.pi/5
        rr=r if i%2==0 else r*0.45
        pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
    d.polygon(pts,fill=col)

def card(d,box,mode):
    m=DARK if mode=="dark" else LIGHT
    d.rounded_rectangle(box,radius=10,fill=m["panel"],outline=m["border"],width=2)

def text_w(dr,s,ft):
    bb=dr.textbbox((0,0),s,font=ft)
    return bb[2]-bb[0]

# ---------- 1. candles ----------
def make_candles(mode):
    m=DARK if mode=="dark" else LIGHT
    W,H,N,F=760,110,40,40; frames=[]
    for f in range(F):
        img=Image.new("RGB",(W,H),m["bg"]); d=ImageDraw.Draw(img)
        random.seed(f//5)
        price=H*0.5
        for i in range(N):
            drift=(random.random()-0.48)*12
            o=price; c=max(15,min(H-15,price+drift))
            hi=max(o,c)+random.random()*8; lo=min(o,c)-random.random()*8
            x=i*(W//N)+4; fy=math.sin(f/F*2*math.pi+i*0.35)*4
            col=UP if c>=o else DOWN
            d.line([x+5,hi+fy,x+5,lo+fy],fill=col,width=1)
            d.rectangle([x,min(o,c)+fy,x+10,max(o,c)+fy],fill=col)
            price=c
        frames.append(img.convert("P",palette=Image.ADAPTIVE))
    save(frames,f"{OUT}/candles_{mode}.gif",80)

# ---------- 2. ticker tape ----------
def make_ticker(mode):
    m=DARK if mode=="dark" else LIGHT
    W,H,F=760,64,52
    ft=font(26,True)
    segs=[("TONMOY540  LONG   |  ",UP),("AI-VALIDATOR v2 BUY   |  ",UP),("HONEST-DATA 100%   |  ",UP),
          ("BACKTESTS RUNNING   |  ",UP),("SLEEP 7h DOWN   |  ",DOWN),("COFFEE INFINITY UP   |  ",UP),("TREND BULLISH   |  ",UP)]
    tmp=Image.new("RGB",(10,10)); td=ImageDraw.Draw(tmp)
    items=[(s,w,GOLD) for s,_ in [] for w in []]  # noop guard
    widths=[]; strip_w=0
    for s,col in segs:
        w=text_w(td,s,ft); widths.append((s,w,col)); strip_w+=w
    strip=Image.new("RGB",(strip_w*2,H),m["bg"]); sd=ImageDraw.Draw(strip)
    x=0
    for rep in range(2):
        for s,w,col in widths:
            sd.text((x,H//2-14),s,fill=col,font=ft); x+=w
    frames=[]
    for f in range(F):
        off=int(f/F*strip_w)
        frames.append(strip.crop((off,0,off+W,H)).convert("P",palette=Image.ADAPTIVE))
    save(frames,f"{OUT}/ticker_{mode}.gif",42)

# ---------- 3. glow banner ----------
def make_glow(mode):
    m=DARK if mode=="dark" else LIGHT
    W,H,F=760,90,44; f1=font(30,True); frames=[]
    ink=(15,20,28) if mode=="light" else m["txt"]
    for f in range(F):
        img=Image.new("RGB",(W,H),m["bg"]); d=ImageDraw.Draw(img)
        for gy in range(0,H,18): d.line([0,gy,W,gy],fill=m["grid"])
        for gx in range(0,W,40): d.line([gx,0,gx,H],fill=m["grid"])
        sx=int((f/F)*(W+300)-150)
        for k in range(120):
            gx=sx-60+k
            if 0<=gx<W:
                a=math.sin(k/120*math.pi)
                factor=a if mode=="dark" else a*0.55
                col=tuple(int(m["bg"][i]*(1-factor)+ACC[i]*factor) for i in range(3))
                d.line([gx,0,gx,H],fill=col)
        for i in range(14):
            px=(i*173+f*11)%W; py=(i*67)%H
            s=2+2*math.sin(f/5+i)
            if s>0.5:
                r=max(1,int(s*0.8))
                d.ellipse([px-r,py-r,px+r,py+r],fill=GOLD if i%3 else UP)
        y=int(H/2-18+math.sin(f/F*2*math.pi)*5)
        d.text((W//2-175,y),"TONMOY540",fill=ink,font=f1)
        frames.append(img.convert("P",palette=Image.ADAPTIVE))
    save(frames,f"{OUT}/glow_{mode}.gif",70)

# ---------- 4. status frame ----------
def make_status(mode):
    m=DARK if mode=="dark" else LIGHT
    W,H,F=760,110,50; f1=font(22,True); frames=[]
    for f in range(F):
        img=Image.new("RGB",(W,H),m["bg"]); d=ImageDraw.Draw(img)
        for i in range(26):
            px=(i*97-f*3)%W; py=(i*53+int(8*math.sin(f/6+i)))%H
            d.ellipse([px,py,px+2,py+2],fill=(60,70,85) if mode=="dark" else (180,188,196))
        ax=(f*6)%(W+120)-60; ay=30+math.sin(f/5)*6
        d.polygon([(ax,ay+14),(ax+9,ay-6),(ax+18,ay+14)],fill=UP)
        bx=W-ax; by=78+math.cos(f/5)*6
        d.polygon([(bx,by-14),(bx+9,by+6),(bx+18,by-14)],fill=DOWN)
        r=3+int(2*math.sin(f/4))
        d.rounded_rectangle([W//2-130,H//2-26,W//2+130,H//2+26],radius=10,fill=m["panel"],outline=m["border"],width=2)
        d.text((W//2-118,H//2-10),"TONMOY540 // OPEN",fill=UP,font=f1)
        cx=W//2+108; cy=H//2
        d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=UP)
        frames.append(img.convert("P",palette=Image.ADAPTIVE))
    save(frames,f"{OUT}/status_{mode}.gif",70)

# ---------- 5. real activity graph ----------
def make_activity(mode):
    m=DARK if mode=="dark" else LIGHT
    ca=json.load(open("D:/github profile/_ca.json"))
    totals=[w["total"] for w in ca][-26:]
    W,H,F=760,170,60
    f2=font(13)
    maxv=max(1,max(totals))
    frames=[]
    for f in range(F):
        img=Image.new("RGB",(W,H),m["bg"]); d=ImageDraw.Draw(img)
        for gy in range(20,H-20,25): d.line([10,gy,W-10,gy],fill=m["grid"])
        n=len(totals); step=(W-40)/n
        shown=min(n,int(f/F*n)+1)
        pts=[]
        for i in range(shown):
            h=8+int(totals[i]/maxv*80)
            x=20+i*step; y=H-25-h
            pts.append((x,y))
            col=UP if totals[i]>0 else m["border"]
            d.rectangle([x,y,x+step*0.6,H-25],fill=UP if totals[i]>0 else m["panel"],outline=col)
        if len(pts)>1:
            d.line(pts,fill=UP,width=2)
        d.text((15,8),"WEEKLY COMMIT ACTIVITY · real data from your repos",fill=m["mut"],font=f2)
        nz=sum(1 for t in totals if t>0)
        d.text((15,H-18),f"{nz} active weeks · {sum(totals)} commits · 12 public events",fill=m["mut"],font=f2)
        if shown==n and pts:
            lx,ly=pts[-1]; r=3+int(2*math.sin(f/3))
            d.ellipse([lx-r,ly-r,lx+r,ly+r],fill=GOLD)
        frames.append(img.convert("P",palette=Image.ADAPTIVE))
    save(frames,f"{OUT}/activity_{mode}.gif",55)

# ---------- 6. astrocat mascot ----------
def make_cat():
    m=DARK
    W,H,F=300,220,60; f1=font(16)
    cat=(" /\\_/\\  ","( o.o ) "," > ^ <  ","/|   |\\ "," |~~~|  "," d   b  ")
    rocket=("   /\\   ","  /  \\  "," | >> | ","  \\__/  ","  ~~~~  ")
    frames=[]
    for f in range(F):
        img=Image.new("RGB",(W,H),m["bg"]); d=ImageDraw.Draw(img)
        for i in range(30):
            px=(i*89+f*2)%W; py=(i*53+f)%H
            s=1+math.sin(f/4+i)
            if s>0.4:
                d.point((px,py),fill=(90,100,120) if s<1.2 else (200,210,225))
        fy=int(math.sin(f/F*2*math.pi)*8)
        for i,line in enumerate(cat):
            col=GOLD if i==1 else m["txt"]
            d.text((40,20+i*18+fy),line,fill=col,font=f1)
        rx=int((f*7)%(W+140))-70; ry=150+int(math.sin(f/4)*6)
        flame=UP if (f//2)%2==0 else GOLD
        for i,line in enumerate(rocket):
            d.text((rx,ry+i*16),line,fill=m["txt"],font=f1)
        d.text((rx+3,ry+5*16),"/\\/" if (f//2)%2 else "\\|/",fill=flame,font=f1)
        d.text((150,30),"ASTROCAT",fill=ACC,font=f1)
        d.text((150,52),"orbit %ddeg" % int(f/F*360),fill=m["mut"],font=f1)
        d.text((150,74),"fuel: COFFEE inf",fill=UP,font=f1)
        frames.append(img.convert("P",palette=Image.ADAPTIVE))
    save(frames,f"{OUT}/astrocat.gif",80)

# ---------- 7. moto banner typewriter ----------
def make_moto(mode):
    m=DARK if mode=="dark" else LIGHT
    moto="HONEST DATA. CLEAR LIMITS. NO FOMO."
    W,H,F=760,90,70; f1=font(28,True); f2=font(15)
    tmp=Image.new("RGB",(10,10)); tw=text_w(ImageDraw.Draw(tmp),moto,f1)
    X0=(W-tw)//2
    ink=(15,20,28) if mode=="light" else m["txt"]
    frames=[]
    for f in range(F):
        img=Image.new("RGB",(W,H),m["bg"]); d=ImageDraw.Draw(img)
        for gy in range(0,H,18): d.line([0,gy,W,gy],fill=m["grid"])
        phase=f%(len(moto)+22)
        n=min(len(moto),phase)
        d.text((X0,H//2-22),moto[:n],fill=ink,font=f1)
        if (f//4)%2==0 and phase<len(moto)+20:
            bw=text_w(d,moto[:n],f1)
            d.rectangle([X0+bw+4,H//2-18,X0+bw+9,H//2+10],fill=UP)
        if phase>=len(moto):
            d.text((X0,H//2+16),"- building decision-support software",fill=m["mut"],font=f2)
        frames.append(img.convert("P",palette=Image.ADAPTIVE))
    save(frames,f"{OUT}/moto_{mode}.gif",55)

# ---------- 8. trophy strip ----------
def make_trophies(mode):
    m=DARK if mode=="dark" else LIGHT
    W,H,F=760,150,40
    trophies=[("FIRST REPO","ai-trade-validator live"),("RELEASES","v2 shipped"),
              ("COMMITS","pushed daily"),("STREAK","building up")]
    f1=font(17,True); f2=font(13)
    frames=[]
    for f in range(F):
        img=Image.new("RGB",(W,H),m["bg"]); d=ImageDraw.Draw(img)
        cw=(W-50)/4
        for i,(name,sub) in enumerate(trophies):
            x=15+i*cw; fy=math.sin(f/F*2*math.pi+i*0.8)*4
            card(d,[x,15+fy,x+cw-12,H-15+fy],mode)
            cx=x+cw/2-6; cy=45+fy
            r=13+3*math.sin(f/3+i)
            star(d,cx,cy,r,GOLD if i%2==0 else UP)
            d.text((x+8,78+fy),name,fill=m["txt"],font=f1)
            d.text((x+8,100+fy),sub,fill=m["mut"],font=f2)
        frames.append(img.convert("P",palette=Image.ADAPTIVE))
    save(frames,f"{OUT}/trophies_{mode}.gif",90)

for mode in ("dark","light"):
    make_candles(mode); make_ticker(mode); make_glow(mode); make_status(mode)
    make_activity(mode); make_moto(mode); make_trophies(mode)
make_cat()
tot=0
for f in sorted(os.listdir(OUT)):
    s=os.path.getsize(os.path.join(OUT,f)); tot+=s
    print(f,s)
print("TOTAL",tot)
