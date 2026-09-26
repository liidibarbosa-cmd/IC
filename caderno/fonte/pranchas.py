"""Gera caderno.html (5 folhas A3) a partir de dados.json e geometria.json.

Plantas em SVG com escala real: largura em mm = extensão (m) x 1000 / escala.
Imprimir o PDF em A3 sem ajuste de escala.
"""
import json, math, os, html
from shapely.geometry import Polygon, LineString, Point

AQUI = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(AQUI, 'dados.json')))
G = json.load(open(os.path.join(AQUI, 'geometria.json')))
Z = D['zonas']
DATA = '26/09/2026'
REV = 'Nº 00'
CADERNO = 'CADERNO DE DETALHAMENTO DE REVESTIMENTO DE PISO 01/02'
NF = 5

C = dict(bg='#f7f2e8', ink='#22251a', rust='#903f2a', rust_t='#7a3423', olive='#3f422f', olive2='#4f5439',
         band='#ece4d4', cream='#f5e7c4', line='#d8cfbc',
         P01='#e9d6ae', P02='#c7c6a9', PP01='#f4f2ec', NE='#f7f2e8', verde='#cdd5ae', agua='#c5d6d4')
esc = lambda s: html.escape(str(s))
br = lambda v, n=2: f'{v:.{n}f}'.replace('.', ',')


# =============================================================== SVG de planta
class Planta:
    def __init__(self, x0, y0, x1, y1, escala):
        self.x0, self.y0, self.x1, self.y1, self.s = x0, y0, x1, y1, escala
        self.W, self.H = x1 - x0, y1 - y0
        self.el = []
        self.defs = []

    def mm(self, v):        # mm no papel -> m no desenho
        return v * self.s / 1000

    def pt(self, v):        # pt no papel -> m
        return self.mm(v * 0.352778)

    def P(self, p):
        return (round(p[0] - self.x0, 4), round(self.y1 - p[1], 4))

    def path(self, pts, closed=True):
        q = [self.P(p) for p in pts]
        return 'M' + ' L'.join(f'{a},{b}' for a, b in q) + (' Z' if closed else '')

    def add(self, s):
        self.el.append(s)

    def poly(self, pts, holes=(), fill='none', stroke='none', sw=0.1, extra=''):
        d = self.path(pts) + ''.join(' ' + self.path(h) for h in holes)
        self.add(f'<path d="{d}" fill="{fill}" fill-rule="evenodd" stroke="{stroke}" stroke-width="{self.mm(sw)}" {extra}/>')

    def line(self, pts, stroke, sw, dash=None, cap='butt', extra=''):
        da = f' stroke-dasharray="{" ".join(str(self.mm(d)) for d in dash)}"' if dash else ''
        self.add(f'<path d="{self.path(pts, False)}" fill="none" stroke="{stroke}" stroke-width="{self.mm(sw)}" '
                 f'stroke-linecap="{cap}" stroke-linejoin="round"{da} {extra}/>')

    def text(self, p, s, size=5.5, weight=500, fill=C['ink'], anchor='middle', rot=0, ls=0, family='Manrope', italic=False):
        x, y = self.P(p)
        tr = f' transform="rotate({rot} {x} {y})"' if rot else ''
        st = ' font-style="italic"' if italic else ''
        self.add(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{self.pt(size)}" font-weight="{weight}" '
                 f'fill="{fill}" text-anchor="{anchor}" dominant-baseline="middle" letter-spacing="{self.pt(ls)}"{tr}{st}>{esc(s)}</text>')

    def badge(self, p, s, fill=C['olive'], tfill=C['cream'], size=4.6, w_mm=None, h_mm=3.0, round_=True, rot=0):
        x, y = self.P(p)
        w = self.mm(w_mm if w_mm else (2.2 + 0.62 * size * 0.352778 * len(s) * 1.0 + 1.2))
        h = self.mm(h_mm)
        r = h / 2 if round_ else self.mm(0.6)
        tr = f' transform="rotate({rot} {x} {y})"' if rot else ''
        self.add(f'<g{tr}><rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" rx="{r}" fill="{fill}"/>'
                 f'<text x="{x}" y="{y + self.mm(0.1)}" font-family="Manrope" font-size="{self.pt(size)}" font-weight="700" fill="{tfill}" '
                 f'text-anchor="middle" dominant-baseline="middle">{esc(s)}</text></g>')

    def circle_badge(self, p, s, fill=C['rust'], d_mm=4.2, size=4.1):
        x, y = self.P(p)
        r = self.mm(d_mm / 2)
        self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/><text x="{x}" y="{y + self.mm(0.1)}" font-family="Manrope" '
                 f'font-size="{self.pt(size)}" font-weight="700" fill="{C["cream"]}" text-anchor="middle" dominant-baseline="middle">{esc(s)}</text>')

    def diamond(self, p, s, fill=C['olive2'], d_mm=5.0, size=4.0):
        x, y = self.P(p)
        r = self.mm(d_mm / 2)
        self.add(f'<path d="M{x},{y - r} L{x + r},{y} L{x},{y + r} L{x - r},{y} Z" fill="{fill}" stroke="{C["bg"]}" stroke-width="{self.mm(0.3)}"/>'
                 f'<text x="{x}" y="{y + self.mm(0.1)}" font-family="Manrope" font-size="{self.pt(size)}" font-weight="700" '
                 f'fill="{C["cream"]}" text-anchor="middle" dominant-baseline="middle">{esc(s)}</text>')

    def svg(self):
        wmm, hmm = self.W * 1000 / self.s, self.H * 1000 / self.s
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{wmm:.3f}mm" height="{hmm:.3f}mm" '
                f'viewBox="0 0 {self.W:.4f} {self.H:.4f}"><defs>{"".join(self.defs)}</defs>{"".join(self.el)}</svg>'), wmm, hmm


def padroes(pl):
    m = pl.mm
    pl.defs.append(f'<pattern id="pp_{pl.s}" patternUnits="userSpaceOnUse" width="{m(1.6)}" height="{m(1.6)}">'
                   f'<rect width="{m(1.6)}" height="{m(1.6)}" fill="{C["PP01"]}"/>'
                   f'<circle cx="{m(0.4)}" cy="{m(0.4)}" r="{m(0.16)}" fill="#b9b3a3"/>'
                   f'<circle cx="{m(1.2)}" cy="{m(1.2)}" r="{m(0.13)}" fill="#c9c3b3"/></pattern>')
    pl.defs.append(f'<pattern id="ne_{pl.s}" patternUnits="userSpaceOnUse" width="{m(1.4)}" height="{m(1.4)}" patternTransform="rotate(45)">'
                   f'<rect width="{m(1.4)}" height="{m(1.4)}" fill="{C["bg"]}"/>'
                   f'<line x1="0" y1="0" x2="0" y2="{m(1.4)}" stroke="{C["rust"]}" stroke-width="{m(0.18)}"/></pattern>')
    pl.defs.append(f'<pattern id="gr_{pl.s}" patternUnits="userSpaceOnUse" width="{m(2.0)}" height="{m(2.0)}">'
                   f'<rect width="{m(2.0)}" height="{m(2.0)}" fill="{C["verde"]}"/>'
                   f'<path d="M{m(0.5)},{m(0.9)} l{m(0.12)},{-m(0.35)} l{m(0.12)},{m(0.35)} M{m(1.4)},{m(1.8)} l{m(0.12)},{-m(0.35)} l{m(0.12)},{m(0.35)}" '
                   f'fill="none" stroke="#8f9a6a" stroke-width="{m(0.1)}"/></pattern>')


