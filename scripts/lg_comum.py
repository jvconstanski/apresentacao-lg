"""Base comum dos geradores da skill apresentacao-lg.

Tokens da marca LG, leitura e validação do deck.json, formatação de número em
pt-BR, marcação inline (**destaque** e [DADO: ...]) e roteamento a 0°, 45° e 90°
para o diagrama de rede. Todo caminho é relativo a este arquivo (pathlib).
"""
from __future__ import annotations

import datetime as _dt
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "assets"
FONTES_TTF = ASSETS / "fonts" / "ttf"
FONTES_WOFF2 = ASSETS / "fonts" / "woff2"
LOGOS = ASSETS / "logo"
GRAFISMO = ASSETS / "grafismo"

LARGURA, ALTURA = 1920, 1080  # tela de desenho de todo slide (16:9)


def utf8_console() -> None:
    """Força UTF-8 no stdout e no stderr (console cp1252 do Windows)."""
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


# --------------------------------------------------------------------------
# Tokens (brandbook LG v1 e site v2). Nenhuma cor fora desta lista.
# --------------------------------------------------------------------------
COR = {
    "azul": "#1266D3",
    "azul_hover": "#105BBC",
    "azul_claro": "#2C7FED",   # azul sobre fundo escuro
    "verde": "#21C45D",        # só ponto de chegada e botão principal
    "grafite": "#22262B",
    "grafite_2": "#2C3138",
    "grafite_3": "#3A414A",
    "cinza": "#6F7D90",        # traço, borda e decoração
    "cinza_texto": "#56637A",  # texto de apoio sobre claro (AA)
    "cinza_claro": "#AEB8C5",  # texto de apoio sobre grafite
    "fundo": "#F9FAFB",
    "apoio": "#EAEDF0",
    "borda": "#E1E7EF",        # malha e linha de cota no claro
    "malha_apoio": "#DCE3EC",
    "malha_escura": "#30363E",
    "branco": "#FFFFFF",
}
SERIES = [COR["azul"], COR["grafite"], COR["cinza"], COR["cinza_claro"]]
FATIAS = [COR["azul"], COR["grafite"], COR["cinza"], COR["cinza_claro"], COR["malha_apoio"], COR["borda"]]
EASE = "cubic-bezier(.22,.61,.36,1)"

FUNDOS = {"claro", "apoio", "escuro", "azul"}

# --------------------------------------------------------------------------
# Catálogo de layouts: campos obrigatórios, limites e fundo padrão.
# Mantido em sincronia com references/layouts.md e references/schema.md.
# --------------------------------------------------------------------------
LAYOUTS: dict[str, dict] = {
    "capa": {"obrig": ["titulo"], "fundo": "claro", "fundos": {"claro"},
             "palavras": {"titulo": 12, "subtitulo": 18}},
    "secao": {"obrig": ["titulo"], "fundo": "escuro", "fundos": {"escuro"},
              "palavras": {"titulo": 8, "descricao": 25}},
    "afirmacao": {"obrig": ["titulo"], "fundo": "claro", "fundos": {"claro", "apoio", "escuro"},
                  "palavras": {"titulo": 16, "texto": 35}},
    "kpis": {"obrig": ["titulo", "itens"], "fundo": "claro", "fundos": {"claro", "apoio"},
             "itens": (2, 4), "palavras": {"titulo": 14}},
    "grafico-barras": {"obrig": ["titulo", "categorias", "series"], "fundo": "claro", "fundos": {"claro"},
                       "palavras": {"titulo": 14, "subtitulo": 20}},
    "grafico-linha": {"obrig": ["titulo", "categorias", "series"], "fundo": "claro", "fundos": {"claro"},
                      "palavras": {"titulo": 14, "subtitulo": 20}},
    "grafico-donut": {"obrig": ["titulo", "itens"], "fundo": "claro", "fundos": {"claro"},
                      "itens": (2, 6), "palavras": {"titulo": 14}},
    "tabela": {"obrig": ["titulo", "colunas", "linhas"], "fundo": "claro", "fundos": {"claro", "apoio"},
               "palavras": {"titulo": 14}},
    "comparativo": {"obrig": ["titulo", "esquerda", "direita"], "fundo": "claro", "fundos": {"claro"},
                    "palavras": {"titulo": 14}},
    "linha-do-tempo": {"obrig": ["titulo", "marcos"], "fundo": "apoio", "fundos": {"apoio", "claro"},
                       "itens": (3, 6), "palavras": {"titulo": 14}},
    "rede": {"obrig": ["titulo", "nos", "linhas"], "fundo": "claro", "fundos": {"claro"},
             "palavras": {"titulo": 12, "texto": 40}},
    "citacao": {"obrig": ["texto", "autor", "fonte"], "fundo": "escuro", "fundos": {"escuro", "claro"},
                "palavras": {"texto": 40}},
    "pilares": {"obrig": ["titulo", "itens"], "fundo": "claro", "fundos": {"claro", "apoio"},
                "itens": (3, 4), "palavras": {"titulo": 12, "texto": 30}},
    "processo": {"obrig": ["titulo", "etapas"], "fundo": "apoio", "fundos": {"apoio", "claro"},
                 "itens": (3, 5), "palavras": {"titulo": 14}},
    "topicos": {"obrig": ["titulo", "itens"], "fundo": "claro", "fundos": {"claro", "apoio"},
                "itens": (2, 6), "palavras": {"titulo": 14}},
    "encerramento": {"obrig": ["titulo"], "fundo": "azul", "fundos": {"azul", "escuro"},
                     "palavras": {"titulo": 12, "texto": 30}},
}
LAYOUTS_SEM_TITULO_AFIRMACAO = {"capa", "secao", "citacao", "encerramento"}

