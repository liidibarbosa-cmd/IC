"""Detalhes ilustrativos (sem escala) da folha 06: rodapé, perfil metálico, soleira baguete e trilho embutido.

Unidades do SVG = mm no papel. Só aparecem cotas informadas pela arquitetura ou pelo fabricante
(rodapé 8 cm, baguete 5 cm, espessura do porcelanato); o resto é indicado como A CONFIRMAR.
"""
INK, RUST, OLIVE2 = '#22251a', '#903f2a', '#4f5439'
P01, P02, MARM, METAL = '#e9d6ae', '#c7c6a9', '#f1ede4', '#9aa0a6'


def defs(k):
    return f"""<defs>
<pattern id="cp{k}" patternUnits="userSpaceOnUse" width="2.2" height="2.2"><rect width="2.2" height="2.2" fill="#ddd5c5"/>
<circle cx="0.6" cy="0.7" r="0.22" fill="#a79d89"/><circle cx="1.7" cy="1.6" r="0.18" fill="#b8ae9a"/></pattern>
<pattern id="ar{k}" patternUnits="userSpaceOnUse" width="1.2" height="1.2"><rect width="1.2" height="1.2" fill="#ece6da"/>
<circle cx="0.6" cy="0.6" r="0.12" fill="#b6ad9c"/></pattern>
<pattern id="pa{k}" patternUnits="userSpaceOnUse" width="2.4" height="2.4" patternTransform="rotate(45)">
<rect width="2.4" height="2.4" fill="#e6dfd0"/><line x1="0" y1="0" x2="0" y2="2.4" stroke="#8f8676" stroke-width="0.25"/></pattern>
<pattern id="mv{k}" patternUnits="userSpaceOnUse" width="14" height="6"><rect width="14" height="6" fill="{MARM}"/>
<path d="M0,4 C3,2.6 6,5 9,3.2 S13,2 14,2.6" fill="none" stroke="#c9c2b4" stroke-width="0.25"/></pattern>
</defs>"""


def lead(x0, y0, x1, y1, txt, anchor='start', dy=0):
    """linha de chamada com ponto + texto em até 2 linhas (\\n)"""
    lines = txt.split('\n')
    tx = x1 + (1.2 if anchor == 'start' else -1.2)
    t = ''.join(f'<tspan x="{tx}" dy="{0 if i == 0 else 3.1}">{l}</tspan>' for i, l in enumerate(lines))
    return (f'<circle cx="{x0}" cy="{y0}" r="0.45" fill="{INK}"/><path d="M{x0},{y0} L{x1},{y1}" stroke="{INK}" stroke-width="0.2" fill="none"/>'
            f'<text x="{tx}" y="{y1 + 0.9 + dy}" font-family="Manrope" font-size="2.35" fill="{INK}" text-anchor="{anchor}">{t}</text>')


def cota_v(x, y0, y1, txt):
    return (f'<path d="M{x},{y0} L{x},{y1} M{x - 1},{y0} L{x + 1},{y0} M{x - 1},{y1} L{x + 1},{y1}" stroke="{RUST}" stroke-width="0.25"/>'
            f'<text x="{x + 1.6}" y="{(y0 + y1) / 2 + 0.9}" font-family="Manrope" font-weight="700" font-size="2.7" fill="{RUST}">{txt}</text>')


def cota_h(y, x0, x1, txt, below=False):
    ty = y + 3.6 if below else y - 1.4
    return (f'<path d="M{x0},{y} L{x1},{y} M{x0},{y - 1} L{x0},{y + 1} M{x1},{y - 1} L{x1},{y + 1}" stroke="{RUST}" stroke-width="0.25"/>'
            f'<text x="{(x0 + x1) / 2}" y="{ty}" font-family="Manrope" font-weight="700" font-size="2.7" fill="{RUST}" text-anchor="middle">{txt}</text>')


def svg(k, body, w=127, h=100):
    return f'<svg width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">{defs(k)}{body}</svg>'


