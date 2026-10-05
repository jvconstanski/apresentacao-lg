"""Orquestra a apresentação LG: deck.json → HTML + PDF + PPTX, com conferência.

Uso:
    python build.py deck.json [--saida PASTA] [--formatos html,pdf,pptx] [--previas]

Grava em ./apresentacoes/{AAAA-MM-DD}-{tema-kebab}/ relativo ao diretório de
trabalho (ou em --saida). A data vem de meta.data_arquivo (AAAA-MM-DD) ou de hoje.

Códigos de saída:
    0  tudo gerado e conferido
    2  deck.json inválido (erros listados)
    3  texto estourando o slide (lista com slide e trecho)
    4  conferência falhou (arquivo vazio, contagem de slides ou páginas errada)
    5  um gerador falhou (mensagem do erro)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lg_comum as C  # noqa: E402


def main(argv=None) -> int:
    C.utf8_console()
    ap = argparse.ArgumentParser(description="Gera HTML, PDF e PPTX da apresentação LG a partir do deck.json.")
    ap.add_argument("deck", type=Path, help="arquivo deck.json")
    ap.add_argument("--saida", type=Path, default=None,
                    help="pasta base (padrão: ./apresentacoes no diretório de trabalho)")
    ap.add_argument("--formatos", default="html,pdf,pptx", help="lista separada por vírgula")
    ap.add_argument("--previas", action="store_true", help="grava um PNG por slide em previas/ (pede Playwright)")
    ap.add_argument("--permitir-estouro", action="store_true", help="não falha quando houver texto estourando")
    a = ap.parse_args(argv)

    formatos = {f.strip().lower() for f in a.formatos.split(",") if f.strip()}
    if "pdf" in formatos:
        formatos.add("html")

    try:
        deck = C.ler_deck(a.deck)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print("ERRO: não consegui ler o deck:", e)
        return 2
    erros, avisos = C.validar(deck)
    for av in avisos:
        print("AVISO:", av)
    if erros:
        for e in erros:
            print("ERRO:", e)
        print(f"\n{len(erros)} erro(s) no deck.json. Nada foi gerado.")
        return 2

    base = (a.saida or Path.cwd() / "apresentacoes").resolve()
    nome = C.nome_base(deck)
    pasta = base / f"{C.data_deck(deck)}-{nome}"
    maior = len(str(pasta / f"{nome}.pptx"))
    if os.name == "nt" and maior >= 255:
        print(f"ERRO: o caminho de saída tem {maior} caracteres e passa do limite de 260 do Windows.")
        print("Use --saida com uma pasta mais curta (por exemplo, --saida C:/apresentacoes) ou um tema mais curto.")
        return 5
    pasta.mkdir(parents=True, exist_ok=True)
    destino_deck = pasta / "deck.json"
    if a.deck.resolve() != destino_deck.resolve():
        shutil.copy2(a.deck, destino_deck)

    total = len(deck["slides"])
    relatorio = {"pasta": str(pasta), "slides": total, "arquivos": {}, "estouro": [], "avisos": list(avisos),
                 "marcas_dado": C.contar_marcas_dado(deck)}
    falhas, problemas = [], []

    html = pasta / f"{nome}.html"
    if "html" in formatos:
        try:
            import render_html
            html.write_text(render_html.render(deck), encoding="utf-8")
        except Exception as e:
            falhas.append(f"HTML: {e}")

    pdf = pasta / f"{nome}.pdf"
    if "pdf" in formatos and html.exists():
        try:
            import export_pdf
            previas = pasta / "previas" if a.previas else None
            r = export_pdf.exportar(html, pdf, previas)
            relatorio["motor_pdf"] = r["motor"]
            relatorio["estouro"] = (r.get("estouro") or []) + (r.get("geometria") or [])
            relatorio["previas"] = r.get("previas", [])
            relatorio["avisos"] += r.get("avisos", [])
            if r.get("estouro") is None:
                relatorio["avisos"].append("Estouro de texto não conferido (PDF feito sem Playwright).")
        except Exception as e:
            falhas.append(f"PDF: {e}")

    pptx = pasta / f"{nome}.pptx"
    if "pptx" in formatos:
        try:
            import render_pptx
            _, av_pptx = render_pptx.render(deck, pptx)
            relatorio["avisos"] += av_pptx
            faltam = render_pptx.fontes_instaladas()
            if faltam:
                relatorio["avisos"].append("Fontes da marca não instaladas aqui (o PPTX usa as da marca; instale os TTF de "
                                           "assets/fonts/ttf para ver como foi desenhado): " + ", ".join(faltam))
        except Exception as e:
            falhas.append(f"PPTX: {e}")

    # conferência
    for rotulo, arq in (("html", html), ("pdf", pdf), ("pptx", pptx)):
        if rotulo not in formatos:
            continue
        if not arq.exists() or arq.stat().st_size == 0:
            problemas.append(f"{rotulo.upper()} ausente ou vazio: {arq}")
            continue
        info = {"caminho": str(arq), "kb": round(arq.stat().st_size / 1024)}
        if rotulo == "pptx":
            from pptx import Presentation
            n = len(Presentation(str(arq)).slides)
            info["slides"] = n
            if n != total:
                problemas.append(f"PPTX com {n} slides, esperado {total}")
        if rotulo == "pdf":
            import export_pdf
            n = export_pdf.contar_paginas(arq)
            info["paginas"] = n
            if n != total:
                problemas.append(f"PDF com {n} páginas, esperado {total}")
        relatorio["arquivos"][rotulo] = info

    relatorio["falhas"] = falhas
    relatorio["problemas"] = problemas
    (pasta / "relatorio-build.json").write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nPasta: {pasta}")
    for rotulo, info in relatorio["arquivos"].items():
        extra = f", {info['slides']} slides" if "slides" in info else (f", {info['paginas']} páginas" if "paginas" in info else "")
        print(f"  {rotulo.upper():5} {info['caminho']} ({info['kb']} KB{extra})")
    if relatorio.get("previas"):
        print(f"  Prévias: {pasta / 'previas'} ({len(relatorio['previas'])} PNG)")
    for av in relatorio["avisos"]:
        if av not in avisos:
            print("AVISO:", av)
    if relatorio["marcas_dado"]:
        print(f"PENDENTE: {relatorio['marcas_dado']} marca(s) [DADO: ...] para validar antes de apresentar.")
    for pb in relatorio["estouro"]:
        print("ESTOURO:", json.dumps(pb, ensure_ascii=False))
    for fl in falhas:
        print("FALHA:", fl)
    for pb in problemas:
        print("CONFERÊNCIA:", pb)

    if falhas:
        return 5
    if problemas:
        return 4
    if relatorio["estouro"] and not a.permitir_estouro:
        return 3
    print("OK: apresentação gerada e conferida.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
