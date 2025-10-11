function renderShapePreview(shape, terrain) {
  const preview = document.getElementById("shapePreview");
  preview.innerHTML = "";
  shape.forEach((row, y) => {
    row.forEach((cell, x) => {
      const div = document.createElement("div");
      if (cell) div.style.backgroundColor = getColor(terrain);
      preview.appendChild(div);
    });
  });
}

document.querySelectorAll("#colorOptions button").forEach(btn => {
  btn.addEventListener("click", () => {
    terrain = btn.dataset.color;
    renderShapePreview(activeShape, terrain);
  });
});

document.getElementById("cardName").textContent = `Card: ${selectedCard.id}`;
renderShapePreview(activeShape, terrain);