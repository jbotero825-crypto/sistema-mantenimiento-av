import ezdxf, math
from ezdxf.render import forms
from ezdxf.math import Vec3
OUT='sistema-bombeo-3d.dxf'
doc=ezdxf.new('R2010',setup=True); doc.units=ezdxf.units.M
msp=doc.modelspace()
L={'FOSAS':8,'TUBERIA_AZUL':5,'TUBERIA_ROJA':1,'FALTANTE':6,'VALVULAS':3,'BOMBA':94,'BIODIGESTOR':84,'MULA':2,'ESTRUCTURA':250,'EJES_TUBERIA':7,'TEXTO':7}
for n,c in L.items(): doc.layers.add(n,color=c)
# plano 2D -> metros (X este, Y norte, Z altura)
X=lambda x: -10.5+(x-333)*0.035 if x<=420 else -7.455+(x-420)*0.0135
Yp=lambda y: -(2.7+(y-447)*0.025 if y<=447 else 2.7+(y-447)*0.012)
HB,HR=0.4,0.75
def P(p): return Vec3(X(p[0]),Yp(p[1]),p[2])
b=lambda x,y:(x,y,HB); r=lambda x,y:(x,y,HR)
def mesh(m,layer): m.render_mesh(msp,dxfattribs={'layer':layer})
def boxm(cx,cy,cz,sx,sy,sz,layer):
    m=forms.cube().scale(sx,sy,sz).translate(cx,cy,cz); mesh(m,layer)
def text(t,p,h=0.35,layer='TEXTO'):
    msp.add_text(t,height=h,dxfattribs={'layer':layer}).set_placement((p[0],p[1],p[2]))
# fosas 5 x 4.6 x 3
W,D,H=5,4.6,3; tw=0.15
FOS={'Fosa 1':-10.5,'Fosa 2':X(1255)}
for n,x0 in FOS.items():
    y0=-2.7; y1=y0-D; cx=x0+W/2; cy=(y0+y1)/2
    boxm(cx,cy,-H-tw/2,W+2*tw,D+2*tw,tw,'FOSAS')
    boxm(cx,y0+tw/2,-H/2,W+2*tw,tw,H,'FOSAS'); boxm(cx,y1-tw/2,-H/2,W+2*tw,tw,H,'FOSAS')
    boxm(x0-tw/2,cy,-H/2,tw,D,H,'FOSAS'); boxm(x0+W+tw/2,cy,-H/2,tw,D,H,'FOSAS')
    text(n,(x0+0.3,y1-0.8,0),0.6)
    text('5 x 4,6 m - 3 m prof.',(x0+0.3,y1-1.5,0),0.35)
# tuberias
def pipe(pts,layer,rad):
    v=[P(p) for p in pts]
    msp.add_polyline3d(v,dxfattribs={'layer':'EJES_TUBERIA'})
    for a,c in zip(v,v[1:]):
        if (c-a).magnitude<1e-4: continue
        mesh(forms.cylinder_2p(16,rad,a,c),layer)
    for p in v: mesh(forms.sphere(12,6,rad*1.05).translate(p.x,p.y,p.z),layer)
RB,RR=0.13,0.10
pipe([(-40,640,2.2),(-40,640,2.6),(-40,560,2.6),b(-40,560),b(-40,40),b(180,40),b(180,340),b(327,340)],'TUBERIA_AZUL',RB)
pipe([b(240,340),b(240,102),b(1960,102)],'TUBERIA_AZUL',RB)
pipe([b(1315,102),b(1315,480),(1315,480,-2.6)],'FALTANTE',RB)
pipe([(180,40,HB),r(180,40),r(1960,40)],'TUBERIA_ROJA',RR)
pipe([r(300,40),r(220,92),r(220,318),r(380,318),r(380,400),r(327,400),(327,400,HB)],'TUBERIA_ROJA',RR)
pipe([r(345,400),r(345,480),(345,480,-2.6)],'TUBERIA_ROJA',RR)
# estructura (lineas negras del dibujo) como bordillos
def curb(pts):
    v=[P((x,y,0)) for x,y in pts]
    for a,c in zip(v,v[1:]):
        mid=(a+c)/2; d=c-a
        if abs(d.x)>abs(d.y): boxm(mid.x,mid.y,0.1,abs(d.x),0.12,0.2,'ESTRUCTURA')
        else: boxm(mid.x,mid.y,0.1,0.12,abs(d.y),0.2,'ESTRUCTURA')
