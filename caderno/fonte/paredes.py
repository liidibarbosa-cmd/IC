"""Caderno de Detalhamento de Revestimento de Parede 02/02 — Rev. 00.

Mesmo DWG ("PROJETO IVAN E ANA - R01.dwg", Planta de Piso; coordenadas locais = modelo − (3895, 760))
e mesma identidade visual do caderno 01/02 (reaproveita pranchas.py).
Cada pano de parede registra a face do DWG, a altura informada e as aberturas descontadas.
"""
import json, math, os, csv, html
import pranchas as PR
from shapely.geometry import LineString
from pranchas import Planta, C, br, esc, tags

AQUI = os.path.dirname(os.path.abspath(__file__))
PR.CADERNO = 'CADERNO DE DETALHAMENTO DE REVESTIMENTO DE PAREDE 02/02'
PR.NF = 5
NF = 5
ARQ, INF, OBRA = 'Arquivo', 'Informado', 'Obra'

# ------------------------------------------------------------------ produtos
PROD = {
    'RP01': dict(nome='Pedra Moledo', fab='Pedreira (compra à parte)', formato='A CONFIRMAR', esp='A CONFIRMAR',
                 acab='Natural (pedra)', rejunte='A CONFIRMAR', linha='#7d6b4f', fill='#ece3cf'),
    'RP02': dict(nome='Porcelanato Santorini OFW NAT', fab='Portinari', formato='90 × 90 cm', esp='7,0 mm',
                 acab='Natural (NAT), retificado', rejunte='Corda · junta seca', linha='#a88a5c', fill='#ecdfc4'),
    'RP03': dict(nome='Porcelanato Confete WH NAT', fab='CEUSA · cód. 5041209A', formato='100 × 100 cm', esp='9,0 mm',
                 acab='Natural, retificado', rejunte='A CONFIRMAR', linha='#8f887a', fill='#f6f3ec'),
    'RP04': dict(nome='Porcelanato Confete PK NAT (Pink)', fab='CEUSA · cód. 5041210A', formato='100 × 100 cm', esp='9,0 mm',
                 acab='Natural, retificado', rejunte='Sugestão do fabricante: Quartzolit Preto Grafite, Rejuntabras Marfim ou Quartzobras Castor',
                 linha='#b56f62', fill='#e6c0b4'),
    'RP05': dict(nome='Revestimento Fatto Oliva AC', fab='Decortiles · SC 8068139', formato='30 × 90 cm', esp='A CONFIRMAR',
                 acab='Acetinado (AC), V1', rejunte='A CONFIRMAR', linha='#6a6f42', fill='#b5b98c'),
    'RP06': dict(nome='Travertino Rock Face', fab='Pedreira (compra à parte)', formato='A CONFIRMAR', esp='A CONFIRMAR',
                 acab='Rock face (bruto)', rejunte='A CONFIRMAR', linha='#8c6d4a', fill='#e4d6bd'),
    'RP07': dict(nome='Cerâmica simples — Eliane Forma Branco AC (fundo da marcenaria)', fab='Eliane · SC 8039383', formato='30 × 40 cm',
                 esp='6,5 mm', acab='Acetinado, V1', rejunte='Junta 2 mm (fabricante) · cor A CONFIRMAR', linha='#5f6a70', fill='#fbfaf6'),
}

# --------------------------------------------------------------------- panos
# face: (a, b) no DWG; lado: ponto do lado revestido (para desenhar a linha na planta)
NICHO_H, NICHO_P, NICHO_Z = 0.30, 0.10, 1.00      # informado (imagens): altura, profundidade, base a 1,00 m
J01 = ('J01', 2.50, 2.50, 0.50)                    # quadro de esquadrias Rev. 01: larg., alt., peitoril
J02 = ('J02', 2.35, 0.45, 1.10)
J04 = ('J04', 1.00, 0.60, 1.50)
BOCA = ('Boca da churrasqueira', 0.80, 0.80, None)  # informado; posição vertical A CONFIRMAR

PANOS = []
def pano(pid, elev, cod, amb, parede, a, b, lado, alt, aberturas=(), nicho=False, pos=(), controle=(ARQ, INF), obs='', faixa=None):
    larg = round(math.dist(a, b), 3) if faixa is None else faixa[1] - faixa[0]
    bruta = larg * alt if faixa is None else larg * (faixa[3] - faixa[2])
    ab = sum(w * h for _, w, h, _ in aberturas)
    ni = (2 * NICHO_P * larg + 2 * NICHO_P * NICHO_H) if nicho else 0.0
    PANOS.append(dict(id=pid, elev=elev, cod=cod, amb=amb, parede=parede, a=a, b=b, lado=lado, alt=alt, larg=larg,
                      aberturas=[list(x) for x in aberturas], pos=list(pos), nicho=nicho, faixa=faixa,
                      bruta=round(bruta, 4), desc=round(ab, 4), nicho_m2=round(ni, 4), liq=round(bruta - ab + ni, 4),
                      controle=list(controle), obs=obs))

# Sala e fachadas — Pedra Moledo
pano('F-S', 'E01', 'RP01', 'Sala — fachada sul (externa)', 'face externa sul, x 11,441 → 15,341',
     (11.441, 19.536), (15.341, 19.536), (13.4, 19.2), 3.20, obs='Inclui a face do pilar junto à garagem (0,15 m), conforme imagem enviada')
pano('F-L', 'E02', 'RP01', 'Sala — fachada leste (externa)', 'face externa leste, y 19,536 → 24,055 (até o muro)',
     (15.341, 19.536), (15.341, 24.055), (15.7, 21.8), 3.20, aberturas=[J01], pos=[0.70],
     obs='Desconta só a janela J01; pedra abaixo, acima e dos lados')
pano('S-TV', 'E03', 'RP01', 'Sala — parede da TV (interna)', 'face interna sul, x 11,591 → 15,191',
     (11.591, 19.686), (15.191, 19.686), (13.4, 20.0), 3.40, obs='Parede toda; PD 3,40 m do DWG (imagem cota 3,75 × 3,591 m)')
# Banheiros — box planificado: lateral (RP02 0,90) + fundo (revestimento especial, janela e nicho) + lateral (RP02 0,90)
def box(elev, amb, fundo_cod, lat1, fundo, lat2, lados, jan=None, jpos=None):
    pano(f'{elev}-L1', elev, 'RP02', amb, 'lateral do box (0,90 m)', lat1[0], lat1[1], lados[0], 2.85)
    pano(f'{elev}-F', elev, fundo_cod, amb, 'fundo do box (parede da janela / nicho)', fundo[0], fundo[1], lados[1], 2.85,
         aberturas=[jan] if jan else [], pos=[jpos] if jan else [], nicho=True)
    pano(f'{elev}-L2', elev, 'RP02', amb, 'lateral do box (0,90 m)', lat2[0], lat2[1], lados[2], 2.85)

box('E04', 'Banheiro Casal', 'RP03', ((6.141, 37.286), (6.141, 36.386)), ((6.141, 36.386), (4.191, 36.386)),
    ((4.191, 36.386), (4.191, 37.286)), [(6.0, 36.8), (5.2, 36.5), (4.3, 36.8)], J04, 6.141 - 5.366)
box('E05', 'WC 02', 'RP04', ((7.191, 31.586), (6.291, 31.586)), ((6.291, 31.586), (6.291, 33.086)),
    ((6.291, 33.086), (7.191, 33.086)), [(6.7, 31.7), (6.4, 32.3), (6.7, 33.0)], J04, 31.811 - 31.586)
box('E06', 'WC 01', 'RP04', ((7.191, 29.936), (6.291, 29.936)), ((6.291, 29.936), (6.291, 31.436)),
    ((6.291, 31.436), (7.191, 31.436)), [(6.7, 30.05), (6.4, 30.7), (6.7, 31.35)], J04, 30.161 - 29.936)
box('E07', 'Banheiro Externo', 'RP05', ((12.191, 32.486), (11.291, 32.486)), ((11.291, 32.486), (11.291, 33.886)),
    ((11.291, 33.886), (12.191, 33.886)), [(11.7, 32.6), (11.4, 33.2), (11.7, 33.8)])
