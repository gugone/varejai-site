(function () {
  // PENDÊNCIA: confirmar o número oficial de WhatsApp da VarejAI (docs/PORTFOLIO.md).
  // O mesmo número aparece nos links wa.me das páginas.
  var WHATSAPP = "5582920003978";

  var toggle = document.getElementById("nav-toggle");
  var nav = document.getElementById("main-nav");

  function fecharMenu() {
    nav.classList.remove("open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Abrir menu");
  }

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var aberto = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(aberto));
      toggle.setAttribute("aria-label", aberto ? "Fechar menu" : "Abrir menu");
    });
    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", fecharMenu);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("open")) {
        fecharMenu();
        toggle.focus();
      }
    });
  }

  var ano = document.getElementById("footer-year");
  if (ano) ano.textContent = new Date().getFullYear();

  // Formulário de contato: monta a mensagem e abre o WhatsApp. Nada é enviado a servidor.
  var form = document.getElementById("contact-form");
  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var nomeInput = form.elements.nome;
      if (!nomeInput.value.trim()) {
        nomeInput.focus();
        nomeInput.setAttribute("aria-invalid", "true");
        return;
      }
      nomeInput.removeAttribute("aria-invalid");
      var d = new FormData(form);
      var linhas = ["Olá! Vim pelo site da VarejAI.", "Nome: " + d.get("nome")];
      if (d.get("loja")) linhas.push("Loja/empresa: " + d.get("loja"));
      if (d.get("cidade")) linhas.push("Cidade: " + d.get("cidade"));
      if (d.get("produto")) linhas.push("Interesse: " + d.get("produto"));
      if (d.get("mensagem")) linhas.push("", d.get("mensagem"));
      window.open("https://wa.me/" + WHATSAPP + "?text=" + encodeURIComponent(linhas.join("\n")), "_blank", "noopener");
    });
  }
})();
