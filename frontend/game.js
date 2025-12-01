import { getColor, highlightCurrentSeason, renderScoringCards, renderShapePreview, showShapeButtons, showTerrainButtons, updateCoinTracker } from './ui.js';

export const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
export const gridSize = 11;
export const cellSize = canvas.width / gridSize;
export let gridData = Array.from({ length: gridSize }, () => Array(gridSize).fill(0));
export let hoverX = null;
export let hoverY = null;
export let availableShapes = [];
export let gameStarted = false;
export let seasonRemaining = 8;
export let scoreTypes = [];
export let currentSeason = 0;
export let currentCard = null;
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

export function setGridData(newGrid) {
  gridData = newGrid;
}

export function setCurrentCard(card) {
  currentCard = card;
}

export function setGameStarted(started) {
  gameStarted = started;
}

export function setSeasonRemaining(value) {
  seasonRemaining = value;
}

export function setCurrentCardCost(cost) {
  currentCard.cost = cost;
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
export function updateSeasonScores(endData) {
  console.log(endData);
  if (!endData || !endData.breakdown || endData.season === undefined) {
      console.warn("Invalid endData:", endData);
      return;
  }

  const seasonNames = ["spring", "summer", "autumn", "winter"];
  const finishedSeasonIndex = (endData.season - 1 + 4) % 4; 
  const seasonId = seasonNames[finishedSeasonIndex];

  const scores = endData.breakdown;

  let seasonTotal = 0;

  for (const key of ["A", "B", "C", "D", "coins", "monsters"]) {
      if (scores[key] !== undefined) {
          const row = document.querySelector(`#${seasonId} .breakdown-row[data-key="${key}"] span`);
          if (row) {
              row.textContent = scores[key];
              seasonTotal += scores[key];
          }
      }
  }

  totalPoints += seasonTotal;
  document.getElementById("totalPoints").textContent = `Total: ${totalPoints}`;

  // Highlight next season
  const newSeasonIndex = endData.season % 4;
  highlightCurrentSeason(seasonNames[newSeasonIndex]);

  if (endData.gameOver) {
      console.log("Game Over!");
  }
}


export async function fetchSession() {
  try {
    const response = await fetch('https://cartographersstudy.onrender.com/api/session');
    const data = await response.json();

    setScoreTypes(data.scoreTypes);
    setCurrentSeason(data.currentSeason);
    setSeasonRemaining(data.seasonTime);
    setCurrentCard(data.currentCard);

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
  fetchSession();
  const playerToken = localStorage.getItem("playerToken"); // secure backend-issued token

  console.log("Current Card on submit:", currentCard);
  const payload = {
    new_grid: gridData.map(row => row.map(cell => String(cell))),
  };
  console.log("Submitting payload:", payload);

  try {
    const response = await fetch("https://cartographersstudy.onrender.com/api/validate", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${playerToken}`
      },
      body: JSON.stringify(payload)
    });

    const result = await response.json();

    if (!response.ok) {
      console.error("Server rejected move:", result);
      alert(result.detail || result.error || "Invalid move.");
    } else {
      console.log("Move validated:", result);
      localStorage.setItem("savedGrid", JSON.stringify(gridData));
      const response2 = await fetch ("https://cartographersstudy.onrender.com/api/coin-check", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${playerToken}`
        }
      });
      const result2 = await response2.json();
      if (!response2.ok) {
        console.error("Coin-check failed.", result2);
        alert(result2.detail || result2.error)
      } else {
        updateCoinTracker(result2.coins);
      }
    }
  } catch (err) {
    console.error("Validation failed:", err);
    alert("Network error during validation.");
  }
}