# Lavanderia, cozinha e balcão
pano('LAV', 'E08', 'RP02', 'Lavanderia', 'parede inferior inteira (divisa com a garagem)', (8.441, 20.286), (5.691, 20.286), (7.0, 20.4), 2.85)
pano('COZ-O', 'E09', 'RP07', 'Cozinha', 'parede esquerda inteira', (5.691, 22.436), (5.691, 26.636), (5.8, 24.5), 2.85,
     aberturas=[J02], pos=[23.761 - 22.436], controle=(ARQ, INF, OBRA), obs='Altura = PD 2,85 m (paredes inteiras, informado)')
pano('COZ-N', 'E09', 'RP07', 'Cozinha', 'parede superior inteira', (5.691, 26.636), (9.941, 26.636), (7.8, 26.5), 2.85,
     controle=(ARQ, INF, OBRA), obs='Altura = PD 2,85 m (paredes inteiras, informado)')
pano('BAL-S', 'E10', 'RP02', 'Cozinha — balcão', 'face sul da mureta 1,90 × 0,15 (DWG Prefeitura)', (9.141, 24.036), (7.241, 24.036), (8.2, 23.95), 1.00)
pano('BAL-N', 'E10', 'RP02', 'Cozinha — balcão', 'face norte da mureta 1,90 × 0,15 (DWG Prefeitura)', (7.241, 24.186), (9.141, 24.186), (8.2, 24.27), 1.00)
# Varanda — Travertino Rock Face
pano('VAR-F', 'E11', 'RP06', 'Varanda Gourmet', 'faixa da bancada: 2,75 m, de 0,98 a 1,48 m, junto à churrasqueira',
     (11.291, 28.686), (11.291, 31.436), (11.4, 30.0), 3.40, faixa=(0.85, 3.60, 0.98, 1.48), controle=(ARQ, INF, OBRA),
     obs='Posição ao longo da parede: junto à churrasqueira, conforme elevação enviada')
pano('CH-F', 'E11', 'RP06', 'Varanda Gourmet — churrasqueira', 'frente (0,90 × 3,40 m)', (12.091, 31.436), (12.091, 32.336), (12.2, 31.9), 3.40,
     aberturas=[BOCA], pos=[0.05], controle=(INF, OBRA), obs='Desconta a boca 0,80 × 0,80; posição vertical da boca A CONFIRMAR')
pano('CH-L', 'E12', 'RP06', 'Varanda Gourmet — churrasqueira', 'lateral esquerda (0,80 × 3,40 m)', (11.291, 31.436), (12.091, 31.436), (11.7, 31.3), 3.40,
     controle=(INF,), obs='Lateral direita encostada na parede do Banheiro Externo: sem revestimento')

TOT = {}
for p in PANOS:
    TOT[p['cod']] = round(TOT.get(p['cod'], 0) + p['liq'], 4)

ELEV = {
    'E01': ('Fachada sul da Sala', 'Pedra Moledo externa · vista de fora', 3),
    'E02': ('Fachada leste da Sala', 'Pedra Moledo externa · vista de fora', 3),
    'E03': ('Sala — parede da TV', 'Pedra Moledo interna · vista de dentro', 3),
    'E04': ('Banheiro Casal — box planificado', 'vista de dentro, olhando o fundo do box', 4),
    'E05': ('WC 02 — box planificado', 'vista de dentro, olhando o fundo do box', 4),
    'E06': ('WC 01 — box planificado', 'vista de dentro, olhando o fundo do box', 4),
    'E07': ('Banheiro Externo — box planificado', 'vista de dentro, olhando o fundo do box', 4),
    'E08': ('Lavanderia — parede inferior', 'vista de dentro', 5),
    'E09': ('Cozinha — paredes esquerda e superior', 'planificadas no canto', 5),
    'E10': ('Cozinha — balcão (mureta)', 'faces sul e norte iguais', 5),
    'E11': ('Varanda Gourmet — parede esquerda e churrasqueira', 'vista de dentro', 5),
    'E12': ('Churrasqueira — lateral esquerda', 'vista de dentro', 5),
}

PEND = [
    'Fatto Oliva (Banheiro Externo) e cerâmica simples (Cozinha): altura adotada = PD 2,85 m — confirmar.',
    'Churrasqueira: altura de instalação da boca 0,80 × 0,80 (desenhada em posição indicativa).',
    'Rodapé × revestimento até o piso: nos trechos revestidos dos banheiros, lavanderia, cozinha e parede da TV, o Caderno 01/02 prevê rodapé R01 (≈ 28,35 m). Confirmar se o rodapé sai desses trechos.',
    'Churrasqueira (0,90 × 0,80 m) ocupa 0,72 m² do piso P02 da Varanda e trechos de rodapé R02 — o Caderno 01/02 não desconta. Confirmar a atualização.',
    'Fachada sul: pano inclui a face do pilar junto à garagem (0,15 m), conforme imagem — conferir.',
    'Parede da TV: largura pela geometria do DWG = 3,60 m (imagem cota 3,75 m); altura = PD 3,40 m do DWG (imagem cota 3,591 m).',
    'Banheiro Externo: o quadro de esquadrias indica J06 sobre P11 (outra parede); o nicho segue o fundo do box, conforme informado.',
    'Balcão: revestidas apenas as duas faces de 1,90 × 1,00 m; topo e cabeceiras (0,15 m) sem revestimento — confirmar. Mureta só consta no DWG da Prefeitura.',
    'Moledo e Travertino Rock Face (pedreira): formato, espessura, assentamento e rejunte A CONFIRMAR. Confete WH e Fatto Oliva: rejunte e espessura A CONFIRMAR na ficha.',
    'Imagens de referência: divergências anotadas nas folhas 03 a 05 (formato do Confete Pink, fundo do box do Banheiro Externo, extensão na Lavanderia).',
    'Paginação não faz parte deste caderno. Quantitativos líquidos, sem perdas de compra. Conferir todas as medidas no local.',
]


# ================================================================ planta 1/100
def base_neutra(pl):
    """Planta limpa: pisos neutros, paredes cheias, vãos e esquadrias do DWG (mesma geometria do caderno 01/02)."""
    PR.padroes(pl)
    for v in PR.G['verdes']:
        pl.poly(v, fill=f'url(#gr_{pl.s})', stroke='#a3ab85', sw=0.08, extra='fill-opacity="0.55"')
    for zid, z in PR.Z.items():
        if zid == 'CAL':
            continue
        f = '#fdfbf6' if z['cod'] in ('P01', 'P02') else '#f2eee4'
        pl.poly(z['pts'], z['holes'], fill=f, stroke='none')
    pl.poly(PR.G['piscina'], fill='#e3ebe9', stroke=C['ink'], sw=0.15)
    lote = PR.G['lote'] + [PR.G['lote'][0]]
    pl.line(lote, C['olive2'], 0.15, dash=(3.0, 0.8, 0.5, 0.8))
    for w in PR.G['paredes']:
        pl.poly(w, fill=C['ink'], stroke=C['ink'], sw=0.05)
    for vid, v in PR.D['vaos'].items():
        if vid == 'P04':
            continue
        a, b = v['a'], v['b']
        if vid == 'P03':
            a, b = (17.266, a[1]), (17.266, b[1])
        faixa = LineString([a, b]).buffer(0.075, cap_style=2)
        pl.poly([tuple(p) for p in faixa.exterior.coords][:-1], fill=C['porta'], stroke='none')
        L = math.dist(a, b)
        nx, ny = -(b[1] - a[1]) / L * 0.075, (b[0] - a[0]) / L * 0.075
        for k in (1, -1):
            pl.line([(a[0] + k * nx, a[1] + k * ny), (b[0] + k * nx, b[1] + k * ny)], C['ink'], 0.07)
    for L in PR.G['linhas']['caixilhos']:
        pl.line(L, C['ink'], 0.12)
    for L in PR.G['linhas']['portas']:
        pl.line(L, '#6b6d5c', 0.08)