def fill_de(cod, pl):
    return {'P01': C['P01'], 'P02': C['P02'], 'PP01': f'url(#pp_{pl.s})', 'NE': f'url(#ne_{pl.s})'}[cod]


def base(pl, tint=1.0, calcada=True):
    padroes(pl)
    # áreas verdes e piscina
    for v in G['verdes']:
        pl.poly(v, fill=f'url(#gr_{pl.s})', stroke='#8f9a6a', sw=0.1)
    # zonas de piso
    for zid, z in Z.items():
        if zid == 'CAL' and not calcada:
            continue
        pl.poly(z['pts'], z['holes'], fill=fill_de(z['cod'], pl), stroke='none',
                extra=f'fill-opacity="{tint}"' if z['cod'] in ('P01', 'P02') else '')
    pl.poly(G['piscina'], fill=C['agua'], stroke=C['ink'], sw=0.18)
    # divisa e calçada
    if calcada:
        pl.line(G['faixa1'], C['olive2'], 0.1, dash=(1.2, 0.8))
        pl.line(G['faixa2'], C['ink'], 0.13)
        pl.line(G['meiofio'], C['ink'], 0.18)
    lote = G['lote'] + [G['lote'][0]]
    pl.line(lote, C['olive2'], 0.18, dash=(3.0, 0.8, 0.5, 0.8))
    # esquadrias, portas e soleiras
    for L in G['linhas']['soleiras']:
        pl.line(L, C['ink'], 0.08)
    for L in G['linhas']['caixilhos']:
        pl.line(L, C['ink'], 0.13)
    for L in G['linhas']['portas']:
        pl.line(L, C['ink'], 0.1)
    # paredes (faces do DWG poligonizadas)
    for w in G['paredes']:
        pl.poly(w, fill=C['ink'], stroke=C['ink'], sw=0.05)


def rotulo(pl, p, nome, cod, area_txt, rot=0, size=5.3, cod_fill=C['olive'], sub=None):
    """nome + selo do código + área (ou comprimento), empilhados"""
    d = pl.pt(size * 1.55)
    ang = math.radians(rot)
    def off(k):  # desloca ao longo do eixo "vertical" do rótulo (no referencial da planta)
        return (p[0] + math.sin(ang) * k * d, p[1] - math.cos(ang) * k * d)
    lines = [('nome', nome), ('cod', cod), ('area', area_txt)] + ([('sub', sub)] if sub else [])
    n = len(lines)
    for i, (k, s) in enumerate(lines):
        q = off(i - (n - 1) / 2)
        if k == 'nome':
            pl.text(q, s.upper(), size=size, weight=700, rot=-rot, ls=0.35)
        elif k == 'cod':
            pl.badge(q, s, fill=cod_fill, rot=-rot)
        elif k == 'area':
            pl.text(q, s, size=size, weight=500, rot=-rot)
        else:
            pl.text(q, s, size=size * 0.9, weight=500, rot=-rot, fill=C['rust_t'])


# ------------------------------------------------------------ planta de pisos
AREA = {}
for p in D['pisos']:
    for z in p['zonas']:
        AREA[z] = p['area'] if len(p['zonas']) == 1 else None

POS = {  # posição dos rótulos (m, coordenadas locais) e rotação
    'QCA': ((12.27, 38.0), 0), 'CLO': ((8.04, 38.0), 0), 'BCA': ((5.17, 38.0), 90), 'Q02': ((7.74, 34.75), 0),
    'W02': ((7.69, 32.33), 0), 'W01': ((7.69, 30.68), 0), 'Q01': ((7.74, 28.3), 0), 'ESC': ((12.94, 35.13), 0),
    'BEX': ((12.94, 33.18), 0), 'CIR': ((10.55, 32.0), 90), 'COZ': ((7.82, 24.55), 0), 'LAV': ((7.07, 21.3), 0),
    'DEP': ((9.19, 21.3), 90), 'SAL': ((12.6, 23.4), 0), 'GAR': ((7.9, 17.6), 0), 'VAR': ((13.3, 30.1), 0),
    'DEC': ((19.85, 29.4), 0), 'RAM': ((7.2, 12.6), 0), 'COR': ((4.92, 28.2), 90),
}


def folha_pisos():
    pl = Planta(3.6, 5.8, 29.6, 40.6, 125)
    base(pl)
    soleiras(pl)
    nomes = {'QCA': 'Quarto Casal', 'CLO': 'Closet Casal'}
    for zid, (p, rot) in POS.items():
        z = Z[zid]
        if zid in ('QCA', 'CLO'):
            a = 'ver quadro ²'
        else:
            a = br(AREA[zid]) + ' m²'
        nome = nomes.get(zid, z['nome'])
        if zid == 'DEC':
            nome = 'Deck'
        if zid == 'COR':
            rotulo(pl, p, 'Corredor Lateral Externo', 'P02 ou PI01', a, rot=rot, cod_fill=C['rust'], size=4.6)
            continue
        size = 4.6 if zid in ('BCA', 'W01', 'W02', 'BEX', 'DEP', 'LAV', 'CIR') else 5.3
        rotulo(pl, p, nome, z['cod'], a, rot=rot, size=size)
    # rótulos fora do lote com linha de chamada
    for zid, alvo, lab, lines in [('ACE', (16.8, 23.35), (25.2, 24.9), ['Acesso externo lateral', 'PP01', br(AREA['ACE']) + ' m²']),
                                  ('CAL', (19.8, 21.6), (25.3, 15.4), ['Calçada — faixas 1,25 + 1,10', 'PP01', br(AREA['CAL']) + ' m²', 'término A CONFIRMAR'])]:
        pl.line([alvo, (lab[0] - 1.6, lab[1] + 0.9)], C['olive2'], 0.12)
        pl.add(f'<circle cx="{pl.P(alvo)[0]}" cy="{pl.P(alvo)[1]}" r="{pl.mm(0.55)}" fill="{C["olive2"]}"/>')
        rotulo(pl, lab, lines[0], lines[1], lines[2], sub=lines[3] if len(lines) > 3 else None)
    pl.text((19.84, 35.9), 'PISCINA', size=5.3, weight=700, ls=0.35)
    pl.text((19.84, 35.35), 'não pavimentada', size=4.6, weight=400, italic=True)
    for p in [(19.0, 39.39), (24.2, 37.3), (13.9, 15.4), (16.95, 21.05)]:
        pl.text(p, 'ÁREA VERDE', size=4.2, weight=600, fill='#5d6640', ls=0.3)
    pl.text((12.3, 6.7), 'RUA APARECIDA DE FREITAS PINTO', size=5.0, weight=600, fill=C['olive2'], ls=0.6)
    pl.text((27.6, 30.5), 'AVENIDA 3', size=5.0, weight=600, fill=C['olive2'], ls=0.6, rot=-65.07)
    # transições
    for t, p in TPOS.items():
        pl.diamond(p, t)
    return pl


