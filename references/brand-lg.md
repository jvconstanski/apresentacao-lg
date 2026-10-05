# Marca LG Mobilidade Urbana aplicada a slides

Fonte: Brandbook LG Mobilidade Urbana v1 e o Design DNA do caminho visual "Placa de orientação". Os geradores (`scripts/`) já aplicam tudo abaixo. Este arquivo serve para decidir layout, conferir prévia e explicar escolha ao usuário.

## Tese

Placa de orientação urbana cruzada com prancha de projeto viário. A LG orienta a decisão do gestor com estudo técnico. O único gesto expressivo é a linha de ônibus que sobe a 45° e segue reta.

## Cores (só estas)

| Token | Hex | Papel no slide |
|---|---|---|
| fundo | `#F9FAFB` | Fundo claro padrão (papel de plotagem) |
| apoio | `#EAEDF0` | Fundo alternado (linha do tempo, processo), painel "hoje" do comparativo |
| branco | `#FFFFFF` | Só card: tabela, painel "proposta", nota lateral |
| grafite | `#22262B` | Texto principal, fundo das aberturas de seção e da citação |
| grafite-2 | `#2C3138` | Apoio no fundo escuro |
| linha escura | `#3A414A` | Marca de dado pendente no fundo escuro |
| azul | `#1266D3` | Destaque de texto, série principal, rota, fundo do encerramento |
| azul hover | `#105BBC` | Reservado (estado de link) |
| azul sobre escuro | `#2C7FED` | Destaque e rota sobre grafite |
| verde | `#21C45D` | Só o ponto de chegada da rota e o botão do próximo passo (menos de 10% da tela) |
| cinza | `#6F7D90` | Traço, borda, marcador de lista neutro, série 3 |
| cinza texto | `#56637A` | Texto de apoio sobre claro (contraste AA) |
| cinza claro | `#AEB8C5` | Texto de apoio sobre grafite, barras não destacadas, série 4 |
| malha / borda | `#E1E7EF` | Malha de quadras e linhas de cota no claro |
| malha apoio | `#DCE3EC` | Malha sobre o fundo de apoio |
| gradiente | `135°, #1266D3 → #21C45D` | Só o traçado de conversão. Nunca fundo de slide |

Proporção de referência por deck: neutros perto de 62%, grafite 22%, azul 9%, verde 7%. Texto sobre verde é sempre grafite (contraste 6,7:1).

Ordem das séries nos gráficos: azul, grafite, cinza, cinza claro. Barra destacada: azul; as demais em cinza claro. Rosca: azul, grafite, cinza, cinza claro, malha apoio, borda.

## Tipografia

| Uso | Fonte | Medida na tela 1920 × 1080 |
|---|---|---|
| Display (capa) | Archivo, largura 87,5%, peso 800, espaço −0,03em | 112 px, entrelinha 0,98 |
| Display 2 (seção, afirmação, encerramento) | idem | 96 px |
| Título de conteúdo | idem | 64 px, entrelinha 1,03 |
| Subtítulo de item (h3) | Archivo, largura 87,5%, peso 700 | 28 a 34 px |
| Rótulo | Archivo 600, caixa alta, espaço +0,1em | 20 px |
| Texto | IBM Plex Sans 400 e 600 | 24 a 32 px, entrelinha 1,35 a 1,45 |
| Fonte do dado e rodapé | IBM Plex Sans 400 | 18 px |
| Código ou identificador técnico | IBM Plex Mono 400 | só dentro de texto, marcado com crase |

Regras: caixa de frase, nunca Title Case. Salto de 3x entre display e o nível seguinte (112 → 36, 96 → 32). Números tabulares em tabela e KPI. Sem itálico de destaque. Sem fonte monoespaçada em rótulo.

