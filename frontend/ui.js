import { activeShape, currentCardCost, drawGrid, setActiveShape, setTerrain, terrain } from './game.js';

export function showShapeButtons(shapes) {
  const container = document.getElementById('shape-buttons');
  container.innerHTML = '';

  shapes.forEach((shape, index) => {
    const btn = document.createElement('button');
    btn.textContent = `Shape ${index + 1}`;
    btn.addEventListener('click', () => {
      setActiveShape(shape);
      renderShapePreview(shape, terrain, currentCardCost);
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

export function renderShapePreview(shape, terrain, cost = null) {
  const preview = document.getElementById("shapePreview");
  preview.innerHTML = "";

  if (cost !== null) {
    const costLabel = document.createElement("div");
    costLabel.textContent = `Cost: ${cost}`;
    costLabel.className = "shape-cost";
    preview.appendChild(costLabel);
  }

  shape.forEach(row => {
    const rowDiv = document.createElement("div");
    rowDiv.className = "shape-row";
    row.forEach(cell => {
      const div = document.createElement("div");
      div.className = "shape-cell";
      if (cell) div.style.backgroundColor = getColor(terrain);
      rowDiv.appendChild(div);
    });
    preview.appendChild(rowDiv);
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
        renderShapePreview(activeShape, type, currentCardCost);
      });
      container.appendChild(btn);
    });
  }