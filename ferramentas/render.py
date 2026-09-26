import pickle,sys,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
o=pickle.load(open('flat.pkl','rb'))
def render(x0,x1,y0,y1,fn,w=20,texts=True,dims=True,hatch=False,layers=None,lw=0.4,fs=4):
    fig=plt.figure(figsize=(w,w*(y1-y0)/(x1-x0)))
    ax=fig.add_axes([0,0,1,1]); ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect('equal'); ax.axis('off')
    cols={}
    import itertools
    pal=itertools.cycle(['k','tab:blue','tab:red','tab:green','tab:orange','tab:purple','tab:brown','tab:pink','tab:olive','tab:cyan'])
    for x in o:
        if layers and x['layer'] not in layers: continue
        if x['kind']=='line':
            xs=[p[0] for p in x['pts']]; ys=[p[1] for p in x['pts']]
            if max(xs)<x0 or min(xs)>x1 or max(ys)<y0 or min(ys)>y1: continue
            c=cols.setdefault(x['layer'],next(pal))
            ax.plot(xs,ys,color=c,lw=lw)
        elif x['kind']=='hatch' and hatch:
            xs=[p[0] for p in x['pts']]; ys=[p[1] for p in x['pts']]
            if not xs or max(xs)<x0 or min(xs)>x1 or max(ys)<y0 or min(ys)>y1: continue
            ax.fill(xs,ys,alpha=0.12,color='tab:gray')
        elif x['kind']=='text' and texts:
            p=x['p']
            if x0<p[0]<x1 and y0<p[1]<y1: ax.text(p[0],p[1],x['text'][:40].replace('\\pxqc;',''),fontsize=fs,color='darkred')
        elif x['kind']=='dim' and dims:
            p=x['p']
            if x0<p[0]<x1 and y0<p[1]<y1: ax.text(p[0],p[1],f"{x['m']:.2f}",fontsize=fs*0.8,color='blue')
    fig.savefig(fn,dpi=100); plt.close(fig)
    return cols
if __name__=='__main__':
    a=list(map(float,sys.argv[1:5])); print(render(*a,sys.argv[5],texts=False,dims=False,lw=0.2))
