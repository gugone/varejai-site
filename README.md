# varejai-site

Site institucional da Varejai — HTML/CSS/JS estático, sem build step.

## Estrutura

```
index.html
assets/
  css/style.css
  js/main.js
  img/            (logo Varejai, ícone RETINA)
```

## Rodar localmente

Qualquer servidor estático funciona, por exemplo:

```
python3 -m http.server 8000
```

e abrir `http://localhost:8000`.

## Pendências antes de publicar

- **E-mail de contato**: `contato@varejai.com.br` está como placeholder em `index.html`
  (link "fale direto") e em `assets/js/main.js` (destino do formulário). Confirmar o
  e-mail real antes de publicar.
- **Seção Apura**: copy propositalmente neutra ("em breve"), sem inventar
  funcionalidade — atualizar quando houver informação real do produto.
- **GitHub Pages**: repositório está privado; publicar via Pages gratuito exige torná-lo
  público (ou plano pago do GitHub para Pages em repo privado).
