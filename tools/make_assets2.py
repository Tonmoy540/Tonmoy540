# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import math, os, random

OUT="D:/github profile/assets"
UP=(38,166,154); DOWN=(239,83,80); ACC=(41,98,255); GOLD=(247,166,0)
DARK=dict(bg=(19,23,34),panel=(30,34,43),txt=(209,212,220),mut=(120,123,134),grid=(40,46,60),border=(42,46,57))
LIGHT=dict(bg=(246,248,250),panel=(227,231,236),txt=(36,41,46),mut=(87,96,106),grid=(195,202,212),border=(208,215,222))

def font(sz,bold=False):
    for name in (("consolab.ttf" if bold else "consola.ttf"),"courbd.ttf","cour.ttf","arial.ttf"):
        try: return ImageFont.truetype(name,sz)
        except: pass
    return ImageFont.load_default()

def save(frames,path,dur):
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=dur,loop=0,optimize=True)

# ================= 3D rotating candlestick chart =================
def make_3d(mode):
    m=DARK if mode=="dark" else LIGHT
    W,H,F=760,300,72
    random.seed(7)
    N=14
    candles=[]
    price=0.0
    for i in range(N):
        drift=(random.random()-0.45)*0.6
        o,c=price,price+drift
        hi=max(o,c)+random.random()*0.35; lo=min(o,c)-random.random()*0.35
        candles.append((i,o,c,hi,lo)); price=c
    frames=[]
    for f in range(F):
        img=Image.new("RGB",(W,H),m["bg"]); d=ImageDraw.Draw(img)
        ang=f/F*2*math.pi
        ca,sa=math.cos(ang),math.sin(ang)
        cx,cy=W/2,H/2+40
        D=900.0; FOV=520.0
        def proj(x,y,z):
            # y is height (up), z depth
            x2=x*ca - z*sa; z2=x*sa + z*ca
            s=FOV/(D+z2)
            return (cx+x2*s, cy-y*s, z2)
        # floor grid
        GS=300; STEP=GS/5
        def p2(t): return (t[0],t[1])
        for gi in range(-5,6):
            t=[p2(proj(gi*STEP,0,-GS)),p2(proj(gi*STEP,0,GS))]
            d.line([t[0],t[1]],fill=m["grid"],width=1)
            t=[p2(proj(-GS,0,gi*STEP)),p2(proj(GS,0,gi*STEP))]
            d.line([t[0],t[1]],fill=m["grid"],width=1)
        # candles sorted far->near
        draw_list=[]
        for i,o,c,hi,lo in candles:
            x=(i-(N-1)/2)*(GS*2/N)*0.9
            z=0
            top=proj(x,hi*55,0); bot=proj(x,lo*55,0)
            draw_list.append((top[2],x,o,c,hi,lo,top,bot))
        draw_list.sort(key=lambda t:-t[0])
        for _,x,o,c,hi,lo,top,bot in draw_list:
            col=UP if c>=o else DOWN
            # wick
            d.line([(top[0],top[1]),(bot[0],bot[1])],fill=col,width=2)
            # body: draw two verticals + horizontal fill lines between open/close heights
            yo=proj(x,o*55,0); yc=proj(x,c*55,0)
            hw=max(2,int(6*FOV/(D+top[2])))
            yhi,ylo=sorted([yo[1],yc[1]])
            yy=int(yhi)
            while yy<=ylo:
                d.line([yo[0]-hw,yy,yo[0]+hw,yy],fill=col)
                yy+=1
            # 3D side face (depth illusion)
            yo2=proj(x*0.55,o*55,90); yc2=proj(x*0.55,c*55,90)
            hi2=max(yo2[1],yc2[1]); lo2=min(yo2[1],yc2[1])
            dark=tuple(int(v*0.55) for v in col)
            d.polygon([(yo[0]+hw,yo[1]),(yo2[0]+hw*0.6,yo2[1]),(yo2[0]+hw*0.6,yc2[1]),(yo[0]+hw,yc[1])],fill=dark)
        # moving price line (top of last candle heights path)
        path=[(proj((i-(N-1)/2)*(GS*2/N)*0.9,(c2)*55+18,0)[0],proj((i-(N-1)/2)*(GS*2/N)*0.9,(c2)*55+18,0)[1]) for i,_,c2,_,_ in candles]
        d.line(path,fill=ACC,width=2)
        px,py=path[-1]; r=4+int(2*math.sin(f/4))
        d.ellipse([px-r,py-r,px+r,py+r],fill=GOLD)
        ft=font(14,True); fs=font(12)
        d.text((14,10),"TONMOY//3D · PERSPECTIVE VIEW",fill=m["txt"],font=ft)
        d.text((14,H-24),"auto-rotate · FOV 52 · %d%%" % int(f/F*360),fill=m["mut"],font=fs)
        frames.append(img.convert("P",palette=Image.ADAPTIVE))
    save(frames,f"{OUT}/chart3d_{mode}.gif",45)