def d1():
    # corte: parede + rodapé embutido 8 cm (face alinhada ao acabamento da parede) + piso
    b = ''
    b += '<rect x="6" y="4" width="22" height="70" fill="url(#pa1)" stroke="#8f8676" stroke-width="0.2"/>'      # alvenaria
    b += '<rect x="28" y="4" width="4" height="31.2" fill="#efe9dd" stroke="#8f8676" stroke-width="0.2"/>'      # reboco
    b += '<rect x="28" y="36" width="0.9" height="24.6" fill="url(#ar1)"/>'                                      # argamassa no rebaixo
    b += f'<rect x="28.9" y="36" width="3.1" height="24.6" fill="{P01}" stroke="{INK}" stroke-width="0.3"/>'   # rodapé embutido
    b += f'<rect x="28" y="35.2" width="4" height="0.8" fill="#b7a58a"/>'                                       # junta superior
    b += '<rect x="28" y="66" width="75" height="12" fill="url(#cp1)" stroke="#8f8676" stroke-width="0.2"/>'   # contrapiso
    b += '<rect x="28" y="64" width="75" height="2" fill="url(#ar1)"/>'                                          # argamassa
    b += f'<rect x="28" y="60.6" width="75" height="3.4" fill="{P01}" stroke="{INK}" stroke-width="0.3"/>'      # porcelanato
    b += f'<path d="M32,4 L32,74" stroke="{RUST}" stroke-width="0.25" stroke-dasharray="1.2 0.8"/>'             # plano da parede
    b += cota_v(38, 36, 60.6, 'h = 8 cm')
    b += lead(30.5, 46, 56, 30, 'Rodapé embutido na parede: face alinhada ao\nacabamento da parede (sem saliência)')
    b += lead(28.5, 50, 20, 84, 'Rebaixo no reboco na altura do rodapé —\nprofundidade = peça + argamassa (A CONFIRMAR)', anchor='start')
    b += lead(30, 35.6, 56, 18, 'Junta superior rodapé × parede: acabamento A CONFIRMAR')
    b += lead(32.2, 60.8, 60, 72, 'Peça recortada do mesmo\nporcelanato do piso (R01 = P01;\nR02 = P02) · rejunte cor Corda')
    b += lead(80, 62.2, 84, 52, 'Porcelanato 90 × 90\nP01 7,0 mm · P02 8,0 mm')
    b += lead(100, 70, 104, 93, 'Argamassa colante / contrapiso', anchor='end')
    b += lead(14, 20, 8, 96, 'Parede', anchor='start')
    b += (f'<text x="33" y="7" font-family="Manrope" font-size="2.2" fill="{RUST}">plano de acabamento da parede</text>')
    return svg(1, b)


def d2():
    # corte: mesmo porcelanato em dois níveis, perfil metálico em L (cantoneira de acabamento)
    b = ''
    # nível superior (esquerda)
    b += '<rect x="4" y="44" width="58" height="16" fill="url(#cp2)" stroke="#8f8676" stroke-width="0.2"/>'
    b += '<rect x="4" y="41" width="58" height="3" fill="url(#ar2)"/>'
    b += f'<rect x="4" y="36" width="58" height="5" fill="{P01}" stroke="{INK}" stroke-width="0.35"/>'
    # nível inferior (direita)
    b += '<rect x="62" y="52" width="61" height="8" fill="url(#cp2)" stroke="#8f8676" stroke-width="0.2"/>'
    b += '<rect x="63.2" y="49" width="59.8" height="3" fill="url(#ar2)"/>'
    b += f'<rect x="63.2" y="44" width="59.8" height="5" fill="{P01}" stroke="{INK}" stroke-width="0.35"/>'
    # perfil em L: aba perfurada sob o piso superior + face vertical aparente
    b += f'<path d="M44,42.7 L62,42.7 L62,36 L63.2,36 L63.2,44 L44,44 Z" fill="{METAL}" stroke="{INK}" stroke-width="0.35"/>'
    for x in (45.5, 49.5, 53.5, 57.5):             # furos de ancoragem da aba
        b += f'<rect x="{x}" y="43.0" width="2.6" height="0.75" fill="#e9e3d7" stroke="{INK}" stroke-width="0.12"/>'
    b += cota_v(76, 36, 44, 'desnível (h)')
    b += lead(62.6, 37, 70, 16, 'Perfil metálico em L (cantoneira)\nface aparente rente ao piso superior\nmaterial, acabamento e altura A CONFIRMAR')
    b += lead(51, 43.4, 51, 70, 'Aba perfurada embutida na argamassa,\nsob o porcelanato do nível superior')
    b += lead(20, 38.5, 20, 24, 'Mesmo porcelanato nos dois lados')
    b += lead(100, 46.5, 112, 82, 'Piso — nível inferior', anchor='end')
    b += lead(26, 52, 26, 82, 'Contrapiso / argamassa colante')
    b += (f'<text x="63.5" y="96" font-family="Manrope" font-size="2.35" fill="{OLIVE2}" text-anchor="middle">'
          'Aplicar somente quando o mesmo material mudar de nível. Níveis não documentados neste caderno.</text>')
    return svg(2, b)


