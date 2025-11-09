import { getColor, highlightCurrentSeason, renderScoringCards, renderShapePreview, showShapeButtons, showTerrainButtons } from './ui.js';

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
let previousGrid = null;
gridData[1][3] = "Mountain";
gridData[2][8] = "Mountain";
gridData[5][5] = "Mountain";
gridData[8][2] = "Mountain";
gridData[9][7] = "Mountain";
gridData[1][5] = "Ruins";
gridData[2][1] = "Ruins";
gridData[2][9] = "Ruins";
gridData[8][1] = "Ruins";
gridData[8][9] = "Ruins";
gridData[9][5] = "Ruins";

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

export function setScoreTypes(types) {
  scoreTypes = types;
}

export function setCurrentSeason(index) {
  currentSeason = index;
}

let totalPoints = 0;

function updateSeasonScores(seasonId, scores) {
  // scores = { A: 7, B: 4, coins: 2, monsters: -1 }
  let seasonTotal = 0;

  for (const [key, val] of Object.entries(scores)) {
    const row = document.querySelector(`#${seasonId} .breakdown-row[data-key="${key}"] span`);
    if (row) {
      row.textContent = val;
      seasonTotal += val;
    }
  }

  totalPoints += seasonTotal;
  document.getElementById("totalPoints").textContent = `Total: ${totalPoints}`;
}

export async function fetchSession() {
  try {
    const response = await fetch('https://cartographersstudy.onrender.com/api/session');
    const data = await response.json();

    setScoreTypes(data.scoreTypes);
    setCurrentSeason(data.currentSeason);
    setSeasonRemaining(data.seasonTime);

    renderScoringCards(data.scoreTypesNames, data.currentSeason);
    highlightCurrentSeason(data.currentSeason);
  } catch (err) {
    console.error('Failed to fetch session:', err);
  }
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
        if (cell === "Ruins") {
          ctx.fillStyle = "#888"; // grayish ruins
          ctx.globalAlpha = 0.3;   // semi-transparent
          ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
          ctx.globalAlpha = 1.0;
        } else {
          ctx.fillStyle = getColor(cell);
          ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
        }
      }
    }
  }

  if (gameStarted && !placementLocked && hoverX !== null && hoverY !== null) {
    drawPreview(hoverX, hoverY);
  }
}

