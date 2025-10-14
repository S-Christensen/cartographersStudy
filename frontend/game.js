
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const gridSize = 11;
const cellSize = canvas.width / gridSize;
let gridData = Array.from({ length: gridSize }, () => Array(gridSize).fill(0));
gridData[1][3] = "Mountain";
gridData[2][8] = "Mountain";
gridData[5][5] = "Mountain";
gridData[8][2] = "Mountain";
gridData[9][7] = "Mountain";

// Function to fetch a new card from the backend
async function drawCard() {
  try {
    const response = await fetch('/api/draw-card', { method: 'POST' });
    const data = await response.json();
    // Update card name
    document.getElementById("cardName").textContent = `Card: ${data.cardName}`;
    // Show only allowed terrain buttons
    if (typeof showTerrainButtons === 'function') {
      showTerrainButtons(data.allowedTerrains);
    } else if (typeof renderColorOptions === 'function') {
      renderColorOptions(data.allowedTerrains);
    }
  } catch (err) {
    console.error('Failed to draw card:', err);
  }
}

// Attach event listener to the draw card button
document.addEventListener('DOMContentLoaded', function() {
  const drawBtn = document.getElementById('drawCardBtn');
  if (drawBtn) {
    drawBtn.addEventListener('click', drawCard);
  }
});

function getColor(value) {
  if (value === "Forest") return "#228B22";
  if (value === "Water") return "#1E90FF";
  if (value === "Farm") return "#DAA520";
  if (value === "Village") return "#8B0000";
  if (value === "Mountain") return "#8D6F64";
  if (value === "Monster") return "#CC6CE7";
  return "#1e1e1e";
}

let hoverX = null, hoverY = null;

canvas.addEventListener("mousemove", (e) => {
  hoverX = Math.floor(e.offsetX / cellSize);
  hoverY = Math.floor(e.offsetY / cellSize);
  drawGrid();
});

function drawGrid() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  for (let y = 0; y < gridSize; y++) {
    for (let x = 0; x < gridSize; x++) {
      ctx.fillStyle = getColor(gridData[y][x]);
      ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
      ctx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
    }
  }

  if (hoverX !== null && hoverY !== null) {
    drawPreview(hoverX, hoverY);
  }
}

function drawPreview(x, y) {
  for (let dy = 0; dy < activeShape.length; dy++) {
    for (let dx = 0; dx < activeShape[0].length; dx++) {
      if (activeShape[dy][dx]) {
        const gx = x + dx;
        const gy = y + dy;
        if (gx < gridSize && gy < gridSize && gridData[gy][gx] === 0) {
          ctx.fillStyle = getColor(terrain);
          ctx.globalAlpha = 0.5;
          ctx.fillRect(gx * cellSize, gy * cellSize, cellSize, cellSize);
          ctx.globalAlpha = 1.0;
        }
      }
    }
  }
}

let activeShape = [[1, 1], [1, 1]]; // Default shape, will be set on card draw
let terrain = "Forest"; // Default terrain, will be set on card draw
let lastPlacedCells = [];
let placementLocked = false;

function setActiveShape(shape) {
  activeShape = shape;
  drawGrid();
}

function setTerrain(newTerrain) {
  terrain = newTerrain;
  drawGrid();
}

function canPlaceAt(x, y) {
  for (let dy = 0; dy < activeShape.length; dy++) {
    for (let dx = 0; dx < activeShape[0].length; dx++) {
      if (activeShape[dy][dx]) {
        const gx = x + dx;
        const gy = y + dy;
        if (gx >= gridSize || gy >= gridSize || gridData[gy][gx] !== 0) {
          return false;
        }
      }
    }
  }
  return true;
}

canvas.addEventListener("click", () => {
  if (placementLocked) return;
  if (hoverX === null || hoverY === null) return;
  if (canPlaceAt(hoverX, hoverY)) {
    lastPlacedCells = [];
    for (let dy = 0; dy < activeShape.length; dy++) {
      for (let dx = 0; dx < activeShape[0].length; dx++) {
        if (activeShape[dy][dx]) {
          gridData[hoverY + dy][hoverX + dx] = terrain;
          lastPlacedCells.push([hoverY + dy, hoverX + dx]);
        }
      }
    }
    placementLocked = true;
    drawGrid();
  }
});

document.addEventListener('DOMContentLoaded', function() {
  const undoBtn = document.getElementById('undoBtn');
  if (undoBtn) {
    undoBtn.addEventListener('click', function() {
      lastPlacedCells.forEach(([y, x]) => {
        if (gridData[y][x] !== "Mountain") {
          gridData[y][x] = 0;
        }
      });
      lastPlacedCells = [];
      placementLocked = false;
      drawGrid();
    });
  }
  drawCard();
});