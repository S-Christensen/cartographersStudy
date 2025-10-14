
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
  // Track last placed shape's cells and placement lock
  let lastPlacedCells = [];
  let placementLocked = false;

  canvas.addEventListener("click", () => {
    if (placementLocked) return;
    if (canPlaceAt(hoverX, hoverY)) {
      // Place new shape and record its cells
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

  // Add Undo button functionality
  document.addEventListener('DOMContentLoaded', function() {
    // ...existing code...
    // Add Undo button if not present
    let undoBtn = document.getElementById('undoBtn');
    if (!undoBtn) {
      undoBtn = document.createElement('button');
      undoBtn.id = 'undoBtn';
      undoBtn.textContent = 'Undo';
      const sidebar = document.getElementById('sidebar');
      if (sidebar) sidebar.appendChild(undoBtn);
    }
    undoBtn.addEventListener('click', function() {
      // Remove last placed shape
      lastPlacedCells.forEach(([y, x]) => {
        if (gridData[y][x] !== "Mountain") {
          gridData[y][x] = 0;
        }
      });
      lastPlacedCells = [];
      placementLocked = false;
      drawGrid();
    });
  });
}

canvas.addEventListener("click", () => {
  if (canPlaceAt(hoverX, hoverY)) {
    for (let dy = 0; dy < activeShape.length; dy++) {
      for (let dx = 0; dx < activeShape[0].length; dx++) {
        if (activeShape[dy][dx]) {
          gridData[hoverY + dy][hoverX + dx] = terrain;
        }
      }
    }
    drawGrid();
  }
})
drawGrid();