export async function submitMove() {
  localStorage.setItem("savedGrid", JSON.stringify(gridData));
  return;
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

// Fetch a new card from the backend
export async function drawCard() {
  try {
    // Check current session state
    const sessionRes = await fetch("https://cartographersstudy.onrender.com/api/session");
    const session = await sessionRes.json();

    if (session.seasonTime <= 0) {
      // Trigger backend to start next season
      const endRes = await fetch("https://cartographersstudy.onrender.com/api/end-season", {
        method: "POST"
      });
      const endData = await endRes.json();

      if (endData.error) {
        console.error("Season end error:", endData.error);
        return;
      }

      // Update UI with new season info
      highlightCurrentSeason(endData.seasonName?.toLowerCase());
    }


    const response = await fetch('https://cartographersstudy.onrender.com/api/draw-card', {
      method: 'POST'
    });
    const card = await response.json();

    // Refresh seasonRemaining
    await fetchSession();

    if (card.error) {
      alert(card.error);
      return;
    }

    // Handle Ruins card
    if (card.type === "Ruins") {
      alert("Ruins card drawn! The next shape must be placed on a Ruins tile.");

      // Show ruins card name
      document.getElementById("ruinsCardName").textContent = `Ruins Card: ${card.id}`;

      // Immediately draw the next card
      const nextResponse = await fetch('https://cartographersstudy.onrender.com/api/draw-card', {
        method: 'POST'
      });
      const nextCard = await nextResponse.json();
      // TODO: Handle Monster card if drawn as next card

      if (nextCard.error) {
        alert(nextCard.error);
        return;
      }

      // Show next card name below ruins card
      document.getElementById("activeCardName").textContent = `Card: ${nextCard.id}`;

      // Set up terrain and shape
      setCurrentCardCost(nextCard.cost);
      setAvailableShapes(nextCard.shape);
      setActiveShape(nextCard.shape[0]);
      terrain = nextCard.terrainOptions[0];
      await fetchSession();
      if (nextCard.cost === 1 && nextCard.shape.length > 1) {
        showShapeButtons(nextCard.shape);
        document.getElementById('terrain-buttons').style.display = 'none';
      } else if (nextCard.terrainOptions.length > 1) {
        showTerrainButtons(nextCard.terrainOptions);
        document.getElementById('shape-buttons').innerHTML = '';
        document.getElementById('terrain-buttons').style.display = '';
      } else {
        showTerrainButtons(nextCard.terrainOptions);
      }
      renderShapePreview(activeShape, terrain, nextCard.cost, seasonRemaining);
      placementLocked = false;
      lastPlacedCells = [];
      drawGrid();
      return;
    } else {
      // Normal card flow
      document.getElementById("ruinsCardName").textContent = "";
      document.getElementById("activeCardName").textContent = `Card: ${card.id}`;

      setCurrentCardCost(card.cost);
      setAvailableShapes(card.shape);
      setActiveShape(card.shape[0]);
      terrain = card.terrainOptions[0];

      if (card.type === "Monster") {
        alert("Monster card drawn! This isn't functional at the moment but might be in 2 weeks.");
        terrain = "Monster";
        setCurrentCardCost(card.cost);
        setAvailableShapes(card.shape);
        setActiveShape(card.shape[0]);
        document.getElementById("ruinsCardName").textContent = "";
        document.getElementById("activeCardName").textContent = `Card: ${card.id}`;
        document.getElementById('terrain-buttons').style.display = 'none';

        renderShapePreview(activeShape, terrain, card.cost, seasonRemaining);
        placementLocked = false;
        lastPlacedCells = [];
        drawGrid();
        return;
      } else if (card.cost === 1 && card.shape.length > 1) {
        showShapeButtons(card.shape);
        document.getElementById('terrain-buttons').style.display = 'none';
      } else if (card.terrainOptions.length > 1) {
        showTerrainButtons(card.terrainOptions);
        document.getElementById('shape-buttons').innerHTML = '';
        document.getElementById('terrain-buttons').style.display = '';
      } else {
        showTerrainButtons(card.terrainOptions);
      }
    }
    renderShapePreview(activeShape, terrain, card.cost, seasonRemaining);
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
        if (gx < gridSize && gy < gridSize && (gridData[gy][gx] === 0 || gridData[gy][gx] === "Ruins")) {
          if (gridData[gy][gx] === "Ruins") {
            ctx.fillStyle = "#888"; // ruins base color
            ctx.globalAlpha = 0.3;
            ctx.fillRect(gx * cellSize, gy * cellSize, cellSize, cellSize);
            ctx.globalAlpha = 1.0;
          }
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
export let terrain = "Monster"; // Default terrain, will be set on card draw
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
        if (gx >= gridSize || gy >= gridSize || (gridData[gy][gx] !== 0 && gridData[gy][gx] !== "Ruins")) {
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
    previousGrid = gridData.map(row => [...row]);
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
      fetchSession();
      document.getElementById("scoringContainer").style.display = "";
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
      undoLastPlacement();
      placementLocked = false; 
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
  return previousGrid ? previousGrid.map(row => [...row]) : gridData.map(row => [...row]);
}

function undoLastPlacement() {
  const previous = getPreviousGrid();
  for (let y = 0; y < gridSize; y++) {
    for (let x = 0; x < gridSize; x++) {
      gridData[y][x] = previous[y][x];
    }
  }
  lastPlacedCells = [];
  drawGrid();
}
