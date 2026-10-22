# varejai-site

Site institucional da Varejai. HTML/CSS/JS estático, sem build step. No ar em
[varejai.com.br](https://varejai.com.br) via GitHub Pages.

## Estrutura

```
index.html           (home: hero, portfólio com selos, prova, sobre, contato)
retina/ whatsapp-commerce/ erp/ ponto/ achei/ compras/   (uma página por produto)
equipe/ privacidade/
apura/index.html     (landing do APURA: oculta, fora do menu e do sitemap, noindex)
(o levantamento interno do portfólio fica no repositório privado do ERP: docs/estudos/PORTFOLIO-VAREJAI.md)
assets/og/           (imagens 1200x630 para compartilhamento, uma por página)
robots.txt
sitemap.xml
assets/
  css/style.css       (design system do site: header, footer, cards, etc)
  css/apura.css       (acento verde e estilos exclusivos da landing do APURA)
  js/main.js
  js/apura.js         (formulário da landing do APURA -> WhatsApp)
  img/                (logo Varejai, ícone RETINA)
```

## Rodar localmente

Qualquer servidor estático funciona, por exemplo:

```
python3 -m http.server 8000
```

e abrir `http://localhost:8000`.

## Pendências

- **WhatsApp**: todos os CTAs usam `wa.me/5582920003978` (número que já estava no
  formulário do APURA). Confirmar se é o número oficial da VarejAI; para trocar, buscar e
  substituir `5582920003978` em todo o repositório (HTML e `assets/js/*.js`).

- **E-mail de contato**: `contato@varejai.com.br` está como placeholder em `index.html`
  (link "fale direto") e em `assets/js/main.js` (destino do formulário). Confirmar o
  e-mail real, se ainda não for esse.

## SEO: Google Search Console

1. Acesse [search.google.com/search-console](https://search.google.com/search-console),
   adicione a propriedade de domínio `varejai.com.br`.
2. O Google vai pedir um registro **TXT** de verificação. Adicione esse registro no
   painel de DNS do domínio (mesmo lugar onde estão os 4 registros A do GitHub Pages).
3. Depois de verificado, em Sitemaps, envie `https://varejai.com.br/sitemap.xml`.

O `robots.txt` já libera todos os crawlers e aponta pro sitemap, então não precisa de
mais nada além do cadastro em si.
