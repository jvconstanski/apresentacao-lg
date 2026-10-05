# Catálogo de layouts

16 layouts, os mesmos no HTML, no PDF e no PPTX. O nome é o valor do campo `layout` no `deck.json`. Campos completos em `schema.md`; limites de palavras em `copy-lg.md`.

Escolha pelo que o conteúdo é, não pela variedade. Deck típico de 12 a 18 slides: capa, uma afirmação de contexto, uma ou duas aberturas de seção, slides de evidência (KPIs, gráficos, tabela), proposta (comparativo, rede, pilares, processo, linha do tempo) e encerramento.

## Mapa rápido

| O conteúdo é... | Layout |
|---|---|
| Abertura do deck | `capa` |
| Mudança de parte da narrativa | `secao` |
| Uma frase que o público precisa guardar | `afirmacao` |
| 2 a 4 números que resumem a situação | `kpis` |
| Comparar valores entre categorias | `grafico-barras` |
| Evolução no tempo | `grafico-linha` |
| Partes de um todo (até 6) | `grafico-donut` |
| Valores exatos que serão lidos e conferidos | `tabela` |
| Hoje e proposta, cenário A e B | `comparativo` |
| Datas ou prazos de um cronograma | `linha-do-tempo` |
| Rede de linhas, rota, integração, terminais | `rede` |
| Frase real de alguém, com fonte | `citacao` |
| 3 ou 4 critérios ou princípios sem ordem | `pilares` |
| Etapas em ordem | `processo` |
| Lista de entregas, requisitos ou pontos | `topicos` |
| Fechamento com próximo passo e contato | `encerramento` |

## Os 16 layouts

### 1. `capa`
- **Quando:** primeiro slide.
- **Campos:** `titulo` (obrigatório), `rotulo` (ocasião ou destinatário), `subtitulo`, `data` (usa `meta.data` se faltar), `local`.
- **Visual:** fundo claro, logo no alto à esquerda, título display embaixo à esquerda, malha de quadras à direita com duas rotas e a chegada em verde.

### 2. `secao`
- **Quando:** abre cada parte do arco (contexto, evidência, proposta). Use 1 a 3 por deck.
- **Campos:** `titulo` (obrigatório), `descricao`, `numero` (só quando o roteiro tem partes numeradas de verdade).
- **Visual:** fundo grafite com malha escura, rota azul atravessando o alto, título display-2 embaixo.

### 3. `afirmacao`
- **Quando:** a tese do deck, a tensão do problema ou a conclusão de um bloco de dados.
- **Campos:** `titulo` (obrigatório, a frase), `rotulo`, `texto` (uma ou duas frases de apoio), `fonte`, `fundo` (`claro`, `apoio` ou `escuro`).
- **Visual:** só tipografia, centrada na vertical, alinhada à esquerda.

### 4. `kpis`
- **Quando:** 2 a 4 números que o público deve lembrar.
- **Campos:** `titulo`, `itens[]` com `valor` (texto, já formatado: "−18%", "R$ 6,10"), `rotulo`, `legenda`, `destaque` (true no número principal, sai em azul); `fonte`.
- **Visual:** números grandes em Archivo, separados por linha fina, sem card.

### 5. `grafico-barras`
- **Quando:** comparar categorias (linhas, bairros, anos, itens de custo).
- **Campos:** `titulo`, `subtitulo` (unidade e recorte), `categorias[]`, `series[]` com `nome` e `valores[]`, `orientacao` (`vertical` ou `horizontal`; use horizontal com rótulo longo), `destaque` (índice ou lista de índices, base 0), `prefixo`, `sufixo`, `casas`, `fonte`.
- **Visual:** SVG no HTML e gráfico nativo no PPTX. Destaque em azul, demais em cinza claro.

### 6. `grafico-linha`
- **Quando:** série no tempo (demanda mensal, tarifa por ano, custo por trimestre).
- **Campos:** como em barras, mais `y_min` (início do eixo) e `destacar_ultimo` (padrão true: último ponto vira a chegada verde).
- **Visual:** linha azul de 6 px, paradas quadradas em cada ponto, rótulo de valor nos pontos (todos até 8 pontos; primeiro e último acima disso).

