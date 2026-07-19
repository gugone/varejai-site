(function () {
  var WHATSAPP = "5582920003978";

  var form = document.getElementById("apura-form");
  if (!form) return;

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    var nome = document.getElementById("apura-nome").value.trim();
    var perfil = document.getElementById("apura-perfil").value;
    var qtd = document.getElementById("apura-qtd").value.trim() || "não informado";

    var msg =
      "Olá! Sou " + nome + " (" + perfil + ", lojas/clientes: " + qtd + ") " +
      "e quero reservar minha vaga no plano Fundador do APURA.";

    window.open("https://wa.me/" + WHATSAPP + "?text=" + encodeURIComponent(msg), "_blank");
  });
})();