for c in ([[262,420],[262,122],[1228,122]],[[1266,122],[1880,122]],[[262,420],[1040,420]],[[1228,122],[1228,430]],[[1266,122],[1266,430]],[[1266,420],[1630,420]]): curb(c)
# valvulas
VAL={'V1':(380,358,HR,'y',0),'V2':(345,428,HR,'y',0),'V3':(258,40,HR,'x',0),'V4':(110,40,HB,'x',0),'V5':(180,190,HB,'y',0),
     'V6':(240,230,HB,'y',0),'V7':(1315,260,HB,'y',1),'V8':(1390,102,HB,'x',0),'V9':(420,40,HR,'x',1)}
for k,(x,y,h,ax,miss) in VAL.items():
    c=P((x,y,h)); d=Vec3(0.34,0,0) if ax=='x' else Vec3(0,0.34,0)
    lay='FALTANTE' if miss else 'VALVULAS'
    mesh(forms.cone_2p(16,0.24,c-d,c),lay); mesh(forms.cone_2p(16,0.24,c+d,c),lay)
    mesh(forms.cylinder_2p(8,0.03,c,c+Vec3(0,0,0.4)),lay)
    msp.add_circle((c.x,c.y,c.z+0.4),0.16,dxfattribs={'layer':lay})
    text(k+(' (falta)' if miss else ''),(c.x+0.25,c.y+0.25,c.z+0.6),0.3,lay)
# bomba
pc=P((327,370,HB))
mesh(forms.cylinder_2p(24,0.34,pc+Vec3(-0.25,0,0),pc+Vec3(0.25,0,0)),'BOMBA')
mesh(forms.cylinder_2p(20,0.24,pc+Vec3(-0.95,0,0),pc+Vec3(-0.25,0,0)),'BOMBA')
boxm(pc.x-0.3,pc.y,pc.z-0.36,1.5,0.7,0.12,'BOMBA')
text('Bomba de lobulos',(pc.x-1.2,pc.y+0.6,pc.z+0.6),0.3,'BOMBA')
# biodigestor
bx=X(1960)+1.3; by=(Yp(40)+Yp(102))/2
mesh(forms.cylinder_2p(32,1.4,Vec3(bx,by,0),Vec3(bx,by,2.2)),'BIODIGESTOR')
mesh(forms.sphere(32,16,1.4).translate(bx,by,2.2),'BIODIGESTOR')
text('Biodigestor',(bx-1.4,by-1.9,0),0.45,'BIODIGESTOR')
# mula
mx=X(-40); my=Yp(640)-1.05
mesh(forms.cylinder_2p(24,0.8,Vec3(mx,my+1.3,1.55),Vec3(mx,my-1.3,1.55)),'MULA')
boxm(mx,my-0.55,0.6,1.8,4.2,0.3,'MULA'); boxm(mx,my-2.1,1.35,1.8,1.1,1.4,'MULA')
for dx in (-0.9,0.9):
    for dy in (0.8,-0.3,-1.9):
        mesh(forms.cylinder_2p(16,0.35,Vec3(mx+dx-0.12,my+dy,0.35),Vec3(mx+dx+0.12,my+dy,0.35)),'MULA')
text('Mula (carrotanque)',(mx-1.5,my-3.2,0),0.45,'MULA')
doc.set_modelspace_vport(height=30,center=(-4,-1))
doc.saveas(OUT); print('ok')
