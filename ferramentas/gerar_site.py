"""Gera as partes do site que saem da vitrine (produtos.json do repo do ERP).

Uso: python ferramentas/gerar_site.py <caminho/produtos.json> [--resumo resumo.md]

O que muda (e só isto):
- os cartões do portfólio na home (entre <div class="portfolio-grid"> e a legenda dos selos);
- a lista "Produtos" do rodapé e a "Outros produtos" de todas as páginas;
- as páginas `pagina: "gerada"` (<id>/index.html), montadas pelo modelo abaixo;
- os produtos do sitemap.xml e do llms.txt.
As páginas `pagina: "propria"` (feitas à mão) ficam como estão, fora o rodapé e a lista de outros produtos.
Sem dependências: só a biblioteca padrão. Idempotente: rodar duas vezes não muda nada.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import urllib.parse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SITE = "https://varejai.com.br"
SELOS = {"disponivel": ("status-disponivel", "Disponível"), "piloto": ("status-piloto", "Em piloto"),
         "breve": ("status-breve", "Em breve")}
ICONES = {   # o miolo do <svg viewBox="0 0 24 24">
    "whatsapp": '<path d="M21 11.5a8.5 8.5 0 0 1-12.5 7.5L3.5 20.5l1.5-4.5A8.5 8.5 0 1 1 21 11.5z"/><path d="M8 9h1l1.2 4.5h4.6L16 10H10"/><circle cx="10.8" cy="15.6" r=".6" fill="currentColor"/><circle cx="14.2" cy="15.6" r=".6" fill="currentColor"/>',
    "erp": '<rect x="3.5" y="4" width="17" height="11" rx="2"/><path d="M7 19.5h10M12 15v4.5M7 8h4M7 11h7"/>',
    "ponto": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "achei": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/><path d="M10.5 7.5v6M7.5 10.5h6"/>',
    "compras": '<path d="M3.5 4h2l2.2 10.5h10.6L20.5 7H7"/><circle cx="9.5" cy="18.5" r="1.4"/><circle cx="17" cy="18.5" r="1.4"/>',
    "pricing": '<path d="M3.5 12.5V4.5a1 1 0 0 1 1-1h8l8 8-9 9z"/><circle cx="8" cy="8" r="1.4"/><path d="M11 14l4-4"/>',
    "recebimento": '<path d="M6 3.5h9l3 3v14H6z"/><path d="M9 11l2 2 4-4M9 16.5h6"/>',
    "reforma": '<path d="M5 20.5V8l7-4.5L19 8v12.5"/><path d="M9 20.5v-6h6v6M3.5 20.5h17"/>',
    "ofertas": '<path d="M4 9.5 15.5 4v16L4 14.5z"/><path d="M4 9.5v5M18 9a3 3 0 0 1 0 6"/>',
    "recebiveis": '<rect x="3.5" y="6" width="17" height="12" rx="2"/><path d="M3.5 10h17M7 14.5h3"/>',
    "tarefas": '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4v-.5h6V4M8.5 10l1.5 1.5L13 8.5M8.5 15.5h7"/>',
    "ifood": '<path d="M5 11h14l-1.5 9.5h-11z"/><path d="M8.5 11V8a3.5 3.5 0 0 1 7 0v3"/>',
    "crm": '<circle cx="9" cy="8.5" r="3"/><path d="M3.5 19.5a5.5 5.5 0 0 1 11 0"/><path d="M16 7.5a2.5 2.5 0 0 1 0 5M17.5 19.5a4.5 4.5 0 0 0-2-3.7"/>',
}
WA_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
          'stroke-linejoin="round" aria-hidden="true"><path d="M20.5 11.6a8.5 8.5 0 0 1-12.6 7.5L3.5 20.5l1.4-4.2A8.5 '
          '8.5 0 1 1 20.5 11.6z"/><path d="M9 9.2c.3 2.4 2.4 4.6 5 5.2l1.2-1.3-1.9-1-.8.7c-.9-.4-1.7-1.2-2.1-2.1l.7-.8-1-1.9z" '
          'fill="currentColor" stroke="none"/></svg>')
PROIBIDO = re.compile(r"f[ée]lix|\d{3}\.\d{3}\.\d{3}-\d{2}|@(?!varejai\.com\.br)\w", re.I)


def e(t: str) -> str:
    return html.escape(t, quote=True)


def carregar(caminho: Path) -> dict:
    v = json.loads(caminho.read_text(encoding="utf-8"))
    ids = set()
    for p in v["produtos"]:
        assert re.fullmatch(r"[a-z0-9-]+", p["id"]), f"id inválido: {p['id']}"
        assert p["id"] not in ids, f"id repetido: {p['id']}"
        ids.add(p["id"])
        assert p["selo"] in SELOS, f"{p['id']}: selo {p['selo']!r}"
        assert p["pagina"] in ("propria", "gerada"), f"{p['id']}: pagina {p['pagina']!r}"
        if p["pagina"] == "propria":
            assert (RAIZ / p["id"] / "index.html").exists(), f"{p['id']}: página própria não existe no site"
        assert not PROIBIDO.search(json.dumps(p, ensure_ascii=False)), f"{p['id']}: texto com dado que não vai ao site"
    return v


def selo(p: dict) -> str:
    cls, txt = SELOS[p["selo"]]
    return f'<span class="status {cls}">{txt}</span>'


def icone(p: dict) -> str:
    if p.get("icone_img"):
        return f'<img src="{e(p["icone_img"])}" alt="" class="product-icon" width="48" height="48" />'
    return ('<span class="product-icon product-icon-svg"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            f'{ICONES[p["icone"]]}</svg></span>')


def art(p: dict) -> str:
    """O artigo do nome ("o VarejAI Pricing", "a Reforma tributária")."""
    return p.get("artigo", "o")


def wa(v: dict, p: dict) -> str:
    de = {"o": "do", "a": "da"}[art(p)]
    msg = (f"Olá! Vim pelo site e quero entrar na lista de espera {de} {p['nome']}." if p["selo"] == "breve"
           else f"Olá! Vim pelo site e quero conhecer {art(p)} {p['nome']}.")
    return f"https://wa.me/{v['whatsapp']}?text={urllib.parse.quote(msg)}"


def cartao(p: dict) -> str:
    return f"""        <article class="product-card">
          <div class="product-card-top">
            {icone(p)}
            {selo(p)}
          </div>
          <h3>{e(p["nome"])}</h3>
          <p class="product-tagline">{e(p["tagline"])}</p>
          <p>{e(p["resumo"])}</p>
          <p class="product-for">Para: <span>{e(p["para"])}</span></p>
          <a class="product-link" href="/{p["id"]}">Conhecer {art(p)} {e(p["nome"])} <span aria-hidden="true">→</span></a>
        </article>
