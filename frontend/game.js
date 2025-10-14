
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

async function submitMove() {
  try {
    const response = await fetch('https://cartographersstudy.onrender.com/api/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prev_grid: getPreviousGrid(),
        new_grid: gridData,
        card: {
          id: document.getElementById("cardName").textContent.replace("Card: ", ""),
          shapes: [activeShape],
          terrainOptions: [terrain]
        },
        ruins_required: false
      })
    });

    const result = await response.json();
    console.log('Validation result:', result);

    if (result.valid) {
      alert("Valid placement!");
      placementLocked = true;
    } else {
      alert("Invalid move: " + result.message);
      undoLastPlacement();
    }
  } catch (err) {
    console.error('Failed to validate move:', err);
  }
}

// Function to fetch a new card from the backend
async function drawCard() {
  try {
    const response = await fetch('https://cartographersstudy.onrender.com/api/draw-card', {
      method: 'POST'
    });
    const data = await response.json();
    console.log("Card data:", data);

    if (data.error) {
      throw new Error("Server error: " + data.error);
    }

    document.getElementById("cardName").textContent = `Card: ${data.cardName}`;
    activeShape = data.shape;
    terrain = data.allowedTerrains[0];
    showTerrainButtons(data.allowedTerrains);
    renderShapePreview(activeShape, terrain);
    placementLocked = false;
    lastPlacedCells = [];
    drawGrid();
  } catch (err) {
    console.error('Failed to draw card:', err);
    alert("Error drawing card: " + err.message);
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
  const startBtn = document.getElementById('startBtn');
  const drawBtn = document.getElementById('drawCardBtn');
  const submitBtn = document.getElementById('submitBtn');
  const undoBtn = document.getElementById('undoBtn');

  // Hide game controls until Start is pressed
  function showGameControls() {
    if (drawBtn) drawBtn.style.display = '';
    if (submitBtn) submitBtn.style.display = '';
    if (undoBtn) undoBtn.style.display = '';
    if (startBtn) startBtn.style.display = 'none';
  }

  if (startBtn) {
    startBtn.addEventListener('click', function() {
      showGameControls();
      drawCard();
    });
  }

  if (drawBtn) {
    drawBtn.addEventListener('click', drawCard);
  }
  if (submitBtn) {
    submitBtn.addEventListener('click', submitMove);
  }
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
  // Hide controls initially
  if (drawBtn) drawBtn.style.display = 'none';
  if (submitBtn) submitBtn.style.display = 'none';
  if (undoBtn) undoBtn.style.display = 'none';
});

function getPreviousGrid() {
  const clone = gridData.map(row => [...row]);
  lastPlacedCells.forEach(([y, x]) => {
    clone[y][x] = 0;
  });
  return clone;
}

function undoLastPlacement() {
  lastPlacedCells.forEach(([y, x]) => {
    if (gridData[y][x] !== "Mountain") {
      gridData[y][x] = 0;
    }
  });
  lastPlacedCells = [];
  drawGrid();
}