# ================= order book depth ladder =================
def make_ladder(mode):
    m=DARK if mode=="dark" else LIGHT
    W,H,F=760,220,56
    ft=font(13,True)
    random.seed(11)
    asks=[1.0,0.85,0.72,0.6,0.5,0.42,0.35]
    bids=[0.95,0.8,0.66,0.55,0.47,0.4,0.33]
    frames=[]
    for f in range(F):
        img=Image.new("RGB",(W,H),m["bg"]); d=ImageDraw.Draw(img)
        rowh=22; y0=14
        # header
        d.text((14,10-0),"ORDER BOOK · AI-VALIDATOR/LIVE",fill=m["mut"],font=ft)
        y=y0+18
        for i,a in enumerate(asks):
            w=(a*0.92+0.06*math.sin(f/3+i))*(W-260)
            wob=a*(1+0.06*math.sin(f/2.5+i*1.7))
            d.rectangle([170,y,170+w,y+rowh-5],fill=DOWN)
            d.text((14,y-1),"ASK %.4f" % (52800+i*7+f*0.3+14-i*2),fill=m["txt"],font=ft)
            d.text((240+w+8,y-1),"%.2f BTC" % (wob*8+2),fill=DOWN,font=ft)
            y+=rowh
        # spread line
        mid=52790+math.sin(f/4)*22
        d.line([14,y+3,746,y+3],fill=m["border"],width=2)
        d.text((300,y-5),"SPREAD %.2f" % (18+3*math.sin(f/3)),fill=GOLD,font=ft)
        y+=rowh+6
        for i,b in enumerate(bids):
            w=(b*0.92+0.06*math.cos(f/3+i))*(W-260)
            wob=b*(1+0.06*math.cos(f/2.5+i*1.7))
            d.rectangle([170,y,170+w,y+rowh-5],fill=UP)
            d.text((14,y-1),"BID %.4f" % (52780-i*7-f*0.3,1),fill=m["txt"],font=ft) if False else None
            d.text((14,y-1),"BID %.4f" % (52780-i*7-f*0.3),fill=m["txt"],font=ft)
            d.text((240+w+8,y-1),"%.2f BTC" % (wob*9+3),fill=UP,font=ft)
            y+=rowh
        # pulse max bid
        if (f//3)%2==0:
            d.text((700,200-16),"▲ WALL",fill=UP,font=ft)
        frames.append(img.convert("P",palette=Image.ADAPTIVE))
    save(frames,f"{OUT}/orderbook_{mode}.gif",60)

# ================= risk gauge =================
def make_gauge(mode):
    m=DARK if mode=="dark" else LIGHT
    W,H,F=760,200,64
    ft=font(16,True); fs=font(12)
    cx,cy,r=W//2,H-24,140
    frames=[]
    for f in range(F):
        img=Image.new("RGB",(W,H),m["bg"]); d=ImageDraw.Draw(img)
        # dial arc green->gold->red
        for k in range(180):
            a=math.pi+k/180*math.pi
            t=k/180
            col=(int(UP[0]*(1-t)+DOWN[0]*t),int(UP[1]*(1-t)+DOWN[1]*t),int(UP[2]*(1-t)+DOWN[2]*t))
            x=cx+r*math.cos(a); y=cy+r*math.sin(a)
            d.ellipse([x-3,y-3,x+3,y+3],fill=col)
        # ticks
        for k in range(0,181,15):
            a=math.pi+k/180*math.pi
            x1=cx+(r-12)*math.cos(a); y1=cy+(r-12)*math.sin(a)
            x2=cx+r*math.cos(a); y2=cy+r*math.sin(a)
            d.line([x1,y1,x2,y2],fill=m["txt"],width=2)
        # needle swings between low and moderate zone (left-center)
        target=0.28+0.16*math.sin(f/F*2*math.pi)+0.05*math.sin(f/3)
        a=math.pi+target*math.pi
        nx=cx+(r-26)*math.cos(a); ny=cy+(r-26)*math.sin(a)
        d.line([cx,cy,nx,ny],fill=m["txt"],width=4)
        d.ellipse([cx-8,cy-8,cx+8,cy+8],fill=GOLD)
        d.text((cx-r,cy-24),"RISK: LOW",fill=UP,font=ft)
        d.text((cx+r-118,cy-24),"BLOWUP",fill=DOWN,font=ft)
        pct=int(target*100)
        d.text((cx-60,cy-r+30),"RISK APPETITE %d%%" % pct,fill=m["txt"],font=ft)
        d.text((cx-120,H-18),"position sizing ON · stop-loss honored · no revenge trade",fill=m["mut"],font=fs)
        frames.append(img.convert("P",palette=Image.ADAPTIVE))
    save(frames,f"{OUT}/gauge_{mode}.gif",50)

for mode in ("dark","light"):
    make_3d(mode); make_ladder(mode); make_gauge(mode)
for f in sorted(os.listdir(OUT)):
    if f.startswith(("chart3d","orderbook","gauge")):
        print(f,os.path.getsize(os.path.join(OUT,f)))
