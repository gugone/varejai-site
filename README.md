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

## Publicar em varejai.com.br (GitHub Pages)

O arquivo `CNAME` na raiz já está configurado com `varejai.com.br`. Falta:

1. Tornar este repositório **público** — Pages gratuito não funciona em repo privado
   (Settings → General → Danger Zone → Change repository visibility).
2. Mesclar o PR que traz o site pra `main`.
3. Ligar o Pages: Settings → Pages → Build and deployment → Source: "Deploy from a
   branch" → `main` / `(root)`.
4. Em Settings → Pages → Custom domain, confirmar `varejai.com.br`.
5. No provedor onde o domínio foi registrado, apontar o DNS pro GitHub Pages:
   - 4 registros **A** no domínio raiz (`@`):
     `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - (opcional) 1 registro **CNAME** de `www` para `gugone.github.io`
6. Aguardar a propagação de DNS e marcar "Enforce HTTPS" no painel do Pages assim que
   disponível.