BANDA = 0.10     # espessura gráfica da faixa de revestimento na planta (fora de escala)


def faixa_pano(p):
    a, b = p['a'], p['b']
    L = math.dist(a, b)
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    n1 = (-uy, ux)
    m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    s = 1 if (p['lado'][0] - m[0]) * n1[0] + (p['lado'][1] - m[1]) * n1[1] > 0 else -1
    o = (n1[0] * s * BANDA, n1[1] * s * BANDA)
    pts = [a, b, (b[0] + o[0], b[1] + o[1]), (a[0] + o[0], a[1] + o[1])]
    mid = (m[0] + o[0] / 2, m[1] + o[1] / 2)
    return pts, mid


# etiquetas: (código, posição da etiqueta, [ids dos panos apontados])
TAGS = [
    ('RP01', (14.75, 18.75), ['F-S']), ('RP01', (16.55, 22.9), ['F-L']), ('RP01', (14.3, 20.45), ['S-TV']),
    ('RP03', (5.17, 35.55), ['E04-F']), ('RP02', (5.17, 38.95), ['E04-L1', 'E04-L2']),
    ('RP04', (4.95, 32.33), ['E05-F']), ('RP02', (7.75, 32.33), ['E05-L1', 'E05-L2']),
    ('RP04', (4.95, 30.68), ['E06-F']), ('RP02', (7.75, 30.68), ['E06-L1', 'E06-L2']),
    ('RP05', (12.0, 33.12), ['E07-F']), ('RP02', (13.0, 33.12), ['E07-L1', 'E07-L2']),
    ('RP02', (6.35, 20.95), ['LAV']), ('RP07', (6.75, 25.85), ['COZ-O', 'COZ-N']),
    ('RP02', (6.55, 24.11), ['BAL-S', 'BAL-N']), ('RP06', (13.2, 31.25), ['VAR-F', 'CH-F', 'CH-L']),
]
# marcadores de elevação: posição e direção do olhar (graus, 0 = leste, 90 = norte)
MARC = {'E01': ((12.2, 18.75), 90), 'E02': ((16.45, 21.4), 180), 'E03': ((12.6, 20.75), 270), 'E04': ((5.62, 38.0), 270),
        'E05': ((8.62, 32.33), 180), 'E06': ((8.62, 30.68), 180), 'E07': ((14.05, 33.12), 180), 'E08': ((7.55, 20.95), 270),
        'E09': ((8.6, 25.75), 150), 'E10': ((9.5, 23.35), 90), 'E11': ((14.05, 29.95), 180), 'E12': ((11.72, 30.4), 90)}


def planta():
    pl = Planta(3.6, 18.2, 17.4, 40.35, 75)
    base_neutra(pl)
    # balcão (DWG Prefeitura) e churrasqueira (informada) — contornos
    pl.poly([(7.241, 24.036), (9.141, 24.036), (9.141, 24.186), (7.241, 24.186)], fill='#e7e0d1', stroke=C['ink'], sw=0.13)
    ch = [(11.291, 31.436), (12.091, 31.436), (12.091, 32.336), (11.291, 32.336)]
    pl.poly(ch, fill='#ede4d2', stroke=C['ink'], sw=0.18)
    pl.line([ch[0], ch[2]], '#8a8272', 0.08)
    pl.line([ch[1], ch[3]], '#8a8272', 0.08)
    # faixas de revestimento
    mids = {}
    for p in PANOS:
        pts, mid = faixa_pano(p)
        pl.poly(pts, fill=PROD[p['cod']]['linha'], stroke=C['ink'], sw=0.06)
        mids[p['id']] = mid
    # nomes dos ambientes (discretos)
    for p, t, r in [((4.55, 38.3), 'BANHEIRO CASAL', 90), ((7.69, 32.85), 'WC 02', 0), ((7.69, 31.2), 'WC 01', 0),
                    ((13.2, 33.62), 'BANHEIRO EXTERNO', 0), ((7.07, 21.75), 'LAVANDERIA', 0), ((7.9, 25.2), 'COZINHA', 0),
                    ((13.2, 24.2), 'SALA TV / SALA JANTAR', 0), ((13.3, 28.55), 'VARANDA GOURMET', 0),
                    ((12.27, 38.1), 'QUARTO CASAL', 0), ((8.04, 38.1), 'CLOSET CASAL', 0), ((7.74, 34.75), 'QUARTO 02', 0),
                    ((7.74, 28.3), 'QUARTO 01', 0), ((12.94, 35.15), 'ESCRITÓRIO', 0), ((10.55, 32.0), 'CIRCULAÇÃO INTERNA', 90),
                    ((7.9, 17.6), 'GARAGEM', 0), ((4.92, 28.2), 'CORREDOR LATERAL EXTERNO', 90)]:
        pl.text(p, t, size=4.2, weight=600, ls=0.45, rot=-r, fill='#77796a')
    pl.text((8.19, 23.72), 'balcão 1,90 × 0,15', size=3.6, weight=500, italic=True, fill='#5a5d49')
    pl.text((12.55, 32.0), 'churrasqueira', size=3.6, weight=500, italic=True, fill='#5a5d49', anchor='start')
    pl.text((12.55, 31.72), '0,90 × 0,80', size=3.6, weight=500, italic=True, fill='#5a5d49', anchor='start')
    # etiquetas com linha de chamada
    for cod, pos, ids in TAGS:
        for pid in ids:
            t = mids[pid]
            pl.line([pos, t], '#5a5d49', 0.12)
            pl.add(f'<circle cx="{pl.P(t)[0]}" cy="{pl.P(t)[1]}" r="{pl.mm(0.45)}" fill="#5a5d49"/>')
    for cod, pos, ids in TAGS:
        x, y = pl.P(pos)
        w, h = pl.mm(9.2), pl.mm(3.3)
        pl.add(f'<rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" rx="{h / 2}" fill="{PROD[cod]["linha"]}" '
               f'stroke="{C["bg"]}" stroke-width="{pl.mm(0.35)}"/>'
               f'<text x="{x}" y="{y + pl.mm(0.1)}" font-family="Manrope" font-size="{pl.pt(4.6)}" font-weight="700" fill="#fff" '
               f'text-anchor="middle" dominant-baseline="middle" letter-spacing="{pl.pt(0.2)}">{cod}</text>')
    # marcadores de elevação (código / folha)
    for e, (p, ang) in MARC.items():
        x, y = pl.P(p)
        r = pl.mm(2.7)
        t = math.radians(-ang)
        tip = (x + math.cos(t) * r * 1.85, y + math.sin(t) * r * 1.85)
        b1 = (x + math.cos(t + 0.62) * r, y + math.sin(t + 0.62) * r)
        b2 = (x + math.cos(t - 0.62) * r, y + math.sin(t - 0.62) * r)
        folha = ELEV[e][2]
        pl.add(f'<path d="M{tip[0]},{tip[1]} L{b1[0]},{b1[1]} L{b2[0]},{b2[1]} Z" fill="{C["ink"]}"/>'
               f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fdfbf6" stroke="{C["ink"]}" stroke-width="{pl.mm(0.25)}"/>'
               f'<path d="M{x - r * 0.82},{y} L{x + r * 0.82},{y}" stroke="{C["ink"]}" stroke-width="{pl.mm(0.18)}"/>'
               f'<text x="{x}" y="{y - r * 0.38}" font-family="Manrope" font-size="{pl.pt(3.9)}" font-weight="700" fill="{C["ink"]}" '
               f'text-anchor="middle" dominant-baseline="middle">{e}</text>'
               f'<text x="{x}" y="{y + r * 0.42}" font-family="Manrope" font-size="{pl.pt(3.5)}" font-weight="500" fill="{C["rust_t"]}" '
               f'text-anchor="middle" dominant-baseline="middle">{folha:02d}</text>')
    return pl


