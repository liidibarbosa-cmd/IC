"""Dados do Caderno de Detalhamento de Revestimento de Piso 01/02.

Lê a conversão JSON do DWG ("PROJETO IVAN E ANA - R01.dwg", gerada por read.mjs)
e produz:
  - geometria.json : primitivas de desenho da "PLANTA DE PISO" do DWG (coord. locais)
  - dados.json     : quadro de pisos, memória de rodapés, transições e pendências
  - ../quantitativos/*.csv

Coordenadas locais = coordenadas do espaço do modelo - (3895, 760), em metros.
Toda medida vem da geometria do DWG ou de informação da arquiteta; cada valor
carrega a sua origem.
"""
import json, math, sys, os, csv, pickle
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import polygonize, unary_union

AQUI = os.path.dirname(os.path.abspath(__file__))
DB = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, 'db.json')
OX, OY = 3895.0, 760.0

db = json.load(open(DB))
MS = {e['handle']: e for e in db['entities'] if e['ownerBlockRecordSoftId'] == '1F'}
sys.path.insert(0, AQUI)
import geo  # noqa: E402  (achata blocos/polilinhas)

flat = geo.walk([e for e in db['entities'] if e['ownerBlockRecordSoftId'] == '1F'])


def loc(p):
    return (round(p[0] - OX, 4), round(p[1] - OY, 4))


def inreg(p):
    return 3895 < p[0] < 3935 and 760 < p[1] < 805


# ---------------------------------------------------------------- arcos exatos
def bulge_pts(a, b, bu, n=240):
    if abs(bu) < 1e-12:
        return [a, b]
    th = 4 * math.atan(bu)
    c = math.dist(a, b)
    r = c / (2 * math.sin(th / 2))
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    ux, uy = (b[0] - a[0]) / c, (b[1] - a[1]) / c
    d = r * math.cos(th / 2)
    cx, cy = mx - uy * d, my + ux * d
    a0 = math.atan2(a[1] - cy, a[0] - cx)
    return [(cx + abs(r) * math.cos(a0 + th * i / n), cy + abs(r) * math.sin(a0 + th * i / n)) for i in range(n + 1)]


def pl_exact(h, closed=None):
    e = MS[h]
    v = e['vertices']
    cl = (e.get('flag', 0) & 1) if closed is None else closed
    n = len(v)
    pts = []
    for i in range(n if cl else n - 1):
        a = loc((v[i]['x'], v[i]['y']))
        b = loc((v[(i + 1) % n]['x'], v[(i + 1) % n]['y']))
        s = bulge_pts(a, b, v[i].get('bulge', 0) or 0)
        pts += s if not pts else s[1:]
    return pts


def hatch_loops(h):
    return [[loc(p) for p in x['pts']] for x in flat if x['kind'] == 'hatch' and x['handle'] == h]


# ------------------------------------------------------------ geometria base
lote = pl_exact('264F96')                    # divisa (aberta: falta a diagonal)
arco_divisa = [p for p in lote if p[1] <= 15.2971 + 1e-9 and p[0] >= 6.9 - 1e-9]
faixa1 = [(4.041, 8.786)] + pl_exact('264F97')          # 265182 + 264F97
faixa2 = [(4.041, 7.686)] + pl_exact('264F98')          # 265181 + 264F98
meiofio = pl_exact('265180')[:-1] + pl_exact('264F99')  # 265180 + 264F99
piscina = pl_exact('2650B9', closed=True)
verde_topo = pl_exact('2651AA', closed=True)             # 6,30 m²
verde_dir = pl_exact('26517D') + [pl_exact('26517D')[0]]
verde_frente = pl_exact('26517F', closed=True)           # 16,97 m²
verde_sala = pl_exact('265197', closed=True)             # 6,82 m²

# paredes: faces de parede poligonizadas (camadas de alvenaria/muro)
WL = {'04', 'ALVENARIA', '_a const_hum', '_parede int', '03', '01', 'caixilho'}
segs = []
for x in flat:
    if x['kind'] == 'line' and x['layer'] in WL:
        P = [loc(p) for p in x['pts']]
        if all(0 < p[0] < 35 and 3 < p[1] < 45 for p in P):
            for a, b in zip(P, P[1:]):
                if math.dist(a, b) > 1e-4:
                    segs.append(LineString([a, b]))
paredes = [p for p in polygonize(unary_union(segs)) if p.area > 1e-4 and p.area / (p.length / 2) < 0.16]

