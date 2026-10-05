"""deck.json → HTML único, offline e autocontido, na identidade visual da LG.

Uso:
    python render_html.py caminho/deck.json [-o saida.html]

Tudo vai embutido no arquivo: fontes (WOFF2 em base64; IBM Plex nos arquivos oficiais da IBM, sem alteração), logos, malha de quadras,
CSS e JS. Tela de desenho 1920 × 1080 escalada para caber na janela; no celular em
pé, os slides viram modo leitura com rolagem, sem texto cortado.
"""
from __future__ import annotations

import argparse
import base64
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lg_comum as C  # noqa: E402


# --------------------------------------------------------------------------
# utilidades
# --------------------------------------------------------------------------
def esc(t) -> str:
    return html.escape("" if t is None else str(t), quote=True)


def h(texto) -> str:
    """Texto com marcação inline → HTML (destaque azul e caixa de dado pendente)."""
    partes = []
    for trecho, tipo in C.segmentos(texto):
        if tipo == "destaque":
            partes.append(f'<span class="hl">{esc(trecho)}</span>')
        elif tipo == "dado":
            partes.append(f'<span class="dado">{esc(trecho)}</span>')
        elif tipo == "codigo":
            partes.append(f'<code class="cod">{esc(trecho)}</code>')
        else:
            partes.append(esc(trecho))
    return "".join(partes)


def svg_txt(texto) -> str:
    return esc(C.texto_puro(texto))


def b64(caminho: Path) -> str:
    return base64.b64encode(caminho.read_bytes()).decode("ascii")


def quebrar(texto: str, maximo: int, linhas: int = 2) -> list[str]:
    palavras = C.texto_puro(texto).split()
    saida, atual = [], ""
    for p in palavras:
        teste = f"{atual} {p}".strip()
        if len(teste) <= maximo or not atual:
            atual = teste
        else:
            saida.append(atual)
            atual = p
    if atual:
        saida.append(atual)
    if len(saida) > linhas:
        saida = saida[:linhas]
        saida[-1] = saida[-1].rstrip(".,;:") + "…"
    return saida


def miolo_svg(caminho: Path) -> str:
    bruto = caminho.read_text(encoding="utf-8")
    inicio = bruto.index(">", bruto.index("<svg")) + 1
    fim = bruto.rindex("</svg>")
    return bruto[inicio:fim]


