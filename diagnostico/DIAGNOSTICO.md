# Diagnóstico — Caderno de pisos, rodapés e revestimentos
Residência Ivan e Carol · Nova Odessa, SP · diagnóstico de 26/09/2026 (antes da produção)

Nenhuma prancha foi gerada. Este documento registra o que foi lido nos arquivos, o que foi medido e o que falta decidir.

## 1. Arquivos abertos e dados extraídos

| Arquivo | Leitura | Dados extraídos |
|---|---|---|
| `PROJETO IVAN E ANA - R01.dwg` | **Lido.** Formato AC1032 (AutoCAD 2018+), lido pela LibreDWG (WebAssembly). Retornou o código 64 (aviso não crítico de valor fora de limite em algum objeto). 4.829 entidades, 704 blocos, 89 camadas. | Unidade `INSUNITS=6` (**metros**). Espaço do modelo com 6 plantas lado a lado e dois layouts (`Layout1`, `Layout2`) com viewports a 1:100. Validação: a área do lote calculada pela geometria (463,87 m²) é igual à do quadro de áreas do próprio DWG. |
| `CADERNO … PORTAS E JANELAS.pdf` | **Lido.** 4 folhas A3 retrato (297 × 420 mm), Rev. 01, 30/08/2026. | Identidade visual, carimbo, quadro de esquadrias (P01–P11, J01–J09) e notas. **A planta é uma imagem raster** (2000 × 2600 px, com mobiliário e renderização) e **não serve como fonte de medida**. |
| Planta cotada complementar | Não fornecida | O próprio DWG tem 36 cotas na planta de piso e 436 no arquivo inteiro. |
| Lista de materiais e áreas | **Não fornecida** | O DWG não tem nenhum texto de material (não aparecem "porcelanato", "Santorini", "rodapé" nem "pedra"). |

### Desenhos encontrados no espaço do modelo (coordenada X aproximada)
1. x≈3643–3727: folha A1 da Prefeitura (planta baixa, implantação, cortes, fachadas, quadro de áreas), do eng. Hamilton Vianna.
2. x≈3750: cópia da planta da Prefeitura.
3. x≈3790: planta de ar-condicionado.
4. x≈3825 e x≈3860: plantas de forro de gesso (com PD por ambiente).
5. **x≈3895–3935: "PLANTA DE PISO"**. É a planta que corresponde ao caderno: as posições e larguras de P01, P03, P05 (3,00 + 3,00), P07, J01 e J02 coincidem. Na planta da Prefeitura, P5 tem 2,85 m e P6 tem 2,70 m. Esta é a base proposta para o novo caderno.

Na planta de piso, os ambientes são polilinhas fechadas na camada `001`, na face interna das paredes, e cada uma tem cota própria. Os pisos estão hachurados na camada `001` com os padrões NET (interno e externo), AR-HBONE (corredor lateral) e GRASS (rampa e frente do lote). Os padrões **não identificam produto**.

## 2. Ambientes, áreas e origem
Ver `ambientes_dwg.csv` e a imagem `conferencia_planta_piso_dwg.png`.

| ID | DWG | Nome provável no caderno | Área geométrica | Rótulo DWG | Perímetro bruto |
|---|---|---|---|---|---|
| A01 | Banho suíte master | Banheiro Casal | 6,825 | 6,83 | 10,90 |
| A02 | Closet | Closet Casal | 12,250 | 12,25 | 14,00 |
| A03 | Suíte master | Quarto Casal | 16,275 | **15,75** | 16,30 |
| A04 | Suíte 2 | Quarto 0? | 12,300 | 12,30 | 14,20 |
| A05 | Banho suíte 2 | WC 0? | 4,200 | 4,20 | 8,60 |
| A06 | Banho suíte 1 | WC 0? | 4,200 | 4,20 | 8,60 |
| A07 | Suíte 1 | Quarto 0? | 12,300 | 12,30 | 14,20 |
| A08 | Home office | Escritório | 7,260 | 7,26 | 11,00 |
| A09 | Banho 4 | Banheiro Externo | 4,620 | 4,62 | 9,40 |
| A10 | Circulação | Corredor | 10,080 | **12,85** | 19,20 |
| A10n | Nicho 0,70 × 3,15 | ? | 2,205 | — | — |
| A11 | Cozinha | Cozinha | 17,850 | 17,85 | 16,90 |
| A12 | A.S. | Lavanderia | 5,500 | 5,50 | 9,50 |
| A13 | Despensa | Depósito | 2,400 | 2,40 | 6,40 |
| A14 | Estar/Jantar | Sala TV + Sala Jantar | 41,010 | 41 | 26,50 |
| E01 | Garagem | Garagem | 37,650 | 37,65 / **36,97** | 25,00 (frente aberta) |
| E02 | Varanda cob. leve | Gourmet? | 18,225 | 18,22 | 17,10 |