No PPTX os nomes de fonte são: `Archivo SemiCondensed ExtraBold`, `Archivo SemiCondensed` (negrito), `Archivo SemiBold`, `IBM Plex Sans`, `IBM Plex Sans SmBld` (o seminegrito, com o nome que o Windows mostra), `IBM Plex Mono`. Os TTF estão em `assets/fonts/ttf/` (licença OFL, redistribuíveis). Os arquivos IBM Plex são os oficiais da IBM, sem alteração (o nome "Plex" é reservado na licença); os de Archivo são instâncias estáticas da fonte variável.

## Espaçamento e forma

- Escala: 8, 16, 24, 32, 48, 72, 112 px.
- Margem do slide: 112 px nas laterais, 72 px no topo, conteúdo até 968 px de altura; rodapé em 1000 px.
- Canto: 4 px no botão, 2 px no card, 0 na imagem. Nunca pílula.
- Sombra azulada `rgba(18,38,70,.06 a .14)`, nunca preta. Sem vidro, sem grão, sem 3D.

## Logo por fundo

| Fundo | Arquivo |
|---|---|
| Claro ou apoio | `assets/logo/lg-horizontal.svg` (PNG: `assets/logo/png/lg-horizontal.png`) |
| Grafite | `assets/logo/lg-horizontal-negativo.svg` (azul sobe para `#2C7FED`) |
| Azul | `assets/logo/lg-horizontal-mono-branco.svg` |
| Impressão em uma cor | `assets/logo/lg-horizontal-mono.svg` |

O símbolo (`lg-simbolo*.svg`) vai no rodapé de cada slide de conteúdo. Mínimo: horizontal com 140 px, símbolo com 24 px. Proteção em volta igual à largura do traço do símbolo. Nunca distorcer, trocar as cores, aplicar sombra ou pôr sobre fundo poluído.

## Grafismo

- **Malha de quadras** (`assets/grafismo/planta*.svg`): linhas de 1,2 px como textura. Entra na capa (lado direito), na abertura de seção (fundo inteiro, versão escura) e no diagrama de rede. Fora disso, o fundo é liso.
- **Traçado de conversão:** faixa que sobe a 45° e segue reta, sempre com o gradiente, acima do título. Altura 40 px, traço 8,6 px, largura 340 px.
- **Rota:** linha de 12 px que entra pela borda, converte só a 0°, 45° e 90° e termina num ponto quadrado. A rota é o único elemento que atravessa a margem e sai do slide.
- **Paradas:** quadrado branco com contorno grafite. Terminal: quadrado maior. Chegada: quadrado verde cheio.
- **Movimento (só HTML):** curva `cubic-bezier(.22,.61,.36,1)`; 620 ms na revelação (sobe até 24 px, 90 ms entre rótulo, título e texto); 1.200 ms no traçado e na rota. `prefers-reduced-motion` desliga tudo. O PDF sai sem transição.

## Proibido

1. Gradiente azul para verde como fundo de slide ou véu sobre foto.
2. Hero centralizado sobre foto e fileira de três cards iguais (template genérico).
3. Estética de aplicativo de mobilidade: neon, mockup de celular flutuando, botão pílula.
4. Foto de ônibus gerada por IA, banco de imagem, aperto de mão, gente sorrindo para o notebook.
5. Logo girando, quique, parallax 3D, contador de número animado, gradiente em movimento.
6. Linha diagonal fora de 45°, curva livre em rota, seta decorativa.
7. Verde em texto corrido, em fundo de slide ou como cor de série comum.
8. Reflexos visuais genéricos: fundo creme, itálico de destaque, rótulos 01/02/03 em itens que não são etapas, rótulo monoespaçado, botão pílula.

## Régua antes de entregar

1. Tapando o logo, o slide ainda parece da LG?
2. O traçado de conversão está acima do título?
3. O verde aparece só na chegada ou no botão do próximo passo?
4. O título está em Archivo, caixa de frase, com salto de escala?
5. Toda linha anda a 0°, 45° ou 90°?
6. Nada de pílula, itálico de destaque ou fundo creme?
7. Nome de serviço no lugar de adjetivo?
