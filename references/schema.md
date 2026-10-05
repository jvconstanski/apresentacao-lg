# Formato do deck.json

Um arquivo JSON em UTF-8 com dois blocos: `meta` (dados do deck) e `slides` (lista em ordem). Os três geradores leem o mesmo arquivo. O `build.py` valida antes de gerar e lista cada erro com o número do slide.

## meta

| Campo | Tipo | Uso |
|---|---|---|
| `titulo` | texto | Título do documento (aba do navegador, propriedades do PPTX) |
| `tema` | texto | Nome da pasta e dos arquivos (vira kebab-case). Sem ele, usa `titulo` |
| `data` | texto | Data mostrada na capa ("Outubro de 2026") |
| `data_arquivo` | `AAAA-MM-DD` | Data do nome da pasta de saída. Sem ela, usa a data de hoje |
| `rodape` | texto | Texto do rodapé de cada slide. Padrão: "LG Mobilidade Urbana" |
| `publico` | texto | Para quem é (registro da suposição, não aparece no slide) |
| `objetivo` | texto | O que a apresentação precisa conseguir (registro, não aparece) |

## slides

Cada item tem `layout` (um dos 16 de `layouts.md`) e os campos do layout. Campos que vários layouts aceitam:

| Campo | Uso |
|---|---|
| `rotulo` | Linha em caixa alta acima do título (não aparece em `secao` nem em `citacao`) |
| `fonte` | Linha "Fonte: ..." no pé do slide. O prefixo entra sozinho |
| `notas` | Notas do apresentador (tecla N no HTML, painel de notas no PPTX) |
| `fundo` | `claro`, `apoio`, `escuro` ou `azul`, quando o layout permite (ver abaixo) |

Fundo padrão e alternativas: capa `claro`; secao `escuro`; afirmacao `claro` (ou `apoio`, `escuro`); kpis, tabela, pilares, topicos `claro` (ou `apoio`); graficos, comparativo, rede `claro`; linha-do-tempo e processo `apoio` (ou `claro`); citacao `escuro` (ou `claro`); encerramento `azul` (ou `escuro`).

## Marcação dentro do texto

| Escreva | Sai como |
|---|---|
| `**trecho**` | Destaque em azul (no fundo azul, sublinhado verde) |
| `[DADO: validar]` | Caixa tracejada cinza: dado que o usuário precisa confirmar |
| `[DADO: exemplo]` | Mesma caixa: dado fictício de demonstração |
| `` `campo_tarifa` `` | IBM Plex Mono: código, fórmula ou nome de campo citado |

Nada de outro markdown: asterisco simples, sublinhado e cerquilha saem como texto.

## Números

- Em `kpis`, `valor` é texto já formatado em pt-BR: `"−18%"`, `"R$ 6,10"`, `"174 mil"`. Use o sinal de menos `−`, não o hífen.
- Em gráficos, `valores` são números JSON (`24.1`, não `"24,1"`). O gerador formata em pt-BR com `prefixo`, `sufixo` e `casas`: `{"prefixo": "R$ ", "casas": 2}` mostra `R$ 4,20`; `{"sufixo": " mil", "casas": 1}` mostra `24,1 mil`; `{"sufixo": "%"}` mostra `46%`.
- Em `tabela`, células podem ser texto (`"24.100"`, `"R$ 4,20"`) ou número. Coluna com maioria de números alinha à direita.
- Valor ausente não entra no gráfico. Tire a categoria e diga na `fonte`: `"... [DADO: validar · março sem leitura]"`.

## Campos por layout

| Layout | Obrigatórios | Opcionais |
|---|---|---|
| `capa` | `titulo` | `rotulo`, `subtitulo`, `data`, `local` |
| `secao` | `titulo` | `descricao`, `numero` |
| `afirmacao` | `titulo` | `rotulo`, `texto`, `fonte`, `fundo` |
| `kpis` | `titulo`, `itens[]` (`valor`, `rotulo`, `legenda`, `destaque`) | `rotulo`, `fonte` |
| `grafico-barras` | `titulo`, `categorias[]`, `series[]` (`nome`, `valores[]`) | `subtitulo`, `orientacao`, `destaque`, `prefixo`, `sufixo`, `casas`, `fonte` |
| `grafico-linha` | `titulo`, `categorias[]`, `series[]` | `subtitulo`, `y_min`, `destacar_ultimo`, `prefixo`, `sufixo`, `casas`, `fonte` |
| `grafico-donut` | `titulo`, `itens[]` (`rotulo`, `valor`, `destaque`) | `centro` (`valor`, `rotulo`), `percentual`, `casas`, `fonte` |
| `tabela` | `titulo`, `colunas[]`, `linhas[][]` | `destaque_linha`, `fonte` |
| `comparativo` | `titulo`, `esquerda`, `direita` (`rotulo`, `titulo`, `itens[]`) | `fonte` |
| `linha-do-tempo` | `titulo`, `marcos[]` (`data`, `titulo`, `texto`) | `atual`, `chegada`, `fonte` |
| `rede` | `titulo`, `nos[]` (`id`, `x`, `y`, `tipo`, `rotulo`, `rotulo_pos`), `linhas[]` (`nome`, `cor`, `nos[]`) | `texto`, `escala`, `fonte` |
| `citacao` | `texto`, `autor`, `fonte` | `cargo` |
| `pilares` | `titulo`, `itens[]` (`titulo`, `texto`) | `rotulo`, `texto` |
| `processo` | `titulo`, `etapas[]` (`titulo`, `texto`) | `rotulo`, `fonte` |
| `topicos` | `titulo`, `itens[]` | `nota` (`rotulo`, `texto`), `fonte` |
| `encerramento` | `titulo` | `rotulo`, `texto`, `proximo_passo`, `contato[]`, `fundo` |

## Exemplo mínimo

```json
{
  "meta": {
    "titulo": "Revisão tarifária 2027",
    "tema": "revisao-tarifaria-2027",
    "data": "Outubro de 2026",
    "rodape": "Revisão tarifária 2027",
    "publico": "Equipe técnica do órgão gestor",
    "objetivo": "Aprovar as premissas do cálculo"
  },
  "slides": [
    {"layout": "capa", "rotulo": "Estudo técnico", "titulo": "Premissas da revisão tarifária de 2027",
     "subtitulo": "Custos, demanda e cenários para a decisão do órgão gestor"},
    {"layout": "kpis", "titulo": "O custo por passageiro subiu mais do que a tarifa",
     "itens": [
       {"valor": "[DADO: validar]", "rotulo": "custo por passageiro", "legenda": "Variação 2024 a 2026", "destaque": true},
       {"valor": "[DADO: validar]", "rotulo": "tarifa pública", "legenda": "Mesmo período"}
     ],
     "fonte": "Planilha de custos do contrato [DADO: validar]"},
    {"layout": "grafico-barras", "titulo": "Pessoal e combustível pesam mais no custo por quilômetro",
     "categorias": ["Pessoal", "Combustível", "Manutenção", "Capital", "Outros"],
     "series": [{"nome": "R$ por km", "valores": [4.1, 2.3, 1.1, 1.0, 0.5]}],
     "destaque": [0, 1], "prefixo": "R$ ", "casas": 2,
     "fonte": "Planilha de custos [DADO: exemplo]"},
    {"layout": "encerramento", "titulo": "Próximo passo: validar as premissas com a equipe do contrato",
     "proximo_passo": "Agendar a reunião técnica", "contato": ["Rua Bom Jesus, 212, Juvevê, Curitiba/PR"]}
  ]
}
```

Exemplo completo, com os 16 layouts: `examples/exemplo-deck.json`.
