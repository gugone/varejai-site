"""Tira as fotos da prévia (computador e celular) das páginas que mudaram, com o site servido em `--base`.

Uso: python ferramentas/previa.py --base http://127.0.0.1:8765 --saida previa/ index.html pricing/index.html ...
Precisa do Playwright (`pip install playwright && playwright install chromium`); `--chrome` usa o Chrome instalado.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

TAMANHOS = {"computador": (1280, 900), "celular": (390, 844)}


def nome(pagina: str) -> str:
    pasta = pagina.removesuffix("index.html").strip("/")
    return pasta or "home"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--chrome", help="caminho do Chrome instalado (sem baixar o Chromium do Playwright)")
    ap.add_argument("paginas", nargs="+")
    a = ap.parse_args()
    a.saida.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=a.chrome) if a.chrome else pw.chromium.launch()
        for pagina in a.paginas:
            if not pagina.endswith("index.html"):
                continue
            caminho = "/" + pagina.removesuffix("index.html")
            for tam, (w, h) in TAMANHOS.items():
                aba = nav.new_page(viewport={"width": w, "height": h})
                aba.goto(a.base.rstrip("/") + caminho, wait_until="networkidle")
                # o menu fixo e o botão flutuante não entram no meio da foto
                aba.add_style_tag(content=".site-header{position:static!important}.wa-float{display:none!important}")
                if caminho == "/":
                    aba.locator("#produtos").scroll_into_view_if_needed()
                    aba.locator("#produtos").screenshot(path=str(a.saida / f"home-produtos-{tam}.png"))
                else:
                    aba.screenshot(path=str(a.saida / f"{nome(pagina)}-{tam}.png"), full_page=tam == "computador")
                aba.close()
        nav.close()


if __name__ == "__main__":
    main()
