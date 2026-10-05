# apresentacao-lg

Skill do Claude Code que monta apresentações de slides na identidade visual da LG Mobilidade Urbana. Você entrega um tema, um texto, uma planilha ou um arquivo; a skill planeja a narrativa, escreve a copy no tom da LG e gera três arquivos a partir do mesmo conteúdo:

- **HTML** interativo: um arquivo só, funciona sem internet, com navegação por teclado, clique e toque, tela cheia (tecla F) e notas do apresentador (tecla N).
- **PDF** 16:9, um slide por página, pronto para enviar.
- **PPTX** editável no PowerPoint: caixas de texto reais, gráficos e tabela nativos com as cores da marca.

## Instalação

1. Copie a pasta `apresentacao-lg/` para um destes lugares:
   - `.claude/skills/` do projeto, para usar só naquele projeto;
   - `~/.claude/skills/` (no Windows, `C:\Users\<seu-usuário>\.claude\skills\`), para usar em todos.
2. Instale as dependências (Python 3.10 ou mais novo):
   ```bash
   pip install -r requirements.txt
   python -m playwright install chromium
   ```
   Sem o Chromium do Playwright, o PDF sai pelo Chrome ou pelo Edge instalado no computador, mas sem a conferência automática de texto estourando.
3. Instale as fontes da marca para abrir o PPTX como foi desenhado. Estão em `assets/fonts/ttf/`:
   - Windows: selecione os arquivos `.ttf`, clique com o botão direito e escolha **Instalar**.
   - macOS: abra cada arquivo e clique em **Instalar fonte**.

   O HTML e o PDF já levam as fontes embutidas. Quem só recebe o PPTX também precisa instalar as fontes; sem elas o PowerPoint troca por uma fonte sem serifa do sistema e o texto muda de largura.
4. Teste:
   ```bash
   python scripts/build.py examples/exemplo-deck.json --saida ./teste-lg
   ```
   Deve terminar com `OK: apresentação gerada e conferida.` e criar `teste-lg/{data}-nova-rede-de-onibus-exemplo/` com os três arquivos.

## Como usar

No Claude Code, peça do jeito que falaria com alguém da equipe:

- "Monta uma apresentação da LG sobre a revisão tarifária, para a secretaria de mobilidade."
- "Transforma esse relatório em apresentação."
- "Monta slides desses dados" (com a planilha ou os números colados).
- `/apresentacao-lg proposta de nova rede para o consórcio`

A skill pergunta no máximo uma coisa (público ou objetivo, se faltar). Os arquivos saem em `./apresentacoes/{AAAA-MM-DD}-{tema}/` no diretório de trabalho.

Sem o Claude Code, dá para escrever o `deck.json` à mão (formato em `references/schema.md`) e rodar:

```bash
python scripts/build.py meu-deck.json            # HTML, PDF e PPTX
python scripts/build.py meu-deck.json --previas  # mais um PNG por slide, para conferir
python scripts/build.py meu-deck.json --formatos html,pptx
python scripts/build.py meu-deck.json --saida "D:/apresentacoes"
```

Cada gerador também roda sozinho: `scripts/render_html.py`, `scripts/export_pdf.py` e `scripts/render_pptx.py`.

## Dado que falta

A skill não inventa número, nome nem citação. O que não veio no material aparece no slide como `[DADO: validar]`, numa caixa tracejada, e o build informa quantas pendências ficaram. Troque cada marca pelo dado real no `deck.json` e rode o build de novo.

## Códigos de saída do build

| Código | Significa |
|---|---|
| 0 | Tudo gerado e conferido |
| 2 | `deck.json` com erro (a lista diz qual slide e qual campo) |
| 3 | Texto maior que o slide (encurte a copy ou divida o slide) |
| 4 | Arquivo vazio ou número de slides ou de páginas diferente do esperado |
| 5 | Um gerador falhou (a mensagem diz qual) |

## Solução de problemas

- **"Playwright não instalado" ou "Executable doesn't exist":** rode `python -m playwright install chromium`. Em máquina sem acesso para baixar o Chromium, mantenha o Chrome ou o Edge instalado: o PDF sai por eles.
- **Acento quebrado no terminal do Windows:** os scripts já forçam UTF-8; se ainda aparecer, rode `set PYTHONIOENCODING=utf-8` (cmd) ou `$env:PYTHONIOENCODING="utf-8"` (PowerShell) antes.
- **"passa do limite de 260 do Windows":** a pasta de trabalho está funda demais. Rode com `--saida C:/apresentacoes` (ou outra pasta curta).
- **PPTX com fonte diferente:** instale os TTF de `assets/fonts/ttf/` e reabra o arquivo.
- **Gráfico no PPTX:** é gráfico nativo. Clique com o botão direito e escolha **Editar dados** para mudar os números.

## Estrutura

```
apresentacao-lg/
├── SKILL.md                 # instruções que o Claude segue
├── README.md                # este arquivo
├── requirements.txt
├── references/
│   ├── brand-lg.md          # cores, fontes, logo por fundo, grafismo, proibições
│   ├── copy-lg.md           # tom de voz, título-afirmação, limites, regra do dado
│   ├── layouts.md           # os 16 layouts e quando usar cada um
│   └── schema.md            # formato do deck.json
├── scripts/
│   ├── build.py             # orquestra e confere
│   ├── render_html.py       # deck.json → HTML
│   ├── export_pdf.py        # HTML → PDF (e prévias PNG)
│   ├── render_pptx.py       # deck.json → PPTX
│   └── lg_comum.py          # tokens, validação e utilitários
├── assets/
│   ├── logo/                # SVG da marca e PNG para o PPTX
│   ├── grafismo/            # malha de quadras (SVG e PNG)
│   └── fonts/               # TTF para instalar, WOFF2 embutidos no HTML
└── examples/
    └── exemplo-deck.json    # deck de exemplo com os 16 layouts
```

## Licenças

Archivo, IBM Plex Sans e IBM Plex Mono são distribuídas sob a SIL Open Font License 1.1 (textos em `assets/fonts/ttf/OFL-Archivo.txt` e `assets/fonts/ttf/OFL-IBM-Plex.txt`). Os arquivos IBM Plex são os oficiais da IBM, sem alteração ("Plex" é nome reservado na licença). Os arquivos de Archivo são instâncias estáticas geradas da fonte variável original, sem mudança de desenho. Logo, malha e cores são da LG Mobilidade Urbana: uso restrito a materiais da empresa.