def folha1():
    pl = planta()
    svg, wmm, hmm = pl.svg()
    left = 10 + (235 - wmm) / 2
    top = 10 + (307 - hmm) / 2
    itens = ''.join(f"<div class='it' style='align-items:flex-start'><div class='sw' style='background:{v['linha']};border-color:{C['ink']};margin-top:0.4mm'></div>"
                    f"<div><b>{k}</b> {esc(v['nome'].split(' — ')[0])}<div style='font-size:5.8pt;color:{C['olive2']}'>{esc(v['fab'])}</div></div></div>"
                    for k, v in PROD.items())
    leg = f"""
<div class="abs leg" style="left:250.5mm;top:10mm;width:37mm">
  <div class="lbl">Legenda</div>{itens}
  <div class="it"><svg width="7mm" height="4mm" viewBox="0 0 7 4" style="margin-right:2.4mm;flex:none"><rect x="0" y="0" width="7" height="1.6" fill="{C['ink']}"/><rect x="0" y="1.6" width="7" height="1" fill="#a88a5c" stroke="{C['ink']}" stroke-width="0.15"/></svg><div>Face revestida (faixa gráfica, fora de escala)</div></div>
  <div class="it"><svg width="7mm" height="7mm" viewBox="0 0 7 7" style="margin-right:2.4mm;flex:none"><path d="M3.5,0.1 L5.1,2.2 L1.9,2.2Z" fill="{C['ink']}"/><circle cx="3.5" cy="4.3" r="2.5" fill="#fdfbf6" stroke="{C['ink']}" stroke-width="0.25"/><line x1="1.5" y1="4.3" x2="5.5" y2="4.3" stroke="{C['ink']}" stroke-width="0.18"/></svg><div>Elevação: código / folha</div></div>
  <div class="lbl" style="margin-top:7mm">Escala</div>
  <div class="disp" style="font-size:21pt;margin-top:1.4mm">1/75</div>
  {PR.escala_bar(75)}
  <div class="small" style="margin-top:2.2mm;color:{C['olive2']}">Imprimir em A3 sem ajuste de escala.</div>
</div>"""
    rows = ''.join(f"<tr><td style='padding:0.6mm 1.5mm'><span class='cb' style='background:{PROD[c]['linha']}'>{c}</span></td><td style='padding:0.6mm 1.5mm'>{esc(PROD[c]['nome'].split(' — ')[0])}</td><td class='n' style='padding:0.6mm 1.5mm'>{br(TOT[c])}</td></tr>" for c in PROD)
    idx = ''.join(f"<tr><td style='padding:0.5mm 1.5mm'><span class='cb ol' style='border-radius:1mm;height:4.4mm;min-width:6mm;font-size:4.4pt'>{e}</span></td><td style='padding:0.5mm 1.5mm;font-size:6.2pt'>{esc(t)}</td><td class='n' style='padding:0.5mm 1.5mm;font-size:6.2pt'>{f:02d}/{NF:02d}</td></tr>"
                  for e, (t, s, f) in ELEV.items())
    t1 = f"""
<div class="abs" style="left:10mm;top:322mm;width:77mm">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:1.6mm"><span class="ttl">Revestimentos</span><span style="font-size:5.6pt;color:{C['olive2']}">áreas líquidas em m²</span></div>
  <table style="font-size:6pt">{rows}
  <tr class="tot"><td colspan="2" style="padding:0.8mm 1.5mm">Total</td><td class="n" style="padding:0.8mm 1.5mm">{br(sum(TOT.values()))}</td></tr></table>
</div>
<div class="abs" style="left:92mm;top:322mm;width:77mm">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:1.6mm"><span class="ttl">Elevações</span><span style="font-size:5.6pt;color:{C['olive2']}">escala 1/50</span></div>
  <table>{idx}</table>
</div>"""
    return f"""<section class="sheet">
<div class="abs" style="left:{left:.2f}mm;top:{top:.2f}mm">{svg}</div>{leg}{t1}
{PR.carimbo(1, 'Planta de revestimentos de parede', '1/75', 321.7, 90.5)}</section>"""


# ============================================================= quadro (folha 02)
def folha2():
    rows = ''
    for c, pr in PROD.items():
        rows += f"<tr class='sec'><td colspan='10'>{esc(c + ' · ' + pr['nome'] + ' — ' + pr['fab']).upper()}</td></tr>"
        grupos = {}
        for x in [x for x in PANOS if x['cod'] == c]:
            k = (x['elev'], x['parede'].replace('face sul', 'faces sul e norte').replace('face norte', 'faces sul e norte'), x['larg'], x['alt'])
            if k in grupos:
                g = grupos[k]
                g['n'] += 1
                for f in ('bruta', 'desc', 'nicho_m2', 'liq'):
                    g[f] = round(g[f] + x[f], 4)
            else:
                grupos[k] = dict(x, n=1, parede=k[1])
        for p in grupos.values():
            ab = ' + '.join(f"{n} {br(w)}×{br(h)}" for n, w, h, _ in p['aberturas']) or '—'
            dims = ('2 × ' if p['n'] == 2 else '') + f"{br(p['larg'])} × {br(p['faixa'][3] - p['faixa'][2] if p['faixa'] else p['alt'])}"
            rows += (f"<tr><td><span class='cb ol' style='border-radius:1mm;font-size:4.6pt'>{p['elev']}</span></td>"
                     f"<td>{esc(p['amb'])}<div style='font-size:5.8pt;color:{C['olive2']}'>{esc(p['parede'])}</div></td>"
                     f"<td class='n'>{dims}</td><td class='n'>{br(p['bruta'])}</td><td style='font-size:6.1pt'>{esc(ab)}</td>"
                     f"<td class='n'>{br(p['desc']) if p['desc'] else '—'}</td><td class='n'>{br(p['nicho_m2']) if p['nicho'] else '—'}</td>"
                     f"<td class='n'><b>{br(p['liq'])}</b></td><td style='font-size:5.8pt'>{esc(p['obs'])}</td><td>{tags(p['controle'])}</td></tr>")
        rows += f"<tr class='sub'><td></td><td colspan='6'>Subtotal {c}</td><td class='n'>{br(TOT[c])}</td><td colspan='2'></td></tr>"
    rows += f"<tr class='tot'><td></td><td colspan='6'>TOTAL GERAL DE REVESTIMENTOS DE PAREDE</td><td class='n'>{br(sum(TOT.values()))}</td><td colspan='2'></td></tr>"
    spec = ''.join(f"<tr><td><span class='cb' style='background:{v['linha']}'>{k}</span></td><td>{esc(v['nome'])}</td><td>{esc(v['fab'])}</td>"
                   f"<td style='white-space:nowrap'>{esc(v['formato'])}</td><td style='white-space:nowrap'>{esc(v['esp'])}</td><td>{esc(v['acab'])}</td><td style='font-size:6.1pt'>{esc(v['rejunte'])}</td></tr>"
                   for k, v in PROD.items())
    return f"""<section class="sheet">
<div class="abs head" style="left:10mm;top:10mm"><div class="lbl">Revestimentos de parede · Revisão 00</div><h1>Quadro de revestimentos</h1></div>
<div class="abs" style="left:10mm;top:33mm;width:277mm">
<table>
<colgroup><col style="width:11mm"><col style="width:58mm"><col style="width:24mm"><col style="width:13mm"><col style="width:30mm"><col style="width:13mm"><col style="width:12mm"><col style="width:14mm"><col><col style="width:27mm"></colgroup>
<tr><th>Elev.</th><th>Ambiente / pano</th><th class="n">Larg. × alt. (m)</th><th class="n">Bruta</th><th>Aberturas descontadas</th><th class="n">Desc.</th><th class="n">Nicho</th><th class="n">Líquida m²</th><th>Observação</th><th>Controle</th></tr>
{rows}
</table>
</div>
<div class="normas notes" style="top:332mm;height:78.1mm;display:flex;gap:6mm;padding-top:4.5mm">
<div style="flex:1"><h4 style="margin-top:0">Critérios (informados)</h4><ol>
<li><b class="nn">1</b><span>Área líquida = largura × altura − aberturas + nicho. Alturas a partir do piso acabado.</span></li>
<li><b class="nn">2</b><span>Alturas: Moledo externo 3,20 m; Moledo interno = PD 3,40 m; Santorini 2,85 m e balcão 1,00 m; Confete = PD do local (2,85 m); travertino: faixa 0,98–1,48 m e churrasqueira 3,40 m.</span></li>
<li><b class="nn">3</b><span>Box: 0,90 m de cada parede lateral em Santorini em todos os banheiros.</span></li>
</ol></div>
<div style="flex:1"><h4 style="margin-top:0">&nbsp;</h4><ol>
<li><b class="nn">4</b><span>Nicho em toda a largura da parede da janela (no Banheiro Externo, no fundo do box): altura 0,30 m, profundidade 0,10 m, base a 1,00 m. Interior no mesmo revestimento da parede: acréscimo = base + teto + 2 laterais.</span></li>
<li><b class="nn">5</b><span>Dados técnicos pelos links informados (sites consultados indiretamente); conferir na ficha técnica antes da compra.</span></li>
</ol></div><div class="small" style="position:absolute;left:7.5mm;right:7.5mm;bottom:5.5mm">{PR.LEG_CONTROLE}</div></div>
{PR.carimbo(2, 'Quadro de revestimentos', 'Sem escala', 332.0, 78.1)}
</section>"""


