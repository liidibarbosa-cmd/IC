import json, math
db=json.load(open('db.json'))
BR={b['name']:b for b in db['tables']['BLOCK_RECORD']['entries']}
BRH={b['handle']:b for b in db['tables']['BLOCK_RECORD']['entries']}
MS=[e for e in db['entities'] if e['ownerBlockRecordSoftId']=='1F']
def bulge_pts(p0,p1,b,n=16):
    if abs(b)<1e-9: return [p0,p1]
    x0,y0=p0;x1,y1=p1
    th=4*math.atan(b); c=math.hypot(x1-x0,y1-y0)
    if c<1e-12: return [p0,p1]
    r=c/(2*math.sin(th/2))
    mx,my=(x0+x1)/2,(y0+y1)/2
    d=r*math.cos(th/2)
    ux,uy=(x1-x0)/c,(y1-y0)/c
    cx,cy=mx-uy*d,my+ux*d
    a0=math.atan2(y0-cy,x0-cx)
    return [(cx+abs(r)*math.cos(a0+th*i/n)*(1 if r>0 else 1), cy+abs(r)*math.sin(a0+th*i/n)) for i in range(n+1)] if r>0 else \
           [(cx+abs(r)*math.cos(a0+th*i/n), cy+abs(r)*math.sin(a0+th*i/n)) for i in range(n+1)]
def arc_pts(c,r,a0,a1,n=24):
    if a1<a0: a1+=2*math.pi
    return [(c[0]+r*math.cos(a0+(a1-a0)*i/n), c[1]+r*math.sin(a0+(a1-a0)*i/n)) for i in range(n+1)]
def mk(T):
    return lambda p: T(p)
def ident(p): return p
def compose(T, ins):
    ip=ins['insertionPoint']; sx=ins.get('xScale',1) or 1; sy=ins.get('yScale',1) or 1; rot=ins.get('rotation',0)
    ex=ins.get('extrusionDirection',{}).get('z',1)
    bp=BR.get(ins['name'],{}).get('basePoint',{'x':0,'y':0})
    cr,sr=math.cos(rot),math.sin(rot)
    def f(p):
        x=(p[0]-bp['x'])*sx; y=(p[1]-bp['y'])*sy
        X=ip['x']+x*cr-y*sr; Y=ip['y']+x*sr+y*cr
        if ex<0: X=-X
        return T((X,Y))
    return f
def walk(ents, T=ident, layer=None, depth=0, out=None, blk=None):
    if out is None: out=[]
    for e in ents:
        L=e.get('layer'); 
        if layer and L=='0': L=layer
        t=e['type']
        polys=[]
        if t=='LINE': polys=[[ (e['startPoint']['x'],e['startPoint']['y']),(e['endPoint']['x'],e['endPoint']['y'])]]
        elif t in('LWPOLYLINE','POLYLINE2D'):
            v=e['vertices']; pts=[]
            closed = (e.get('flag',0)&1)
            n=len(v); rng=range(n if closed else n-1)
            for i in rng:
                a=v[i]; b=v[(i+1)%n]
                seg=bulge_pts((a['x'],a['y']),(b['x'],b['y']),a.get('bulge',0) or 0)
                pts+= seg if not pts else seg[1:]
            if n==1: pts=[(v[0]['x'],v[0]['y'])]
            polys=[pts]
        elif t=='ARC': polys=[arc_pts((e['center']['x'],e['center']['y']),e['radius'],e['startAngle'],e['endAngle'])]
        elif t=='CIRCLE': polys=[arc_pts((e['center']['x'],e['center']['y']),e['radius'],0,2*math.pi,36)]
        elif t=='INSERT':
            b=BR.get(e['name'])
            if b and depth<8:
                walk(b['entities'], compose(T,e), L, depth+1, out, blk or e['name'])
            continue
        elif t in('TEXT','MTEXT'):
            p=e.get('startPoint') or e.get('insertionPoint')
            out.append(dict(kind='text',layer=L,p=T((p['x'],p['y'])),text=e.get('text',''),h=e.get('textHeight',0.2),blk=blk,rot=e.get('rotation',0)))
            continue
        elif t=='HATCH':
            for bp in e.get('boundaryPaths',[]):
                if 'vertices' in bp:
                    v=bp['vertices']; pts=[]
                    for i in range(len(v)):
                        a=v[i]; b2=v[(i+1)%len(v)]
                        seg=bulge_pts((a['x'],a['y']),(b2['x'],b2['y']),a.get('bulge',0) or 0)
                        pts+= seg if not pts else seg[1:]
                    out.append(dict(kind='hatch',layer=L,pts=[T(p) for p in pts],pattern=e.get('patternName'),blk=blk,handle=e['handle']))
                elif 'edges' in bp:
                    pts=[]
                    for ed in bp['edges']:
                        if 'start' in ed and 'end' in ed: pts+= [(ed['start']['x'],ed['start']['y']),(ed['end']['x'],ed['end']['y'])]
                        elif 'center' in ed:
                            a0,a1=ed['startAngle'],ed['endAngle']
                            if not ed.get('isCCW',1): a0,a1=-a1,-a0
                            pts+=arc_pts((ed['center']['x'],ed['center']['y']),ed['radius'],a0,a1)
                    out.append(dict(kind='hatch',layer=L,pts=[T(p) for p in pts],pattern=e.get('patternName'),blk=blk,handle=e['handle'],edges=True))
            continue
        elif t=='DIMENSION':
            out.append(dict(kind='dim',layer=L,p=T((e['textPoint']['x'],e['textPoint']['y'])),m=e.get('measurement'),text=e.get('text'),blk=blk,e=e))
            continue
        for pts in polys:
            out.append(dict(kind='line',layer=L,pts=[T(p) for p in pts],type=t,blk=blk,handle=e.get('handle')))
    return out
def model():
    return walk(MS)