SOLSEG = {'T01': 'P02', 'T02': 'P07', 'T03': 'P05a', 'T04': 'P05b', 'T05': 'P10', 'T06': 'P11', 'T07': 'P03',
          'T08': ((4.191, 15.036), (11.591, 15.036)), 'T09': ((11.591, 15.036), (11.591, 19.536))}


def soleiras(pl):
    for so in D['soleiras']:
        seg = SOLSEG[so['t']]
        a, b = (D['vaos'][seg]['a'], D['vaos'][seg]['b']) if isinstance(seg, str) else seg
        assert abs(math.dist(a, b) - so['comp']) < 0.006, so
        pl.line([a, b], '#8d8475', 1.25)
        pl.line([a, b], '#f1ede4', 0.75)


TPOS = {'T01': (4.74, 20.21), 'T02': (5.616, 21.29), 'T03': (13.49, 27.76), 'T04': (15.266, 25.94),
        'T05': (14.666, 38.06), 'T06': (14.666, 32.99), 'T07': (17.341, 23.455), 'T08': (7.8, 15.036),
        'T09': (11.591, 17.3), 'T10': (15.341, 30.1), 'T11': (19.84, 32.886), 'T12': (22.241, 36.2),
        'T13': (5.47, 10.036), 'T14': (9.941, 24.536)}


# ----------------------------------------------------------- planta de rodapés
def inward(zp, a, b, d=0.055):
    poly = Polygon(zp['pts'], zp['holes'])
    L = math.dist(a, b)
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    for nx, ny in [(-uy, ux), (uy, -ux)]:
        if poly.buffer(1e-4).contains(Point(m[0] + nx * 0.2, m[1] + ny * 0.2)):
            return nx * d, ny * d
    raise ValueError('sem lado interno', a, b)


def runs(tr, vaos):
    a, b = tr['a'], tr['b']
    L = math.dist(a, b)
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    cuts = []
    for v in vaos:
        V = D['vaos'][v['id']]
        if v['trecho'] != tr['nome']:
            continue
        t0 = (V['a'][0] - a[0]) * ux + (V['a'][1] - a[1]) * uy
        t1 = (V['b'][0] - a[0]) * ux + (V['b'][1] - a[1]) * uy
        cuts.append((min(t0, t1), max(t0, t1)))
    cuts.sort()
    out, t = [], 0.0
    for c0, c1 in cuts:
        if c0 > t + 1e-6:
            out.append((t, c0))
        t = max(t, c1)
    if t < L - 1e-6:
        out.append((t, L))
    return [((a[0] + ux * s0, a[1] + uy * s0), (a[0] + ux * s1, a[1] + uy * s1)) for s0, s1 in out]


VPOS = {  # deslocamento do selo do vão (m) em relação ao meio do vão
    'P01': (0, -0.55), 'P02': (0, -0.55), 'P03': (0.55, 0), 'P04': (0.0, 0), 'P05a': (0, 0.55), 'P05b': (0.62, 0),
    'P06sal': (0, -0.55), 'P06coz': (0, 0.0), 'P06dep': (0.0, 0), 'P06q01': (0, 0), 'P06w01': (0, 0),
    'P06q02': (0, 0), 'P06w02': (0, 0), 'P06qca': (0, 0), 'P06esc': (0, 0), 'P07': (-0.62, 0),
    'P08': (0, 0), 'P09': (0, 0), 'P10': (0.62, 0), 'P11': (0.62, 0)}


def folha_rodapes():
    pl = Planta(3.6, 14.4, 24.4, 40.6, 100)
    base(pl, tint=0.55, calcada=False)
    cor = {'R01': C['rust'], 'R02': '#2f5f55'}
    for r in D['rodapes']:
        zp = Z[r['zona']]
        for tr in r['trechos']:
            nx, ny = inward(zp, tr['a'], tr['b'])
            for a, b in runs(tr, r['vaos']):
                a2, b2 = (a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny)
                pl.line([a2, b2], cor[r['cod']], 0.75)
                for q in (a2, b2):   # marca de início/fim de trecho
                    t = 0.13 / 0.055
                    pl.line([(q[0] - nx * 0.4, q[1] - ny * 0.4), (q[0] + nx * t, q[1] + ny * t)], cor[r['cod']], 0.22)
    for vid, v in D['vaos'].items():
        m = ((v['a'][0] + v['b'][0]) / 2, (v['a'][1] + v['b'][1]) / 2)
        dx, dy = VPOS[vid]
        p = (m[0] + dx, m[1] + dy)
        pl.circle_badge(p, v['cod'], d_mm=4.0, size=3.9)
        vert = abs(v['a'][0] - v['b'][0]) < 1e-6
        q = (p[0], p[1] - 0.36) if not vert else (p[0], p[1] - 0.36)
        qx, qy = pl.P(q)
        w, h = pl.mm(6.2), pl.mm(2.5)
        pl.add(f'<rect x="{qx - w / 2}" y="{qy - h / 2}" width="{w}" height="{h}" rx="{pl.mm(0.5)}" fill="{C["bg"]}" fill-opacity="0.92"/>')
        pl.text(q, br(v['larg']), size=4.6, weight=700, fill=C['rust_t'])
    for r in D['rodapes']:
        zid = r['zona']
        if zid not in POS:
            continue
        p, rot = POS[zid]
        nome = Z[zid]['nome'] if zid != 'DEC' else 'Deck'
        size = 4.6 if zid in ('BCA', 'W01', 'W02', 'BEX', 'DEP', 'LAV', 'CIR') else 5.3
        if zid in ('SAL',):
            p = (13.0, 23.2)
        rotulo(pl, p, nome, r['cod'], br(r['liquido']) + ' m', rot=rot, size=size,
               cod_fill=cor[r['cod']])
    rotulo(pl, POS['COR'][0], 'Corredor Lateral Externo', 'sem rodapé', 'P02 ou PI01', rot=90, size=4.6, cod_fill=C['olive2'])
    pl.text((19.84, 35.9), 'PISCINA', size=5.3, weight=700, ls=0.35)
    pl.text((19.84, 35.3), 'sem rodapé na borda', size=4.6, weight=400, italic=True)
    pl.text((8.0, 15.5), 'frente aberta — sem rodapé', size=4.4, weight=500, italic=True, fill=C['olive2'])
    pl.text((11.9, 17.3), 'lateral aberta — sem rodapé', size=4.4, weight=500, italic=True, fill=C['olive2'], rot=90)
    return pl


# ==================================================================== HTML
def fonts_css():
    out = []
    for w in (300, 400, 500, 600, 700):
        out.append(f"@font-face{{font-family:'Manrope';font-weight:{w};src:url('fonts/manrope-latin-{w}-normal.woff2') format('woff2');}}")
    for w in (300, 400):
        out.append(f"@font-face{{font-family:'Outfit';font-weight:{w};src:url('fonts/outfit-latin-{w}-normal.woff2') format('woff2');}}")
    return '\n'.join(out)


