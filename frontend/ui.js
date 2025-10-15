import { activeShape, drawGrid, setActiveShape, setTerrain, terrain } from './game.js';

export function showShapeButtons(shapes) {
  const container = document.getElementById('shape-buttons');
  container.innerHTML = '';

  shapes.forEach((shape, index) => {
    const btn = document.createElement('button');
    btn.textContent = `Shape ${index + 1}`;
    btn.addEventListener('click', () => {
      setActiveShape(shape);
      renderShapePreview(shape, terrain);
      drawGrid();
    });
    container.appendChild(btn);
  });
}

export function getColor(terrain) {
  const colors = {
    Forest: "#228B22",
    Village: "#8B0000",
    Water: "#1E90FF",
    Farm: "#DAA520",
    Mountain: "#a0522d",
    Monster: "#800080"
  };
  return colors[terrain] || "#000000";
}

 export function renderShapePreview(shape, terrain) {
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

  export function showTerrainButtons(allowedTerrains) {
    const container = document.getElementById('terrain-buttons');
    container.innerHTML = '';
    allowedTerrains.forEach(type => {
      const btn = document.createElement('button');
      btn.textContent = type.charAt(0).toUpperCase() + type.slice(1);
      btn.className = 'terrain-btn ' + type;
      btn.dataset.color = type;
      btn.addEventListener('click', () => {
        setTerrain(type);
        renderShapePreview(activeShape, type);
      });
      container.appendChild(btn);
    });
  }