# --------------------------------------------------------------------------
# CSS
# --------------------------------------------------------------------------
CSS = r"""
@font-face{font-family:"Archivo";src:url(data:font/woff2;base64,__ARCHIVO__) format("woff2");font-weight:600 800;font-stretch:87.5% 100%;font-style:normal;font-display:block}
@font-face{font-family:"IBM Plex Sans";src:url(data:font/woff2;base64,__PLEX__) format("woff2");font-weight:400;font-style:normal;font-display:block}
@font-face{font-family:"IBM Plex Sans";src:url(data:font/woff2;base64,__PLEXSB__) format("woff2");font-weight:600;font-style:normal;font-display:block}
@font-face{font-family:"IBM Plex Mono";src:url(data:font/woff2;base64,__MONO__) format("woff2");font-weight:400;font-style:normal;font-display:block}
:root{--azul:#1266D3;--azul-claro:#2C7FED;--verde:#21C45D;--grafite:#22262B;--grafite-2:#2C3138;--grafite-3:#3A414A;--cinza:#6F7D90;--cinza-texto:#56637A;--cinza-claro:#AEB8C5;--fundo:#F9FAFB;--apoio:#EAEDF0;--borda:#E1E7EF;--branco:#FFFFFF;
--gradiente:linear-gradient(135deg,#1266D3,#21C45D);--ease:cubic-bezier(.22,.61,.36,1);
--f-display:"Archivo","Arial Narrow",Arial,sans-serif;--f-texto:"IBM Plex Sans","Segoe UI",Arial,sans-serif;--f-mono:"IBM Plex Mono",Consolas,monospace;
--sombra:0 1px 2px rgba(18,38,70,.06),0 8px 24px rgba(18,38,70,.08);
--t-display:112px;--t-display-2:96px;--t-titulo:64px;--t-h3:34px;--t-sub:32px;--t-corpo:28px;--t-apoio:24px;--t-legenda:22px;--t-rotulo:20px;--t-fonte:18px;
--mx:112px;--mt:72px;--mb:112px}
*,*::before,*::after{box-sizing:border-box}
html,body{margin:0;height:100%;background:#22262B;overflow:hidden;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font-family:var(--f-texto);color:var(--grafite)}
p,ul,ol,h1,h2,h3,blockquote{margin:0;padding:0}
ul,ol{list-style:none}
.palco{position:absolute;left:50%;top:50%;width:1920px;height:1080px;transform:translate(-50%,-50%) scale(var(--s,.5));transform-origin:50% 50%}
.slide{--k:1;--ke:1;position:absolute;inset:0;overflow:hidden;opacity:0;visibility:hidden;transition:opacity 620ms var(--ease),visibility 0s linear 620ms}
.slide.ativo{opacity:1;visibility:visible;transition:opacity 620ms var(--ease)}
.f-claro{background:var(--fundo);color:var(--grafite)}
.f-apoio{background:var(--apoio);color:var(--grafite)}
.f-escuro{background:var(--grafite);color:var(--fundo)}
.f-azul{background:var(--azul);color:#fff}
.arte{position:absolute;inset:0;pointer-events:none;overflow:hidden}
.arte svg{position:absolute;display:block}
.sl-corpo{position:relative;height:100%;padding:var(--mt) var(--mx) var(--mb);display:flex;flex-direction:column;overflow:hidden}
.sl-cab{flex:0 0 auto;max-width:1560px}
.sl-conteudo{flex:1 1 auto;min-height:0;position:relative;margin-top:48px}
.tracado{display:block;position:relative;width:340px;height:40px;margin:0 0 24px;flex:0 0 auto}
.tracado::before{content:"";position:absolute;inset:0;background:var(--gradiente);clip-path:polygon(0 100%,40px 0,100% 0,100% 8.6px,43.6px 8.6px,12.1px 100%)}
.slide.ativo .tracado::before{animation:tracar 1200ms var(--ease) 80ms both}
@keyframes tracar{from{clip-path:polygon(0 100%,40px 0,40px 0,40px 8.6px,43.6px 8.6px,12.1px 100%)}to{clip-path:polygon(0 100%,40px 0,100% 0,100% 8.6px,43.6px 8.6px,12.1px 100%)}}
.rotulo{margin:0 0 16px;font-family:var(--f-display);font-weight:600;font-stretch:100%;font-size:calc(var(--t-rotulo)*var(--k));letter-spacing:.1em;text-transform:uppercase;line-height:1.3;color:var(--cinza-texto)}
.f-escuro .rotulo{color:var(--cinza-claro)}.f-azul .rotulo{color:#EAEDF0}
.display,.display-2,.titulo,.h3,.cit{font-family:var(--f-display);font-stretch:87.5%;font-weight:800;text-wrap:balance}
.display{font-size:calc(var(--t-display)*var(--k));line-height:.98;letter-spacing:-.03em}
.display-2{font-size:calc(var(--t-display-2)*var(--k));line-height:1;letter-spacing:-.03em;max-width:1560px}
.titulo{font-size:calc(var(--t-titulo)*var(--k));line-height:1.03;letter-spacing:-.03em;max-width:1560px}
.h3{font-size:calc(var(--t-h3)*var(--k));line-height:1.12;letter-spacing:-.015em;font-weight:700}
.sub{margin-top:24px;font-size:calc(var(--t-sub)*var(--k));line-height:1.35;color:var(--cinza-texto);max-width:1120px;text-wrap:pretty}
.apoio{margin-top:24px;font-size:calc(var(--t-corpo)*var(--k));line-height:1.45;color:var(--cinza-texto);max-width:1200px;text-wrap:pretty}
.corpo{font-size:calc(var(--t-corpo)*var(--k));line-height:1.45}
.pq{margin-top:8px;font-size:calc(var(--t-apoio)*var(--k));line-height:1.45;color:var(--cinza-texto);text-wrap:pretty}
.f-escuro .sub,.f-escuro .apoio,.f-escuro .pq{color:var(--cinza-claro)}.f-azul .sub,.f-azul .apoio,.f-azul .pq{color:#EAEDF0}
.hl{color:var(--azul)}.f-escuro .hl{color:var(--azul-claro)}
.f-azul .hl{text-decoration:underline;text-decoration-color:var(--verde);text-decoration-thickness:.08em;text-underline-offset:.14em}
.dado{display:inline-block;font-family:var(--f-texto);font-stretch:100%;font-weight:600;font-size:.82em;letter-spacing:0;line-height:1.2;vertical-align:.08em;padding:.08em .4em;border:2px dashed var(--cinza);border-radius:2px;color:var(--cinza-texto);background:rgba(111,125,144,.08);white-space:nowrap;text-transform:none}
.display .dado,.display-2 .dado,.titulo .dado,.cit .dado{font-size:.34em;vertical-align:.3em}
.kpi-valor .dado{font-size:.24em;vertical-align:.6em}
.cod{font-family:var(--f-mono);font-size:.88em;letter-spacing:0;padding:0 .2em;background:rgba(111,125,144,.1);border-radius:2px}
.f-escuro .dado,.f-azul .dado{color:#EAEDF0;border-color:var(--cinza-claro);background:rgba(255,255,255,.08)}
.sl-fonte{flex:0 0 auto;margin-top:24px;font-size:calc(var(--t-fonte)*var(--k));color:var(--cinza-texto);line-height:1.4}
.f-escuro .sl-fonte{color:var(--cinza-claro)}
.sl-rodape{position:absolute;left:var(--mx);right:var(--mx);bottom:40px;height:32px;display:flex;align-items:center;gap:16px;font-size:var(--t-fonte);line-height:1;color:var(--cinza-texto)}
.sl-rodape svg{width:27px;height:32px;flex:0 0 auto}
.sl-rodape .num{margin-left:auto;font-family:var(--f-display);font-weight:600;letter-spacing:.1em;font-variant-numeric:tabular-nums}
.f-escuro .sl-rodape{color:var(--cinza-claro)}
.lista li{position:relative;padding-left:36px;margin-top:16px;font-size:calc(var(--t-corpo)*var(--k));line-height:1.4}
.lista li::before{content:"";position:absolute;left:0;top:.5em;width:12px;height:12px;background:var(--cinza)}
.lista.azul li::before{background:var(--azul)}
/* revelação */
.rv{opacity:0;transform:translateY(24px)}
.slide.ativo .rv{opacity:1;transform:none;transition:opacity 620ms var(--ease),transform 620ms var(--ease);transition-delay:calc(var(--d,0)*90ms + 120ms)}
.rota{stroke-dasharray:1;stroke-dashoffset:1}
.slide.ativo .rota{stroke-dashoffset:0;transition:stroke-dashoffset 1200ms var(--ease);transition-delay:calc(var(--d,0)*150ms + 200ms)}
.pto{opacity:0}
.slide.ativo .pto{opacity:1;transition:opacity 300ms var(--ease);transition-delay:calc(var(--d,0)*90ms + 900ms)}
.barra{transform-box:fill-box;transform-origin:50% 100%;transform:scaleY(0)}
.barra-h{transform-box:fill-box;transform-origin:0 50%;transform:scaleX(0)}
.slide.ativo .barra,.slide.ativo .barra-h{transform:none;transition:transform 620ms var(--ease);transition-delay:calc(var(--d,0)*60ms + 250ms)}
.fatia{opacity:0}
.slide.ativo .fatia{opacity:1;transition:opacity 620ms var(--ease);transition-delay:calc(var(--d,0)*90ms + 200ms)}
/* capa */
.l-capa .capa-arte{left:auto;right:0;top:0;width:860px;height:1080px;-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 200px);mask-image:linear-gradient(90deg,transparent 0,#000 200px)}
.l-capa .sl-corpo{padding-bottom:96px}
.capa-logo{display:block;width:300px;height:auto}
.capa-txt{margin-top:auto;max-width:960px}
.capa-meta{margin-top:48px;font-family:var(--f-display);font-weight:600;font-size:calc(var(--t-rotulo)*var(--k));letter-spacing:.1em;text-transform:uppercase;color:var(--cinza-texto)}
/* seção */
.l-secao .sl-corpo{justify-content:flex-end}
.secao-num{font-family:var(--f-display);font-stretch:87.5%;font-weight:800;font-size:calc(200px*var(--k));line-height:.86;letter-spacing:-.03em;color:var(--azul-claro);margin-bottom:40px;font-variant-numeric:tabular-nums}
/* afirmação e citação */
.l-afirmacao .sl-corpo,.l-citacao .sl-corpo{justify-content:center}
.cit{font-size:calc(64px*var(--k));line-height:1.08;letter-spacing:-.025em;max-width:1500px}
.cit-autor{margin-top:48px;font-family:var(--f-display);font-weight:600;font-size:calc(var(--t-legenda)*var(--k));letter-spacing:.1em;text-transform:uppercase}
/* KPIs */
.kpis-grade{display:grid;gap:0 48px;align-content:center;height:100%}
.kpi{border-left:1px solid var(--cinza);padding:8px 0 0 32px;min-width:0}
.kpi-valor{font-family:var(--f-display);font-stretch:87.5%;font-weight:800;font-size:calc(var(--kv)*var(--k)*var(--ke));line-height:.92;letter-spacing:-.03em;white-space:nowrap;overflow:hidden;font-variant-numeric:tabular-nums}
.kpi-valor.destaque{color:var(--azul)}
.kpi-rotulo{margin-top:24px;font-weight:600;font-size:calc(var(--t-corpo)*var(--k));line-height:1.3}
/* gráficos */
.grafico{position:absolute;inset:0}
.grafico svg{display:block;width:100%;height:100%}
.legenda-series{display:flex;flex-wrap:wrap;gap:8px 40px;margin-top:24px}
.legenda-series li{display:flex;align-items:center;gap:12px;font-size:calc(var(--t-legenda)*var(--k));color:var(--grafite)}
.legenda-series i{display:block;width:20px;height:20px}
.donut-grade{display:grid;grid-template-columns:auto 1fr;gap:112px;align-items:center;height:100%}
.donut-svg{height:100%;max-height:600px;aspect-ratio:1/1;display:flex;align-items:center}
.donut-svg svg{width:100%;height:100%;display:block}
.legenda-donut li{display:grid;grid-template-columns:24px 1fr auto;gap:24px;align-items:center;padding:20px 0;border-top:1px solid var(--borda);font-size:calc(var(--t-corpo)*var(--k));line-height:1.3}
.legenda-donut li:last-child{border-bottom:1px solid var(--borda)}
.legenda-donut i{display:block;width:24px;height:24px}
.legenda-donut b{font-weight:600;font-variant-numeric:tabular-nums}
/* tabela */
.tabela-card{background:#fff;border-radius:2px;box-shadow:var(--sombra);overflow:hidden}
.tabela-card table{width:100%;border-collapse:collapse;font-size:calc(var(--t-apoio)*var(--k));line-height:1.35}
.tabela-card th{text-align:left;font-family:var(--f-display);font-weight:600;font-size:calc(var(--t-fonte)*var(--k));letter-spacing:.1em;text-transform:uppercase;color:var(--cinza-texto);background:var(--apoio);padding:16px 24px}
.tabela-card td{padding:16px 24px;border-top:1px solid var(--borda)}
.tabela-card .num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.tabela-card tr.destaque td{font-weight:600}
.tabela-card tr.destaque td:first-child{box-shadow:inset 6px 0 0 var(--azul)}
/* comparativo */
.comp{display:grid;grid-template-columns:1fr 160px 1fr;height:100%;align-items:stretch;align-content:center}
.comp-lado{padding:48px;border-radius:2px;min-width:0}
.comp-a{background:var(--apoio)}
.comp-b{background:#fff;box-shadow:var(--sombra);border-top:6px solid var(--azul)}
.comp-b .rotulo{color:var(--azul)}
.comp-ponte{position:relative}
.comp-ponte svg{position:absolute;left:0;top:50%;width:160px;height:120px;transform:translateY(-50%)}
/* linha do tempo */
.l-linha-do-tempo .sl-conteudo,.l-processo .sl-conteudo{display:flex;align-items:center}
.tl{display:grid;gap:0 32px;position:relative;align-content:start;padding-top:24px;width:100%}
.tl::before{content:"";position:absolute;left:calc(-1*var(--mx));right:calc(-1*var(--mx));top:calc(24px + 120px + 25px);height:6px;background:var(--grafite);transform-origin:0 50%;transform:scaleX(0)}
.slide.ativo .tl::before{transform:none;transition:transform 1200ms var(--ease) 150ms}
.tl-data{height:120px;display:flex;align-items:flex-end;padding-bottom:16px;font-family:var(--f-display);font-stretch:87.5%;font-weight:800;font-size:calc(44px*var(--k));line-height:1;letter-spacing:-.02em;color:var(--azul)}
.tl-pto{height:56px;display:flex;align-items:center}
.tl-pto i{display:block;width:28px;height:28px;background:#fff;border:4px solid var(--grafite);position:relative}
.tl-pto i.atual{background:var(--azul);border-color:var(--azul)}
.tl-pto i.chegada{width:36px;height:36px;background:var(--verde);border-color:var(--verde)}
.tl-marco{min-width:0;padding-right:8px}
.tl-marco .h3{margin-top:24px;font-size:calc(28px*var(--k))}
/* rede */
.l-rede .sl-corpo{max-width:760px}
.rede-diagrama{position:absolute;right:0;top:0;width:1160px;height:1080px}
.rede-diagrama svg{width:100%;height:100%;display:block}
.legenda-rede{margin-top:40px}
.legenda-rede li{display:flex;align-items:center;gap:16px;margin-top:16px;font-size:calc(var(--t-apoio)*var(--k))}
.legenda-rede i{display:block;width:48px;height:12px;flex:0 0 auto}
/* pilares */
.pilares-grade{display:grid;grid-template-columns:5fr 7fr;gap:112px;height:100%;align-items:center}
.pilares li{display:grid;grid-template-columns:72px 1fr;padding:32px 0;border-top:1px solid var(--borda)}
.pilares li:last-child{border-bottom:1px solid var(--borda)}
.pilares .marca{display:block;width:20px;height:20px;margin-top:.5em;background:var(--azul)}
/* processo */
.proc{position:relative;height:480px;width:100%;flex:0 0 auto}
.proc svg{position:absolute;left:calc(-1*var(--mx));top:0;width:1920px;height:480px;overflow:visible}
.proc-etapa{position:absolute;min-width:0}
.proc-etapa .n{font-family:var(--f-display);font-stretch:87.5%;font-weight:800;font-size:calc(56px*var(--k));line-height:1;color:var(--azul);font-variant-numeric:tabular-nums}
.proc-txt{position:absolute}
.proc-txt .h3{font-size:calc(30px*var(--k))}
/* tópicos */
.topicos-grade{display:grid;gap:96px;height:100%;align-content:start}
.topicos-grade.com-nota{grid-template-columns:8fr 4fr}
.lista-g li{position:relative;padding-left:44px;margin-bottom:24px;font-size:calc(var(--t-corpo)*var(--k));line-height:1.4}
.lista-g li::before{content:"";position:absolute;left:0;top:.48em;width:14px;height:14px;background:var(--azul)}
.nota{background:#fff;box-shadow:var(--sombra);border-top:6px solid var(--azul);border-radius:2px;padding:40px}
/* encerramento */
.l-encerramento .sl-corpo{padding-bottom:96px}
.prox{display:inline-block;margin-top:48px;padding:20px 32px;border-radius:4px;background:var(--verde);color:var(--grafite);font-family:var(--f-display);font-weight:700;font-size:calc(var(--t-corpo)*var(--k));line-height:1.2}
.contato{display:flex;flex-wrap:wrap;gap:12px 48px;margin-top:48px;font-size:calc(var(--t-apoio)*var(--k));color:#EAEDF0}
.f-escuro .contato{color:var(--cinza-claro)}
/* interface */
.progresso{position:fixed;left:0;top:0;width:100%;height:4px;background:rgba(255,255,255,.08);z-index:10}
.progresso span{display:block;height:100%;background:var(--azul-claro);transform-origin:0 50%;transform:scaleX(0);transition:transform 620ms var(--ease)}
.controles{position:fixed;right:16px;bottom:16px;z-index:10;display:flex;align-items:center;gap:4px;padding:6px;border-radius:4px;background:rgba(34,38,43,.9);color:#F9FAFB;font:600 13px/1 var(--f-display);letter-spacing:.1em;opacity:0;transition:opacity 180ms var(--ease)}
.mostra-ui .controles,.controles:focus-within{opacity:1}
.controles button{all:unset;cursor:pointer;width:36px;height:36px;display:grid;place-items:center;border-radius:4px}
.controles button:hover{background:#3A414A}
.controles button:focus-visible{outline:2px solid var(--verde)}
.controles svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2.2}
.contador{min-width:76px;text-align:center;font-variant-numeric:tabular-nums}
.notas{position:fixed;left:16px;right:16px;bottom:68px;z-index:11;max-height:40vh;overflow:auto;padding:16px 20px;border-radius:2px;background:rgba(34,38,43,.95);color:#F9FAFB;font:16px/1.5 var(--f-texto);display:none}
.ver-notas .notas{display:block}
/* celular em pé: modo leitura */
.retrato .palco{left:0;top:0;width:100%;height:100%;transform:none}
.retrato .slide{overflow-y:auto;overflow-x:hidden;--k:1!important;--ke:1!important;--t-display:40px;--t-display-2:34px;--t-titulo:28px;--t-h3:19px;--t-sub:18px;--t-corpo:16px;--t-apoio:15px;--t-legenda:14px;--t-rotulo:11px;--t-fonte:12px;--mx:24px;--mt:40px;--mb:24px}
.retrato .sl-corpo{height:auto;min-height:calc(100% - 96px);overflow:visible;max-width:none!important}
.retrato .sl-conteudo{flex:0 0 auto;margin-top:24px}
.retrato .tracado{width:170px;height:20px;margin-bottom:12px}
.retrato .tracado::before{clip-path:polygon(0 100%,20px 0,100% 0,100% 4.3px,21.8px 4.3px,6px 100%)}
.retrato .slide.ativo .tracado::before{animation:none}
.retrato .arte{opacity:.28}
.retrato .arte path,.retrato .arte rect,.retrato .l-capa .capa-arte{display:none}
.retrato .l-processo .sl-conteudo,.retrato .l-linha-do-tempo .sl-conteudo{display:block}
.retrato .proc-txt .h3{font-size:19px}
.retrato .sl-rodape{position:static;margin:24px var(--mx) 64px}
.retrato .capa-logo{width:160px}
.retrato .secao-num{font-size:72px;margin-bottom:16px}
.retrato .cit{font-size:26px}
.retrato .kpis-grade{grid-template-columns:1fr 1fr!important;gap:24px 16px;--kv:44px!important}
.retrato .kpi{padding-left:12px}
.retrato .kpi-rotulo{margin-top:8px}
.retrato .grafico{position:relative;inset:auto}
.retrato .grafico svg{height:auto}
.retrato .donut-grade,.retrato .pilares-grade,.retrato .topicos-grade.com-nota,.retrato .comp{display:block}
.retrato .donut-svg{height:auto;max-width:260px;margin:0 auto 16px}
.retrato .legenda-donut li{padding:10px 0;gap:12px}
.retrato .comp-lado{padding:20px;margin-bottom:12px}
.retrato .comp-ponte{display:none}
.retrato .tabela-card{overflow-x:auto}
.retrato .tabela-card th,.retrato .tabela-card td{padding:8px 10px}
.retrato .tl{display:block;padding:0 0 0 24px;border-left:4px solid var(--grafite)}
.retrato .tl::before{display:none}
.retrato .tl-data{height:auto;padding:16px 0 4px;font-size:22px}
.retrato .tl-pto{display:none}
.retrato .tl-marco .h3{margin-top:4px;font-size:17px}
.retrato .rede-diagrama{position:relative;width:100%;height:auto;aspect-ratio:1160/1080;margin-top:16px}
.retrato .proc svg{display:none}
.retrato .proc,.retrato .proc-etapa,.retrato .proc-txt{position:static!important;width:auto!important;height:auto}
.retrato .proc-etapa{margin-top:20px}
.retrato .proc-etapa .n{font-size:24px}
.retrato .pilares li{grid-template-columns:28px 1fr;padding:16px 0}
.retrato .pilares .marca{width:10px;height:10px}
.retrato .lista-g li{padding-left:24px;margin-bottom:12px}
.retrato .lista-g li::before{width:8px;height:8px}
.retrato .lista li{padding-left:20px}
.retrato .lista li::before{width:8px;height:8px}
.retrato .nota{padding:20px;margin-top:24px}
.retrato .prox{padding:12px 16px;margin-top:24px}
.retrato .controles{opacity:1;bottom:8px;right:8px}
.medindo .rv{transform:none!important;transition:none!important}
.retrato .proc{height:auto}
@media (prefers-reduced-motion:reduce){.slide,.slide *,.slide *::before{transition:none!important;animation:none!important}.rv,.pto,.fatia{opacity:1;transform:none}.rota{stroke-dashoffset:0}.barra,.barra-h,.tl::before{transform:none}}
@page{size:1920px 1080px;margin:0}
@media print{
html,body{height:auto;overflow:visible;background:none}
.palco{position:static;transform:none!important;width:1920px;height:auto}
.slide{position:relative;inset:auto;width:1920px;height:1080px;opacity:1!important;visibility:visible!important;break-after:page;page-break-after:always;transition:none!important}
.slide *,.slide *::before{animation:none!important;transition:none!important}
.rv,.pto,.fatia{opacity:1!important;transform:none!important}
.rota{stroke-dashoffset:0!important}
.barra,.barra-h,.tl::before{transform:none!important}
.progresso,.controles,.notas{display:none!important}
}
"""

