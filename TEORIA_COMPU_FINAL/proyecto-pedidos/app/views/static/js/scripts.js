// Botón "Cargar ejemplo"
const btnEjemplo = document.getElementById("btn-ejemplo");
if (btnEjemplo) {
  btnEjemplo.addEventListener("click", () => {
    document.getElementById("texto").value = btnEjemplo.dataset.ejemplo;
  });
}

// Dibuja los grafos DOT (solo en la página de autómatas)
const grafos = document.querySelectorAll(".grafo");
if (grafos.length && window.Viz) {
  Viz.instance().then((viz) => {
    grafos.forEach((el) => {
      try {
        el.replaceChildren(viz.renderSVGElement(el.dataset.dot));
      } catch (e) {
        el.textContent = "No se pudo dibujar el gráfico: " + e.message;
      }
    });
  });
} else if (grafos.length) {
  grafos.forEach((el) => (el.textContent = "No se pudo cargar viz.js. Revisa tu conexión."));
}
