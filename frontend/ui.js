import { activeShape, currentCardCost, drawGrid, setActiveShape, setTerrain, terrain } from './game.js';

export function showShapeButtons(shapes) {
  const container = document.getElementById('shape-buttons');
  container.innerHTML = '';

  shapes.forEach((shape, index) => {
    const btn = document.createElement('button');
    if (index === 0) btn.textContent = 'Shape + Coin';
    else btn.textContent = `Shape`;
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

export function renderShapePreview(shape, terrain, cost = null, seasonRemaining = null) {
  const preview = document.getElementById("shapePreview");
  preview.innerHTML = "";

  if (cost !== null || seasonRemaining !== null) {
    const costLabel = document.createElement("div");
    costLabel.className = "shape-cost";

    let text = "";
    if (cost !== null) text += `Card Cost: ${cost}`;
    if (seasonRemaining !== null) text += ` | Season Remaining: ${seasonRemaining}`;

    costLabel.textContent = text;
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

function formatName(name) {
  return name
    .replace(/([A-Z])/g, ' $1') // insert space before capital letters
    .replace(/^./, str => str.toUpperCase()); // capitalize first letter
}

export function renderScoringCards(scoreTypes, currentSeason) {
  const container = document.getElementById("scoringDisplay");
  container.innerHTML = "";
  const scoreNames = scoreTypes.map(fn => fn.name);
  scoreNames.forEach((card, index) => {
    const div = document.createElement("div");
    div.className = "scoring-card";
    if (index !== currentSeason && index !== (currentSeason + 1) % 4) {
      div.classList.add("inactive");
    }
    div.textContent = formatName(card);
    container.appendChild(div);
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