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

function showTerrainButtons(allowedTerrains) {
    const container = document.getElementById('terrain-buttons');
    container.innerHTML = '';

    allowedTerrains.forEach(type => {
        const btn = document.createElement('button');
        btn.textContent = type.charAt(0).toUpperCase() + type.slice(1);
        btn.className = 'terrain-btn ' + type;
        btn.dataset.color = type;
        btn.addEventListener('click', () => {
            terrain = type;
            renderShapePreview(activeShape, terrain);
        });
        container.appendChild(btn);
    });
}

showTerrainButtons(['forest', 'village']);

document.getElementById("cardName").textContent = `Card: ${selectedCard.id}`;
renderShapePreview(activeShape, terrain);
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

function showTerrainButtons(allowedTerrains) {
  const container = document.getElementById('terrain-buttons');
  container.innerHTML = '';
  allowedTerrains.forEach(type => {
    const btn = document.createElement('button');
    btn.textContent = type.charAt(0).toUpperCase() + type.slice(1);
    btn.className = 'terrain-btn ' + type;
    btn.dataset.color = type;
    btn.addEventListener('click', () => {
      if (typeof setTerrain === 'function') setTerrain(type);
      renderShapePreview(typeof activeShape !== 'undefined' ? activeShape : [[1]], type);
    });
    container.appendChild(btn);
  });
}