## 3. Deck, rampa e calçada (para conferência, ainda não incorporados)
- **Área externa da piscina ("deck"?):** o contorno da hachura NET externa (#266280, laço 1) mede 61,372 m². Somando o setor de giro de P03, que a hachura recorta (0,636 m²), a área de piso é **62,008 m²**. A área não inclui a piscina (3,80 × 6,00 = 22,80 m²), as áreas permeáveis (6,30 m² e 17,976 m²) nem as faixas de 1,00 m junto à suíte master (7,40 m²) e junto à varanda (8,281 m²). Essas faixas pertencem à mesma hachura, mas estão em laços separados. **O limite do deck precisa ser confirmado.**
- **Rampa:** vai da linha da garagem (y = 15,036; 7,40 m de largura) até a divisa. Considerando o limite direito em x = 11,591 (alinhamento da garagem), a área é **34,606 m²**. A borda curva é o arco da divisa, com r = 12,142 m e centro comum ao meio-fio (r = 14,642 m). O trecho do arco dentro da rampa mede **5,028 m**, e o arco completo da divisa mede 10,175 m (48,02°). Há uma guia/muro em x = 11,691 (10 cm à direita), então o limite deve ser confirmado. A planta da Prefeitura indica inclinação de 4 % em 5,00 m e piso da garagem em +0,75 (ver divergências).
- **Calçada:** 2,50 m de largura (faixa de acesso 1,25 + faixa livre 1,10 + meio-fio 0,15), igual às cotas da planta da Prefeitura. A frente do lote na divisa mede **40,315 m** (2,86 reto + 10,175 em arco + 27,28 reto), e o meio-fio externo mede 43,318 m. A área é **104,54 m²** se o término na Av. 3 for fechado com uma reta do canto do lote até o fim do meio-fio. **As linhas do DWG terminam abertas nesse ponto**, então o valor só vale depois que você confirmar o término.

## 4. Base para o cálculo do rodapé
- **Com segurança:** perímetros de A01–A09 e A11–A14, tirados de polilinhas fechadas e confirmados pelas cotas. Vãos de porta medidos no DWG por blocos de porta (raio da folha), linhas de soleira (camada `01`) e interrupções das faces de parede (ver `vaos_portas_dwg_x_caderno.csv`).
- **Ainda sem segurança:**
  - Circulação: o nicho 0,70 × 3,15 m está aberto para ela, e o rótulo (12,85 m²) não bate com a geometria.
  - Divisa entre Cozinha e Estar: 4,20 m sem parede no DWG, e o caderno põe ali P04, de 4,20 m.
  - Divisão entre Sala TV e Sala Jantar: não existe no DWG.
  - Larguras de desconto: **13 das 20 portas têm largura diferente entre o caderno e o DWG**.
- Janelas não serão descontadas. J01 (peitoril 0,50) está sobre parede com rodapé.

## 5. Divergências encontradas
1. **Vãos (caderno × DWG):**
   - P02: 0,90 × 0,80.
   - P06: 0,90 × 0,80 em quartos, WCs e escritório; 0,80 na cozinha; 0,70 no depósito.
   - P08 e P09: 1,00 × 0,90.
   - P10: 2,50 × 2,70.
   - P11: 0,90 × 0,80, com vão total de 1,25.
2. **P04 (4,20):** o caderno descreve como porta de correr "voltada para área externa" (nota 3), mas na planta ela fica no limite Cozinha/Sala, onde o DWG não tem esquadria nem parede.
3. **Áreas:**
   - Suíte master: rótulo 15,75 × geometria 16,275.
   - Circulação: rótulo 12,85 × geometria 10,08 (12,285 com o nicho).
   - Garagem: 37,65 (forro) × 36,97 (Prefeitura).
   - Na Prefeitura: Banho 3 6,30 × 6,83; Banho 4 4,27 × 4,62; Circulação 10,08; Suíte master 28,70 (provavelmente somando o closet); área permeável 6,55 × 6,30 na planta de piso.
4. **Nomes:** o DWG usa Suíte 1/2, Banho suíte 1/2, Banho 4, A.S., Despensa, Home office e Estar/Jantar; o caderno usa Quarto 01/02, WC 01/02, Banheiro Externo, Lavanderia, Depósito, Escritório, Sala TV e Sala Jantar.
5. **Níveis:** só existem na planta da Prefeitura (+0,75 em todos os ambientes, home office +0,20, piscina −1,40, rua 0,00/−0,67). A planta de piso não tem níveis. Rampa de 4 % em 5,00 m (≈0,20 m) não vence 0,00 → +0,75.
6. **Janelas (Prefeitura × caderno):** J01 2,50 × 2,00 × 2,50 × 2,50; J2 1,80 × J03 1,50; banho externo 1,25 × 0,50 × 0,90 × 0,40. Janelas não entram no desconto de rodapé.

## 6. Dúvidas que impedem a execução
Estão na mensagem de chat desta sessão, em lista única.

## 7. Como reproduzir
`ferramentas/read.mjs` converte o DWG em JSON (`npm i @mlightcad/libredwg-web`). `geo.py` expande blocos e achata a geometria, `render.py` renderiza e `gaps.py` detecta os vãos por borda de ambiente. Coordenadas locais da planta de piso = coordenadas do modelo − (3895, 760).