def d3():
    # corte + planta da soleira baguete de mármore Itaúnas
    b = ''
    b += '<rect x="4" y="30" width="120" height="12" fill="url(#cp3)" stroke="#8f8676" stroke-width="0.2"/>'
    b += '<rect x="4" y="28" width="120" height="2" fill="url(#ar3)"/>'
    b += f'<rect x="4" y="24.6" width="52" height="3.4" fill="{P01}" stroke="{INK}" stroke-width="0.3"/>'
    b += f'<rect x="72" y="24.6" width="52" height="3.4" fill="{P02}" stroke="{INK}" stroke-width="0.3"/>'
    b += f'<rect x="56.4" y="24.6" width="15.2" height="5.4" fill="url(#mv3)" stroke="{INK}" stroke-width="0.35"/>'
    b += cota_h(21.4, 56.4, 71.6, '5 cm')
    b += lead(68, 27, 76, 5, 'Soleira mármore Itaúnas, tipo baguete\nprofundidade 5 cm · espessura A CONFIRMAR\ntopo no nível do piso acabado')
    b += lead(20, 26.3, 18, 13, 'Piso do ambiente A (ex.: P01)')
    b += lead(110, 26.3, 118, 48, 'Piso do ambiente B (ex.: P02 ou PP01)', anchor='end')
    b += f'<text x="4" y="55" font-family="Manrope" font-weight="700" font-size="2.6" fill="{RUST}" letter-spacing="0.6">PLANTA</text>'
    # planta
    b += f'<rect x="4" y="60" width="120" height="13" fill="{P01}" opacity="0.8"/>'
    b += f'<rect x="4" y="79" width="120" height="13" fill="{P02}" opacity="0.8"/>'
    b += f'<rect x="4" y="73" width="22" height="6" fill="{INK}"/><rect x="102" y="73" width="22" height="6" fill="{INK}"/>'
    b += f'<rect x="26" y="74.4" width="76" height="3.2" fill="url(#mv3)" stroke="{INK}" stroke-width="0.3"/>'
    b += cota_h(69.5, 26, 102, 'comprimento = largura do vão (DWG)')
    b += cota_v(106.5, 74.4, 77.6, '5 cm')
    return svg(3, b)


def d4():
    # corte: porta de correr com trilho embutido no piso
    b = ''
    b += '<rect x="4" y="60" width="120" height="16" fill="url(#cp4)" stroke="#8f8676" stroke-width="0.2"/>'
    b += '<path d="M4,58 L52,58 L52,66 L66,66 L66,58 L124,58 L124,60 L4,60 Z" fill="url(#ar4)"/>'
    b += '<rect x="52" y="60" width="14" height="6" fill="#ffffff" opacity="0.0"/>'
    # rebaixo
    b += f'<path d="M52,58 L52,66 L66,66 L66,58" fill="#f4efe5" stroke="{INK}" stroke-width="0.3"/>'
    b += f'<rect x="4" y="54.6" width="46" height="3.4" fill="{P01}" stroke="{INK}" stroke-width="0.3"/>'
    b += f'<rect x="68" y="54.6" width="10" height="3.4" fill="url(#mv4)" stroke="{INK}" stroke-width="0.3"/>'
    b += f'<rect x="78" y="54.6" width="46" height="3.4" fill="{P02}" stroke="{INK}" stroke-width="0.3"/>'
    # trilho
    b += f'<path d="M53.5,65 L64.5,65 L64.5,54.6 L62.8,54.6 L62.8,63.4 L55.2,63.4 L55.2,54.6 L53.5,54.6 Z" fill="{METAL}" stroke="{INK}" stroke-width="0.3"/>'
    b += f'<rect x="58.4" y="52" width="1.2" height="11.4" fill="{INK}"/>'
    # folha da porta
    b += f'<rect x="55" y="8" width="8" height="42" fill="#d7e3e3" stroke="{INK}" stroke-width="0.35"/>'
    b += f'<rect x="55" y="46" width="8" height="4" fill="#6b4f3a" stroke="{INK}" stroke-width="0.3"/>'
    b += f'<circle cx="59" cy="51.2" r="1.3" fill="#fff" stroke="{INK}" stroke-width="0.3"/>'
    b += lead(59, 28, 72, 18, 'Folha de correr (alumínio marrom com vidro)')
    b += lead(64, 60, 84, 27, 'Trilho embutido no piso\n(rebaixo/nicho), não sobreposto —\nesquadrias, notas 3 e 10')
    b += lead(58, 65.5, 58, 82, 'Rebaixo no contrapiso: dimensões conforme\nfabricante da esquadria — A CONFIRMAR')
    b += lead(73, 56.3, 100, 44, 'Soleira baguete D3\n(troca de material)')
    b += lead(20, 56.3, 20, 42, 'Topo do trilho no nível do\npiso acabado: conferir\nfolga em obra')
    b += (f'<text x="63.5" y="95" font-family="Manrope" font-size="2.35" fill="{OLIVE2}" text-anchor="middle">'
          '<tspan x="63.5">Aplica-se a P04, P05 e P07 (caderno de esquadrias). P10: tipo de trilho A CONFIRMAR.</tspan>'
          '<tspan x="63.5" dy="3.1">Nas portas externas, compatibilizar o trilho com a soleira baguete.</tspan></text>')
    return svg(4, b)


CARDS = [
    ('D1', 'Rodapé embutido em porcelanato — h = 8 cm', 'Corte ilustrativo · sem escala', d1),
    ('D2', 'Perfil metálico em L — mesmo material com desnível', 'Corte ilustrativo · sem escala', d2),
    ('D3', 'Soleira baguete — mármore Itaúnas', 'Corte e planta ilustrativos · sem escala', d3),
    ('D4', 'Trilho de porta de correr embutido no piso', 'Corte ilustrativo · sem escala', d4),
]