// Fetch a new card from the backend
let ruinsFlag = false;
let lastRuin = "";
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
      updateSeasonScores(endData);
    }


    const response = await fetch('https://cartographersstudy.onrender.com/api/draw-card', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${playerToken}`
        }
      });
    let currentCard = await response.json();

    // Refresh seasonRemaining
    await fetchSession();

    if (currentCard.error) {
      alert(currentCard.error);
      return;
    }

    // Handle Ruins card
    if (currentCard.type === "Ruins") {
      lastRuin = currentCard.id;
      // Immediately draw the next card
      const nextResponse = await fetch('https://cartographersstudy.onrender.com/api/draw-card', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${playerToken}`
        }
      });
      currentCard = await nextResponse.json();

      if (currentCard.error) {
        alert(currentCard.error);
        return;
      } 
      if (currentCard.type === "Ruins") {
        // Show ruins card name
        lastRuin = currentCard.id;
        // Immediately draw the next card
        const nextResponse = await fetch('https://cartographersstudy.onrender.com/api/draw-card', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${playerToken}`
        }
      });
        currentCard = await nextResponse.json();
        if (currentCard.error) {
          alert(currentCard.error);
          return;
        }
      }

      if (currentCard.type === "Standard") {
        alert("Ruins card drawn! The next shape must be placed on a Ruins tile.");
        document.getElementById("ruinsCardName").textContent = `Ruins Card: ${lastRuin}`;
        ruinsFlag = false;
        }

      // Show next card name below ruins card
      document.getElementById("activeCardName").textContent = `Card: ${currentCard.id}`;

      // Set up terrain and shape
      setAvailableShapes(currentCard.shape);
      setActiveShape(currentCard.shape[0]);
      terrain = currentCard.terrainOptions[0];
      await fetchSession();
      if (currentCard.cost === 1 && currentCard.shape.length > 1) {
        showShapeButtons(currentCard.shape);
        document.getElementById('terrain-buttons').style.display = 'none';
      } else if (currentCard.terrainOptions.length > 1) {
        showTerrainButtons(currentCard.terrainOptions);
        document.getElementById('shape-buttons').innerHTML = '';
        document.getElementById('terrain-buttons').style.display = '';
      } else {
        showTerrainButtons(currentCard.terrainOptions);
      }
      renderShapePreview(activeShape, terrain, currentCard.cost, seasonRemaining);
      placementLocked = false;
      lastPlacedCells = [];
      drawGrid();
      localStorage.setItem("currentCard", JSON.stringify(currentCard));
      return;
    } else {
      // Normal card flow
      if (ruinsFlag && currentCard.type === "Standard") {
        alert("Ruins card drawn! The next shape must be placed on a Ruins tile.");
        ruinsFlag = false;
        }

      document.getElementById("ruinsCardName").textContent = "";
      document.getElementById("activeCardName").textContent = `Card: ${currentCard.id}`;

      setAvailableShapes(currentCard.shape);
      setActiveShape(currentCard.shape[0]);
      terrain = currentCard.terrainOptions[0];

      if (currentCard.type === "Monster") {
        alert("Monster card drawn! This isn't functional at the moment but might be in 2 weeks.");
        terrain = "Monster";
        setAvailableShapes(currentCard.shape);
        setActiveShape(currentCard.shape[0]);
        document.getElementById("ruinsCardName").textContent = "";
        document.getElementById("activeCardName").textContent = `Card: ${currentCard.id}`;
        document.getElementById('terrain-buttons').style.display = 'none';

        renderShapePreview(activeShape, terrain, currentCard.cost, seasonRemaining);
        placementLocked = false;
        lastPlacedCells = [];
        drawGrid();
        localStorage.setItem("currentCard", JSON.stringify(currentCard));
        return;
      } else if (currentCard.cost === 1 && currentCard.shape.length > 1) {
        showShapeButtons(currentCard.shape);
        document.getElementById('terrain-buttons').style.display = 'none';
      } else if (currentCard.terrainOptions.length > 1) {
        showTerrainButtons(currentCard.terrainOptions);
        document.getElementById('shape-buttons').innerHTML = '';
        document.getElementById('terrain-buttons').style.display = '';
      } else {
        showTerrainButtons(currentCard.terrainOptions);
      }
    }
    renderShapePreview(activeShape, terrain, currentCard.cost, seasonRemaining);
    placementLocked = false;
    lastPlacedCells = [];
    drawGrid();
    localStorage.setItem("currentCard", JSON.stringify(currentCard));
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

document.addEventListener('DOMContentLoaded', function () {
  const startBtn = document.getElementById('startBtn');
  const drawBtn = document.getElementById('drawCardBtn');
  const submitBtn = document.getElementById('submitBtn');
  const undoBtn = document.getElementById('undoBtn');

  function showGameControls() {
    if (drawBtn) drawBtn.style.display = '';
    if (submitBtn) submitBtn.style.display = '';
    if (undoBtn) undoBtn.style.display = '';
    if (startBtn) startBtn.style.display = 'none';
  }

  function restoreSavedGrid() {
    const saved = localStorage.getItem("savedGrid");
    if (saved) {
      gridData = JSON.parse(saved);
      drawGrid();
    }
  }

  function restoreSavedCard() {
    const card = localStorage.getItem("currentCard");
    if (!card) return;

    setCurrentCard(JSON.parse(card));
    console.log("Loaded card from localStorage:", currentCard);

    document.getElementById("activeCardName").textContent = `Card: ${currentCard.id}`;
    if (currentCard.ruinFlag) {
      alert("You have a ruins card to place!");
    }

    setActiveShape(currentCard.shape[0]);
    setTerrain(currentCard.terrainOptions[0]);

    if (currentCard.type === "Monster") {
      alert("Monster card drawn! This isn't functional at the moment but might be in 2 weeks.");
      setTerrain("Monster");
      document.getElementById("ruinsCardName").textContent = "";
      document.getElementById("terrain-buttons").style.display = 'none';
    } else if (currentCard.cost === 1 && currentCard.shape.length > 1) {
      showShapeButtons(currentCard.shape);
      document.getElementById('terrain-buttons').style.display = 'none';
    } else if (currentCard.terrainOptions.length > 1) {
      showTerrainButtons(currentCard.terrainOptions);
      document.getElementById('shape-buttons').innerHTML = '';
      document.getElementById('terrain-buttons').style.display = '';
    } else {
      showTerrainButtons(currentCard.terrainOptions);
    }

    renderShapePreview(activeShape, terrain, currentCard.cost, seasonRemaining);
    setPlacementLocked(false);
    setLastPlacedCells([]);
    drawGrid();
  }

  function startGameFromSavedState() {
    showGameControls();
    setGameStarted(true);
    fetchSession();
    document.getElementById("scoringContainer").style.display = "";
    restoreSavedGrid();
    restoreSavedCard();
  }

  // Auto-start if saved grid exists
  if (localStorage.getItem("savedGrid")) {
    startGameFromSavedState();
  }
    // Hide controls initially
  if (drawBtn) drawBtn.style.display = 'none';
  if (submitBtn) submitBtn.style.display = 'none';
  if (undoBtn) undoBtn.style.display = 'none';

  // Manual start
  if (startBtn) {
    startBtn.addEventListener('click', function () {
      showGameControls();
      setGameStarted(true);
      fetchSession();
      document.getElementById("scoringContainer").style.display = "";
    });
  }

  // Button listeners
  if (drawBtn) drawBtn.addEventListener('click', drawCard);
  if (undoBtn) {
    undoBtn.addEventListener('click', function () {
      undoLastPlacement();
      placementLocked = false;
      drawGrid();
    });
  }
  if (gameStarted) {
    showGameControls();
  }
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
