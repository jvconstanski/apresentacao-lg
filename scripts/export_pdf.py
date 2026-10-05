"""HTML da apresentação LG → PDF 16:9, um slide por página, sem transições.

Uso:
    python export_pdf.py apresentacao.html [-o saida.pdf] [--previas pasta]

Motor, nesta ordem: Chromium do Playwright, Chrome ou Edge pelo Playwright e, por
último, o Chrome ou o Edge instalado rodando em modo headless. Com o Playwright o
script também confere estouro de texto (slide por slide) e, se pedido, grava uma
prévia PNG de cada slide para conferência visual.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lg_comum as C  # noqa: E402


def _navegadores_instalados() -> list[str]:
    candidatos = []
    for nome in ("chrome", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "msedge", "microsoft-edge"):
        achado = shutil.which(nome)
        if achado:
            candidatos.append(achado)
    raizes = [os.environ.get(v) for v in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA")]
    for raiz in filter(None, raizes):
        for rel in ("Google/Chrome/Application/chrome.exe", "Microsoft/Edge/Application/msedge.exe",
                    "Chromium/Application/chrome.exe"):
            p = Path(raiz) / rel
            if p.exists():
                candidatos.append(str(p))
    for p in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
              "/Applications/Chromium.app/Contents/MacOS/Chromium"):
        if Path(p).exists():
            candidatos.append(p)
    vistos, saida = set(), []
    for c in candidatos:
        if c not in vistos:
            vistos.add(c)
            saida.append(c)
    return saida


def _com_playwright(html: Path, pdf: Path, previas: Path | None) -> dict:
    from playwright.sync_api import sync_playwright  # import tardio: dependência opcional

    with sync_playwright() as p:
        navegador, motor, ultimo_erro = None, "", None
        for canal in (None, "chrome", "msedge"):
            try:
                navegador = p.chromium.launch(channel=canal) if canal else p.chromium.launch()
                motor = f"playwright-{canal or 'chromium'}"
                break
            except Exception as e:  # navegador ausente: tenta o próximo
                ultimo_erro = e
        if navegador is None:
            raise RuntimeError(f"nenhum Chromium disponível pelo Playwright ({ultimo_erro})")
        pagina = navegador.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        pagina.goto(html.resolve().as_uri())
        pagina.wait_for_function("window.__LG_PRONTO === true", timeout=30000)
        estouro = pagina.evaluate("window.__LG_ESTOURO || []")
        pagina.emulate_media(media="print", reduced_motion="reduce")
        pagina.wait_for_timeout(150)
        geometria = pagina.evaluate("window.__LG_GEOMETRIA ? window.__LG_GEOMETRIA() : []")
        total = pagina.locator("section.slide").count()
        pagina.pdf(path=str(pdf), width="1920px", height="1080px", print_background=True,
                   prefer_css_page_size=True, margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        gravadas = []
        if previas:
            previas.mkdir(parents=True, exist_ok=True)
            for i in range(total):
                destino = previas / f"slide-{i + 1:02d}.png"
                pagina.locator("section.slide").nth(i).screenshot(path=str(destino))
                gravadas.append(str(destino))
        navegador.close()
    return {"motor": motor, "slides": total, "estouro": estouro, "geometria": geometria, "previas": gravadas}


def _com_navegador(html: Path, pdf: Path) -> dict:
    for exe in _navegadores_instalados():
        with tempfile.TemporaryDirectory() as perfil:
            cmd = [exe, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                   f"--user-data-dir={perfil}", "--no-pdf-header-footer", "--print-to-pdf-no-header",
                   "--virtual-time-budget=10000", "--run-all-compositor-stages-before-draw",
                   f"--print-to-pdf={pdf.resolve()}", html.resolve().as_uri()]
            try:
                subprocess.run(cmd, check=True, capture_output=True, timeout=180)
            except (subprocess.SubprocessError, OSError):
                continue
        if pdf.exists() and pdf.stat().st_size > 0:
            return {"motor": f"headless:{Path(exe).name}", "slides": None, "estouro": None,
                    "geometria": None, "previas": []}
    raise RuntimeError("não achei Chrome, Edge nem Chromium instalado")


def exportar(html: Path, pdf: Path, previas: Path | None = None) -> dict:
    html, pdf = Path(html), Path(pdf)
    pdf.parent.mkdir(parents=True, exist_ok=True)
    erros = []
    try:
        return _com_playwright(html, pdf, previas)
    except ImportError:
        erros.append("Playwright não instalado (pip install playwright && python -m playwright install chromium)")
    except Exception as e:  # segue para o navegador instalado
        erros.append(f"Playwright falhou: {e}")
    try:
        r = _com_navegador(html, pdf)
        r["avisos"] = erros + ["PDF gerado sem a conferência de estouro de texto (só roda com Playwright)."]
        return r
    except Exception as e:
        erros.append(str(e))
    raise RuntimeError("; ".join(erros))


def contar_paginas(pdf: Path) -> int:
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(pdf)).pages)
    except ImportError:
        import re
        dados = Path(pdf).read_bytes()
        return len(re.findall(rb"/Type\s*/Page(?![s\w])", dados))


def main(argv=None) -> int:
    C.utf8_console()
    ap = argparse.ArgumentParser(description="Exporta o HTML da apresentação LG para PDF 16:9.")
    ap.add_argument("html", type=Path)
    ap.add_argument("-o", "--saida", type=Path)
    ap.add_argument("--previas", type=Path, help="pasta para gravar um PNG por slide")
    a = ap.parse_args(argv)
    pdf = a.saida or a.html.with_suffix(".pdf")
    r = exportar(a.html, pdf, a.previas)
    print(f"PDF: {pdf.resolve()} ({pdf.stat().st_size // 1024} KB, {contar_paginas(pdf)} páginas, motor {r['motor']})")
    for av in r.get("avisos", []):
        print("AVISO:", av)
    problemas = (r.get("estouro") or []) + (r.get("geometria") or [])
    for pb in problemas:
        print("ESTOURO:", json.dumps(pb, ensure_ascii=False))
    return 3 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