JS = r"""
(function(){
var D=document,palco=D.getElementById('palco'),slides=[].slice.call(D.querySelectorAll('.slide')),N=slides.length;
var barra=D.querySelector('.progresso span'),cont=D.getElementById('contador'),notas=D.getElementById('notas');
var i=0,timer=null;
function pad(n){return String(n)}
function medir(){
  var retrato=innerWidth<innerHeight&&innerWidth<900;
  D.body.classList.toggle('retrato',retrato);
  palco.style.setProperty('--s',Math.min(innerWidth/1920,innerHeight/1080));
}
function ir(n){
  n=Math.max(0,Math.min(N-1,n));
  slides.forEach(function(el,k){el.classList.toggle('ativo',k===n);el.setAttribute('aria-hidden',k===n?'false':'true')});
  i=n;barra.style.transform='scaleX('+((n+1)/N)+')';cont.textContent=pad(n+1)+' / '+pad(N);
  var t=slides[n].querySelector('template.nt');notas.innerHTML=t?t.innerHTML:'<p>Sem notas neste slide.</p>';
  if(location.hash!=='#'+(n+1)){try{history.replaceState(null,'','#'+(n+1))}catch(e){}}
  slides[n].scrollTop=0;
}
function prox(){ir(i+1)}function ant(){ir(i-1)}
function tela(){if(!D.fullscreenElement){(D.documentElement.requestFullscreen||function(){}).call(D.documentElement)}else{D.exitFullscreen()}}
D.addEventListener('keydown',function(e){
  if(e.altKey||e.ctrlKey||e.metaKey)return;
  var k=e.key;
  if(k==='ArrowRight'||k==='ArrowDown'&&!D.body.classList.contains('retrato')||k==='PageDown'||k===' '||k==='Enter'){e.preventDefault();prox()}
  else if(k==='ArrowLeft'||k==='ArrowUp'&&!D.body.classList.contains('retrato')||k==='PageUp'||k==='Backspace'){e.preventDefault();ant()}
  else if(k==='Home'){ir(0)}else if(k==='End'){ir(N-1)}
  else if(k==='f'||k==='F'){tela()}
  else if(k==='n'||k==='N'){D.body.classList.toggle('ver-notas')}
  else if(k==='Escape'){D.body.classList.remove('ver-notas')}
});
palco.addEventListener('click',function(e){
  if(e.target.closest('a,button'))return;
  if(String(window.getSelection&&getSelection())!=='')return;
  (e.clientX/innerWidth<0.33)?ant():prox();
});
var x0=null,y0=null;
palco.addEventListener('touchstart',function(e){x0=e.touches[0].clientX;y0=e.touches[0].clientY},{passive:true});
palco.addEventListener('touchend',function(e){if(x0===null)return;var dx=e.changedTouches[0].clientX-x0,dy=e.changedTouches[0].clientY-y0;if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy)*1.5){dx<0?prox():ant();e.preventDefault()}x0=null},{passive:false});
D.getElementById('b-ant').onclick=ant;D.getElementById('b-prox').onclick=prox;D.getElementById('b-tela').onclick=tela;
D.addEventListener('mousemove',function(){D.body.classList.add('mostra-ui');clearTimeout(timer);timer=setTimeout(function(){D.body.classList.remove('mostra-ui')},2500)});
addEventListener('resize',medir);
addEventListener('hashchange',function(){var n=parseInt(location.hash.slice(1),10);if(n&&n-1!==i)ir(n-1)});
function estoura(s){
  var c=s.querySelector('.sl-corpo');if(c&&c.scrollHeight>c.clientHeight+2)return true;
  var m=s.querySelector('.sl-conteudo');if(m&&m.scrollHeight>m.clientHeight+2)return true;
  var f=s.querySelectorAll('[data-fit]');for(var j=0;j<f.length;j++){if(f[j].scrollWidth>f[j].clientWidth+2)return true}
  return false;
}
function encolher(s){
  var g=s.querySelectorAll('[data-encolhe]');if(!g.length)return;
  s.style.setProperty('--ke',1);var r=1;
  for(var j=0;j<g.length;j++){var el=g[j];if(el.scrollWidth>el.clientWidth+1)r=Math.min(r,el.clientWidth/el.scrollWidth)}
  if(r<1)s.style.setProperty('--ke',(r*0.97).toFixed(3));
}
function ajustar(){
  var era=D.body.classList.contains('retrato');D.body.classList.remove('retrato');D.body.classList.add('medindo');
  var lista=[];
  slides.forEach(function(s,idx){
    var k=1;s.style.setProperty('--k',1);encolher(s);
    while(estoura(s)&&k>0.8){k=Math.round((k-0.04)*100)/100;s.style.setProperty('--k',k);encolher(s)}
    s.dataset.k=k;
    if(estoura(s)){s.dataset.estouro='1';lista.push({slide:idx+1,layout:s.dataset.layout,motivo:'conteúdo maior que o espaço mesmo com a fonte reduzida a 80%'})}
  });
  D.body.classList.toggle('retrato',era);D.body.classList.remove('medindo');
  window.__LG_ESTOURO=lista;
}
window.__LG_GEOMETRIA=function(){
  var out=[];
  slides.forEach(function(s,idx){
    var r=s.getBoundingClientRect(),sc=r.width/1920,limB=s.querySelector('.sl-rodape')?1004:1080;
    s.querySelectorAll('h1,h2,h3,p,li,td,th,blockquote,.kpi-valor,svg text').forEach(function(el){
      if(el.closest('.arte')||el.closest('.sl-rodape'))return;
      var b=el.getBoundingClientRect();if(!b.width&&!b.height)return;
      var L=(b.left-r.left)/sc,T=(b.top-r.top)/sc,R=(b.right-r.left)/sc,B=(b.bottom-r.top)/sc;
      if(L<-1||T<-1||R>1921||B>limB+1){out.push({slide:idx+1,layout:s.dataset.layout,elemento:el.tagName.toLowerCase(),texto:(el.textContent||'').trim().slice(0,70),caixa:[Math.round(L),Math.round(T),Math.round(R),Math.round(B)]})}
    });
  });
  return out;
};
medir();
var h0=parseInt(location.hash.slice(1),10);ir(h0?h0-1:0);
(D.fonts&&D.fonts.ready?D.fonts.ready:Promise.resolve()).then(function(){ajustar();window.__LG_PRONTO=true});
})();
"""