"""


def trocar(texto: str, padrao: str, novo: str, onde: str) -> str:
    r, n = re.subn(padrao, lambda _m: novo, texto, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f"não achei o trecho a trocar em {onde}: {padrao[:60]}")
    return r


def rodape(v: dict) -> str:
    links = "\n".join(f'          <a href="/{p["id"]}">{e(p["nome"])}</a>' for p in v["produtos"])
    return f'<nav class="footer-nav" aria-label="Produtos">\n{links}\n        </nav>'


def outros(v: dict, atual: str | None) -> str:
    itens = "\n".join(
        f'        <a class="mini-card" href="/{p["id"]}">{selo(p)}<b>{e(p["nome"])}</b><span>{e(p["tagline"])}</span></a>'
        for p in v["produtos"] if p["id"] != atual)
    return f'<div class="mini-grid">\n{itens}\n      </div>'


def pagina(v: dict, p: dict) -> str:
    """A página de um produto `gerada`, no mesmo desenho das feitas à mão."""
    titulo = f'{p["nome"]} | {p["tagline"]} | VarejAI'
    desc = p["resumo"]
    url = f'{SITE}/{p["id"]}'
    link_wa = wa(v, p)
    cta = "Entrar na lista de espera" if p["selo"] == "breve" else "Falar no WhatsApp"
    cls, txt = SELOS[p["selo"]]
    faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in p["faq"]]},
        ensure_ascii=False, indent=2)
    bc_ld = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "VarejAI", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": p["nome"], "item": url}]}, ensure_ascii=False, indent=2)
    problemas = "\n".join(f'        <article class="card"><span class="card-index">{i:02d}</span><h3>{e(t)}</h3>'
                          f'<p>{e(d)}</p></article>' for i, (t, d) in enumerate(p["problemas"], 1))
    passos = "\n".join(f'        <div class="step"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in p["passos"])
    feito = "\n".join(f"          <li>{e(x)}</li>" for x in p["feito_para"])
    faq = "\n".join(f"        <details><summary>{e(q)}</summary><p>{e(r)}</p></details>" for q, r in p["faq"])
    base = (RAIZ / "index.html").read_text(encoding="utf-8")
    cabecalho = re.search(r'<a class="skip-link".*?</header>', base, re.S).group(0)
    fim = re.search(r'<footer class="site-footer">.*</html>', base, re.S).group(0)
    fim = re.sub(r'<nav class="footer-nav" aria-label="Produtos">.*?</nav>', lambda _m: rodape(v), fim, count=1,
                 flags=re.S)
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<!-- gerada por ferramentas/gerar_site.py a partir da vitrine do ERP: edite a vitrine, não este arquivo -->
<title>{e(titulo)}</title>
<meta name="description" content="{e(desc)}" />
<meta name="robots" content="index, follow" />
<link rel="canonical" href="{url}" />
<meta name="theme-color" content="#0f0f14" />
<meta property="og:type" content="website" />
<meta property="og:locale" content="pt_BR" />
<meta property="og:site_name" content="VarejAI" />
<meta property="og:url" content="{url}" />
<meta property="og:title" content="{e(titulo)}" />
<meta property="og:description" content="{e(desc)}" />
<meta property="og:image" content="{SITE}/assets/og/home.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{e(titulo)}" />
<meta name="twitter:description" content="{e(desc)}" />
<meta name="twitter:image" content="{SITE}/assets/og/home.png" />
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml" />
<link rel="icon" type="image/png" href="/assets/img/retina-icon.png" sizes="any" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@600;700;800&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/assets/css/style.css" />
<script type="application/ld+json">
{bc_ld}
</script>
<script type="application/ld+json">
{faq_ld}
</script>
</head>
<body>
{cabecalho}

<main id="conteudo">

  <section class="product-hero">
    <div class="container">
      <nav class="breadcrumb" aria-label="Você está em">
        <ol><li><a href="/">Início</a></li><li><a href="/#produtos">Produtos</a></li><li aria-current="page">{e(p["nome"])}</li></ol>
      </nav>
      <div class="product-hero-grid">
        <div>
          <div class="product-hero-title">
            {icone(p)}
            <span class="product-name">{e(p["nome"])}</span>
            {selo(p)}
          </div>
          <h1>{e(p["h1"])}</h1>
          <p class="lead">{e(p["lead"])}</p>
          <div class="btn-row">
            <a class="btn btn-whatsapp" href="{e(link_wa)}" target="_blank" rel="noopener">{WA_SVG}{cta}</a>
            <a class="btn btn-ghost" href="#como-funciona">Como funciona</a>
          </div>
        </div>
        <aside class="fact-card" aria-labelledby="ficha-{p["id"]}">
          <h2 id="ficha-{p["id"]}">Ficha rápida</h2>
          <dl>
            <div><dt>Estado</dt><dd>{txt}: {e(p["estado"])}</dd></div>
            <div><dt>Para quem</dt><dd>{e(p["para"])}</dd></div>
            <div><dt>Implantação</dt><dd>{e(p["implantacao"])}</dd></div>
            <div><dt>Contratação</dt><dd>Sozinho ou junto com o ERP VarejAI</dd></div>
          </dl>
        </aside>
      </div>
    </div>
  </section>

  <section class="section section-alt">
    <div class="container">
      <div class="section-head">
        <p class="eyebrow">O problema</p>
        <h2>O que hoje pesa na loja</h2>
      </div>
      <div class="card-grid">
{problemas}
      </div>
    </div>
  </section>

  <section class="section" id="como-funciona">
    <div class="container">
      <div class="section-head">
        <p class="eyebrow">Na prática</p>
        <h2>Como funciona</h2>
      </div>
      <div class="steps numbered">
{passos}
      </div>
    </div>
  </section>

  <section class="section section-alt">
    <div class="container split">
      <div>
        <p class="eyebrow">Para quem é</p>
        <h2>Feito para</h2>
        <ul class="check-list">
{feito}
        </ul>
      </div>
      <div class="state-box">
        <span class="status {cls}">{txt}</span>
        <h3>Estado hoje</h3>
        <p>{e(p["estado"])}</p>
      </div>
    </div>
  </section>

  <section class="section section-tight">
    <div class="container">
      <div class="cta-band">
        <div>
          <h2>Vamos ver se {art(p)} {e(p["nome"])} serve para a sua loja?</h2>
          <p>Conversa direta pelo WhatsApp com quem construiu o produto.</p>
        </div>
        <div class="btn-row">
          <a class="btn btn-whatsapp" href="{e(link_wa)}" target="_blank" rel="noopener">{WA_SVG}{cta}</a>
        </div>
      </div>
    </div>
  </section>

  <section class="section" id="perguntas">
    <div class="container">
      <div class="section-head">
        <p class="eyebrow">Perguntas frequentes</p>
        <h2>Dúvidas sobre {art(p)} {e(p["nome"])}</h2>
      </div>
      <div class="faq">
{faq}
      </div>
    </div>
  </section>

  <section class="section section-tight">
    <div class="container">
      <h2 class="list-title">Outros produtos VarejAI</h2>
      {outros(v, p["id"])}
    </div>
  </section>

</main>

{fim}
"""


