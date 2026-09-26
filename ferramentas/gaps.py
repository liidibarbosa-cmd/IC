import pickle,math,collections
from shapely.geometry import LineString,Point,Polygon
from shapely.ops import unary_union
o=pickle.load(open('flat.pkl','rb'))
ox,oy=3895,760
def inreg(p): return 3895<p[0]<3935 and 760<p[1]<805
segs=collections.defaultdict(list)
for x in o:
    if x['kind']=='line' and all(inreg(p) for p in x['pts']) and x['layer']!='001':
        for a,b in zip(x['pts'],x['pts'][1:]):
            segs[x['layer']].append(LineString([(a[0]-ox,a[1]-oy),(b[0]-ox,b[1]-oy)]))
rooms={}
for x in o:
    if x['kind']=='line' and x['layer']=='001' and x.get('type')=='LWPOLYLINE' and all(inreg(p) for p in x['pts']):
        P=Polygon([(p[0]-ox,p[1]-oy) for p in x['pts']])
        rooms[x['handle']]=P
names={'2651E3':'BANHO SUITE MASTER','2651EF':'CLOSET','2651F0':'SUITE MASTER','2651EE':'SUITE 2','2651ED':'HOME OFFICE','2651E1':'BANHO 4','2651E0':'BANHO SUITE 2','2651DF':'BANHO SUITE 1','2651EB':'SUITE 1','2651EC':'CIRCULACAO','2651E8':'COZINHA','2651E9':'A.S.','2651EA':'DESPENSA'}
if __name__=='__main__':
  WL=[l for l in ('ALVENARIA','04','_parede int','02','caixilho','01','03','ABERTURA','_a const_hum') if l in segs]
  for h,P in rooms.items():
    if h not in names: continue
    print('==',names[h],h,'A=%.3f per=%.3f'%(P.area,P.length))
    c=list(P.exterior.coords)
    for a,b in zip(c,c[1:]):
        L=math.dist(a,b)
        if L<0.01: continue
        n=int(L/0.01)
        cover=collections.Counter(); miss=[]
        for i in range(n+1):
            t=i/n; p=Point(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
            hit=None
            for l in WL:
                if any(s.distance(p)<0.004 for s in segs[l]): hit=l;break
            cover[hit]+=1
            if hit is None: miss.append(t*L)
        # gap intervals
        gaps=[];
        for d in miss:
            if gaps and d-gaps[-1][1]<0.025: gaps[-1][1]=d
            else: gaps.append([d,d])
        gaps=[(round(g[0],2),round(g[1],2)) for g in gaps if g[1]-g[0]>0.05]
        print('  edge (%.3f,%.3f)->(%.3f,%.3f) L=%.3f'%(a+b+(L,)),dict(cover),'GAPS',gaps)