# ================================================================ elevações 1/50
K = 20.0     # mm por metro (1/50)


def pat_defs():
    return f"""<defs>
<pattern id="t1" patternUnits="userSpaceOnUse" width="9" height="7"><rect width="9" height="7" fill="{PROD['RP01']['fill']}"/>
<path d="M0.3,0.4 L4,0.2 L4.4,3 L0.6,3.4 Z M4.8,0.3 L8.6,0.6 L8.3,3.2 L4.9,3 Z M0.4,3.8 L3,3.7 L3.2,6.6 L0.3,6.7 Z M3.6,3.6 L8.5,3.7 L8.7,6.5 L3.7,6.6 Z" fill="#e0d3b8" stroke="#a8997a" stroke-width="0.15"/></pattern>
<pattern id="t2" patternUnits="userSpaceOnUse" width="4" height="4"><rect width="4" height="4" fill="{PROD['RP02']['fill']}"/><circle cx="1" cy="1" r="0.12" fill="#c9b894"/></pattern>
<pattern id="t3" patternUnits="userSpaceOnUse" width="3" height="3"><rect width="3" height="3" fill="{PROD['RP03']['fill']}"/>
<circle cx="0.7" cy="0.8" r="0.18" fill="#d9b44a"/><circle cx="2.2" cy="2.1" r="0.15" fill="#7fa6c9"/><circle cx="2.3" cy="0.6" r="0.12" fill="#d4789b"/></pattern>
<pattern id="t4" patternUnits="userSpaceOnUse" width="3" height="3"><rect width="3" height="3" fill="{PROD['RP04']['fill']}"/>
<circle cx="0.7" cy="0.8" r="0.18" fill="#b94a79"/><circle cx="2.2" cy="2.1" r="0.15" fill="#e8a33c"/><circle cx="2.3" cy="0.6" r="0.12" fill="#fff"/></pattern>
<pattern id="t5" patternUnits="userSpaceOnUse" width="2.2" height="6"><rect width="2.2" height="6" fill="{PROD['RP05']['fill']}"/><path d="M0.4,0 C0.7,2 0.2,4 0.5,6" stroke="#8e936a" stroke-width="0.2" fill="none"/></pattern>
<pattern id="t6" patternUnits="userSpaceOnUse" width="8" height="3"><rect width="8" height="3" fill="{PROD['RP06']['fill']}"/>
<path d="M0,1.5 L8,1.5 M3,0 L3,1.5 M6.5,1.5 L6.5,3" stroke="#b8a584" stroke-width="0.25"/></pattern>
<pattern id="t7" patternUnits="userSpaceOnUse" width="3" height="3" patternTransform="rotate(45)"><rect width="3" height="3" fill="{PROD['RP07']['fill']}"/><line x1="0" y1="0" x2="0" y2="3" stroke="#e2dccd" stroke-width="0.25"/></pattern>
</defs>"""


PAT = {'RP01': 't1', 'RP02': 't2', 'RP03': 't3', 'RP04': 't4', 'RP05': 't5', 'RP06': 't6', 'RP07': 't7'}


def T(x, y, s, size=2.3, anchor='middle', weight=500, fill=C['ink'], rot=0):
    tr = f' transform="rotate({rot} {x} {y})"' if rot else ''
    return (f'<text x="{x:.2f}" y="{y:.2f}" font-family="Manrope" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{tr}>{esc(s)}</text>')


def dim_h(x0, x1, y, txt, above=False):
    ty = y - 1.0 if above else y + 3.0
    return (f'<path d="M{x0:.2f},{y:.2f} L{x1:.2f},{y:.2f} M{x0:.2f},{y - 1:.2f} L{x0:.2f},{y + 1:.2f} M{x1:.2f},{y - 1:.2f} L{x1:.2f},{y + 1:.2f}" stroke="{C["rust"]}" stroke-width="0.2"/>'
            + T((x0 + x1) / 2, ty, txt, 2.2, weight=700, fill=C['rust_t']))


def dim_v(x, y0, y1, txt, left=True):
    tx = x - 1.2 if left else x + 1.2
    return (f'<path d="M{x:.2f},{y0:.2f} L{x:.2f},{y1:.2f} M{x - 1:.2f},{y0:.2f} L{x + 1:.2f},{y0:.2f} M{x - 1:.2f},{y1:.2f} L{x + 1:.2f},{y1:.2f}" stroke="{C["rust"]}" stroke-width="0.2"/>'
            + T(tx, (y0 + y1) / 2 + 0.8, txt, 2.2, anchor='end' if left else 'start', weight=700, fill=C['rust_t']))


def badge(x, y, s, fill):
    w = 2.4 + len(s) * 1.35
    return (f'<rect x="{x - w / 2:.2f}" y="{y - 1.7:.2f}" width="{w:.2f}" height="3.4" rx="1.7" fill="{fill}"/>'
            + T(x, y + 0.8, s, 2.1, weight=700, fill='#fff'))