CSS = """
@page { size: 297mm 420mm; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: %(bg)s; }
body { font-family: 'Manrope', sans-serif; color: %(ink)s; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.sheet { width: 297mm; height: 420mm; position: relative; overflow: hidden; background: %(bg)s; page-break-after: always; break-after: page; }
.sheet:last-child { page-break-after: auto; break-after: auto; }
.abs { position: absolute; }
.disp { font-family: 'Outfit', sans-serif; font-weight: 300; }
.lbl { font-size: 6.5pt; font-weight: 700; letter-spacing: 2.2pt; color: %(rust_t)s; text-transform: uppercase; }
.small { font-size: 6.4pt; line-height: 1.45; }
/* carimbo */
.car { position: absolute; left: 174.9mm; width: 112.2mm; background: %(olive)s; border-radius: 4.6mm; color: %(cream)s; padding: 5.2mm 5.2mm 4.6mm 5.2mm; }
.car .logo { height: 7.4mm; }
.car .fl { position: absolute; right: 5.2mm; top: 5.0mm; text-align: right; }
.car .fl .k { font-size: 5.6pt; letter-spacing: 2.2pt; }
.car .fl .v { font-family: 'Outfit'; font-weight: 300; font-size: 29pt; line-height: 1; margin-top: 0.8mm; letter-spacing: -0.5pt; }
.car .cad { font-size: 5.1pt; letter-spacing: 1.1pt; margin-top: 2.2mm; opacity: .92; font-weight: 600; max-width: 62mm; line-height: 1.45; }
.car.cp .row { margin-top: 1.9mm; } .car.cp .tipo { margin-top: 2.3mm; } .car.cp .tipo .v { font-size: 13.5pt; }
.car .k { font-size: 5.2pt; letter-spacing: 0.5pt; text-transform: uppercase; opacity: .95; }
.car .tipo .k { letter-spacing: 2.2pt; }
.car .tipo { margin-top: 3.2mm; }
.car .tipo .v { font-family: 'Outfit'; font-weight: 300; font-size: 14.5pt; line-height: 1.12; margin-top: 0.6mm; }
.car .v { font-size: 7.2pt; line-height: 1.3; }
.car .row { display: flex; margin-top: 2.6mm; }
.car .row > div { flex: 1; }
.car .btn { position: absolute; left: 5.2mm; right: 5.2mm; bottom: 4.6mm; height: 6.8mm; border-radius: 3.4mm; background: %(rust)s;
  display: flex; align-items: center; justify-content: center; font-size: 6.6pt; font-weight: 700; letter-spacing: 0.5pt; color: %(cream)s; }
/* tabelas */
table { border-collapse: separate; border-spacing: 0; width: 100%%; }
th { background: %(olive)s; color: %(cream)s; font-size: 6.1pt; font-weight: 700; letter-spacing: 0.3pt; text-align: left; padding: 1.9mm 1.6mm; text-transform: uppercase; }
th:first-child { border-top-left-radius: 2.2mm; } th:last-child { border-top-right-radius: 2.2mm; }
td { font-size: 7.0pt; padding: 1.25mm 1.5mm; border-bottom: 0.25mm solid %(line)s; vertical-align: top; line-height: 1.32; }
td.n, th.n { text-align: right; white-space: nowrap; }
td[data-dif] { color: #903f2a; font-weight: 700; }
tr.sec td { background: %(band)s; color: %(rust_t)s; font-size: 6.3pt; font-weight: 700; letter-spacing: 1.9pt; border-bottom: none; padding: 1.7mm 1.6mm; }
tr.sub td { font-weight: 700; background: #f1ead9; }
tr.tot td { font-weight: 700; border-bottom: none; font-size: 7.4pt; }
.cb { display: inline-flex; align-items: center; justify-content: center; min-width: 5.6mm; height: 5.6mm; border-radius: 2.8mm;
  background: %(rust)s; color: %(cream)s; font-size: 5.0pt; font-weight: 700; padding: 0 1.1mm; }
.cb.ol { background: %(olive)s; } .cb.gr { background: #2f5f55; } .cb.ne { background: transparent; color: %(rust)s; border: 0.3mm solid %(rust)s; }
.tag { display: inline-block; font-size: 5.2pt; font-weight: 700; letter-spacing: 0.3pt; padding: 0.35mm 1.1mm; border-radius: 1.2mm; margin: 0 0.6mm 0.6mm 0; white-space: nowrap; }
.tag.Arquivo { background: #dfe3cf; color: #3f422f; } .tag.Informado { background: #f3dcc9; color: %(rust_t)s; } .tag.Obra { background: %(rust)s; color: %(cream)s; }
.tag.Decisão { background: #f5e7c4; color: %(rust_t)s; border: 0.25mm solid %(rust_t)s; }
.ttl { font-family: 'Outfit'; font-weight: 300; font-size: 12.5pt; }
.head .lbl { font-size: 6.9pt; letter-spacing: 2.6pt; }
.head h1 { font-family: 'Outfit'; font-weight: 300; font-size: 34pt; letter-spacing: -0.4pt; line-height: 1.1; margin-top: 1.2mm; }
.notes h4 { font-size: 6.5pt; font-weight: 700; letter-spacing: 2.2pt; color: %(rust_t)s; text-transform: uppercase; margin: 3.4mm 0 1.6mm; }
.notes ol { list-style: none; }
.notes li { display: flex; font-size: 6.5pt; line-height: 1.42; margin-bottom: 1.1mm; }
.notes li b.nn { color: %(rust_t)s; min-width: 5.6mm; font-weight: 700; }
.normas { position: absolute; left: 10mm; width: 159.1mm; background: %(cream)s; border-radius: 4.6mm; padding: 6.5mm 7.5mm; }
.normas table td { border: none; padding: 0.9mm 0; font-size: 6.9pt; }
.leg .it { display: flex; align-items: center; margin-top: 2.3mm; font-size: 7.2pt; line-height: 1.25; }
.leg .sw { width: 7mm; height: 4.6mm; border-radius: 1mm; margin-right: 2.4mm; flex: none; border: 0.2mm solid #b8ae97; }
.leg .ln { width: 7mm; height: 0; margin-right: 2.4mm; flex: none; }
""" % C


def carimbo(folha, tipo, escala, top, height):
    logo = 'logo_duas.png'
    return f"""
<div class="car{' cp' if height < 85 else ''}" style="top:{top}mm;height:{height}mm">
  <img class="logo" src="{logo}">
  <div class="fl"><div class="k">FOLHA</div><div class="v">{folha:02d}/{NF:02d}</div></div>
  <div class="cad">{esc(CADERNO)}</div>
  <div class="tipo"><div class="k">TIPO</div><div class="v">{esc(tipo)}</div></div>
  <div class="row"><div><div class="k">OBRA</div><div class="v">Design de interiores de casa unifamiliar térrea</div></div></div>
  <div class="row"><div><div class="k">CLIENTES</div><div class="v">Ivan e Carol</div></div><div><div class="k">ENDEREÇO</div><div class="v">Nova Odessa, SP</div></div></div>
  <div class="row"><div><div class="k">ARQ. RESPONSÁVEL</div><div class="v">Lidiane Barbosa<br>CAU A290220-6</div></div>
       <div><div class="k">ARQ. CORRESPONSÁVEL</div><div class="v">Isadora Ferrari<br>CAU A269382-8</div></div></div>
  <div class="row"><div><div class="k">DATA</div><div class="v">{DATA}</div></div>
       <div style="display:flex"><div style="flex:0 0 20mm"><div class="k">REVISÃO</div><div class="v">{REV}</div></div><div><div class="k">ESCALA</div><div class="v">{esc(escala)}</div></div></div></div>
  <div class="btn">CONFERIR AS MEDIDAS NO LOCAL</div>
</div>"""


