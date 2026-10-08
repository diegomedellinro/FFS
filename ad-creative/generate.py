import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SRC, OUT = sys.argv[1], sys.argv[2]
F="/usr/share/fonts/opentype/inter/"
def f(n,s): return ImageFont.truetype(F+n,s)
RED=(255,26,43); WHITE=(255,255,255); PINK=(246,168,196)
src=Image.open(SRC).convert("RGB")

def cover(W,H,focus_y=0.35):
    s=max(W/src.width,H/src.height); im=src.resize((round(src.width*s),round(src.height*s)),Image.LANCZOS)
    x=(im.width-W)//2; y=int((im.height-H)*focus_y); return im.crop((x,y,x+W,y+H))

def grad(W,H,start,end,maxa):
    g=Image.new("L",(1,H))
    for y in range(H):
        t=0 if y<start else min(1,(y-start)/(end-start)); g.putpixel((0,y),int(maxa*t**1.4))
    return g.resize((W,H))

def tracked(d,xy,text,font,fill,track):
    x,y=xy
    for ch in text:
        d.text((x,y),ch,font=font,fill=fill); x+=d.textlength(ch,font=font)+track
    return x

def tw(d,text,font,track=0): return sum(d.textlength(c,font=font)+track for c in text)-track

def make(W,H,name,layout):
    im=cover(W,H,layout.get("focus",0.3))
    dark=Image.new("RGB",(W,H),(11,11,11))
    im=Image.composite(dark,im,grad(W,H,int(H*layout["gs"]),int(H*layout["ge"]),245))
    top=Image.new("L",(W,H),0); ImageDraw.Draw(top).rectangle([0,0,W,int(H*0.16)],fill=150)
    im=Image.composite(dark,im,top.filter(ImageFilter.GaussianBlur(H*0.06)))
    d=ImageDraw.Draw(im); m=int(W*0.065)
    # brand
    tracked(d,(m,m*0.8),"FOOTBALL FRENZY",f("Inter-Bold.otf",int(W*0.026)),WHITE,int(W*0.006))
    d.rectangle([m,m*0.8+W*0.042,m+W*0.06,m*0.8+W*0.046],fill=RED)
    # copy block, bottom-up
    y=H-m
    cta_f=f("Inter-Black.otf",int(W*0.034)); cta="COMPRA AHORA  →"
    bw=tw(d,cta,cta_f,int(W*0.003))+W*0.08; bh=W*0.095
    url_f=f("Inter-Medium.otf",int(W*0.028))
    d.rounded_rectangle([m,y-bh,m+bw,y],radius=bh/2,fill=RED)
    tracked(d,(m+W*0.04,y-bh/2-cta_f.size*0.62),cta,cta_f,WHITE,int(W*0.003))
    d.text((m+bw+W*0.035,y-bh/2-url_f.size*0.6),"footballfrenzy.shop",font=url_f,fill=(220,220,220))
    y-=bh+W*0.05
    sub_f=f("Inter-Medium.otf",int(W*0.034))
    for line in reversed(layout["sub"]):
        y-=sub_f.size*1.3; d.text((m,y),line,font=sub_f,fill=(215,215,215))
    y-=W*0.03
    hf=f("InterDisplay-Black.otf",int(W*layout["hs"]))
    lines=layout["head"]
    for i,(line,col) in enumerate(reversed(lines)):
        y-=hf.size*0.98; d.text((m-W*0.004,y),line,font=hf,fill=col)
    im.save(f"{OUT}/{name}.png",optimize=True); im.convert("RGB").save(f"{OUT}/{name}.jpg",quality=92)

head=[("VÍSTETE",WHITE),("DE ROSA.",PINK)]
make(1080,1080,"ad-1080x1080",dict(gs=.30,ge=.66,hs=.115,head=head,focus=.2,
     sub=["El jersey que todos voltean a ver."]))
make(1080,1350,"ad-1080x1350",dict(gs=.38,ge=.72,hs=.15,head=head,focus=.3,
     sub=["El jersey que todos voltean a ver.","Pide el tuyo hoy."]))
make(1080,1920,"ad-1080x1920",dict(gs=.50,ge=.74,hs=.17,head=head,focus=.3,
     sub=["El jersey que todos voltean a ver.","Pide el tuyo hoy."]))