def elevacao(panels, H, ml=14, mr=16, mt=6, mb=20, extras=''):
    """panels: [{w, cod|None, alt (revestido até), janela:(nome,w,h,peit,pos)|None, nicho, label, faixa:(x0,x1,z0,z1)|None, boca}]"""
    W = sum(p['w'] for p in panels)
    wmm, hmm = W * K, H * K
    tw, th = ml + wmm + mr, mt + hmm + mb
    X = lambda m: ml + m * K
    Y = lambda z: mt + (H - z) * K
    s = pat_defs()
    s += f'<rect x="{X(0):.2f}" y="{Y(H):.2f}" width="{wmm:.2f}" height="{hmm:.2f}" fill="#fbf8f1" stroke="{C["ink"]}" stroke-width="0.35"/>'
    x = 0.0
    chain = [0.0]
    for p in panels:
        cod = p.get('cod')
        if cod and not p.get('faixa'):
            s += f'<rect x="{X(x):.2f}" y="{Y(p["alt"]):.2f}" width="{p["w"] * K:.2f}" height="{p["alt"] * K:.2f}" fill="url(#{PAT[cod]})" stroke="{C["ink"]}" stroke-width="0.25"/>'
        if p.get('faixa'):
            f0, f1, z0, z1 = p['faixa']
            s += f'<rect x="{X(x + f0):.2f}" y="{Y(z1):.2f}" width="{(f1 - f0) * K:.2f}" height="{(z1 - z0) * K:.2f}" fill="url(#{PAT[cod]})" stroke="{C["ink"]}" stroke-width="0.25"/>'
            s += dim_v(X(x + f1) + 3, Y(z1), Y(z0), f"{br(z1 - z0)}", left=False)
            s += dim_v(X(x + f0) - 3, Y(z0), Y(0), f"{br(z0)}")
            s += dim_h(X(x + f0), X(x + f1), Y(z1) - 3, br(f1 - f0), above=True)
        if p.get('nicho'):
            s += (f'<rect x="{X(x):.2f}" y="{Y(NICHO_Z + NICHO_H):.2f}" width="{p["w"] * K:.2f}" height="{NICHO_H * K:.2f}" '
                  f'fill="url(#{PAT[cod]})" stroke="{C["ink"]}" stroke-width="0.35"/>'
                  f'<rect x="{X(x):.2f}" y="{Y(NICHO_Z + NICHO_H):.2f}" width="{p["w"] * K:.2f}" height="{NICHO_H * K:.2f}" fill="#000" fill-opacity="0.10"/>')
            s += T(X(x + p['w'] / 2), Y(NICHO_Z + NICHO_H / 2) + 0.8, 'nicho', 2.0, weight=700)
        if p.get('janela'):
            n, jw, jh, jp, jx = p['janela']
            s += (f'<rect x="{X(x + jx):.2f}" y="{Y(jp + jh):.2f}" width="{jw * K:.2f}" height="{jh * K:.2f}" fill="#fff" stroke="{C["ink"]}" stroke-width="0.3"/>'
                  f'<path d="M{X(x + jx):.2f},{Y(jp + jh):.2f} L{X(x + jx + jw):.2f},{Y(jp):.2f} M{X(x + jx + jw):.2f},{Y(jp + jh):.2f} L{X(x + jx):.2f},{Y(jp):.2f}" stroke="#b9b2a2" stroke-width="0.15"/>')
            s += T(X(x + jx + jw / 2), Y(jp + jh / 2) + 0.8, f'{n} {br(jw)} × {br(jh)}', 2.0, weight=700)
            s += T(X(x + jx + jw / 2), Y(jp + jh / 2) + 3.3, f'peitoril {br(jp)}', 1.9)
        if p.get('boca'):
            bw, bh, bx = p['boca']
            zb = 1.10     # posição indicativa (A CONFIRMAR)
            s += (f'<rect x="{X(x + bx):.2f}" y="{Y(zb + bh):.2f}" width="{bw * K:.2f}" height="{bh * K:.2f}" fill="#fff" stroke="{C["ink"]}" stroke-width="0.3" stroke-dasharray="1 0.6"/>')
            s += T(X(x + bx + bw / 2), Y(zb + bh / 2) + 0.2, 'boca', 2.0, weight=700)
            s += T(X(x + bx + bw / 2), Y(zb + bh / 2) + 2.6, f'{br(bw)} × {br(bh)}', 1.9)
            s += T(X(x + bx + bw / 2), Y(zb) + 2.6, 'altura A CONFIRMAR', 1.7, fill=C['rust_t'])
        if cod:
            s += badge(X(x + p['w'] / 2), Y(min(p['alt'], H)) + 4.2 if not p.get('faixa') else Y(p['faixa'][3]) - 7.5, cod, PROD[cod]['linha'])
        if p.get('label'):
            s += T(X(x + p['w'] / 2), Y(0) + 10.5, p['label'], 1.9, fill=C['olive2'])
        x += p['w']
        chain.append(x)
        if x < W - 1e-6:
            s += f'<path d="M{X(x):.2f},{Y(H):.2f} L{X(x):.2f},{Y(0):.2f}" stroke="{C["ink"]}" stroke-width="0.3"/>'
    for a, b in zip(chain, chain[1:]):
        s += dim_h(X(a), X(b), Y(0) + 3.5, br(b - a))
    if len(chain) > 2:
        s += dim_h(X(0), X(W), Y(0) + 13.5, br(W))
    s += dim_v(X(0) - 3.5, Y(H), Y(0), br(H))
    alts = sorted({p['alt'] for p in panels if p.get('cod') and not p.get('faixa') and p['alt'] < H - 1e-6})
    for a in alts:
        s += dim_v(X(W) + 3.5, Y(a), Y(0), br(a), left=False)
    if any(p.get('nicho') for p in panels):
        s += dim_v(X(W) + 9, Y(NICHO_Z), Y(0), br(NICHO_Z), left=False)
        s += dim_v(X(W) + 9, Y(NICHO_Z + NICHO_H), Y(NICHO_Z), br(NICHO_H), left=False)
    s += f'<path d="M{X(0) - 2:.2f},{Y(0):.2f} L{X(W) + 2:.2f},{Y(0):.2f}" stroke="{C["ink"]}" stroke-width="0.5"/>'
    s += extras
    return f'<svg width="{tw:.2f}mm" height="{th:.2f}mm" viewBox="0 0 {tw:.2f} {th:.2f}" xmlns="http://www.w3.org/2000/svg">{s}</svg>', tw


def bloco(e, svg, nota=''):
    t, sub, _ = ELEV[e]
    return (f"<div><div style='display:flex;align-items:center;gap:2.2mm'><span class='cb ol' style='border-radius:1mm'>{e}</span>"
            f"<span class='ttl' style='font-size:11pt'>{esc(t)}</span></div>"
            f"<div style='font-size:5.6pt;color:{C['olive2']};margin:0.6mm 0 1mm 8.6mm'>{esc(sub)} · 1/50{(' · ' + esc(nota)) if nota else ''}</div>{svg}</div>")


def P_(pid):
    return next(p for p in PANOS if p['id'] == pid)


def elev_simple(pid, H=None, label=''):
    p = P_(pid)
    H = H or p['alt']
    jan = None
    if p['aberturas']:
        n, w, h, peit = p['aberturas'][0]
        if peit is not None:
            jan = (n, w, h, peit, p['pos'][0])
    return elevacao([dict(w=p['larg'], cod=p['cod'], alt=p['alt'], janela=jan, nicho=p['nicho'], label=label)], H)[0]


def elev_box(e):
    ps = [p for p in PANOS if p['elev'] == e]
    panels = []
    for p, lab in zip(ps, ['lateral esquerda', 'fundo do box', 'lateral direita']):
        jan = None
        if p['aberturas']:
            n, w, h, peit = p['aberturas'][0]
            jan = (n, w, h, peit, p['pos'][0])
        panels.append(dict(w=p['larg'], cod=p['cod'], alt=p['alt'], janela=jan, nicho=p['nicho'], label=lab))
    return elevacao(panels, 2.85, mr=20)[0]


def especificacao():
    spec = ''.join(f"<tr><td><span class='cb' style='background:{v['linha']}'>{k}</span></td><td>{esc(v['nome'])}</td><td>{esc(v['fab'])}</td>"
                   f"<td style='white-space:nowrap'>{esc(v['formato'])}</td><td style='white-space:nowrap'>{esc(v['esp'])}</td><td>{esc(v['acab'])}</td><td style='font-size:6.1pt'>{esc(v['rejunte'])}</td></tr>"
                   for k, v in PROD.items())
    return f"""<div class="lbl" style="margin:0 0 2mm">Especificação dos revestimentos</div>
<table>
<colgroup><col style="width:13mm"><col style="width:62mm"><col style="width:36mm"><col style="width:22mm"><col style="width:22mm"><col style="width:36mm"><col></colgroup>
<tr><th>Cód.</th><th>Produto</th><th>Fabricante</th><th>Formato</th><th>Espessura</th><th>Acabamento</th><th>Rejunte</th></tr>{spec}
</table>"""


def ref(img, titulo, obs='', w=127):
    o = f"<div style='font-size:5.8pt;color:{C['rust_t']};margin-top:0.6mm;line-height:1.35'>{esc(obs)}</div>" if obs else ''
    return (f"<figure style='width:{w}mm;margin:0'><img src='imagens/{img}' style='width:{w}mm;display:block;border-radius:2.2mm'>"
            f"<figcaption style='font-size:6pt;margin-top:1.2mm;color:{C['olive2']}'><b style='color:{C['ink']}'>Imagem de referência</b> · {esc(titulo)} "
            f"— ilustrativa; valem as cotas e o quadro.{o}</figcaption></figure>")