# --------------------------------------------------------------------------
# peças compartilhadas
# --------------------------------------------------------------------------
class Ctx:
    def __init__(self, deck: dict):
        self.deck = deck
        self.meta = deck.get("meta", {})
        self.total = len(deck["slides"])
        self.logo = {
            "claro": "data:image/svg+xml;base64," + b64(C.LOGOS / "lg-horizontal.svg"),
            "escuro": "data:image/svg+xml;base64," + b64(C.LOGOS / "lg-horizontal-negativo.svg"),
            "azul": "data:image/svg+xml;base64," + b64(C.LOGOS / "lg-horizontal-mono-branco.svg"),
        }
        self.logo["apoio"] = self.logo["claro"]


def simbolos() -> str:
    plantas = []
    for ident, arq in (("planta-claro", "planta.svg"), ("planta-escura", "planta-escura.svg"),
                       ("planta-apoio", "planta-apoio.svg")):
        plantas.append(f'<symbol id="{ident}" viewBox="0 0 1200 900">{miolo_svg(C.GRAFISMO / arq)}</symbol>')
    sym = ('<symbol id="lg-sym" viewBox="-36 -36 72 87"><g fill="none" stroke-width="12" stroke-linejoin="miter">'
           '<path d="M -24.87 -16.78 A 30.0 30.0 0 0 1 28.19 -10.26" style="stroke:var(--sb,#1266D3)"/>'
           '<path d="M -28.84 -8.27 A 30.0 30.0 0 0 0 -21.21 21.21 L 0.00 42.43 L 21.21 21.21 A 30.0 30.0 0 0 0 28.19 10.26 L 6 10.26" style="stroke:var(--sg,#21C45D)"/>'
           '</g></symbol>')
    return ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
            + "".join(plantas) + sym + "</defs></svg>")


def rodape(s: dict, n: int, ctx: Ctx) -> str:
    fundo = s.get("fundo", "claro")
    cores = {"claro": ("#1266D3", "#21C45D"), "apoio": ("#1266D3", "#21C45D"),
             "escuro": ("#2C7FED", "#21C45D"), "azul": ("#FFFFFF", "#FFFFFF")}[fundo]
    texto = ctx.meta.get("rodape") or "LG Mobilidade Urbana"
    return (f'<footer class="sl-rodape"><svg viewBox="-36 -36 72 87" style="--sb:{cores[0]};--sg:{cores[1]}" aria-hidden="true">'
            f'<use href="#lg-sym" x="-36" y="-36" width="72" height="87"/></svg><span>{esc(texto)}</span><span class="num">{n}</span></footer>')


def cab(s: dict, *, d0: int = 0, classe_titulo: str = "titulo", subtitulo_campo: str = "subtitulo",
        tag: str = "h2", extra: str = "") -> str:
    partes = ['<header class="sl-cab">', f'<span class="tracado rv" style="--d:{d0}" aria-hidden="true"></span>']
    if s.get("rotulo"):
        partes.append(f'<p class="rotulo rv" style="--d:{d0}">{h(s["rotulo"])}</p>')
    partes.append(f'<{tag} class="{classe_titulo} rv" style="--d:{d0 + 1}" data-fit>{h(s.get("titulo"))}</{tag}>')
    if s.get(subtitulo_campo):
        partes.append(f'<p class="apoio rv" style="--d:{d0 + 2}">{h(s[subtitulo_campo])}</p>')
    partes.append(extra)
    partes.append("</header>")
    return "".join(partes)


def fonte(s: dict) -> str:
    if not s.get("fonte"):
        return ""
    txt = s["fonte"]
    prefixo = "" if C.texto_puro(txt).lower().startswith("fonte") else "Fonte: "
    return f'<p class="sl-fonte rv" style="--d:4">{esc(prefixo)}{h(txt)}</p>'


def legenda_series(series: list) -> str:
    if len(series) < 2:
        return ""
    itens = "".join(f'<li><i style="background:{C.SERIES[j % 4]}"></i>{h(se.get("nome", f"Série {j + 1}"))}</li>'
                    for j, se in enumerate(series))
    return f'<ul class="legenda-series rv" style="--d:2">{itens}</ul>'


# --------------------------------------------------------------------------
# gráficos em SVG
# --------------------------------------------------------------------------
def _fmt(s: dict, v, casas=None) -> str:
    return C.numero_br(v, s.get("casas") if casas is None else casas, s.get("prefixo", ""), s.get("sufixo", ""))


def _casas_eixo(passo: float) -> int:
    if float(passo).is_integer():
        return 0
    return 1 if (passo * 10).is_integer() else 2