CLICHES = [
    "revolucionári", "inovador", "inovadora", "no mundo de hoje", "soluções completas",
    "sinergia", "disruptiv", "game changer", "potencializ", "alavanc", "transformador",
    "indispensável", "imperdível", "de ponta", "máxima eficiência", "players", "jornada de",
    "next level", "sucesso garantido", "excelência",
]
RE_EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿️]")
RE_DADO = re.compile(r"\[DADO:[^\]]*\]")
RE_DESTAQUE = re.compile(r"\*\*(.+?)\*\*")


# --------------------------------------------------------------------------
# Leitura
# --------------------------------------------------------------------------
def ler_deck(caminho: Path) -> dict:
    caminho = Path(caminho)
    texto = caminho.read_text(encoding="utf-8-sig")
    deck = json.loads(texto)
    if not isinstance(deck, dict) or not isinstance(deck.get("slides"), list):
        raise ValueError("deck.json precisa de um objeto com a lista \"slides\".")
    deck.setdefault("meta", {})
    for s in deck["slides"]:
        if isinstance(s, dict):
            lay = LAYOUTS.get(s.get("layout", ""))
            if lay and not s.get("fundo"):
                s["fundo"] = lay["fundo"]
    return deck


def slug(texto: str, maximo: int = 60) -> str:
    base = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode("ascii")
    base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower()
    base = base[:maximo].rstrip("-")
    return base or "apresentacao"


def data_deck(deck: dict) -> str:
    bruto = str(deck.get("meta", {}).get("data_arquivo") or "")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", bruto):
        return bruto
    return _dt.date.today().isoformat()


def nome_base(deck: dict) -> str:
    meta = deck.get("meta", {})
    return slug(meta.get("tema") or meta.get("titulo") or "apresentacao")


# --------------------------------------------------------------------------
# Texto
# --------------------------------------------------------------------------
def segmentos(texto: str) -> list[tuple[str, str]]:
    """Quebra o texto em (trecho, tipo) com tipo em normal | destaque | dado | codigo."""
    texto = "" if texto is None else str(texto)
    saida: list[tuple[str, str]] = []
    pos = 0
    padrao = re.compile(r"\*\*(.+?)\*\*|(\[DADO:[^\]]*\])|`([^`]+)`")
    for m in padrao.finditer(texto):
        if m.start() > pos:
            saida.append((texto[pos:m.start()], "normal"))
        if m.group(1) is not None:
            interno = m.group(1)
            # [DADO] dentro de destaque continua sendo marcação de dado
            for trecho, tipo in segmentos(interno):
                saida.append((trecho, "dado" if tipo == "dado" else "destaque"))
        elif m.group(2) is not None:
            saida.append((m.group(2), "dado"))
        else:
            saida.append((m.group(3), "codigo"))
        pos = m.end()
    if pos < len(texto):
        saida.append((texto[pos:], "normal"))
    return saida


def texto_puro(texto) -> str:
    return "".join(t for t, _ in segmentos("" if texto is None else str(texto)))


def contar_palavras(texto) -> int:
    puro = RE_DADO.sub("", texto_puro(texto))
    return len([p for p in re.split(r"\s+", puro.strip()) if p])