def escala_bar(escala):
    mm_per_m = 1000 / escala
    w = 3 * mm_per_m
    segs = ''.join(f'<rect x="{i * mm_per_m}" y="0" width="{mm_per_m}" height="1.5" fill="{C["ink"] if i % 2 == 0 else C["bg"]}" stroke="{C["ink"]}" stroke-width="0.25"/>' for i in range(3))
    nums = ''.join(f'<span style="position:absolute;left:{i * mm_per_m}mm;transform:translateX(-50%)">{i}</span>' for i in range(3)) + \
        f'<span style="position:absolute;left:{w}mm;transform:translateX(-50%);white-space:nowrap">3 m</span>'
    return (f'<svg width="{w + 0.5}mm" height="2mm" viewBox="-0.25 -0.25 {w + 0.5} 2" style="display:block;margin-top:2.4mm">{segs}</svg>'
            f'<div style="position:relative;height:3mm;font-size:5.6pt;margin-top:1.1mm;width:{w}mm">{nums}</div>')


def pisos_totais():
    sub = {}
    for p in D['pisos']:
        sub[p['cod']] = round(sub.get(p['cod'], 0) + p['area'], 2)
    return sub


def folha1():
    pl = folha_pisos()
    svg, wmm, hmm = pl.svg()
    left = 10 + (235 - wmm) / 2
    top = 10 + (307 - hmm) / 2
    sub = pisos_totais()
    P = D['produtos']
    leg = f"""
<div class="abs leg" style="left:250.5mm;top:10mm;width:37mm">
  <div class="lbl">Legenda</div>
  <div class="it"><div class="sw" style="background:{C['P01']}"></div><div><b>P01</b> Santorini OFW NAT 90 × 90</div></div>
  <div class="it"><div class="sw" style="background:{C['P02']}"></div><div><b>P02</b> Santorini SGR HARD 90 × 90</div></div>
  <div class="it"><div class="sw" style="background:{C['PP01']};background-image:radial-gradient(#b9b3a3 0.35mm, transparent 0.4mm);background-size:1.6mm 1.6mm"></div><div><b>PP01</b> Pedra portuguesa branca</div></div>
  <div class="it"><div class="sw" style="background:repeating-linear-gradient(45deg,{C['bg']} 0 0.8mm,{C['rust']} 0.8mm 0.95mm)"></div><div>A definir: P02 ou PI01 (intertravado drenante)</div></div>
  <div class="it"><div class="sw" style="background:{C['verde']}"></div><div>Área verde (sem piso)</div></div>
  <div class="it"><div class="sw" style="background:{C['agua']}"></div><div>Piscina</div></div>
  <div class="it"><svg width="7mm" height="5mm" viewBox="0 0 7 5" style="margin-right:2.4mm;flex:none"><path d="M3.5,0 L6,2.5 L3.5,5 L1,2.5Z" fill="{C['olive2']}"/></svg><div>Transição de piso (folha 05/05)</div></div>
  <div class="it"><svg width="7mm" height="3mm" viewBox="0 0 7 3" style="margin-right:2.4mm;flex:none"><line x1="0" y1="1.5" x2="7" y2="1.5" stroke="#8d8475" stroke-width="1.25"/><line x1="0" y1="1.5" x2="7" y2="1.5" stroke="#f1ede4" stroke-width="0.75"/></svg><div>Soleira mármore Itaúnas, baguete 5 cm</div></div>
  <div class="it"><svg width="7mm" height="3mm" viewBox="0 0 7 3" style="margin-right:2.4mm;flex:none"><line x1="0" y1="1.5" x2="7" y2="1.5" stroke="{C['olive2']}" stroke-width="0.25" stroke-dasharray="3 .8 .5 .8"/></svg><div>Divisa do lote</div></div>
  <div class="lbl" style="margin-top:7mm">Escala</div>
  <div class="disp" style="font-size:21pt;margin-top:1.4mm">1/125</div>
  {escala_bar(125)}
  <div class="small" style="margin-top:2.2mm;color:{C['olive2']}">Imprimir em A3 sem ajuste de escala.</div>
  <div class="small" style="margin-top:6mm">² Quarto Casal + Closet Casal: 28,70 m² no conjunto.</div>
</div>"""
    rows = ''.join(f"""<tr><td><span class="cb {'ne' if c == 'NE' else 'ol'}">{'—' if c == 'NE' else c}</span></td><td>{esc(P[c]['produto'] if c != 'NE' else 'Corredor Lateral Externo — P02 ou PI01 (a definir)')}</td><td class="n">{br(sub[c])}</td></tr>"""
                   for c in ('P01', 'P02', 'PP01', 'NE'))
    tot = round(sub['P01'] + sub['P02'] + sub['PP01'] + sub['NE'], 2)
    R = D['rod_total']
    t1 = f"""
<div class="abs" style="left:10mm;top:322mm;width:77mm">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:1.6mm"><span class="ttl">Pisos</span><span style="font-size:5.6pt;color:{C['olive2']}">áreas em m²</span></div>
  <table><tr><th>Cód.</th><th>Produto</th><th class="n">Área</th></tr>{rows}
  <tr class="tot"><td colspan="2">Total geral</td><td class="n">{br(tot)}</td></tr></table>
</div>
<div class="abs" style="left:92mm;top:322mm;width:77mm">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:1.6mm"><span class="ttl">Rodapés</span><span style="font-size:5.6pt;color:{C['olive2']}">metros lineares</span></div>
  <table><tr><th>Cód.</th><th>Rodapé (h = 8 cm)</th><th class="n">Líquido</th></tr>
  <tr><td><span class="cb">R01</span></td><td>Santorini OFW NAT — mesmo piso P01</td><td class="n">{br(R['R01'])}</td></tr>
  <tr><td><span class="cb gr">R02</span></td><td>Santorini SGR HARD — mesmo piso P02</td><td class="n">{br(R['R02'])}</td></tr>
  <tr class="tot"><td colspan="2">Total</td><td class="n">{br(R['R01'] + R['R02'])}</td></tr></table>
  <div style="font-size:5.6pt;color:{C['olive2']};margin-top:1.4mm;line-height:1.4">Trechos e memória de cálculo nas folhas 03/05 e 04/05. Sem rodapé em PP01 e no Corredor Lateral Externo.</div>
</div>"""
    return f"""<section class="sheet">
<div class="abs" style="left:{left:.2f}mm;top:{top:.2f}mm">{svg}</div>{leg}{t1}
{carimbo(1, 'Planta de especificação de pisos', '1/125', 321.7, 90.5)}</section>"""


def tags(lst):
    return ''.join(f'<span class="tag {t}">{t}</span>' for t in lst)


LEG_CONTROLE = ('Controle dos dados: <span class="tag Arquivo">Arquivo</span> confirmado no arquivo · <span class="tag Informado">Informado</span> '
                'informado pela arquitetura · <span class="tag Obra">Obra</span> conferir em obra · <span class="tag Decisão">Decisão</span> decisão da arquitetura.')