def svg_barras(s: dict) -> str:
    cats = s["categorias"]
    series = s["series"]
    horizontal = s.get("orientacao") == "horizontal"
    W, H = 1696, 560
    todos = [v for se in series for v in se["valores"]]
    vmin, vmax = min(0, min(todos)), max(0, max(todos))
    ini, fim, passo = C.escala_bonita(vmin, vmax, 4)
    ce = _casas_eixo(passo)
    n, ns = len(cats), len(series)
    destaque = C.indices_destaque(s.get("destaque"))
    rotulos = n * ns <= 24
    out = [f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMinYMid meet" role="img" aria-label="{svg_txt(s.get("titulo"))}">',
           '<g font-family="IBM Plex Sans, Segoe UI, Arial, sans-serif">']
    ticks = []
    t = ini
    while t <= fim + passo / 1000:
        ticks.append(round(t, 10))
        t += passo
    if not horizontal:
        pl, pr, pt, pb = 104, 16, 48, 80
        pw, ph = W - pl - pr, H - pt - pb

        def y(v):
            return pt + ph - (v - ini) / (fim - ini) * ph
        for tk in ticks:
            yy = y(tk)
            out.append(f'<line x1="{pl}" x2="{W - pr}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#E1E7EF" stroke-width="1.5"/>')
            out.append(f'<text x="{pl - 16}" y="{yy + 7:.1f}" text-anchor="end" font-size="20" fill="#56637A">{esc(_fmt(s, tk, ce))}</text>')
        banda = pw / n
        grupo = banda * (0.56 if ns == 1 else 0.7)
        bw = (grupo - 6 * (ns - 1)) / ns
        for i, cat in enumerate(cats):
            x0 = pl + i * banda + (banda - grupo) / 2
            for j, se in enumerate(series):
                v = se["valores"][i]
                if ns == 1:
                    cor = C.COR["azul"] if not destaque or i in destaque else C.COR["cinza_claro"]
                else:
                    cor = C.SERIES[j % 4]
                xb = x0 + j * (bw + 6)
                y1, y0 = y(max(v, 0)), y(min(v, 0))
                out.append(f'<rect class="barra" style="--d:{i * ns + j}" x="{xb:.1f}" y="{y1:.1f}" width="{bw:.1f}" height="{max(y0 - y1, 1):.1f}" fill="{cor}"/>')
                if rotulos:
                    ty = y1 - 12 if v >= 0 else y0 + 28
                    out.append(f'<text class="pto" style="--d:{i}" x="{xb + bw / 2:.1f}" y="{ty:.1f}" text-anchor="middle" font-size="22" font-weight="600" fill="#22262B">{esc(_fmt(s, v))}</text>')
            linhas = quebrar(cat, max(8, int(banda / 12)), 2)
            for k, ln in enumerate(linhas):
                out.append(f'<text x="{pl + i * banda + banda / 2:.1f}" y="{H - pb + 34 + k * 26:.1f}" text-anchor="middle" font-size="21" fill="#22262B">{esc(ln)}</text>')
        out.append(f'<line x1="{pl}" x2="{W - pr}" y1="{y(0):.1f}" y2="{y(0):.1f}" stroke="#6F7D90" stroke-width="2"/>')
    else:
        pl, pr, pt, pb = 400, 140, 8, 48
        pw, ph = W - pl - pr, H - pt - pb

        def x(v):
            return pl + (v - ini) / (fim - ini) * pw
        for tk in ticks:
            xx = x(tk)
            out.append(f'<line x1="{xx:.1f}" x2="{xx:.1f}" y1="{pt}" y2="{H - pb}" stroke="#E1E7EF" stroke-width="1.5"/>')
            out.append(f'<text x="{xx:.1f}" y="{H - pb + 32}" text-anchor="middle" font-size="20" fill="#56637A">{esc(_fmt(s, tk, ce))}</text>')
        banda = ph / n
        grupo = banda * (0.6 if ns == 1 else 0.74)
        bh = (grupo - 4 * (ns - 1)) / ns
        for i, cat in enumerate(cats):
            y0 = pt + i * banda + (banda - grupo) / 2
            for j, se in enumerate(series):
                v = se["valores"][i]
                if ns == 1:
                    cor = C.COR["azul"] if not destaque or i in destaque else C.COR["cinza_claro"]
                else:
                    cor = C.SERIES[j % 4]
                yb = y0 + j * (bh + 4)
                xa, xb = x(min(v, 0)), x(max(v, 0))
                out.append(f'<rect class="barra-h" style="--d:{i * ns + j}" x="{xa:.1f}" y="{yb:.1f}" width="{max(xb - xa, 1):.1f}" height="{bh:.1f}" fill="{cor}"/>')
                if rotulos:
                    out.append(f'<text class="pto" style="--d:{i}" x="{xb + 12:.1f}" y="{yb + bh / 2 + 8:.1f}" font-size="22" font-weight="600" fill="#22262B">{esc(_fmt(s, v))}</text>')
            linhas = quebrar(cat, 30, 2)
            base = pt + i * banda + banda / 2 - (len(linhas) - 1) * 13 + 7
            for k, ln in enumerate(linhas):
                out.append(f'<text x="{pl - 24}" y="{base + k * 26:.1f}" text-anchor="end" font-size="21" fill="#22262B">{esc(ln)}</text>')
        out.append(f'<line x1="{x(0):.1f}" x2="{x(0):.1f}" y1="{pt}" y2="{H - pb}" stroke="#6F7D90" stroke-width="2"/>')
    out.append("</g></svg>")
    return "".join(out)


def _y_min_linha(s: dict, vmin: float, vmax: float) -> float:
    if s.get("y_min") is not None:
        return float(s["y_min"])
    if vmin >= 0 and vmin <= 0.4 * vmax:
        return 0.0
    return vmin - (vmax - vmin) * 0.25


def svg_linha(s: dict) -> str:
    cats = s["categorias"]
    series = s["series"]
    W, H = 1696, 560
    pl, pr, pt, pb = 104, 150, 56, 64
    pw, ph = W - pl - pr, H - pt - pb
    todos = [v for se in series for v in se["valores"]]
    vmin, vmax = min(todos), max(todos)
    ini, fim, passo = C.escala_bonita(_y_min_linha(s, vmin, vmax), vmax, 4)
    ce = _casas_eixo(passo)
    n = len(cats)

    def x(i):
        return pl + (i * pw / (n - 1) if n > 1 else pw / 2)

    def y(v):
        return pt + ph - (v - ini) / (fim - ini) * ph
    out = [f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMinYMid meet" role="img" aria-label="{svg_txt(s.get("titulo"))}">',
           '<g font-family="IBM Plex Sans, Segoe UI, Arial, sans-serif">']
    t = ini
    while t <= fim + passo / 1000:
        yy = y(t)
        out.append(f'<line x1="{pl}" x2="{W - pr + 40}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#E1E7EF" stroke-width="1.5"/>')
        out.append(f'<text x="{pl - 16}" y="{yy + 7:.1f}" text-anchor="end" font-size="20" fill="#56637A">{esc(_fmt(s, t, ce))}</text>')
        t += passo
    passo_rot = max(1, math.ceil(n / 12))
    for i, cat in enumerate(cats):
        if i % passo_rot == 0 or i == n - 1:
            out.append(f'<text x="{x(i):.1f}" y="{H - pb + 40}" text-anchor="middle" font-size="21" fill="#22262B">{esc(C.texto_puro(cat))}</text>')
    destacar = s.get("destacar_ultimo", True)
    for j in reversed(range(len(series))):
        se = series[j]
        cor = C.SERIES[j % 4]
        larg = 6 if j == 0 else 4
        pts = " ".join(f"{'M' if i == 0 else 'L'}{x(i):.1f} {y(v):.1f}" for i, v in enumerate(se["valores"]))
        out.append(f'<path class="rota" style="--d:{j}" pathLength="1" d="{pts}" fill="none" stroke="{cor}" stroke-width="{larg}" stroke-linejoin="miter"/>')
        lado = 16 if j == 0 else 11
        for i, v in enumerate(se["valores"]):
            ultimo = i == n - 1
            if j == 0 and ultimo and destacar:
                out.append(f'<rect class="pto" style="--d:{i}" x="{x(i) - 12:.1f}" y="{y(v) - 12:.1f}" width="24" height="24" fill="#21C45D"/>')
            elif n <= 16:
                out.append(f'<rect class="pto" style="--d:{i}" x="{x(i) - lado / 2:.1f}" y="{y(v) - lado / 2:.1f}" width="{lado}" height="{lado}" fill="#FFFFFF" stroke="{cor}" stroke-width="4"/>')
            mostrar = (j == 0 and (n <= 8 or i in (0, n - 1))) or (j > 0 and ultimo)
            if mostrar:
                if ultimo:
                    out.append(f'<text class="pto" style="--d:{i}" x="{x(i) + 24:.1f}" y="{y(v) + 8:.1f}" font-size="22" font-weight="600" fill="#22262B">{esc(_fmt(s, v))}</text>')
                else:
                    vals = se["valores"]
                    vale = 0 < i < n - 1 and vals[i - 1] > v and vals[i + 1] > v
                    ty = y(v) + 44 if vale else y(v) - 22
                    out.append(f'<text class="pto" style="--d:{i}" x="{x(i):.1f}" y="{ty:.1f}" text-anchor="middle" font-size="22" font-weight="600" fill="#22262B">{esc(_fmt(s, v))}</text>')
    out.append("</g></svg>")
    return "".join(out)


def cores_fatias(itens: list) -> list[str]:
    if any(it.get("destaque") for it in itens):
        cinzas = [C.COR["grafite"], C.COR["cinza"], C.COR["cinza_claro"], C.COR["malha_apoio"], C.COR["borda"]]
        saida, k = [], 0
        for it in itens:
            if it.get("destaque"):
                saida.append(C.COR["azul"])
            else:
                saida.append(cinzas[k % len(cinzas)])
                k += 1
        return saida
    return [C.FATIAS[i % len(C.FATIAS)] for i in range(len(itens))]


