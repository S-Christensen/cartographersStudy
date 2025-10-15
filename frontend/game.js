import { getColor, renderShapePreview, showShapeButtons, showTerrainButtons } from './ui.js';

export const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
export const gridSize = 11;
export const cellSize = canvas.width / gridSize;
export let gridData = Array.from({ length: gridSize }, () => Array(gridSize).fill(0));
export let hoverX = null;
export let hoverY = null;
export let availableShapes = [];
export let currentCardCost = null;
export let gameStarted = false;
export let seasonRemaining = 8;
export let scoreTypes = [];
export let currentSeason = 0;
gridData[1][3] = "Mountain";
gridData[2][8] = "Mountain";
gridData[5][5] = "Mountain";
gridData[8][2] = "Mountain";
gridData[9][7] = "Mountain";

export function setGameStarted(started) {
  gameStarted = started;
}

export function setSeasonRemaining(value) {
  seasonRemaining = value;
}

export function setCurrentCardCost(cost) {
  currentCardCost = cost;
}

export function setAvailableShapes(shapes) {
  availableShapes = shapes;
}

export function drawGrid() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  for (let y = 0; y < gridSize; y++) {
    for (let x = 0; x < gridSize; x++) {
      const cell = gridData[y][x];

      // Draw cell border
      ctx.strokeStyle = "#000";
      ctx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);

      // Fill terrain if present
      if (cell && cell !== 0) {
        ctx.fillStyle = getColor(cell);
        ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
      }
    }
  }

  if (gameStarted && !placementLocked && hoverX !== null && hoverY !== null) {
    drawPreview(hoverX, hoverY);
  }
}

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
          shape: [activeShape],
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
export async function drawCard() {
  try {
    const response = await fetch('https://cartographersstudy.onrender.com/api/draw-card', {
      method: 'POST'
    });
    const card = await response.json();
    console.log("Card object:", card);

    document.getElementById("cardName").textContent = `Card: ${card.id}`;
    setCurrentCardCost(card.cost);
    setAvailableShapes(card.shape);
    setActiveShape(card.shape[0]);
    terrain = card.terrainOptions[0]; // default

    if (card.cost === 1 && card.shape.length > 1) {
      // Show shape buttons only
      renderShapePreview(activeShape, terrain, card.cost);
      showShapeButtons(card.shape);
      document.getElementById('terrain-buttons').style.display = 'none';
    } else if (card.terrainOptions.length > 1) {
      // Show terrain buttons only
      showTerrainButtons(card.terrainOptions);
      renderShapePreview(activeShape, terrain, card.cost);
      document.getElementById('shape-buttons').innerHTML = '';
      document.getElementById('terrain-buttons').style.display = '';
    } else {
      // Fallback: show terrain buttons
      showTerrainButtons(card.terrainOptions);
      renderShapePreview(activeShape, terrain, card.cost);
    }
    showTerrainButtons(card.terrainOptions);
    renderShapePreview(activeShape, terrain, card.cost);
    placementLocked = false;
    lastPlacedCells = [];
    drawGrid();
  } catch (err) {
    console.error('Failed to draw card:', err);
    alert("Error drawing card: " + err.message);
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

export let activeShape = [[1, 1], [1, 1]]; // Default shape, will be set on card draw
export let terrain = "Forest"; // Default terrain, will be set on card draw
export let lastPlacedCells = [];
export let placementLocked = false;

export function setActiveShape(shape) {
  activeShape = shape;
  drawGrid();
}

export function setLastPlacedCells(cells) {
  lastPlacedCells = cells;
}
export function setPlacementLocked(locked) {
  placementLocked = locked;
}

export function setTerrain(newTerrain) {
  terrain = newTerrain;
  drawGrid();
}

export function setHover(x, y) {
  hoverX = x;
  hoverY = y;
}


export function canPlaceAt(x, y) {
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
      setGameStarted(true);
      renderScoringCards();
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