def folha3():
    e1 = elev_simple('F-S')
    e2 = elev_simple('F-L')
    e3 = elev_simple('S-TV')
    return f"""<section class="sheet">
<div class="abs head" style="left:10mm;top:10mm"><div class="lbl">Revestimentos de parede · Revisão 00</div><h1>Elevações — Sala e fachadas</h1></div>
<div class="abs" style="left:10mm;top:36mm;width:277mm;display:flex;gap:14mm;flex-wrap:wrap">
{bloco('E01', e1, 'altura 3,20 m a partir do piso acabado externo')}
{bloco('E02', e2, 'desconta só a janela J01')}
{bloco('E03', e3, 'parede toda, PD 3,40 m (DWG)')}
</div>
<div class="abs" style="left:10mm;top:246mm;width:277mm">{especificacao()}</div>
<div class="abs" style="left:158mm;top:148mm">{ref('ref_sala_tv.jpg', 'Sala TV', 'Observação: a imagem mostra Moledo nas faixas ao lado do painel de madeira; o quantitativo considera a parede toda, conforme informado.', 129)}</div>
{nota_box([('RP01', 'Pedra Moledo, compra em pedreira: formato, espessura, assentamento e rejunte A CONFIRMAR.'),
           ('J01', 'Janela conforme Quadro de Esquadrias Rev. 01: 2,50 × 2,50 m, peitoril 0,50 m.'),
           ('E03', 'Largura pela geometria do DWG (3,60 m). A imagem de referência cota 3,75 m e 3,591 m de altura; adotado o PD de 3,40 m (informado).')], 3)}
{PR.carimbo(3, 'Elevações — Sala e fachadas', '1/50', 332.0, 78.1)}
</section>"""


def nota_box(itens, folha, extra=''):
    li = ''.join(f'<li><b class="nn" style="min-width:10.5mm">{esc(k)}</b><span>{esc(v)}</span></li>' for k, v in itens)
    return f"""<div class="normas notes" style="top:332mm;height:78.1mm;padding-top:4.5mm">
<h4 style="margin-top:0">Notas</h4><ol style="{'max-width:66mm' if extra else ''}">{li}</ol>{extra}
<div class="small" style="position:absolute;left:7.5mm;bottom:5mm;width:64mm">
<div class="lbl" style="font-size:6pt;margin-bottom:1mm">Escala 1/50</div>{escala50()}</div></div>"""


def escala50():
    segs = ''.join(f'<rect x="{i * 20}" y="0" width="20" height="1.5" fill="{C["ink"] if i % 2 == 0 else C["bg"]}" stroke="{C["ink"]}" stroke-width="0.25"/>' for i in range(3))
    return f'<svg width="61mm" height="5mm" viewBox="-0.5 -0.5 61 5">{segs}<text x="0" y="4.4" font-size="2" font-family="Manrope">0</text><text x="20" y="4.4" font-size="2" font-family="Manrope">1</text><text x="40" y="4.4" font-size="2" font-family="Manrope">2</text><text x="56" y="4.4" font-size="2" font-family="Manrope">3 m</text></svg>'


def nicho_corte():
    k = 100.0                      # 1/10: 1 m = 100 mm
    z_top, z_bot = 1.42, 0.88      # trecho mostrado
    x0, y0 = 4, 3
    Y = lambda z: y0 + (z_top - z) * k
    esp_par, esp_rev = 0.15, 0.012
    face = x0 + (esp_par + esp_rev) * k                 # face acabada
    s = pat_defs()
    s += f'<rect x="{x0}" y="{Y(z_top)}" width="{esp_par * k}" height="{(z_top - z_bot) * k}" fill="#e6dfd0" stroke="#8f8676" stroke-width="0.2"/>'
    s += f'<rect x="{x0 + esp_par * k}" y="{Y(z_top)}" width="{esp_rev * k}" height="{(z_top - z_bot) * k}" fill="url(#t4)" stroke="{C["ink"]}" stroke-width="0.25"/>'
    # recorte do nicho (profundidade 0,10 a partir da face acabada)
    nx = face - NICHO_P * k
    s += f'<rect x="{nx}" y="{Y(NICHO_Z + NICHO_H)}" width="{NICHO_P * k}" height="{NICHO_H * k}" fill="#fbf8f1" stroke="{C["ink"]}" stroke-width="0.35"/>'
    s += f'<rect x="{nx}" y="{Y(NICHO_Z + NICHO_H)}" width="{esp_rev * k}" height="{NICHO_H * k}" fill="url(#t4)" stroke="{C["ink"]}" stroke-width="0.2"/>'
    s += f'<rect x="{nx}" y="{Y(NICHO_Z) - esp_rev * k}" width="{NICHO_P * k}" height="{esp_rev * k}" fill="url(#t4)" stroke="{C["ink"]}" stroke-width="0.2"/>'
    s += f'<rect x="{nx}" y="{Y(NICHO_Z + NICHO_H)}" width="{NICHO_P * k}" height="{esp_rev * k}" fill="url(#t4)" stroke="{C["ink"]}" stroke-width="0.2"/>'
    s += dim_v(face + 5, Y(NICHO_Z + NICHO_H), Y(NICHO_Z), '0,30', left=False)
    s += dim_h(nx, face, Y(NICHO_Z + NICHO_H) - 4, '0,10', above=True)
    s += f'<path d="M{face + 3},{Y(NICHO_Z)} L{face + 16},{Y(NICHO_Z)}" stroke="{C["rust"]}" stroke-width="0.2" stroke-dasharray="1 0.6"/>'
    s += T(face + 17, Y(NICHO_Z) + 0.8, 'base a 1,00 m do piso acabado', 2.1, anchor='start', fill=C['rust_t'], weight=700)
    s += T(face + 5, Y(z_bot) - 8, 'Fundo, base, teto e laterais no', 2.1, anchor='start')
    s += T(face + 5, Y(z_bot) - 5, 'revestimento da parede (RP03/04/05).', 2.1, anchor='start')
    s += T(face + 5, Y(z_bot) - 2, 'Espessuras ilustrativas.', 2.1, anchor='start')
    s += T(x0 + esp_par * k / 2, Y(z_bot) + 3.5, 'parede', 2.0, fill=C['olive2'])
    return f'<svg width="80mm" height="62mm" viewBox="0 0 80 62" xmlns="http://www.w3.org/2000/svg">{s}</svg>'


def folha4():
    b = ''.join(bloco(e, elev_box(e)) for e in ('E04', 'E05', 'E06', 'E07'))
    extra = (f"<div style='position:absolute;left:80mm;top:4.5mm'><div class='lbl' style='font-size:6pt;margin-bottom:1mm'>Corte do nicho · ampliação 1/10</div>{nicho_corte()}</div>")
    return f"""<section class="sheet">
<div class="abs head" style="left:10mm;top:10mm"><div class="lbl">Revestimentos de parede · Revisão 00</div><h1>Elevações — Banheiros</h1></div>
<div class="abs" style="left:10mm;top:36mm;width:277mm;display:grid;grid-template-columns:1fr 1fr;gap:10mm 8mm">{b}</div>
{nota_box([('Box', 'Planificado: lateral esquerda + fundo + lateral direita, vistos de dentro. Laterais: 0,90 m de Santorini (RP02).'),
           ('Nicho', 'Em toda a largura da parede da janela; no Banheiro Externo, no fundo do box. 0,30 × 0,10 m, base a 1,00 m.'),
           ('J04', 'Janela 1,00 × 0,60 m, peitoril 1,50 m (Quadro de Esquadrias Rev. 01).')], 4, extra)}
<div class="abs" style="left:10mm;top:236mm;display:flex;gap:14mm">{ref('ref_wc_pink.jpg', 'WC 01 / WC 02', 'Divergência: a imagem mostra peças pequenas no Confete Pink; especificado 100 × 100 cm conforme o link informado — confirmar o formato.', 125)}{ref('ref_banheiro_externo.jpg', 'Banheiro Externo', 'Divergência: a imagem mostra porcelanato no fundo do box; especificado Fatto Oliva, conforme informado.', 125)}</div>
{PR.carimbo(4, 'Elevações — Banheiros', '1/50', 332.0, 78.1)}
</section>"""


