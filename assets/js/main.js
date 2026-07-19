(function () {
  var toggle = document.getElementById("nav-toggle");
  var nav = document.getElementById("main-nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var isOpen = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(isOpen));
    });

    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  var yearEl = document.getElementById("footer-year");
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  var form = document.getElementById("contact-form");
  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var data = new FormData(form);
      var nome = data.get("nome") || "";
      var loja = data.get("loja") || "";
      var email = data.get("email") || "";
      var mensagem = data.get("mensagem") || "";

      var subject = "Contato pelo site - " + nome;
      var body =
        "Nome: " + nome + "\n" +
        "Loja/empresa: " + loja + "\n" +
        "E-mail: " + email + "\n\n" +
        mensagem;

      window.location.href =
        "mailto:contato@varejai.com.br?subject=" +
        encodeURIComponent(subject) +
        "&body=" +
        encodeURIComponent(body);
    });
  }
})();
