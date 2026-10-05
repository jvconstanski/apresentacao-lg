---
name: apresentacao-lg
description: "Slides na identidade visual da LG (HTML, PDF e PPTX). Use em /apresentacao-lg, \"apresentação da LG\", \"slides da LG\", \"deck LG\", \"transforma isso em apresentação\", \"monta slides desses dados\"."
version: 1.0.0
argument-hint: "<tema, texto, planilha ou arquivo> [público] [objetivo]"
---

# Apresentação LG Mobilidade Urbana

Transforma um tema, um texto bruto, uma planilha ou um conjunto de dados em apresentação de slides com copy e design da LG Mobilidade Urbana. Um único arquivo de conteúdo (`deck.json`) gera os três formatos: HTML interativo, PDF 16:9 e PPTX editável.

Os caminhos citados aqui são relativos à pasta desta skill (a pasta onde está este `SKILL.md`), chamada abaixo de `<pasta-da-skill>`.

## Quando usar

- Pedido de apresentação, slides ou deck da LG, para prefeitura, órgão gestor, consórcio, operadora ou uso interno.
- Material bruto que precisa virar narrativa em slides: relatório, planilha, resultado de estudo, proposta técnica, cronograma.

## Quando não usar

- Peça de outra marca: esta skill só conhece a identidade da LG.
- Documento corrido (relatório, parecer, e-mail). Slide não substitui relatório técnico.
- Copy aprovada que só precisa de diagramação: aí o trabalho é paginar o texto como veio, sem reescrever (veja `references/copy-lg.md`, seção "Copy pronta").

## Fluxo

1. **Entender o pedido.** Leia tudo que o usuário trouxe (texto, planilha, PDF convertido, dados colados). Fixe tema, público e objetivo da apresentação. Faça no máximo uma pergunta, e só se o objetivo ou o público estiver ausente e mudar o deck. Fora isso, assuma, registre a suposição em `meta.publico` e `meta.objetivo` e diga a suposição em uma linha na entrega.
2. **Planejar a narrativa.** Arco: contexto, problema ou tensão, evidência e dados, solução ou proposta, próximo passo. Uma ideia por slide. Todo título de conteúdo é uma afirmação que diz a conclusão, não o assunto ("A demanda caiu mais rápido do que a oferta", nunca "Demanda"). Regras em `references/copy-lg.md`.
3. **Escolher o layout de cada slide** no catálogo de `references/layouts.md` (16 layouts). Dado comparável vira gráfico; lista de valores exatos vira tabela; sequência vira processo ou linha do tempo; rede, rota ou integração vira diagrama de rede.
4. **Escrever a copy no tom da LG** (`references/copy-lg.md`): nome do serviço no lugar do adjetivo, frases curtas, limites de palavras por layout. Número, nome, depoimento e citação só entram se vieram do material do usuário. Dado que falta vira `[DADO: validar]`; dado fictício de exemplo vira `[DADO: exemplo]`.
5. **Gravar o `deck.json`** no formato de `references/schema.md`, com a ferramenta Write, em `./apresentacoes/{tema-kebab}.deck.json` no diretório de trabalho.
6. **Rodar os geradores:**
   ```bash
   python "<pasta-da-skill>/scripts/build.py" "./apresentacoes/{tema-kebab}.deck.json" --previas
   ```
   Saída em `./apresentacoes/{AAAA-MM-DD}-{tema-kebab}/` (pasta base muda com `--saida`).
7. **Conferir a saída.** Leia o código de saída e o resumo do `build.py`. Depois abra com Read 3 ou 4 prévias de `previas/` (capa, o slide mais denso, um gráfico e o encerramento) e confira: nenhum texto cortado, vazando do slide ou sobreposto; contraste legível; `[DADO: ...]` visível onde falta dado. Achou problema: corrija o `deck.json` (encurte a copy, divida o slide ou troque o layout) e rode o passo 6 de novo.

## Códigos de saída do build

| Código | Significa | O que fazer |
|---|---|---|
| 0 | HTML, PDF e PPTX gerados e conferidos | Entregar |
| 2 | `deck.json` inválido | Corrigir os campos listados em `ERRO:` |
| 3 | Texto estourando o slide | Encurtar a copy ou dividir o slide citado em `ESTOURO:` |
| 4 | Conferência falhou (arquivo vazio, slides ou páginas em número errado) | Ler `CONFERÊNCIA:` e rodar de novo |
| 5 | Um gerador falhou | Ler `FALHA:`; sem Playwright nem Chrome/Edge, o PDF não sai (ver `README.md`) |

`AVISO:` não bloqueia, mas leia: título com cara de assunto, travessão, clichê, palavra demais e fontes da marca ausentes na máquina aparecem ali.

## Regras que não se negociam

- Cor, fonte e espaçamento só dos tokens de `references/brand-lg.md`. Os geradores já aplicam; não escreva cor solta no `deck.json`.
- Verde só no ponto de chegada e no botão do próximo passo. Gradiente azul para verde só no traçado de conversão, nunca como fundo.
- Nunca inventar número, nome, depoimento, citação, preço ou data. Citação exige o campo `fonte`.
- Sem travessão na copy (use vírgula, ponto, dois-pontos ou parênteses), sem emoji, sem clichê.
- Reflexos visuais a evitar, salvo pedido explícito: fundo creme ou off-white quente, palavra de destaque em itálico no título, rótulos numerados 01/02/03 em itens que não são sequência, rótulo em fonte monoespaçada, botão pílula. O destaque da LG é cor azul em peso alto, o canto do botão é de 4 px e a numeração só aparece em etapa de processo.

## Saída

```
apresentacoes/2026-10-05-revisao-tarifaria/
├── revisao-tarifaria.html     # um arquivo só, offline, com fontes e logos embutidos
├── revisao-tarifaria.pdf      # 16:9, um slide por página
├── revisao-tarifaria.pptx     # editável: caixas de texto, gráficos e tabela nativos
├── deck.json                  # cópia do conteúdo que gerou os três
├── previas/slide-NN.png       # com --previas
└── relatorio-build.json       # resultado da conferência
```

Na entrega, informe os três caminhos absolutos, o número de slides, as suposições feitas e quantos `[DADO: ...]` ficaram pendentes.

## Exemplo

**Pedido:** "Monta slides desses dados de bilhetagem para a secretaria aprovar o estudo da nova rede." (planilha anexa)

**Resultado:** deck de 12 a 18 slides com capa, afirmação de contexto, KPIs da demanda, gráfico de linha da série histórica, tabela por linha, comparativo hoje e proposta, diagrama da rede, processo de trabalho, cronograma e encerramento com o próximo passo. Exemplo completo, com os 16 layouts: `examples/exemplo-deck.json`.

Teste rápido da instalação:

```bash
python "<pasta-da-skill>/scripts/build.py" "<pasta-da-skill>/examples/exemplo-deck.json" --saida ./teste-lg
```

## Pronto quando

- `build.py` terminou com código 0 (ou 3 com estouro justificado e avisado).
- As prévias lidas não mostram texto cortado, vazado ou sobreposto.
- Todo número do deck veio do material do usuário ou está marcado com `[DADO: ...]`.
- A entrega lista os caminhos absolutos dos três arquivos e as pendências.

## Referências

- `references/brand-lg.md`: tokens, logo por fundo, grafismo, o que é proibido.
- `references/copy-lg.md`: tom de voz, título-afirmação, limites de palavras, regra do dado.
- `references/layouts.md`: catálogo dos 16 layouts e quando usar cada um.
- `references/schema.md`: formato do `deck.json`, campo a campo.
- `README.md`: instalação, dependências e solução de problemas.