def numero_br(valor, casas: int | None = None, prefixo: str = "", sufixo: str = "") -> str:
    if valor is None:
        return "[DADO: validar]"
    try:
        v = float(valor)
    except (TypeError, ValueError):
        return str(valor)
    if casas is None:
        casas = 0 if float(v).is_integer() else (1 if abs(v) >= 10 else 2)
    bruto = f"{abs(v):,.{casas}f}"
    bruto = bruto.replace(",", "§").replace(".", ",").replace("§", ".")
    sinal = "−" if v < 0 else ""
    return f"{sinal}{prefixo}{bruto}{sufixo}"


def formato_excel(casas: int | None, prefixo: str = "", sufixo: str = "") -> str:
    casas = 0 if casas is None else casas
    corpo = "#,##0" + ("." + "0" * casas if casas else "")
    pre = f'"{prefixo}"' if prefixo else ""
    suf = f'"{sufixo}"' if sufixo else ""
    return f"{pre}{corpo}{suf}"


def indices_destaque(valor) -> set[int]:
    """Aceita um índice ou uma lista de índices (base 0)."""
    if valor is None:
        return set()
    if isinstance(valor, list):
        return {int(v) for v in valor if isinstance(v, (int, float))}
    return {int(valor)} if isinstance(valor, (int, float)) else set()


def escala_bonita(minimo: float, maximo: float, alvo: int = 5) -> tuple[float, float, float]:
    """Retorna (inicio, fim, passo) com passos 1, 2, 2,5 ou 5 × 10^n."""
    if maximo == minimo:
        maximo = minimo + 1
    bruto = (maximo - minimo) / max(alvo, 1)
    exp = math.floor(math.log10(bruto))
    frac = bruto / 10 ** exp
    for c in (1, 2, 2.5, 5, 10):
        if frac <= c:
            passo = c * 10 ** exp
            break
    inicio = math.floor(minimo / passo) * passo
    fim = math.ceil(maximo / passo) * passo
    return inicio, fim, passo