def folha2():
    P = D['produtos']
    sub = pisos_totais()
    rows = ''
    nomes = {'P01': 'P01 · Porcelanato Santorini OFW NAT — Portinari', 'P02': 'P02 · Porcelanato Santorini SGR HARD — Portinari',
             'PP01': 'PP01 · Pedra portuguesa branca', 'NE': 'A definir — P02 (Santorini SGR HARD) ou PI01 (piso intertravado drenante)'}
    for c in ('P01', 'P02', 'PP01', 'NE'):
        rows += f'<tr class="sec"><td colspan="9">{esc(nomes[c]).upper()}</td></tr>'
        for p in [x for x in D['pisos'] if x['cod'] == c]:
            pr = P[c]
            cb = "<span class='cb ne' style='font-size:4.2pt'>P02/PI01</span>" if c == 'NE' else f"<span class='cb ol'>{c}</span>"
            rows += (f"<tr><td>{cb}</td><td>{esc(p['ambiente'])}</td>"
                     f"<td>{esc(pr['produto'])}</td><td>{esc(pr['fabricante'])}</td><td style='white-space:nowrap'>{esc(pr['formato'])}</td>"
                     f"<td>{esc(pr['acabamento'])}</td><td>{esc(pr['rejunte'])}</td>"
                     f"<td class='n'><b>{br(p['area'])}</b></td><td>{tags(p['controle'])}</td></tr>")
        lab = 'Subtotal ' + (c if c != 'NE' else 'a definir (P02 ou PI01)')
        rows += f"<tr class='sub'><td></td><td colspan='6'>{lab}</td><td class='n'>{br(sub[c])}</td><td></td></tr>"
    tot = round(sum(sub.values()), 2)
    rows += f"<tr class='tot'><td></td><td colspan='6'>TOTAL GERAL (P01 + P02 + PP01 + a definir) — cada ambiente contado uma vez</td><td class='n'>{br(tot)}</td><td></td></tr>"

    def ficha(c, titulo):
        linhas = ''.join(f"<tr><td style='width:19mm;color:{C['rust_t']};font-weight:700;font-size:6.1pt'>{esc(k).upper()}</td>"
                         f"<td style='font-size:6.6pt'>{esc(v)}</td></tr>" for k, v in P[c]['spec'])
        return (f"<div style='flex:1'><div style='display:flex;align-items:center;gap:2mm;margin-bottom:1.2mm'>"
                f"<span class='cb ol'>{c}</span><span class='ttl' style='font-size:10.5pt'>{esc(titulo)}</span></div>"
                f"<table>{linhas}</table></div>")
    fichas = ficha('P01', 'Santorini OFW NAT 90 × 90') + ficha('P02', 'Santorini SGR HARD 90 × 90')
    ex = D['extras']
    return f"""<section class="sheet">
<div class="abs head" style="left:10mm;top:10mm"><div class="lbl">Pisos e rodapés · Revisão 00</div><h1>Quadro de pisos</h1></div>
<div class="abs" style="left:10mm;top:33mm;width:277mm">
<table>
<colgroup><col style="width:17mm"><col style="width:50mm"><col style="width:44mm"><col style="width:22mm"><col style="width:24mm"><col style="width:27mm"><col><col style="width:14mm"><col style="width:28mm"></colgroup>
<tr><th>Cód.</th><th>Ambiente</th><th>Produto</th><th>Fabricante</th><th>Formato</th><th>Acabamento</th><th>Rejunte</th><th class="n">Área m²</th><th>Controle</th></tr>
{rows}
</table>
<div class="lbl" style="margin:5mm 0 2.4mm">Especificação dos porcelanatos — dados do fabricante</div>
<div style="display:flex;gap:8mm">{fichas}</div>
</div>
<div class="normas notes" style="top:332mm;height:78.1mm;display:flex;gap:6mm;padding-top:4.5mm">
<div style="flex:1"><h4 style="margin-top:0">Critérios</h4><ol>
<li><b class="nn">1</b><span>Dados técnicos dos porcelanatos pelos links do fabricante informados pela arquitetura (Portinari). Conferir na ficha técnica vigente antes da compra.</span></li>
<li><b class="nn">2</b><span>Rejunte: cor Corda e junta seca, conforme o fabricante. O tipo da argamassa de rejuntamento (NBR 14992) é proposta e depende da aprovação da arquitetura.</span></li>
<li><b class="nn">3</b><span>Áreas pela face interna das paredes, sem soleiras. Nas divergências entre documentos, adotado o maior valor.</span></li>
</ol></div>
<div style="flex:1"><h4 style="margin-top:0">&nbsp;</h4><ol>
<li><b class="nn">4</b><span>Deck com as faixas de 1,00 m sob o beiral. Piscina não pavimentada.</span></li>
<li><b class="nn">5</b><span>Calçada: faixas 1,25 + 1,10 = 2,35 m, sem o meio-fio (com ele: {br(ex['calcada_com_meiofio'])} m²). Término junto à Av. 3 A CONFIRMAR. Rampa: valor informado; pela geometria, {br(ex['rampa_geo'])} m².</span></li>
<li><b class="nn">6</b><span>Quantitativos líquidos, sem perdas de compra. Níveis não considerados.</span></li>
</ol></div><div class="small" style="position:absolute;left:7.5mm;right:7.5mm;bottom:5.5mm">{LEG_CONTROLE}</div></div>
{carimbo(2, 'Quadro de pisos', 'Sem escala', 332.0, 78.1)}
</section>"""