linhas = {'portas': [], 'caixilhos': [], 'soleiras': [], 'calcada': []}
for x in flat:
    if x['kind'] != 'line':
        continue
    P = [loc(p) for p in x['pts']]
    if not all(0 < p[0] < 35 and 3 < p[1] < 45 for p in P):
        continue
    if x['layer'] == '02' and x.get('blk', '') and x['blk'].startswith('*U'):
        linhas['portas'].append(P)
    elif x['layer'] == 'caixilho':
        linhas['caixilhos'].append(P)
    elif x['layer'] == '01' and x.get('handle') not in ('26517D', '26517F', '265197', '2651AA'):
        linhas['soleiras'].append(P)

# ------------------------------------------------------------------ polígonos
def poly(pts):
    return Polygon(pts)


Z = {}  # zonas de piso: id -> dict
def zona(zid, nome, cod, pts, holes=(), **kw):
    P = Polygon(pts, holes)
    rr = lambda ps: [list(map(lambda v: round(v, 4), p)) for p in ps]
    Z[zid] = dict(id=zid, nome=nome, cod=cod, pts=rr(pts), holes=[rr(h) for h in holes],
                  area_geo=round(P.area, 4), perim_geo=round(P.exterior.length, 4), **kw)


R = lambda x0, y0, x1, y1: [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
zona('QCA', 'Quarto Casal', 'P01', R(9.941, 36.386, 14.591, 39.886))
zona('CLO', 'Closet Casal', 'P01', R(6.291, 36.386, 9.791, 39.886))
zona('BCA', 'Banheiro Casal', 'P01', R(4.191, 36.386, 6.141, 39.886))
zona('Q02', 'Quarto 02', 'P01', R(5.691, 33.236, 9.791, 36.236))
zona('W02', 'WC 02', 'P01', R(6.291, 31.586, 9.091, 33.086))
zona('W01', 'WC 01', 'P01', R(6.291, 29.936, 9.091, 31.436))
zona('Q01', 'Quarto 01', 'P01', R(5.691, 26.786, 9.791, 29.786))
zona('ESC', 'Escritório', 'P01', R(11.291, 34.036, 14.591, 36.236))
zona('BEX', 'Banheiro Externo', 'P01', R(11.291, 32.486, 14.591, 33.886))
zona('CIR', 'Circulação Interna', 'P01', [(9.941, 27.836), (11.141, 27.836), (11.141, 36.236), (9.941, 36.236),
                                             (9.941, 33.086), (9.241, 33.086), (9.241, 29.936), (9.941, 29.936)])
zona('COZ', 'Cozinha', 'P01', R(5.691, 22.436, 9.941, 26.636))
zona('LAV', 'Lavanderia', 'P01', R(5.691, 20.286, 8.441, 22.286))
zona('DEP', 'Depósito', 'P01', R(8.591, 20.286, 9.791, 22.286))
zona('SAL', 'Sala TV / Sala Jantar', 'P01', [(9.941, 20.286), (11.591, 20.286), (11.591, 19.686), (15.191, 19.686),
                                              (15.191, 27.686), (9.941, 27.686)])
zona('GAR', 'Garagem', 'P01', [(4.191, 15.036), (11.591, 15.036), (11.591, 19.536), (11.441, 19.536),
                                (11.441, 20.136), (4.191, 20.136)])
zona('VAR', 'Varanda Gourmet', 'P02', [(11.291, 27.836), (15.341, 27.836), (15.341, 32.486), (14.741, 32.486),
                                        (14.741, 32.336), (11.291, 32.336)])
zona('DEC', 'Deck (inclui faixas sob beiral)', 'P02', [
    (18.633, 22.905), (23.528, 33.436), (22.241, 33.436), (22.241, 38.886), (21.741, 38.886), (21.741, 32.886),
    (17.941, 32.886), (17.941, 38.886), (15.941, 38.886), (15.941, 39.886), (14.741, 39.886), (14.741, 32.486),
    (15.341, 32.486), (15.341, 24.205), (17.341, 24.205), (17.341, 22.905)])
# rampa: garagem (y=15,036) até a divisa, limite direito x=11,591 (alinhamento da garagem)
yI = LineString(arco_divisa).intersection(LineString([(11.591, 0), (11.591, 30)])).y
rampa = [(4.041, 15.036), (11.591, 15.036), (11.591, yI)] + [p for p in arco_divisa if p[0] < 11.591][::-1] + [(4.041, 10.036)]
zona('RAM', 'Rampa de acesso à garagem', 'PP01', rampa)
# hachura GRASS (pedra portuguesa) fora da rampa: laço 1 - área verde frontal + laço 3
g1 = hatch_loops('2663C7')
laco1 = [p for p in g1[0] if not (abs(math.dist(p, (5.175384, 22.054023)) - 12.141509) < 0.01 and 6.91 < p[0] < 15.25)]
i6 = min(range(len(laco1)), key=lambda i: math.dist(laco1[i], (6.901, 10.036)))
laco1 = laco1[:i6 + 1] + arco_divisa[1:-1] + laco1[i6 + 1:]
GR = Polygon(laco1).difference(Polygon(verde_frente)).union(Polygon(g1[2]))
ACE = GR.difference(Polygon(rampa).buffer(1e-6))
ace = max(getattr(ACE, 'geoms', [ACE]), key=lambda p: p.area)
zona('ACE', 'Acesso externo lateral (até P03)', 'PP01', [tuple(p) for p in ace.exterior.coords][:-1],
     holes=[[tuple(p) for p in h.coords][:-1] for h in ace.interiors])
# calçada: divisa frontal -> canto do lote -> fim da linha interna do meio-fio (264F98) -> retorno
front = lote[2:] + [lote[0]]
calc = front + [faixa2[-1]] + faixa2[::-1][:-1] + [(4.041, 7.686)]
zona('CAL', 'Calçada (passeio público)', 'PP01', calc)
calc_mf = front + [meiofio[-1]] + meiofio[::-1]
AREA_CALC_COM_MEIOFIO = round(Polygon(calc_mf).area, 4)
cl = hatch_loops('2660B4')[0]
zona('COR', 'Corredor Lateral', 'NE', cl)

for k in Z:
    if not Polygon(Z[k]['pts'], Z[k]['holes']).is_valid:
        raise SystemExit('polígono inválido ' + k)

# ------------------------------------------------------------- quadro de pisos
ARQ, INF, OBRA = 'Arquivo', 'Informado', 'Obra'
def pz(z): return Z[z]['area_geo']
pisos = [
    # cod, ambiente, zonas, área adotada, fonte, controle
    ('P01', 'Quarto Casal + Closet Casal', ['QCA', 'CLO'], 28.70,
     'Rótulo DWG Prefeitura "SUÍTE MASTER A=28,70 m²" = valor informado; geometria DWG 16,28 + 12,25 = 28,53 (maior valor adotado)', [ARQ, INF]),
    ('P01', 'Banheiro Casal', ['BCA'], round(pz('BCA'), 2),
     'Geometria DWG 1,95 × 3,50 = 6,83 (rótulo planta de piso 6,83); informado/Prefeitura 6,30 (maior valor adotado)', [ARQ]),
    ('P01', 'Quarto 01', ['Q01'], 12.30, 'Geometria DWG 4,10 × 3,00 = rótulo 12,30 = informado', [ARQ, INF]),
    ('P01', 'WC 01', ['W01'], 4.20, 'Geometria DWG 2,80 × 1,50 = rótulo 4,20 = informado', [ARQ, INF]),
    ('P01', 'Quarto 02', ['Q02'], 12.30, 'Geometria DWG 4,10 × 3,00 = rótulo 12,30 = informado', [ARQ, INF]),
    ('P01', 'WC 02', ['W02'], 4.20, 'Geometria DWG 2,80 × 1,50 = rótulo 4,20 = informado', [ARQ, INF]),
    ('P01', 'Escritório', ['ESC'], 7.26, 'Geometria DWG 3,30 × 2,20 = rótulo 7,26 = informado', [ARQ, INF]),
    ('P01', 'Banheiro Externo', ['BEX'], round(pz('BEX'), 2),
     'Geometria DWG 3,30 × 1,40 = rótulo 4,62; informado/Prefeitura 4,27 (maior valor adotado)', [ARQ]),
    ('P01', 'Circulação Interna (inclui nicho de marcenaria)', ['CIR'], 12.85,
     'Rótulo DWG planta de piso/forro "CIRCULAÇÃO 12,85 m²"; geometria 1,20 × 8,40 + nicho 0,70 × 3,15 = 12,29; informado 10,08 (maior valor adotado)', [ARQ, OBRA]),
    ('P01', 'Cozinha', ['COZ'], 17.85, 'Geometria DWG 4,25 × 4,20 = rótulo 17,85 = informado', [ARQ, INF]),
    ('P01', 'Sala TV / Sala Jantar (integradas)', ['SAL'], round(pz('SAL'), 2),
     'Geometria DWG 5,25 × 8,00 − 1,65 × 0,60 = 41,01 = informado (Jantar 21,00 + Estar 20,01)', [ARQ, INF]),
    ('P01', 'Lavanderia', ['LAV'], 5.50, 'Geometria DWG 2,75 × 2,00 = rótulo 5,50 = informado', [ARQ, INF]),
    ('P01', 'Depósito', ['DEP'], 2.40, 'Geometria DWG 1,20 × 2,00 = rótulo 2,40 = informado', [ARQ, INF]),
    ('P01', 'Garagem', ['GAR'], round(pz('GAR'), 2),
     'Geometria DWG 7,40 × 5,10 − 0,15 × 0,60 = 37,65 (= rótulo planta de forro); informado/Prefeitura 36,97 (maior valor adotado)', [ARQ]),
    ('P02', 'Varanda Gourmet', ['VAR'], round(pz('VAR') + 1e-9, 2),
     'Contorno da hachura DWG 4,05 × 4,50 + 0,60 × 0,15 = 18,32; informado/Prefeitura 18,22 (maior valor adotado)', [ARQ]),
    ('P02', 'Deck (inclui faixas sob beiral)', ['DEC'], round(pz('DEC'), 2),
     'Hachura DWG 61,37 + giro P03 0,64 + faixas sob beiral 1,00 × 7,40 e 1,00 × 8,28 (beiral: DWG Prefeitura, "PROJEÇÃO DO BEIRAL")', [ARQ, INF, OBRA]),
    ('PP01', 'Rampa de acesso à garagem', ['RAM'], 37.00,
     'Informado: 7,40 × 5,00 com margem; geometria DWG com borda curva = %s (maior valor adotado)' % f"{pz('RAM'):.2f}".replace('.', ','), [INF]),
    ('PP01', 'Acesso externo lateral (até P03)', ['ACE'], round(pz('ACE'), 2),
     'Hachura GRASS do DWG (pedra portuguesa) fora da rampa e das áreas verdes', [ARQ, OBRA]),
    ('PP01', 'Calçada — faixas de acesso e livre (2,35 m)', ['CAL'], round(pz('CAL'), 2),
     'Geometria DWG: divisa frontal 40,32 m × faixas 1,25 + 1,10; término na Av. 3 não fechado no DWG', [ARQ, OBRA]),
    ('NE', 'Corredor Lateral Externo', ['COR'], 23.93,
     'Informado: 1,50 × 15,95 (aprox.); contorno da hachura DWG = %s (maior valor adotado)' % f"{pz('COR'):.2f}".replace('.', ','), [INF, OBRA]),
]

PROD = {
    # dados técnicos: site do fabricante (portinarirevestimentos.com.br), links informados pela arquitetura;
    # consulta indireta em 26/09/2026 (site bloqueado no ambiente de produção) — conferir na ficha técnica.
    'P01': dict(produto='Porcelanato Santorini OFW NAT', fabricante='Portinari', formato='90 × 90 cm',
                acabamento='Natural (NAT)', rejunte='Corda · junta seca', cor='#ead8b4',
                spec=[('Descrição', 'Porcelanato esmaltado Santorini OFW NAT (Off White), borda retificada'),
                      ('Fabricação', '900 × 900 mm · espessura 7,0 mm · monocalibre'),
                      ('Embalagem', '3 peças / 2,43 m² por caixa'),
                      ('Uso', 'áreas internas (Cód. Portinari, variação V e classe de uso: A CONFIRMAR na ficha)'),
                      ('Junta', 'junta seca (fabricante)'),
                      ('Rejunte', 'cor Corda (sugerida pelo fabricante) · proposta: argamassa de rejuntamento tipo II, NBR 14992, em WCs, banheiros, cozinha e lavanderia; tipo I nas áreas secas')]),
    'P02': dict(produto='Porcelanato Santorini SGR HARD', fabricante='Portinari', formato='90 × 90 cm',
                acabamento='HARD (antiderrapante)', rejunte='Corda · junta seca', cor='#c4c5b8',
                spec=[('Descrição', 'Porcelanato esmaltado Santorini SGR HARD (Stone Gray, cinza), cód. 62928, borda retificada'),
                      ('Fabricação', '900 × 900 mm · espessura 8,0 mm · monocalibre'),
                      ('Embalagem', '2 peças / 1,62 m² por caixa'),
                      ('Uso', 'USO 6 (residencial e comercial de tráfego intenso) · variação V3 · interno e externo'),
                      ('Junta', 'junta seca (fabricante)'),
                      ('Rejunte', 'cor Corda (sugerida pelo fabricante) · proposta: argamassa de rejuntamento tipo II, NBR 14992 (área externa)')]),
    'PP01': dict(produto='Pedra portuguesa branca', fabricante='—', formato='A CONFIRMAR', acabamento='A CONFIRMAR',
                 rejunte='A CONFIRMAR', cor='#f3f1ea', spec=[]),
    'NE': dict(produto='A DEFINIR: P02 ou PI01', fabricante='Portinari / A CONFIRMAR', formato='90 × 90 cm ou A CONFIRMAR',
               acabamento='HARD ou drenante', rejunte='Corda ou A CONFIRMAR', cor='none',
               spec=[('Opção 1', 'P02 — Porcelanato Santorini SGR HARD (dados acima)'),
                     ('Opção 2', 'PI01 — Piso intertravado drenante (lajota/bloquete de concreto): dimensões, espessura, cor e resistência A CONFIRMAR (anúncio não acessível)')]),
}

# ------------------------------------------------------------------ vãos (DWG)
# largura = vão medido no DWG (bloco de porta / soleira / interrupção de parede)
V = {}
def vao(vid, cod, largura, a, b, amb, origem):
    L = math.dist(a, b)
    assert abs(L - largura) < 0.006, (vid, L)
    V[vid] = dict(id=vid, cod=cod, larg=largura, a=a, b=b, amb=amb, origem=origem)

vao('P01', 'P01', 1.20, (10.094, 20.211), (11.294, 20.211), 'Garagem / Sala', 'bloco de porta')
vao('P02', 'P02', 0.80, (4.341, 20.211), (5.141, 20.211), 'Garagem / Corredor Lateral', 'bloco de porta')
vao('P03', 'P03', 0.90, (17.341, 23.905), (17.341, 23.005), 'Deck / Acesso externo', 'bloco de porta')
vao('P04', 'P04', 4.20, (9.941, 22.436), (9.941, 26.636), 'Cozinha / Sala', 'informado (passagem; esquadria não desenhada no DWG)')
vao('P05a', 'P05', 3.00, (11.991, 27.761), (14.991, 27.761), 'Sala / Varanda Gourmet', 'soleira DWG')
vao('P05b', 'P05', 3.00, (15.266, 24.436), (15.266, 27.436), 'Sala / Deck', 'soleira DWG')
vao('P06sal', 'P06', 0.90, (10.041, 27.761), (10.941, 27.761), 'Circulação / Sala', 'bloco de porta')
vao('P06coz', 'P06', 0.80, (7.391, 22.361), (8.191, 22.361), 'Cozinha / Lavanderia', 'interrupção de parede')
vao('P06dep', 'P06', 0.70, (8.516, 21.486), (8.516, 22.186), 'Lavanderia / Depósito', 'bloco de porta')
vao('P06q01', 'P06', 0.80, (9.866, 28.886), (9.866, 29.686), 'Circulação / Quarto 01', 'bloco de porta')
vao('P06w01', 'P06', 0.80, (8.191, 29.861), (8.991, 29.861), 'Quarto 01 / WC 01', 'bloco de porta')
vao('P06q02', 'P06', 0.80, (9.866, 33.336), (9.866, 34.136), 'Circulação / Quarto 02', 'bloco de porta')
vao('P06w02', 'P06', 0.80, (8.191, 33.161), (8.991, 33.161), 'Quarto 02 / WC 02', 'bloco de porta')
vao('P06qca', 'P06', 0.90, (10.091, 36.311), (10.991, 36.311), 'Circulação / Quarto Casal', 'bloco de porta')
vao('P06esc', 'P06', 0.80, (11.216, 34.136), (11.216, 34.936), 'Circulação / Escritório', 'bloco de porta')
vao('P07', 'P07', 1.80, (5.616, 20.386), (5.616, 22.186), 'Lavanderia / Corredor Lateral', 'caixilho DWG')
vao('P08', 'P08', 0.90, (9.866, 37.636), (9.866, 38.536), 'Quarto Casal / Closet Casal', 'soleira DWG')
vao('P09', 'P09', 0.90, (6.216, 37.636), (6.216, 38.536), 'Closet Casal / Banheiro Casal', 'interrupção de parede')
vao('P10', 'P10', 2.70, (14.666, 36.711), (14.666, 39.411), 'Quarto Casal / Deck', 'caixilho DWG (4 × 0,675)')
vao('P11', 'P11', 0.80, (14.666, 32.586), (14.666, 33.386), 'Banheiro Externo / Deck', 'bloco de porta')
CADERNO_LARG = {'P01': 1.20, 'P02': 0.90, 'P03': 0.90, 'P04': 4.20, 'P05': 3.00, 'P06': 0.90, 'P07': 1.80,
                'P08': 1.00, 'P09': 1.00, 'P10': 2.50, 'P11': 0.90}

# -------------------------------------------------------------------- rodapés
# trechos = faces de parede com rodapé (coord. do DWG), cada um com posição relativa na planta
ROD = []
def rod(cod, zid, trechos, vaos, obs=''):
    tr = []
    for nome, a, b in trechos:
        tr.append(dict(nome=nome, a=a, b=b, L=round(math.dist(a, b), 3)))
    vs = []
    for vid in vaos:
        v = V[vid]
        # o vão tem de estar sobre um dos trechos (colinear, dentro, tolerância 0,08 m = espessura/2)
        mid = ((v['a'][0] + v['b'][0]) / 2, (v['a'][1] + v['b'][1]) / 2)
        ok = [t for t in tr if LineString([t['a'], t['b']]).distance(Point(mid)) < 0.08 and
              t['L'] + 1e-6 >= v['larg'] and
              LineString([t['a'], t['b']]).distance(Point(v['a'])) < 0.08 and
              LineString([t['a'], t['b']]).distance(Point(v['b'])) < 0.08]
        assert ok, ('vão fora de trecho', zid, vid)
        vs.append(dict(id=vid, cod=v['cod'], larg=v['larg'], trecho=ok[0]['nome']))
    soma = round(sum(t['L'] for t in tr), 3)
    desc = round(sum(v['larg'] for v in vs), 3)
    ROD.append(dict(cod=cod, zona=zid, ambiente=Z[zid]['nome'], trechos=tr, vaos=vs, soma=soma, desc=desc,
                    liquido=round(soma - desc, 3), obs=obs))


def ret(x0, y0, x1, y1):
    return [('inf.', (x0, y0), (x1, y0)), ('dir.', (x1, y0), (x1, y1)), ('sup.', (x1, y1), (x0, y1)), ('esq.', (x0, y1), (x0, y0))]

rod('R01', 'QCA', ret(9.941, 36.386, 14.591, 39.886), ['P06qca', 'P10', 'P08'])
rod('R01', 'CLO', ret(6.291, 36.386, 9.791, 39.886), ['P08', 'P09'], 'Trechos atrás de marcenaria: conferir com o projeto de marcenaria')
rod('R01', 'BCA', ret(4.191, 36.386, 6.141, 39.886), ['P09'])
rod('R01', 'Q02', ret(5.691, 33.236, 9.791, 36.236), ['P06w02', 'P06q02'])
rod('R01', 'W02', ret(6.291, 31.586, 9.091, 33.086), ['P06w02'])
rod('R01', 'W01', ret(6.291, 29.936, 9.091, 31.436), ['P06w01'])
rod('R01', 'Q01', ret(5.691, 26.786, 9.791, 29.786), ['P06q01', 'P06w01'])
rod('R01', 'ESC', ret(11.291, 34.036, 14.591, 36.236), ['P06esc'])
rod('R01', 'BEX', ret(11.291, 32.486, 14.591, 33.886), ['P11'])
rod('R01', 'CIR', [('inf.', (9.941, 27.836), (11.141, 27.836)), ('dir.', (11.141, 27.836), (11.141, 36.236)),
                   ('sup.', (11.141, 36.236), (9.941, 36.236)), ('esq. sup.', (9.941, 36.236), (9.941, 33.086)),
                   ('nicho sup.', (9.941, 33.086), (9.241, 33.086)), ('nicho esq.', (9.241, 33.086), (9.241, 29.936)),
                   ('nicho inf.', (9.241, 29.936), (9.941, 29.936)), ('esq. inf.', (9.941, 29.936), (9.941, 27.836))],
    ['P06sal', 'P06esc', 'P06qca', 'P06q02', 'P06q01'], 'Nicho (futura marcenaria) com piso e rodapé, conforme informado')
rod('R01', 'COZ', ret(5.691, 22.436, 9.941, 26.636), ['P06coz', 'P04'])
rod('R01', 'LAV', ret(5.691, 20.286, 8.441, 22.286), ['P06coz', 'P06dep', 'P07'])
rod('R01', 'DEP', ret(8.591, 20.286, 9.791, 22.286), ['P06dep'])
rod('R01', 'SAL', [('inf. esq.', (9.941, 20.286), (11.591, 20.286)), ('recuo', (11.591, 20.286), (11.591, 19.686)),
                   ('inf. dir.', (11.591, 19.686), (15.191, 19.686)), ('dir.', (15.191, 19.686), (15.191, 27.686)),
                   ('sup.', (15.191, 27.686), (9.941, 27.686)), ('esq.', (9.941, 27.686), (9.941, 20.286))],
    ['P01', 'P05b', 'P05a', 'P06sal', 'P04'], 'J01 (peitoril 0,50) não descontada')
rod('R01', 'GAR', [('esq.', (4.191, 15.036), (4.191, 20.136)), ('sup.', (4.191, 20.136), (11.441, 20.136)),
                   ('pilar dir.', (11.441, 20.136), (11.441, 19.536)), ('pilar inf.', (11.441, 19.536), (11.591, 19.536))],
    ['P02', 'P01'], 'Frente (7,40) e lateral direita (4,50) abertas no DWG: sem rodapé')
rod('R02', 'VAR', [('inf.', (11.291, 27.836), (15.341, 27.836)), ('esq.', (11.291, 32.336), (11.291, 27.836)),
                   ('sup.', (14.741, 32.336), (11.291, 32.336))],
    ['P05a'], 'Lado direito aberto para o deck: sem rodapé')
rod('R02', 'DEC', [('fachada Q. Casal/Escr./B. Ext.', (14.741, 32.486), (14.741, 39.886)),
                   ('muro sup.', (14.741, 39.886), (15.941, 39.886)),
                   ('fachada Sala', (15.341, 24.205), (15.341, 27.836)),
                   ('muro inf.', (15.341, 24.205), (17.341, 24.205)),
                   ('portão P03 + batentes', (17.341, 24.205), (17.341, 22.905)),
                   ('muro portão', (17.341, 22.905), (18.633, 22.905)),
                   ('muro de divisa (diag.)', (18.633, 22.905), (23.528, 33.436))],
    ['P10', 'P11', 'P05b', 'P03'], 'Sem rodapé junto à piscina e às áreas verdes')

TOT = {}
for r in ROD:
    TOT[r['cod']] = round(TOT.get(r['cod'], 0) + r['liquido'], 3)

# ----------------------------------------------------------------- transições
SOL_MARMORE = 'Soleira mármore Itaúnas, baguete 5 cm × comprimento do vão'
PERFIL = 'Perfil metálico (mesmo material, somente com desnível)'
TRANS = [
    # cód, porta, encontro, solução, controle, vão (m) com soleira de mármore (ou None)
    ('T01', 'P02', 'Garagem (P01) / Corredor Lateral Externo (P02 ou PI01)', SOL_MARMORE + ' (0,80 m).', 'Informado', 0.80),
    ('T02', 'P07', 'Lavanderia (P01) / Corredor Lateral Externo (P02 ou PI01)', SOL_MARMORE + ' (1,80 m). Compatibilizar com o trilho embutido (esquadrias, notas 3 e 10).', 'Informado', 1.80),
    ('T03', 'P05', 'Sala TV / Sala Jantar (P01) / Varanda Gourmet (P02)', SOL_MARMORE + ' (3,00 m). Compatibilizar com o trilho embutido.', 'Informado', 3.00),
    ('T04', 'P05', 'Sala TV / Sala Jantar (P01) / Deck (P02)', SOL_MARMORE + ' (3,00 m). Compatibilizar com o trilho embutido.', 'Informado', 3.00),
    ('T05', 'P10', 'Quarto Casal (P01) / Deck (P02)', SOL_MARMORE + ' (2,70 m). Compatibilizar com o trilho da veneziana de correr.', 'Informado', 2.70),
    ('T06', 'P11', 'Banheiro Externo (P01) / Deck (P02)', SOL_MARMORE + ' (0,80 m).', 'Informado', 0.80),
    ('T07', 'P03', 'Deck (P02) / Acesso externo (PP01)', SOL_MARMORE + ' (0,90 m).', 'Informado', 0.90),
    ('T08', '—', 'Garagem (P01) / Rampa (PP01) — frente aberta', SOL_MARMORE + ' (7,40 m, linha y = 15,036).', 'Informado', 7.40),
    ('T09', '—', 'Garagem (P01) / Acesso externo (PP01) — lateral aberta', SOL_MARMORE + ' (4,50 m).', 'Informado', 4.50),
    ('T10', '—', 'Deck (P02) / Piscina', 'Borda da piscina e arremate não documentados: A CONFIRMAR.', 'Decisão', None),
    ('T11', '—', 'Deck (P02) e PP01 / áreas verdes', 'Contenção/arremate entre piso e jardim não documentado: A CONFIRMAR.', 'Decisão', None),
    ('T12', '—', 'Rampa (PP01) / Calçada (PP01) — divisa', 'Mesmo material: sem soleira. Havendo desnível: ' + PERFIL.lower() + '.', 'Informado', None),
    ('T13', 'P04', 'Cozinha (P01) / Sala TV / Sala Jantar (P01)', 'Mesmo material: sem soleira. Havendo desnível: ' + PERFIL.lower() + '. Posição do trilho de P04 A CONFIRMAR.', 'Informado', None),
    ('T14', 'P06/P08/P09', 'Portas internas (P01 / P01)', 'Mesmo material: sem soleira. Havendo desnível: ' + PERFIL.lower() + '.', 'Informado', None),
]
SOLEIRAS = [dict(t=t[0], porta=t[1], encontro=t[2], comp=t[5]) for t in TRANS if t[5]]

# ----------------------------------------------------------------- saída JSON
geometria = dict(
    paredes=[[list(map(lambda v: round(v, 4), c)) for c in p.exterior.coords] for p in paredes],
    linhas=linhas, lote=lote, faixa1=faixa1, faixa2=faixa2, meiofio=meiofio, piscina=piscina,
    verdes=[verde_topo, verde_dir, verde_frente, verde_sala],
)
dados = dict(
    zonas=Z, pisos=[dict(cod=c, ambiente=a, zonas=z, area=ar, fonte=f, controle=ct) for c, a, z, ar, f, ct in pisos],
    produtos=PROD, vaos=V, caderno_larg=CADERNO_LARG, rodapes=ROD, rod_total=TOT, transicoes=TRANS, soleiras=SOLEIRAS,
    extras=dict(calcada_com_meiofio=AREA_CALC_COM_MEIOFIO, rampa_geo=pz('RAM'), deck_hachura=61.372,
                giro_p03=round(math.pi * 0.9 ** 2 / 4, 3)),
)
json.dump(geometria, open(os.path.join(AQUI, 'geometria.json'), 'w'))
json.dump(dados, open(os.path.join(AQUI, 'dados.json'), 'w'), ensure_ascii=False, indent=1)

# -------------------------------------------------------------------- CSVs
Q = os.path.join(AQUI, '..', 'quantitativos')
os.makedirs(Q, exist_ok=True)
br = lambda v, n=2: f'{v:.{n}f}'.replace('.', ',')
with open(os.path.join(Q, 'quadro_pisos.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f, delimiter=';')
    w.writerow(['codigo', 'ambiente', 'produto', 'fabricante', 'formato', 'acabamento', 'rejunte', 'area_m2', 'area_geometria_dwg_m2', 'fonte_da_medida', 'controle'])
    for p in dados['pisos']:
        pr = PROD[p['cod']]
        w.writerow([p['cod'], p['ambiente'], pr['produto'], pr['fabricante'], pr['formato'], pr['acabamento'], pr['rejunte'], br(p['area']),
                    br(sum(Z[z]['area_geo'] for z in p['zonas']), 3), p['fonte'], ' + '.join(p['controle'])])
    sub = {}
    for p in dados['pisos']:
        sub[p['cod']] = sub.get(p['cod'], 0) + p['area']
    for c, v in sub.items():
        w.writerow([c, 'SUBTOTAL ' + PROD[c]['produto'], '', '', '', '', '', br(v), '', '', ''])
    w.writerow(['', 'TOTAL GERAL (P01 + P02 + PP01 + corredor a definir)', '', '', '', '', '', br(sum(sub.values())), '', '', ''])
    w.writerow([])
    w.writerow(['transicao', 'porta', 'encontro', 'soleira mármore Itaúnas baguete 5 cm — comprimento (m)'])
    for so in SOLEIRAS:
        w.writerow([so['t'], so['porta'], so['encontro'], br(so['comp'])])
    w.writerow(['', '', 'TOTAL SOLEIRAS', br(sum(so['comp'] for so in SOLEIRAS))])
with open(os.path.join(Q, 'memoria_rodapes.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f, delimiter=';')
    w.writerow(['codigo', 'ambiente', 'tipo', 'descricao', 'x_ini', 'y_ini', 'x_fim', 'y_fim', 'comprimento_m', 'fonte'])
    for r in ROD:
        for t in r['trechos']:
            w.writerow([r['cod'], r['ambiente'], 'trecho de parede', t['nome'], br(t['a'][0], 3), br(t['a'][1], 3), br(t['b'][0], 3), br(t['b'][1], 3), br(t['L'], 3), 'geometria DWG (face interna)'])
        for v in r['vaos']:
            vv = V[v['id']]
            w.writerow([r['cod'], r['ambiente'], 'vão descontado', f"{v['cod']} ({vv['amb']}) no trecho {v['trecho']}", br(vv['a'][0], 3), br(vv['a'][1], 3), br(vv['b'][0], 3), br(vv['b'][1], 3), br(-v['larg'], 3), vv['origem']])
        w.writerow([r['cod'], r['ambiente'], 'LÍQUIDO', f"{br(r['soma'])} − {br(r['desc'])} = {br(r['liquido'])}", '', '', '', '', br(r['liquido'], 3), r['obs']])
    for c, v in TOT.items():
        w.writerow([c, 'TOTAL ' + c, '', '', '', '', '', '', br(v, 3), ''])

if __name__ == '__main__':
    for p in dados['pisos']:
        print(f"{p['cod']:5} {p['ambiente'][:44]:44} {p['area']:7.2f}  geo={sum(Z[z]['area_geo'] for z in p['zonas']):8.3f}")
    for r in ROD:
        print(f"{r['cod']} {r['ambiente'][:32]:32} soma={r['soma']:7.3f} desc={r['desc']:6.2f} liq={r['liquido']:7.3f}")
    print('TOTAIS', TOT, 'calçada c/ meio-fio', AREA_CALC_COM_MEIOFIO)
