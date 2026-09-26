# Caderno de Detalhamento de Revestimento de Piso 01/02 — Rev. 00
Residência Ivan e Carol · Nova Odessa, SP · 26/09/2026

## Entregáveis
| Arquivo | Conteúdo |
|---|---|
| `CADERNO DE DETALHAMENTO DE REVESTIMENTO DE PISO 01-02 - R00.pdf` | 5 folhas A3 (297 × 420 mm). Imprimir sem ajuste de escala. |
| `quantitativos/QUANTITATIVOS PISOS E RODAPES - R00.xlsx` | Pisos, memória de rodapés (trecho a trecho, com fórmulas), vãos e transições. |
| `quantitativos/quadro_pisos.csv`, `quantitativos/memoria_rodapes.csv` | Os mesmos dados em CSV (`;`, UTF-8). |
| `fonte/` | Arquivos-fonte editáveis que geram o PDF. |
| `fonte/previa/pdf_XX.png` | Renderização de cada folha do PDF (110 dpi). |

Folhas:
- 01/05 — planta de especificação de pisos (1/125)
- 02/05 — quadro de pisos
- 03/05 — planta de rodapés (1/100)
- 04/05 — memória de cálculo dos rodapés
- 05/05 — transições e pendências

## Como regenerar
```bash
cd caderno/fonte
npm i @mlightcad/libredwg-web playwright         # uma vez
node read.mjs  # converte ../../referencias/PROJETO IVAN E ANA - R01.dwg em db.json
python3 dados.py        # geometria.json, dados.json e CSVs  (requer shapely)
python3 planilha.py     # XLSX (requer openpyxl)
python3 pranchas.py     # caderno.html
node imprimir.mjs       # PDF A3 + prévias (Chromium)
```
- **Dados:** áreas adotadas, fontes, controle e trechos de rodapé são editados em `fonte/dados.py`. Cada vão é validado automaticamente: o script para se um vão não estiver sobre um trecho de parede.
- **Desenho:** estilo e posição dos rótulos são editados em `fonte/pranchas.py`.
- **Coordenadas:** coordenadas locais = coordenadas do espaço do modelo do DWG − (3895, 760), em metros ("PLANTA DE PISO").