def folha3():
    pl = folha_rodapes()
    svg, wmm, hmm = pl.svg()
    left = 10 + (235 - wmm) / 2
    top = 10 + (307 - hmm) / 2
    R = D['rod_total']
    leg = f"""
<div class="abs leg" style="left:250.5mm;top:10mm;width:37mm">
  <div class="lbl">Legenda</div>
  <div class="it"><div class="ln" style="border-top:0.75mm solid {C['rust']}"></div><div><b>R01</b> Rodapé Santorini OFW NAT, h = 8 cm</div></div>
  <div class="it"><div class="ln" style="border-top:0.75mm solid #2f5f55"></div><div><b>R02</b> Rodapé Santorini SGR HARD, h = 8 cm</div></div>
  <div class="it"><svg width="7mm" height="4mm" viewBox="0 0 7 4" style="margin-right:2.4mm;flex:none"><line x1="0" y1="2.6" x2="4.2" y2="2.6" stroke="{C['rust']}" stroke-width="0.75"/><line x1="4.1" y1="3.2" x2="4.1" y2="0.8" stroke="{C['rust']}" stroke-width="0.25"/></svg><div>Início / fim de trecho de rodapé</div></div>
  <div class="it"><svg width="7mm" height="5mm" viewBox="0 0 7 5" style="margin-right:2.4mm;flex:none"><circle cx="3.5" cy="2.5" r="2.1" fill="{C['rust']}"/></svg><div>Vão de porta descontado — largura do DWG (m)</div></div>
  <div class="it"><div class="sw" style="background:{C['bg']}"></div><div>Face de parede sem rodapé</div></div>
  <div class="small" style="margin-top:3mm">O rodapé é do mesmo revestimento do piso do ambiente onde está instalado. Janelas não são descontadas.</div>
  <div class="lbl" style="margin-top:7mm">Escala</div>
  <div class="disp" style="font-size:21pt;margin-top:1.4mm">1/100</div>
  {escala_bar(100)}
  <div class="small" style="margin-top:2.2mm;color:{C['olive2']}">Imprimir em A3 sem ajuste de escala.</div>
</div>"""
    cad = D['caderno_larg']
    vrows = ''
    seen = {}
    for vid, v in D['vaos'].items():
        seen.setdefault(v['cod'], []).append(v['larg'])
    for cod, ls in seen.items():
        dw = ' / '.join(sorted({br(x) for x in ls}))
        cd = br(cad[cod])
        dif = '' if all(abs(x - cad[cod]) < 1e-6 for x in ls) else ' data-dif="1"'
        pd = 'padding:0.45mm 1.5mm'
        vrows += (f"<tr><td style='{pd}'><span class='cb' style='height:4.4mm;min-width:4.4mm;font-size:4.6pt'>{cod}</span></td>"
                  f"<td class='n' style='{pd}'{dif}>{dw}</td><td class='n' style='{pd}'>{cd}</td><td class='n' style='{pd}'>{len(ls)}</td></tr>")
        dif = ''
    t1 = f"""
<div class="abs" style="left:10mm;top:322mm;width:77mm">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:1.6mm"><span class="ttl">Vãos descontados</span><span style="font-size:5.6pt;color:{C['olive2']}">medidas em metros</span></div>
  <table style="font-size:6pt"><tr><th>Cód.</th><th class="n">Vão DWG</th><th class="n">Quadro esq.</th><th class="n">Qtd.</th></tr>{vrows}</table>
</div>
<div class="abs" style="left:92mm;top:322mm;width:77mm">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:1.6mm"><span class="ttl">Rodapés</span><span style="font-size:5.6pt;color:{C['olive2']}">metros lineares</span></div>
  <table><tr><th>Cód.</th><th>Rodapé (h = 8 cm)</th><th class="n">Líquido</th></tr>
  <tr><td><span class="cb">R01</span></td><td>Santorini OFW NAT</td><td class="n">{br(R['R01'])}</td></tr>
  <tr><td><span class="cb gr">R02</span></td><td>Santorini SGR HARD</td><td class="n">{br(R['R02'])}</td></tr>
  <tr class="tot"><td colspan="2">Total</td><td class="n">{br(R['R01'] + R['R02'])}</td></tr></table>
  <div style="font-size:5.6pt;color:{C['olive2']};margin-top:1.6mm;line-height:1.45">Descontos pelos vãos do DWG (orientação da arquitetura). Em vermelho, vão do DWG diferente do Quadro de Esquadrias Rev. 01. P04 (4,20) não está desenhada no DWG: largura informada.</div>
</div>"""
    return f"""<section class="sheet">
<div class="abs" style="left:{left:.2f}mm;top:{top:.2f}mm">{svg}</div>{leg}{t1}
{carimbo(3, 'Planta de rodapés', '1/100', 321.7, 90.5)}</section>"""


def folha4():
    rows = ''
    nomes = {'R01': 'R01 · Rodapé Porcelanato Santorini OFW NAT · h = 8 cm', 'R02': 'R02 · Rodapé Porcelanato Santorini SGR HARD · h = 8 cm'}
    for c in ('R01', 'R02'):
        rows += f'<tr class="sec"><td colspan="8">{esc(nomes[c]).upper()}</td></tr>'
        for r in [x for x in D['rodapes'] if x['cod'] == c]:
            tr = ' + '.join(f"{t['nome']} {br(t['L'])}" for t in r['trechos'])
            vs = ' + '.join(f"{v['cod']} {br(v['larg'])}" for v in r['vaos']) or '—'
            obs = ('<div style="font-size:5.8pt;color:#4f5439;margin-top:0.6mm">' + esc(r['obs']) + '</div>') if r['obs'] else ''
            rows += (f"<tr><td><span class='cb {'gr' if c == 'R02' else ''}'>{c}</span></td><td>{esc(r['ambiente'])}"
                     f"{obs}</td>"
                     f"<td style='font-size:6.3pt'>{esc(tr)}</td><td class='n'>{br(r['soma'])}</td>"
                     f"<td style='font-size:6.3pt'>{esc(vs)}</td><td class='n'>{br(r['desc'])}</td><td class='n'><b>{br(r['liquido'])}</b></td>"
                     f"<td>{tags(['Arquivo'] + (['Informado'] if any(v['cod'] == 'P04' for v in r['vaos']) or r['zona'] in ('DEC', 'CIR') else []))}</td></tr>")
        t = D['rod_total'][c]
        rows += f"<tr class='sub'><td></td><td colspan='5'>Subtotal {c}</td><td class='n'>{br(t)}</td><td></td></tr>"
    R = D['rod_total']
    rows += f"<tr class='tot'><td></td><td colspan='5'>TOTAL GERAL DE RODAPÉS (R01 + R02)</td><td class='n'>{br(R['R01'] + R['R02'])}</td><td></td></tr>"
    return f"""<section class="sheet">
<div class="abs head" style="left:10mm;top:10mm"><div class="lbl">Pisos e rodapés · Revisão 00</div><h1>Memória de cálculo dos rodapés</h1></div>
<div class="abs" style="left:10mm;top:33mm;width:277mm">
<table>
<colgroup><col style="width:10mm"><col style="width:40mm"><col><col style="width:13mm"><col style="width:40mm"><col style="width:13mm"><col style="width:15mm"><col style="width:27mm"></colgroup>
<tr><th>Cód.</th><th>Ambiente</th><th>Trechos de parede (m) — posição na planta</th><th class="n">Soma</th><th>Vãos de porta descontados (DWG)</th><th class="n">Vãos</th><th class="n">Líquido</th><th>Controle</th></tr>
{rows}
</table>
</div>
<div class="normas notes" style="top:332mm;height:78.1mm;display:flex;gap:6mm;padding-top:4.5mm">
<div style="flex:1"><h4 style="margin-top:0">Regra de cálculo</h4><ol>
<li><b class="nn">1</b><span>Rodapé líquido = soma dos trechos de parede − vãos de porta aplicáveis. Janelas não são descontadas. Cada face de parede entra uma única vez; as duas faces de uma mesma parede pertencem a ambientes diferentes.</span></li>
<li><b class="nn">2</b><span>Material do rodapé = piso do ambiente: P01 → R01 (Santorini OFW NAT); P02 → R02 (Santorini SGR HARD). Altura 8 cm (informada), rejunte igual ao do piso. Sem rodapé em PP01 (rampa, acesso externo e calçada) e no Corredor Lateral Externo.</span></li>
<li><b class="nn">3</b><span>Trechos sem rodapé: faces abertas da garagem (frente 7,40 e lateral 4,50), lado aberto da varanda, bordas da piscina e limites com áreas verdes.</span></li>
</ol></div>
<div style="flex:1"><h4 style="margin-top:0">&nbsp;</h4><ol>
<li><b class="nn">4</b><span>Vãos pelo DWG (orientação da arquitetura). P04 (4,20) não está no DWG: descontada como passagem entre Cozinha e Sala, conforme informado. Com as larguras do Quadro de Esquadrias Rev. 01 o líquido de R01 seria {br(R['R01'] - DELTA_CAD['R01'])} m e o de R02, {br(R['R02'] - DELTA_CAD['R02'])} m.</span></li>
<li><b class="nn">5</b><span>Circulação Interna: inclui o nicho de 0,70 × 3,15 m (futura marcenaria), com piso e rodapé, conforme informado.</span></li>
<li><b class="nn">6</b><span>Metros lineares líquidos, sem perdas de corte ou de compra.</span></li>
</ol></div><div class="small" style="position:absolute;left:7.5mm;right:7.5mm;bottom:5.5mm">{LEG_CONTROLE}</div></div>
{carimbo(4, 'Memória de cálculo dos rodapés', 'Sem escala', 332.0, 78.1)}
</section>"""