# --------------------------------------------------------------------------
# Rede: trajeto só a 0°, 45° e 90°
# --------------------------------------------------------------------------
def trajeto(pontos: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Liga os pontos em sequência: primeiro a diagonal de 45°, depois a reta."""
    if not pontos:
        return []
    saida = [pontos[0]]
    for (x0, y0), (x1, y1) in zip(pontos, pontos[1:]):
        dx, dy = x1 - x0, y1 - y0
        d = min(abs(dx), abs(dy))
        if d > 1e-9 and abs(abs(dx) - abs(dy)) > 1e-9:
            meio = (x0 + math.copysign(d, dx), y0 + math.copysign(d, dy))
            saida.append(meio)
        saida.append((x1, y1))
    return saida


COR_LINHA_REDE = {"azul": COR["azul"], "grafite": COR["grafite"], "cinza": COR["cinza"],
                  "azul-claro": COR["azul_claro"]}


# --------------------------------------------------------------------------
# Validação
# --------------------------------------------------------------------------
def _textos(obj, caminho=""):
    if isinstance(obj, str):
        yield caminho, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("layout", "fundo", "id", "cor", "tipo", "orientacao", "rotulo_pos"):
                continue
            yield from _textos(v, f"{caminho}.{k}" if caminho else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _textos(v, f"{caminho}[{i}]")


def _num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def validar(deck: dict) -> tuple[list[str], list[str]]:
    erros: list[str] = []
    avisos: list[str] = []
    slides = deck.get("slides", [])
    if not slides:
        erros.append("O deck não tem slides.")
    for i, s in enumerate(slides, 1):
        rot = f"slide {i:02d}"
        if not isinstance(s, dict):
            erros.append(f"{rot}: precisa ser um objeto.")
            continue
        nome = s.get("layout")
        spec = LAYOUTS.get(nome)
        if not spec:
            erros.append(f"{rot}: layout \"{nome}\" não existe. Use um de: {', '.join(LAYOUTS)}.")
            continue
        rot = f"slide {i:02d} ({nome})"
        for campo in spec["obrig"]:
            if s.get(campo) in (None, "", [], {}):
                erros.append(f"{rot}: falta o campo obrigatório \"{campo}\".")
        if s.get("fundo") and s["fundo"] not in spec["fundos"]:
            avisos.append(f"{rot}: fundo \"{s['fundo']}\" não previsto; usando \"{spec['fundo']}\".")
            s["fundo"] = spec["fundo"]
        faixa = spec.get("itens")
        lista = s.get("itens") or s.get("marcos") or s.get("etapas")
        if faixa and isinstance(lista, list) and not (faixa[0] <= len(lista) <= faixa[1]):
            erros.append(f"{rot}: use de {faixa[0]} a {faixa[1]} itens (veio {len(lista)}).")
        for campo, limite in spec.get("palavras", {}).items():
            if s.get(campo) and contar_palavras(s[campo]) > limite:
                avisos.append(f"{rot}: \"{campo}\" tem {contar_palavras(s[campo])} palavras (limite {limite}).")
        if nome not in LAYOUTS_SEM_TITULO_AFIRMACAO and s.get("titulo") and contar_palavras(s["titulo"]) <= 3:
            avisos.append(f"{rot}: o título parece assunto, não conclusão. Escreva a afirmação que o slide prova.")
        # gráficos
        if nome in ("grafico-barras", "grafico-linha"):
            cats = s.get("categorias") or []
            series = s.get("series") or []
            if not isinstance(series, list) or not series:
                erros.append(f"{rot}: \"series\" precisa ser uma lista com ao menos uma série.")
            else:
                if len(series) > 4:
                    erros.append(f"{rot}: no máximo 4 séries.")
                for j, se in enumerate(series):
                    vals = se.get("valores") if isinstance(se, dict) else None
                    if not isinstance(vals, list) or len(vals) != len(cats):
                        erros.append(f"{rot}: série {j + 1} precisa de {len(cats)} valores (um por categoria).")
                    elif not all(_num(v) for v in vals):
                        erros.append(f"{rot}: série {j + 1} tem valor que não é número. Dado ausente: tire a categoria e marque [DADO: validar] na fonte.")
            limite = 12 if nome == "grafico-barras" else 16
            if len(cats) > limite:
                erros.append(f"{rot}: no máximo {limite} categorias.")
        if nome == "grafico-donut":
            for j, it in enumerate(s.get("itens") or []):
                if not _num(it.get("valor")) or it.get("valor") < 0:
                    erros.append(f"{rot}: item {j + 1} precisa de \"valor\" numérico positivo.")
        if nome == "tabela":
            cols = s.get("colunas") or []
            if not (2 <= len(cols) <= 6):
                erros.append(f"{rot}: use de 2 a 6 colunas.")
            linhas = s.get("linhas") or []
            if len(linhas) > 8:
                erros.append(f"{rot}: no máximo 8 linhas. Divida em dois slides ou resuma.")
            for j, ln in enumerate(linhas):
                if not isinstance(ln, list) or len(ln) != len(cols):
                    erros.append(f"{rot}: linha {j + 1} precisa de {len(cols)} células.")
        if nome == "comparativo":
            for lado in ("esquerda", "direita"):
                bloco = s.get(lado) or {}
                if not isinstance(bloco, dict) or not bloco.get("itens"):
                    erros.append(f"{rot}: \"{lado}\" precisa de \"itens\".")
                elif len(bloco["itens"]) > 5:
                    erros.append(f"{rot}: \"{lado}\" aceita no máximo 5 itens.")
        if nome == "rede":
            ids = {n.get("id") for n in s.get("nos") or [] if isinstance(n, dict)}
            for n in s.get("nos") or []:
                if not (_num(n.get("x")) and _num(n.get("y"))):
                    erros.append(f"{rot}: nó \"{n.get('id')}\" precisa de x e y numéricos (grade 0 a 12 por 0 a 8).")
            for ln in s.get("linhas") or []:
                faltam = [x for x in ln.get("nos", []) if x not in ids]
                if faltam:
                    erros.append(f"{rot}: a linha \"{ln.get('nome')}\" cita nós que não existem: {', '.join(map(str, faltam))}.")
                if len(ln.get("nos", [])) < 2:
                    erros.append(f"{rot}: a linha \"{ln.get('nome')}\" precisa de ao menos 2 nós.")
            if len(s.get("linhas") or []) > 5:
                erros.append(f"{rot}: no máximo 5 linhas no diagrama.")
        # copy
        for caminho, txt in _textos(s):
            baixo = txt.lower()
            if "—" in txt or "–" in txt:
                avisos.append(f"{rot}: travessão em \"{caminho}\". Troque por vírgula, ponto, dois-pontos ou parênteses.")
            for c in CLICHES:
                if c in baixo:
                    avisos.append(f"{rot}: clichê \"{c}\" em \"{caminho}\". Use o nome do serviço no lugar do adjetivo.")
            if RE_EMOJI.search(txt):
                avisos.append(f"{rot}: emoji em \"{caminho}\". A marca não usa emoji.")
    return erros, avisos


def contar_marcas_dado(deck: dict) -> int:
    total = 0
    for _, txt in _textos(deck.get("slides", [])):
        total += len(RE_DADO.findall(txt))
    return total