def valores_donut(s: dict) -> list[str]:
    itens = s["itens"]
    total = sum(it["valor"] for it in itens) or 1
    if s.get("percentual", True):
        return [C.numero_br(it["valor"] / total * 100, s.get("casas", 0), "", "%") for it in itens]
    return [_fmt(s, it["valor"]) for it in itens]


def svg_donut(s: dict, fundo_hex: str) -> str:
    itens = s["itens"]
    total = sum(it["valor"] for it in itens) or 1
    cores = cores_fatias(itens)
    cx = cy = 300
    ro, ri = 290, 186
    out = [f'<svg viewBox="0 0 600 600" role="img" aria-label="{svg_txt(s.get("titulo"))}">']
    ang = -90.0
    for i, it in enumerate(itens):
        a = it["valor"] / total * 360
        a0, a1 = math.radians(ang), math.radians(ang + a)
        grande = 1 if a > 180 else 0
        if a >= 359.99:
            out.append(f'<circle class="fatia" cx="{cx}" cy="{cy}" r="{(ro + ri) / 2}" fill="none" stroke="{cores[i]}" stroke-width="{ro - ri}"/>')
        else:
            p = (f"M{cx + ro * math.cos(a0):.2f} {cy + ro * math.sin(a0):.2f} "
                 f"A{ro} {ro} 0 {grande} 1 {cx + ro * math.cos(a1):.2f} {cy + ro * math.sin(a1):.2f} "
                 f"L{cx + ri * math.cos(a1):.2f} {cy + ri * math.sin(a1):.2f} "
                 f"A{ri} {ri} 0 {grande} 0 {cx + ri * math.cos(a0):.2f} {cy + ri * math.sin(a0):.2f}Z")
            out.append(f'<path class="fatia" style="--d:{i}" d="{p}" fill="{cores[i]}" stroke="{fundo_hex}" stroke-width="6" stroke-linejoin="miter"/>')
        ang += a
    centro = s.get("centro") or {}
    if centro.get("valor"):
        out.append(f'<text x="300" y="{318 if centro.get("rotulo") else 334}" text-anchor="middle" font-family="Archivo, Arial Narrow, sans-serif" '
                   f'font-stretch="87.5%" font-weight="800" font-size="104" letter-spacing="-3" fill="#22262B">{svg_txt(centro["valor"])}</text>')
    if centro.get("rotulo"):
        for k, ln in enumerate(quebrar(centro["rotulo"], 20, 2)):
            out.append(f'<text x="300" y="{372 + k * 30}" text-anchor="middle" font-family="IBM Plex Sans, Segoe UI, sans-serif" font-size="24" fill="#56637A">{esc(ln)}</text>')
    out.append("</svg>")
    return "".join(out)


# --------------------------------------------------------------------------
# layouts
# --------------------------------------------------------------------------
def l_capa(s, ctx, n):
    arte = ('<div class="arte capa-arte" aria-hidden="true"><svg viewBox="0 0 860 1080" width="860" height="1080" style="left:0;top:0">'
            '<use href="#planta-claro" x="-290" y="0" width="1440" height="1080"/>'
            '<path class="rota" style="--d:0" pathLength="1" d="M300 1110V900L460 740H880" fill="none" stroke="#22262B" stroke-width="12"/>'
            '<path class="rota" style="--d:2" pathLength="1" d="M880 560H660L500 400V236" fill="none" stroke="#1266D3" stroke-width="12"/>'
            '<rect class="pto" style="--d:1" x="286" y="886" width="28" height="28" fill="#FFFFFF" stroke="#22262B" stroke-width="5"/>'
            '<rect class="pto" style="--d:2" x="646" y="546" width="28" height="28" fill="#FFFFFF" stroke="#1266D3" stroke-width="5"/>'
            '<rect class="pto" style="--d:6" x="480" y="196" width="40" height="40" fill="#21C45D"/>'
            '</svg></div>')
    meta = " · ".join(x for x in (s.get("data") or ctx.meta.get("data"), s.get("local")) if x)
    corpo = [f'<img class="capa-logo rv" src="{ctx.logo["claro"]}" width="300" height="74" alt="LG Mobilidade Urbana">',
             '<div class="capa-txt"><span class="tracado rv" aria-hidden="true"></span>']
    if s.get("rotulo"):
        corpo.append(f'<p class="rotulo rv" style="--d:1">{h(s["rotulo"])}</p>')
    corpo.append(f'<h1 class="display rv" style="--d:1" data-fit>{h(s["titulo"])}</h1>')
    if s.get("subtitulo"):
        corpo.append(f'<p class="sub rv" style="--d:2">{h(s["subtitulo"])}</p>')
    if meta:
        corpo.append(f'<p class="capa-meta rv" style="--d:3">{h(meta)}</p>')
    corpo.append("</div>")
    return arte + '<div class="sl-corpo">' + "".join(corpo) + "</div>"


def l_secao(s, ctx, n):
    arte = ('<div class="arte" aria-hidden="true"><svg viewBox="0 0 1920 1080" width="1920" height="1080" style="left:0;top:0">'
            '<use href="#planta-escura" x="0" y="-180" width="1920" height="1440"/>'
            '<path class="rota" pathLength="1" d="M-20 300H1180L1340 140H1940" fill="none" stroke="#2C7FED" stroke-width="12"/>'
            '<rect class="pto" x="1166" y="286" width="28" height="28" fill="#22262B" stroke="#2C7FED" stroke-width="5"/>'
            '</svg></div>')
    num = s.get("numero")
    partes = ['<div class="sl-corpo">']
    if num not in (None, ""):
        partes.append(f'<p class="secao-num rv">{esc(num)}</p>')
    partes.append('<span class="tracado rv" style="--d:1" aria-hidden="true"></span>')
    partes.append(f'<h2 class="display-2 rv" style="--d:1" data-fit>{h(s["titulo"])}</h2>')
    if s.get("descricao"):
        partes.append(f'<p class="sub rv" style="--d:2">{h(s["descricao"])}</p>')
    partes.append("</div>")
    return arte + "".join(partes)


def l_afirmacao(s, ctx, n):
    partes = ['<div class="sl-corpo"><span class="tracado rv" aria-hidden="true"></span>']
    if s.get("rotulo"):
        partes.append(f'<p class="rotulo rv">{h(s["rotulo"])}</p>')
    partes.append(f'<h2 class="display-2 rv" style="--d:1" data-fit>{h(s["titulo"])}</h2>')
    if s.get("texto"):
        partes.append(f'<p class="sub rv" style="--d:2">{h(s["texto"])}</p>')
    partes.append(fonte(s) + "</div>")
    return "".join(partes)


def l_kpis(s, ctx, n):
    itens = s["itens"]
    kv = {2: 200, 3: 168, 4: 136}.get(len(itens), 136)
    blocos = []
    for i, it in enumerate(itens):
        cls = "kpi-valor destaque" if it.get("destaque") else "kpi-valor"
        b = [f'<div class="kpi rv" style="--d:{i + 2}"><p class="{cls}" data-encolhe>{h(it.get("valor"))}</p>']
        if it.get("rotulo"):
            b.append(f'<p class="kpi-rotulo">{h(it["rotulo"])}</p>')
        if it.get("legenda"):
            b.append(f'<p class="pq">{h(it["legenda"])}</p>')
        b.append("</div>")
        blocos.append("".join(b))
    grade = (f'<div class="kpis-grade" style="grid-template-columns:repeat({len(itens)},1fr);--kv:{kv}px">'
             + "".join(blocos) + "</div>")
    return ('<div class="sl-corpo">' + cab(s) + f'<div class="sl-conteudo">{grade}</div>' + fonte(s) + "</div>")


def l_grafico(s, ctx, n, tipo):
    svg = svg_barras(s) if tipo == "barras" else svg_linha(s)
    return ('<div class="sl-corpo">' + cab(s, extra=legenda_series(s["series"]))
            + f'<div class="sl-conteudo"><div class="grafico rv" style="--d:2">{svg}</div></div>' + fonte(s) + "</div>")


def l_donut(s, ctx, n):
    fundo_hex = C.COR["fundo"]
    cores = cores_fatias(s["itens"])
    vals = valores_donut(s)
    leg = "".join(f'<li class="rv" style="--d:{i + 2}"><i style="background:{cores[i]}"></i><span>{h(it.get("rotulo"))}</span><b>{esc(vals[i])}</b></li>'
                  for i, it in enumerate(s["itens"]))
    grade = (f'<div class="donut-grade"><div class="donut-svg rv" style="--d:1">{svg_donut(s, fundo_hex)}</div>'
             f'<ul class="legenda-donut">{leg}</ul></div>')
    return '<div class="sl-corpo">' + cab(s) + f'<div class="sl-conteudo">{grade}</div>' + fonte(s) + "</div>"


RE_NUM = re.compile(r"^[\s+\-−]*(R\$\s?)?[\d.,]+\s?(%|pp|mil|mi|bi|km|min|h)?\s*$")


def eh_numero(cel) -> bool:
    if isinstance(cel, (int, float)) and not isinstance(cel, bool):
        return True
    return bool(RE_NUM.match(str(cel or "")))


def texto_celula(cel) -> str:
    if isinstance(cel, (int, float)) and not isinstance(cel, bool):
        return C.numero_br(cel)
    return "" if cel is None else str(cel)