# diferença de desconto se fossem usadas as larguras do caderno de esquadrias
DELTA_CAD = {'R01': 0.0, 'R02': 0.0}
for r in D['rodapes']:
    for v in r['vaos']:
        DELTA_CAD[r['cod']] += D['caderno_larg'][v['cod']] - v['larg']
DELTA_CAD = {k: round(v, 3) for k, v in DELTA_CAD.items()}

PEND_DECISAO = [
    'Corredor Lateral Externo (23,93 m², incluído no total): definir entre P02 (Santorini SGR HARD) e PI01 (piso intertravado drenante). Dimensões, espessura, cor e resistência do PI01: A CONFIRMAR (anúncio não acessível na elaboração). Sem rodapé.',
    'P02: o produto do link é o Santorini SGR HARD (SGR = Stone Gray, cinza), não uma versão Off White. Confirmar a cor para a varanda, o deck e o rodapé R02.',
    'P01 (Santorini OFW NAT): confirmar na ficha técnica o código Portinari, a variação de tonalidade e a classe de uso (as fontes consultadas divergem entre USO 5 e USO 6).',
    'Rejunte: aprovar o tipo proposto (NBR 14992 tipo II em áreas externas e molhadas; tipo I em áreas secas), a marca e a largura da junta, conforme o manual de assentamento Portinari.',
    'PP01: formato/granulometria da pedra portuguesa branca, assentamento e rejunte.',
    'Calçada: término junto à Av. 3 (linhas abertas no DWG). A Prefeitura indica concreto vassourado na faixa de acesso e grama na faixa de serviço; confirmar a exigência municipal.',
    'Acesso externo lateral (15,03 m²): a Prefeitura indica concreto vassourado; a planta do caderno de esquadrias mostra grama com pisantes. Confirmar o limite da pedra portuguesa.',
    'Rodapé em áreas molhadas: compatibilizar com o Caderno 02/02 (revestimento de parede).',
    'Soleiras de mármore × trilhos embutidos de P05, P07 e P10, e posição do trilho de P04 (não desenhada no DWG).',
    'Borda da piscina e arremates entre piso e jardim — não documentados.',
]
PEND_OBRA = [
    'Vãos executados × vãos do DWG × Quadro de Esquadrias Rev. 01: 13 das 20 portas têm largura diferente. Descontos de rodapé e comprimentos de soleira pelo DWG.',
    'Áreas divergentes adotadas pelo maior valor: Quarto Casal + Closet 28,70; Banheiro Casal 6,83; Banheiro Externo 4,62; Circulação 12,85; Garagem 37,65; Varanda 18,32; Rampa 37,00; Corredor Lateral Externo 23,93.',
    'Rampa: limite direito considerado no alinhamento da garagem; há guia/muro 0,10 m adiante.',
    'Rodapé atrás de marcenaria (closet, nicho da circulação, armários): conferir com o projeto de marcenaria.',
    'Tubo junto à parede superior da garagem: recortar o rodapé em obra.',
    'Todas as medidas devem ser conferidas no local antes da compra.',
]


def folha5():
    rows = ''.join(f"<tr><td><span class='cb ol' style='border-radius:1mm'>{t}</span></td><td>{esc(p)}</td><td>{esc(e)}</td><td>{esc(o)}</td>"
                   f"<td class='n'>{br(v) if v else '—'}</td><td>{tags([s])}</td></tr>"
                   for t, p, e, o, s, v in D['transicoes'])
    tot_sol = sum(x['comp'] for x in D['soleiras'])
    rows += (f"<tr class='tot'><td></td><td colspan='3'>TOTAL DE SOLEIRAS — mármore Itaúnas, baguete 5 cm ({len(D['soleiras'])} trechos)</td>"
             f"<td class='n'>{br(tot_sol)}</td><td></td></tr>")
    pd = ''.join(f'<li><b class="nn">{i}</b><span>{esc(s)}</span></li>' for i, s in enumerate(PEND_DECISAO, 1))
    po = ''.join(f'<li><b class="nn">{i}</b><span>{esc(s)}</span></li>' for i, s in enumerate(PEND_OBRA, len(PEND_DECISAO) + 1))
    return f"""<section class="sheet">
<div class="abs head" style="left:10mm;top:10mm"><div class="lbl">Pisos e rodapés · Revisão 00</div><h1>Transições e pendências</h1></div>
<div class="abs" style="left:10mm;top:33mm;width:277mm">
<table>
<colgroup><col style="width:12mm"><col style="width:19mm"><col style="width:78mm"><col><col style="width:17mm"><col style="width:32mm"></colgroup>
<tr><th>Cód.</th><th>Porta</th><th>Encontro de pisos</th><th>Solução</th><th class="n">Soleira m</th><th>Controle</th></tr>
{rows}
</table>
<div class="notes" style="display:flex;gap:9mm;margin-top:1mm">
<div style="flex:1"><h4>Pendências — decisão da arquitetura</h4><ol>{pd}</ol></div>
<div style="flex:1"><h4>Pendências — conferência em obra</h4><ol>{po}</ol></div>
</div>
</div>
<div class="normas notes" style="top:332mm;height:78.1mm;padding-top:4.5mm">
<h4 style="margin-top:0">Critérios de transição (informados pela arquitetura)</h4><ol>
<li><b class="nn">1</b><span>Mesmo produto/material, apenas com mudança de nível: perfil metálico.</span></li>
<li><b class="nn">2</b><span>Troca de material: soleira de mármore Itaúnas, tipo baguete, com 5 cm de profundidade pelo comprimento do vão.</span></li>
<li><b class="nn">3</b><span>Níveis não documentados neste caderno. Onde houver desnível entre pisos iguais, aplicar o critério 1.</span></li>
</ol>
<h4>Observações</h4><ol>
<li><b class="nn">·</b><span>Paginação de piso não faz parte deste caderno. Revestimentos de parede: Caderno 02/02.</span></li>
<li><b class="nn">·</b><span>Fonte de títulos substituída pela Outfit (Aloevera Display não disponível).</span></li></ol>
<div class="small" style="position:absolute;left:7.5mm;right:7.5mm;bottom:5.5mm">{LEG_CONTROLE}</div>
</div>
{carimbo(5, 'Transições e pendências', 'Sem escala', 332.0, 78.1)}
</section>"""


def main():
    doc = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{esc(CADERNO)} — Rev. 00</title>
<style>{fonts_css()}{CSS}</style></head><body>
{folha1()}{folha2()}{folha3()}{folha4()}{folha5()}
</body></html>"""
    open(os.path.join(AQUI, 'caderno.html'), 'w').write(doc)
    print('ok', DELTA_CAD)


if __name__ == '__main__':
    main()