### 7. `grafico-donut`
- **Quando:** composição de um todo: custo por item, viagens por motivo, frota por idade.
- **Campos:** `titulo`, `itens[]` com `rotulo`, `valor`, `destaque`; `centro` com `valor` e `rotulo`; `percentual` (padrão true: legenda em %); `fonte`.
- **Visual:** rosca à esquerda, legenda em linhas à direita.

### 8. `tabela`
- **Quando:** valores exatos que o público vai conferir (por linha, por lote, por cenário).
- **Campos:** `titulo`, `colunas[]`, `linhas[][]` (texto ou número), `destaque_linha` (índice base 0), `fonte`.
- **Visual:** card branco, cabeçalho em rótulo caixa alta, números alinhados à direita e tabulares, linha destacada em negrito com barra azul.

### 9. `comparativo`
- **Quando:** antes e depois, hoje e proposta, cenário A e cenário B.
- **Campos:** `titulo`, `esquerda` e `direita`, cada um com `rotulo`, `titulo`, `itens[]` (até 5).
- **Visual:** painel de apoio à esquerda, painel branco com barra azul à direita, rota em 45° ligando os dois.

### 10. `linha-do-tempo`
- **Quando:** cronograma, marcos de contrato, histórico.
- **Campos:** `titulo`, `marcos[]` com `data`, `titulo`, `texto`; `atual` (índice do marco em andamento, sai em azul); `chegada` (padrão true: último marco em verde); `fonte`.
- **Visual:** fundo de apoio, linha grafite de borda a borda com paradas quadradas.

### 11. `rede`
- **Quando:** desenho de rede, troncal e alimentadora, integração em terminal, rota proposta.
- **Campos:** `titulo`, `texto`, `nos[]` com `id`, `x` (0 a 12), `y` (0 a 8), `tipo` (`parada`, `terminal`, `chegada`), `rotulo`, `rotulo_pos` (`direita`, `esquerda`, `acima`, `abaixo`); `linhas[]` com `nome`, `cor` (`azul`, `grafite`, `cinza`, `azul-claro`) e `nos[]` em ordem; `escala` (texto da barra de escala).
- **Visual:** texto e legenda à esquerda; diagrama sobre a malha de quadras à direita, sangrando a borda. O traçado entre dois nós sai a 45° e depois segue reto, então só existem ângulos de 0°, 45° e 90°.
- **Dica:** nós na borda direita (`x` 11 e 12) pedem `rotulo_pos` `esquerda` ou `acima`. Diagrama é ilustrativo: diga isso no `texto`.

### 12. `citacao`
- **Quando:** frase real de cliente, gestor, lei ou documento, com origem conhecida.
- **Campos:** `texto`, `autor` e `fonte` (os três obrigatórios), `cargo`.
- **Visual:** fundo grafite, citação em Archivo grande, autor em rótulo.
- **Regra:** nunca inventar citação. Sem fonte verificável, use `afirmacao`.

### 13. `pilares`
- **Quando:** 3 ou 4 critérios, princípios ou frentes que não têm ordem.
- **Campos:** `titulo`, `texto`, `itens[]` com `titulo` e `texto`.
- **Visual:** título à esquerda; itens empilhados à direita, separados por linha fina, marcados por quadrado azul (sem numeração).

### 14. `processo`
- **Quando:** etapas em sequência, onde a ordem importa.
- **Campos:** `titulo`, `etapas[]` com `titulo` e `texto` (3 a 5).
- **Visual:** fundo de apoio, linha em escada que sobe a 45° a cada etapa, número da etapa em azul, última etapa com chegada verde.

### 15. `topicos`
- **Quando:** lista de entregas, requisitos, premissas ou pontos de atenção.
- **Campos:** `titulo`, `itens[]` (texto), `nota` com `rotulo` e `texto` (bloco lateral opcional).
- **Visual:** lista com marcador quadrado azul; nota em card branco com barra azul.

### 16. `encerramento`
- **Quando:** último slide.
- **Campos:** `titulo` (o próximo passo como afirmação), `texto`, `proximo_passo` (vira o botão verde), `contato[]` (até 3 linhas), `rotulo`, `fundo` (`azul` ou `escuro`).
- **Visual:** fundo azul com rotas brancas em baixa opacidade, logo branco, título display-2.

## Campos comuns

Todo slide aceita `rotulo` (linha em caixa alta acima do título), `fonte` (linha "Fonte:" no pé), `notas` (notas do apresentador: tecla N no HTML, painel de notas no PPTX) e `fundo` quando o layout prevê mais de um.