def colunas_numericas(s: dict) -> list[bool]:
    cols = s["colunas"]
    linhas = s["linhas"]
    return [sum(eh_numero(ln[j]) for ln in linhas) > len(linhas) / 2 for j in range(len(cols))]


def l_tabela(s, ctx, n):
    nums = colunas_numericas(s)
    dest = s.get("destaque_linha")
    th = "".join(f'<th class="{"num" if nums[j] else ""}">{h(c)}</th>' for j, c in enumerate(s["colunas"]))
    trs = []
    for i, ln in enumerate(s["linhas"]):
        tds = "".join(f'<td class="{"num" if nums[j] else ""}">{h(texto_celula(c))}</td>' for j, c in enumerate(ln))
        trs.append(f'<tr class="{"destaque" if dest == i else ""}">{tds}</tr>')
    tabela = f'<div class="tabela-card rv" style="--d:2"><table><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>'
    return '<div class="sl-corpo">' + cab(s) + f'<div class="sl-conteudo">{tabela}</div>' + fonte(s) + "</div>"


def _lado(bloco: dict, classe: str, d: int, lista: str) -> str:
    itens = "".join(f"<li>{h(x)}</li>" for x in bloco.get("itens", []))
    rot = f'<p class="rotulo">{h(bloco["rotulo"])}</p>' if bloco.get("rotulo") else ""
    tit = f'<h3 class="h3">{h(bloco["titulo"])}</h3>' if bloco.get("titulo") else ""
    return f'<div class="comp-lado {classe} rv" style="--d:{d}">{rot}{tit}<ul class="lista {lista}">{itens}</ul></div>'


def l_comparativo(s, ctx, n):
    ponte = ('<div class="comp-ponte" aria-hidden="true"><svg viewBox="0 0 160 120">'
             '<path class="rota" style="--d:2" pathLength="1" d="M0 84H52L88 48H160" fill="none" stroke="#1266D3" stroke-width="8"/>'
             '</svg></div>')
    comp = ('<div class="comp">' + _lado(s["esquerda"], "comp-a", 2, "") + ponte
            + _lado(s["direita"], "comp-b", 3, "azul") + "</div>")
    return '<div class="sl-corpo">' + cab(s) + f'<div class="sl-conteudo">{comp}</div>' + fonte(s) + "</div>"


def l_tempo(s, ctx, n):
    marcos = s["marcos"]
    atual = s.get("atual")
    chegada = s.get("chegada", True)
    cols = []
    for i, m in enumerate(marcos):
        cls = ""
        if chegada and i == len(marcos) - 1:
            cls = "chegada"
        elif atual == i:
            cls = "atual"
        txt = f'<p class="pq">{h(m["texto"])}</p>' if m.get("texto") else ""
        cols.append(f'<div class="tl-marco rv" style="--d:{i + 2}"><p class="tl-data">{h(m.get("data"))}</p>'
                    f'<div class="tl-pto"><i class="{cls}"></i></div><h3 class="h3">{h(m.get("titulo"))}</h3>{txt}</div>')
    grade = f'<div class="tl" style="grid-template-columns:repeat({len(marcos)},1fr)">{"".join(cols)}</div>'
    return '<div class="sl-corpo">' + cab(s) + f'<div class="sl-conteudo">{grade}</div>' + fonte(s) + "</div>"


def geometria_rede(s: dict, W: float = 1160, H: float = 1080):
    u = 74.0
    x0 = W - 112 - 12 * u
    y0 = 160.0

    def p(gx, gy):
        return x0 + gx * u, y0 + gy * u
    return p, u, x0, y0


def svg_rede(s: dict) -> str:
    p, u, x0, y0 = geometria_rede(s)
    nos = {nd["id"]: nd for nd in s["nos"]}
    out = ['<svg viewBox="0 0 1160 1080" preserveAspectRatio="xMaxYMid meet" role="img" aria-label="Diagrama: '
           + svg_txt(s.get("titulo")) + '">',
           '<use href="#planta-claro" x="-280" y="0" width="1440" height="1080"/>']
    for j, ln in enumerate(s["linhas"]):
        cor = C.COR_LINHA_REDE.get(ln.get("cor", ""), C.SERIES[j % 3])
        pts = C.trajeto([p(nos[i]["x"], nos[i]["y"]) for i in ln["nos"]])
        d = " ".join(f"{'M' if k == 0 else 'L'}{x:.1f} {y:.1f}" for k, (x, y) in enumerate(pts))
        out.append(f'<path class="rota" style="--d:{j}" pathLength="1" d="{d}" fill="none" stroke="{cor}" stroke-width="12" stroke-linejoin="miter"/>')
    for k, nd in enumerate(s["nos"]):
        x, y = p(nd["x"], nd["y"])
        tipo = nd.get("tipo", "parada")
        if tipo == "terminal":
            out.append(f'<rect class="pto" style="--d:{k}" x="{x - 20:.1f}" y="{y - 20:.1f}" width="40" height="40" fill="#FFFFFF" stroke="#22262B" stroke-width="6"/>')
            r = 20
        elif tipo == "chegada":
            out.append(f'<rect class="pto" style="--d:{k}" x="{x - 18:.1f}" y="{y - 18:.1f}" width="36" height="36" fill="#21C45D"/>')
            r = 18
        else:
            out.append(f'<rect class="pto" style="--d:{k}" x="{x - 12:.1f}" y="{y - 12:.1f}" width="24" height="24" fill="#FFFFFF" stroke="#22262B" stroke-width="5"/>')
            r = 12
        if nd.get("rotulo"):
            pos = nd.get("rotulo_pos", "direita")
            if pos == "esquerda":
                tx, ty, anc = x - r - 14, y + 8, "end"
            elif pos == "acima":
                tx, ty, anc = x, y - r - 16, "middle"
            elif pos == "abaixo":
                tx, ty, anc = x, y + r + 30, "middle"
            else:
                tx, ty, anc = x + r + 14, y + 8, "start"
            peso = "600" if tipo in ("terminal", "chegada") else "400"
            out.append(f'<text class="pto" style="--d:{k}" x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anc}" font-family="IBM Plex Sans, Segoe UI, sans-serif" '
                       f'font-size="22" font-weight="{peso}" fill="#22262B" stroke="#F9FAFB" stroke-width="8" paint-order="stroke" stroke-linejoin="round">{svg_txt(nd["rotulo"])}</text>')
    if s.get("escala"):
        ex, ey = x0, y0 + 8 * u + 88
        out.append(f'<path d="M{ex} {ey - 10}V{ey}H{ex + 2 * u}V{ey - 10}" fill="none" stroke="#22262B" stroke-width="3"/>')
        out.append(f'<text x="{ex + 2 * u + 16}" y="{ey + 2}" font-family="IBM Plex Sans, Segoe UI, sans-serif" font-size="20" fill="#22262B" stroke="#F9FAFB" stroke-width="6" paint-order="stroke">{svg_txt(s["escala"])}</text>')
    out.append("</svg>")
    return "".join(out)


def l_rede(s, ctx, n):
    leg = ""
    if s["linhas"]:
        itens = "".join(
            f'<li><i style="background:{C.COR_LINHA_REDE.get(ln.get("cor", ""), C.SERIES[j % 3])}"></i>{h(ln.get("nome"))}</li>'
            for j, ln in enumerate(s["linhas"]))
        leg = f'<ul class="legenda-rede rv" style="--d:3">{itens}</ul>'
    diag = f'<div class="rede-diagrama rv" style="--d:1">{svg_rede(s)}</div>'
    return (diag + '<div class="sl-corpo">' + cab(s, subtitulo_campo="texto", extra=leg) + fonte(s) + "</div>")


def l_citacao(s, ctx, n):
    txt = s["texto"].strip()
    if not txt.startswith(("“", '"')):
        txt = f"“{txt}”"
    partes = ['<div class="sl-corpo"><span class="tracado rv" aria-hidden="true"></span>',
              f'<blockquote class="cit rv" style="--d:1" data-fit>{h(txt)}</blockquote>',
              f'<p class="cit-autor rv" style="--d:2">{h(s["autor"])}</p>']
    extra = " · ".join(x for x in (s.get("cargo"), s.get("fonte")) if x)
    if extra:
        partes.append(f'<p class="pq rv" style="--d:3">{h(extra)}</p>')
    partes.append("</div>")
    return "".join(partes)


def l_pilares(s, ctx, n):
    itens = "".join(
        f'<li class="rv" style="--d:{i + 2}"><i class="marca" aria-hidden="true"></i><div><h3 class="h3">{h(it.get("titulo"))}</h3>'
        + (f'<p class="pq">{h(it["texto"])}</p>' if it.get("texto") else "") + "</div></li>"
        for i, it in enumerate(s["itens"]))
    grade = (f'<div class="pilares-grade"><div>{cab(s, subtitulo_campo="texto")}</div>'
             f'<ol class="pilares">{itens}</ol></div>')
    return f'<div class="sl-corpo"><div class="sl-conteudo" style="margin-top:0">{grade}</div>{fonte(s)}</div>'


def geometria_processo(n: int):
    """Escada a 45°: cada etapa sobe 48 px. Coordenadas em px dentro da área de conteúdo."""
    largura = 1696.0
    cw = largura / n
    passo = 48.0
    topo = 88.0
    niveis = [topo + (n - 1 - i) * passo for i in range(n)]
    pontos = [(-112.0, niveis[0])]
    for i in range(n):
        fim_plano = (i + 1) * cw - passo - 24
        if i < n - 1:
            pontos.append((fim_plano, niveis[i]))
            pontos.append((fim_plano + passo, niveis[i + 1]))
        else:
            pontos.append((largura + 112.0, niveis[i]))
    marcos = [(i * cw, niveis[i]) for i in range(n)]
    return cw, niveis, pontos, marcos