def folha5():
    e8 = elev_simple('LAV')
    po, pn = P_('COZ-O'), P_('COZ-N')
    n, w, h, peit = po['aberturas'][0]
    e9 = elevacao([dict(w=po['larg'], cod='RP07', alt=2.85, janela=(n, w, h, peit, po['pos'][0]), label='parede esquerda'),
                   dict(w=pn['larg'], cod='RP07', alt=2.85, label='parede superior')], 2.85)[0]
    e10 = elevacao([dict(w=1.90, cod='RP02', alt=1.00, label='face sul = face norte')], 1.00, mb=14)[0]
    pf, pc = P_('VAR-F'), P_('CH-F')
    e11 = elevacao([dict(w=3.60, cod='RP06', alt=3.40, faixa=(0.85, 3.60, 0.98, 1.48), label='parede esquerda (pintura fora deste caderno)'),
                    dict(w=0.90, cod='RP06', alt=3.40, boca=(0.80, 0.80, 0.05), label='churrasqueira — frente')], 3.40, mr=12)[0]
    e12 = elevacao([dict(w=0.80, cod='RP06', alt=3.40, label='lateral esq.')], 3.40, ml=13, mr=6)[0]
    pend = ''.join(f'<li><b class="nn">{i}</b><span>{esc(s)}</span></li>' for i, s in enumerate(PEND, 1))
    return f"""<section class="sheet">
<div class="abs head" style="left:10mm;top:10mm"><div class="lbl">Revestimentos de parede · Revisão 00</div><h1>Elevações — Cozinha, Lavanderia e Varanda</h1></div>
<div class="abs" style="left:10mm;top:36mm;width:277mm;display:flex;flex-wrap:wrap;gap:8mm 12mm;align-items:flex-start">
{bloco('E09', e9, 'desconta a janela J02')}{bloco('E10', e10, 'mureta 1,90 × 0,15 m, h 1,00 m')}
{bloco('E11', e11, 'faixa junto à churrasqueira')}{bloco('E12', e12)}{bloco('E08', e8, 'parede inteira')}
</div>
<div class="normas notes" style="top:332mm;height:78.1mm;padding-top:4.5mm">
<h4 style="margin-top:0">Pendências</h4><ol style="columns:2;column-gap:6mm">{pend}</ol>
<div class="small" style="position:absolute;left:7.5mm;right:7.5mm;bottom:4.5mm;display:flex;align-items:center;gap:4mm">
<span class="lbl" style="font-size:6pt">Escala 1/50</span>{escala50()}</div></div>
<div class="abs" style="left:104mm;top:250mm;display:flex;gap:7mm">{ref('ref_varanda.jpg', 'Varanda Gourmet', '', 88)}{ref('ref_lavanderia.jpg', 'Lavanderia', 'Divergência: a imagem mostra revestimento só entre bancada e armário; especificada a parede inteira, conforme informado.', 88)}</div>
{PR.carimbo(5, 'Elevações — Cozinha, Lavanderia e Varanda', '1/50', 332.0, 78.1)}
</section>"""


def planilha(Q):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = Workbook()
    ws = wb.active
    ws.title = 'Revestimentos de parede'
    cols = ['Código', 'Produto', 'Elevação', 'Ambiente', 'Pano', 'Largura (m)', 'Altura (m)', 'Área bruta (m²)', 'Aberturas',
            'Desconto (m²)', 'Acréscimo nicho (m²)', 'Área líquida (m²)', 'Observação', 'Controle']
    ws.append(cols)
    for i, w in enumerate([8, 40, 9, 32, 44, 11, 10, 14, 26, 13, 15, 15, 60, 26], 1):
        ws.column_dimensions[chr(64 + i)].width = w
        c = ws.cell(row=1, column=i); c.fill = PatternFill('solid', fgColor='3F422F'); c.font = Font(bold=True, color='F5E7C4')
    subs = []
    for cod, pr in PROD.items():
        ws.append([cod, pr['nome'].upper()])
        for c in ws[ws.max_row]: c.fill = PatternFill('solid', fgColor='ECE4D4'); c.font = Font(bold=True, color='7A3423')
        r0 = ws.max_row + 1
        for p in [x for x in PANOS if x['cod'] == cod]:
            r = ws.max_row + 1
            alt = (p['faixa'][3] - p['faixa'][2]) if p['faixa'] else p['alt']
            ws.append([cod, pr['nome'], p['elev'], p['amb'], p['parede'], p['larg'], alt, f'=F{r}*G{r}',
                       ' + '.join(f"{n} {w}x{h}" for n, w, h, _ in p['aberturas']), p['desc'],
                       (f'=2*{NICHO_P}*F{r}+2*{NICHO_P}*{NICHO_H}' if p['nicho'] else 0), f'=H{r}-J{r}+K{r}', p['obs'], ' + '.join(p['controle'])])
        ws.append(['', f'Subtotal {cod}', '', '', '', '', '', '', '', '', '', f'=SUM(L{r0}:L{ws.max_row})'])
        subs.append(ws.max_row)
        for c in ws[ws.max_row]: c.font = Font(bold=True)
    ws.append(['', 'TOTAL GERAL', '', '', '', '', '', '', '', '', '', '=' + '+'.join(f'L{x}' for x in subs)])
    for c in ws[ws.max_row]: c.font = Font(bold=True)
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(vertical='top', wrap_text=True)
        for k in (5, 6, 7, 9, 10, 11): row[k].number_format = '0.000'
    ws2 = wb.create_sheet('Produtos')
    ws2.append(['Código', 'Produto', 'Fabricante', 'Formato', 'Espessura', 'Acabamento', 'Rejunte'])
    for k, v in PROD.items():
        ws2.append([k, v['nome'], v['fab'], v['formato'], v['esp'], v['acab'], v['rejunte']])
    wb.save(os.path.join(Q, 'QUANTITATIVOS REVESTIMENTOS DE PAREDE - R00.xlsx'))


def main():
    doc = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{esc(PR.CADERNO)} — Rev. 00</title>
<style>{PR.fonts_css()}{PR.CSS}</style></head><body>
{folha1()}{folha2()}{folha3()}{folha4()}{folha5()}
</body></html>"""
    open(os.path.join(AQUI, 'caderno02.html'), 'w').write(doc)
    # quantitativos
    Q = os.path.join(AQUI, '..', 'quantitativos')
    with open(os.path.join(Q, 'quadro_revestimentos_parede.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['codigo', 'produto', 'fabricante', 'elevacao', 'ambiente', 'pano', 'x_ini', 'y_ini', 'x_fim', 'y_fim', 'largura_m', 'altura_m',
                    'area_bruta_m2', 'aberturas', 'desconto_m2', 'acrescimo_nicho_m2', 'area_liquida_m2', 'observacao', 'controle'])
        for p in PANOS:
            pr = PROD[p['cod']]
            alt = (p['faixa'][3] - p['faixa'][2]) if p['faixa'] else p['alt']
            w.writerow([p['cod'], pr['nome'], pr['fab'], p['elev'], p['amb'], p['parede'], *[br(v, 3) for v in (*p['a'], *p['b'])],
                        br(p['larg'], 3), br(alt), br(p['bruta'], 4), ' + '.join(f"{n} {br(a)}x{br(b)}" for n, a, b, _ in p['aberturas']),
                        br(p['desc'], 4), br(p['nicho_m2'], 4), br(p['liq'], 4), p['obs'], ' + '.join(p['controle'])])
        for c, v in TOT.items():
            w.writerow([c, 'SUBTOTAL ' + PROD[c]['nome']] + [''] * 14 + [br(v, 4)])
        w.writerow(['', 'TOTAL GERAL'] + [''] * 14 + [br(sum(TOT.values()), 4)])
    planilha(Q)
    json.dump(dict(produtos=PROD, panos=PANOS, totais=TOT), open(os.path.join(AQUI, 'dados_paredes.json'), 'w'), ensure_ascii=False, indent=1)
    for c, v in TOT.items():
        print(c, round(v, 3))
    print('total', round(sum(TOT.values()), 3))


if __name__ == '__main__':
    main()