def sitemap(v: dict, hoje: str, atual: str) -> str:
    ids = {p["id"] for p in v["produtos"]}
    antigos = dict(re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", atual))
    fixos = [u for u in antigos if u.removeprefix(SITE).strip("/") not in ids]
    urls = [fixos[0]] + [f"{SITE}/{p['id']}" for p in v["produtos"]] + fixos[1:] if fixos else \
        [f"{SITE}/{p['id']}" for p in v["produtos"]]
    corpo = "".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{antigos.get(u, hoje)}</lastmod>\n  </url>\n"
                    for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{corpo}</urlset>\n'


def llms(v: dict, atual: str) -> str:
    linhas = "\n".join(f'- [{p["nome"]}]({SITE}/{p["id"]}): {p["llms"]}. {SELOS[p["selo"]][1]}.'
                       for p in v["produtos"])
    return trocar(atual, r"## Produtos\n\n.*?\n\n(?=## )", f"## Produtos\n\n{linhas}\n\n", "llms.txt")


def gerar(v: dict) -> list[str]:
    """Grava os arquivos e devolve os que mudaram."""
    hoje = dt.date.today().isoformat()
    novos: dict[Path, str] = {}
    home = (RAIZ / "index.html").read_text(encoding="utf-8")
    cartoes = "".join(cartao(p) for p in v["produtos"])
    home = trocar(home, r'(?<=<div class="portfolio-grid">\n).*?(?=      </div>\n      <div class="status-legend")',
                  cartoes, "index.html")
    novos[RAIZ / "index.html"] = home
    for p in v["produtos"]:
        if p["pagina"] == "gerada":
            novos[RAIZ / p["id"] / "index.html"] = pagina(v, p)
    for arq in sorted(set(RAIZ.glob("*/index.html")) | set(novos)):
        txt = novos.get(arq) or arq.read_text(encoding="utf-8")
        txt = re.sub(r'<nav class="footer-nav" aria-label="Produtos">.*?</nav>', lambda _m: rodape(v), txt, count=1,
                     flags=re.S)
        atual = arq.parent.name if arq.parent != RAIZ else None
        txt = re.sub(r'<div class="mini-grid">.*?</div>', lambda _m: outros(v, atual), txt, count=1, flags=re.S)
        novos[arq] = txt
    sm = RAIZ / "sitemap.xml"
    sm_atual = sm.read_text(encoding="utf-8")
    novos[sm] = sitemap(v, hoje, sm_atual)
    ll = RAIZ / "llms.txt"
    novos[ll] = llms(v, ll.read_text(encoding="utf-8"))
    mudou = []
    for arq, txt in novos.items():
        if not arq.exists() or arq.read_text(encoding="utf-8") != txt:
            # data do sitemap: só a página que mudou ganha a data de hoje
            arq.parent.mkdir(parents=True, exist_ok=True)
            arq.write_text(txt, encoding="utf-8", newline="\n")
            mudou.append(arq.relative_to(RAIZ).as_posix())
    if mudou:
        sm_txt = sm.read_text(encoding="utf-8")
        for rel in mudou:
            if rel.endswith("index.html"):
                pasta = rel.removesuffix("index.html").strip("/")
                u = f"{SITE}/{pasta}" if pasta else f"{SITE}/"
                sm_txt = re.sub(rf"(<loc>{re.escape(u)}</loc>\s*<lastmod>)[^<]+", rf"\g<1>{hoje}", sm_txt)
        if sm_txt != sm.read_text(encoding="utf-8"):
            sm.write_text(sm_txt, encoding="utf-8", newline="\n")
            if "sitemap.xml" not in mudou:
                mudou.append("sitemap.xml")
    return mudou


def resumo(v: dict, mudou: list[str]) -> str:
    linhas = ["## O que muda no site", ""]
    linhas += [f"- `{m}`" for m in mudou] or ["- nada"]
    linhas += ["", "## Os produtos na vitrine", "", "| Produto | Selo | Página |", "|---|---|---|"]
    linhas += [f'| [{p["nome"]}]({SITE}/{p["id"]}) | {SELOS[p["selo"]][1]} | {p["pagina"]} |' for p in v["produtos"]]
    return "\n".join(linhas) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("vitrine", type=Path)
    ap.add_argument("--resumo", type=Path, help="grava aqui o texto do pedido de alteração (markdown)")
    a = ap.parse_args()
    v = carregar(a.vitrine)
    mudou = gerar(v)
    if a.resumo:
        a.resumo.write_text(resumo(v, mudou), encoding="utf-8")
    sys.stdout.write("\n".join(mudou) + ("\n" if mudou else "nada mudou\n"))


if __name__ == "__main__":
    main()