def l_processo(s, ctx, n):
    etapas = s["etapas"]
    k = len(etapas)
    cw, niveis, pontos, marcos = geometria_processo(k)
    d = " ".join(f"{'M' if i == 0 else 'L'}{x + 112:.1f} {y:.1f}" for i, (x, y) in enumerate(pontos))
    svg = [f'<svg viewBox="0 0 1920 480" aria-hidden="true"><path class="rota" pathLength="1" d="{d}" fill="none" stroke="#22262B" stroke-width="6" stroke-linejoin="miter"/>']
    for i, (mx, my) in enumerate(marcos):
        if i == k - 1:
            svg.append(f'<rect class="pto" style="--d:{i}" x="{mx + 112:.1f}" y="{my - 18:.1f}" width="36" height="36" fill="#21C45D"/>')
        else:
            svg.append(f'<rect class="pto" style="--d:{i}" x="{mx + 112:.1f}" y="{my - 14:.1f}" width="28" height="28" fill="#FFFFFF" stroke="#22262B" stroke-width="5"/>')
    svg.append("</svg>")
    blocos = []
    for i, et in enumerate(etapas):
        mx, my = marcos[i]
        txt = f'<p class="pq">{h(et["texto"])}</p>' if et.get("texto") else ""
        blocos.append(f'<div class="proc-etapa rv" style="--d:{i + 2};left:{mx:.0f}px;top:{my - 96:.0f}px;width:{cw - 48:.0f}px">'
                      f'<p class="n">{i + 1}</p></div>'
                      f'<div class="proc-txt rv" style="--d:{i + 2};left:{mx:.0f}px;top:{my + 40:.0f}px;width:{cw - 56:.0f}px">'
                      f'<h3 class="h3">{h(et.get("titulo"))}</h3>{txt}</div>')
    proc = '<div class="proc">' + "".join(svg) + "".join(blocos) + "</div>"
    return '<div class="sl-corpo">' + cab(s) + f'<div class="sl-conteudo">{proc}</div>' + fonte(s) + "</div>"


def l_topicos(s, ctx, n):
    itens = "".join(f'<li class="rv" style="--d:{i + 2}">{h(x)}</li>' for i, x in enumerate(s["itens"]))
    nota = s.get("nota")
    corpo = f'<ul class="lista-g">{itens}</ul>'
    if nota:
        rot = f'<p class="rotulo">{h(nota["rotulo"])}</p>' if nota.get("rotulo") else ""
        corpo += f'<aside class="nota rv" style="--d:3">{rot}<p class="corpo">{h(nota.get("texto"))}</p></aside>'
    grade = f'<div class="topicos-grade{" com-nota" if nota else ""}">{corpo}</div>'
    return '<div class="sl-corpo">' + cab(s) + f'<div class="sl-conteudo">{grade}</div>' + fonte(s) + "</div>"


def l_encerramento(s, ctx, n):
    fundo = s.get("fundo", "azul")
    traco = "#FFFFFF" if fundo == "azul" else "#2C7FED"
    arte = ('<div class="arte" aria-hidden="true"><svg viewBox="0 0 1920 1080" width="1920" height="1080" style="left:0;top:0">'
            f'<g fill="none" stroke="{traco}" stroke-opacity=".14" stroke-width="12">'
            '<path class="rota" pathLength="1" d="M-20 150H900L1000 50H1940"/>'
            '<path class="rota" style="--d:1" pathLength="1" d="M1720 1100V700L1820 600H1940"/>'
            '<path class="rota" style="--d:2" pathLength="1" d="M1940 340H1560L1460 440V1100"/></g>'
            f'<g fill="none" stroke="{traco}" stroke-width="3" stroke-opacity=".5">'
            '<rect class="pto" x="890" y="140" width="20" height="20"/><rect class="pto" x="1710" y="690" width="20" height="20"/>'
            '<rect class="pto" x="1550" y="330" width="20" height="20"/></g></svg></div>')
    partes = ['<div class="sl-corpo">', f'<img class="capa-logo rv" src="{ctx.logo[fundo]}" width="300" height="74" alt="LG Mobilidade Urbana">',
              '<div class="capa-txt" style="max-width:1220px">']
    if s.get("rotulo"):
        partes.append(f'<p class="rotulo rv">{h(s["rotulo"])}</p>')
    partes.append(f'<h2 class="display-2 rv" style="--d:1" data-fit>{h(s["titulo"])}</h2>')
    if s.get("texto"):
        partes.append(f'<p class="sub rv" style="--d:2">{h(s["texto"])}</p>')
    if s.get("proximo_passo"):
        partes.append(f'<p class="prox rv" style="--d:3">{h(s["proximo_passo"])}</p>')
    if s.get("contato"):
        itens = "".join(f"<li>{h(c)}</li>" for c in s["contato"])
        partes.append(f'<ul class="contato rv" style="--d:4">{itens}</ul>')
    partes.append("</div></div>")
    return arte + "".join(partes)


RENDER = {
    "capa": l_capa, "secao": l_secao, "afirmacao": l_afirmacao, "kpis": l_kpis,
    "grafico-barras": lambda s, c, n: l_grafico(s, c, n, "barras"),
    "grafico-linha": lambda s, c, n: l_grafico(s, c, n, "linha"),
    "grafico-donut": l_donut, "tabela": l_tabela, "comparativo": l_comparativo,
    "linha-do-tempo": l_tempo, "rede": l_rede, "citacao": l_citacao, "pilares": l_pilares,
    "processo": l_processo, "topicos": l_topicos, "encerramento": l_encerramento,
}
SEM_RODAPE = {"capa", "encerramento"}


def render(deck: dict) -> str:
    ctx = Ctx(deck)
    meta = ctx.meta
    css = (CSS.replace("__ARCHIVO__", b64(C.FONTES_WOFF2 / "archivo-var.woff2"))
              .replace("__PLEXSB__", b64(C.FONTES_WOFF2 / "IBMPlexSans-SemiBold-Latin1.woff2"))
              .replace("__PLEX__", b64(C.FONTES_WOFF2 / "IBMPlexSans-Regular-Latin1.woff2"))
              .replace("__MONO__", b64(C.FONTES_WOFF2 / "IBMPlexMono-Regular-Latin1.woff2")))
    slides_html = []
    for n, s in enumerate(deck["slides"], 1):
        lay = s["layout"]
        fundo = s.get("fundo") or C.LAYOUTS[lay]["fundo"]
        miolo = RENDER[lay](s, ctx, n)
        rod = "" if lay in SEM_RODAPE else rodape(s, n, ctx)
        notas = f'<template class="nt"><p>{h(s["notas"])}</p></template>' if s.get("notas") else ""
        titulo = C.texto_puro(s.get("titulo") or s.get("texto") or lay)
        slides_html.append(f'<section class="slide f-{fundo} l-{lay}" data-layout="{lay}" aria-roledescription="slide" '
                           f'aria-label="{n} de {ctx.total}: {esc(titulo)}">{miolo}{rod}{notas}</section>')
    favicon = "data:image/svg+xml;base64," + b64(C.LOGOS / "lg-simbolo.svg")
    titulo_doc = C.texto_puro(meta.get("titulo") or "Apresentação LG Mobilidade Urbana")
    controles = ('<div class="progresso" aria-hidden="true"><span></span></div>'
                 '<nav class="controles" aria-label="Navegação dos slides">'
                 '<button id="b-ant" type="button" aria-label="Slide anterior"><svg viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7"/></svg></button>'
                 '<span class="contador" id="contador" aria-live="polite">1</span>'
                 '<button id="b-prox" type="button" aria-label="Próximo slide"><svg viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg></button>'
                 '<button id="b-tela" type="button" aria-label="Tela cheia (tecla F)"><svg viewBox="0 0 24 24"><path d="M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5"/></svg></button>'
                 '</nav><aside class="notas" id="notas" aria-label="Notas do apresentador"></aside>')
    return ("<!doctype html>\n<html lang=\"pt-BR\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
            f"<title>{esc(titulo_doc)}</title>\n"
            "<meta name=\"generator\" content=\"apresentacao-lg\">\n"
            f"<link rel=\"icon\" href=\"{favicon}\">\n"
            f"<style>{css}</style>\n</head>\n<body>\n{simbolos()}\n"
            f"<main class=\"palco\" id=\"palco\">{''.join(slides_html)}</main>\n{controles}\n"
            f"<script>{JS}</script>\n</body>\n</html>\n")


def main(argv=None) -> int:
    C.utf8_console()
    ap = argparse.ArgumentParser(description="Gera o HTML da apresentação LG a partir do deck.json.")
    ap.add_argument("deck", type=Path)
    ap.add_argument("-o", "--saida", type=Path)
    a = ap.parse_args(argv)
    deck = C.ler_deck(a.deck)
    erros, avisos = C.validar(deck)
    for av in avisos:
        print("AVISO:", av)
    if erros:
        for e in erros:
            print("ERRO:", e)
        return 2
    saida = a.saida or a.deck.with_suffix(".html")
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(render(deck), encoding="utf-8")
    print(f"HTML: {saida.resolve()} ({saida.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
