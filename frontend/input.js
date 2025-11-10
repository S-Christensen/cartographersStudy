import {
  activeShape,
  canPlaceAt,
  canvas,
  cellSize,
  drawCard,
  drawGrid,
  gridData,
  hoverX,
  hoverY,
  placementLocked,
  seasonRemaining,
  setActiveShape,
  setHover,
  setLastPlacedCells,
  setPlacementLocked,
  submitMove,
  terrain
} from './game.js';
import { renderShapePreview, showShapeButtons, showTerrainButtons } from './ui.js';

document.addEventListener("keydown", (e) => {
  if (e.key === "q") rotateLeft();
  if (e.key === "e") rotateRight();
  if (e.key === "f") flipShape();
});

function rotateLeft() {
  setActiveShape(rotateMatrix(activeShape, -1));
  drawGrid();
}

function rotateRight() {
  setActiveShape(rotateMatrix(activeShape, 1));
  drawGrid();
}

function flipShape() {
  setActiveShape(activeShape.map(row => [...row].reverse()));
  drawGrid();
}

function rotateMatrix(matrix, direction) {
  const rotated = direction === 1
    ? matrix[0].map((_, i) => matrix.map(row => row[i]).reverse())
    : matrix[0].map((_, i) => matrix.map(row => row[row.length - 1 - i]));
  return rotated;
}

window.addEventListener("DOMContentLoaded", () => {
  const grid = localStorage.getItem("savedGrid");
  const startBtn = document.getElementById('startBtn');
  const drawBtn = document.getElementById('drawCardBtn');
  const submitBtn = document.getElementById('submitBtn');
  const undoBtn = document.getElementById('undoBtn');

  if (drawBtn) drawBtn.style.display = '';
  if (submitBtn) submitBtn.style.display = '';
  if (undoBtn) undoBtn.style.display = '';
  if (startBtn) startBtn.style.display = 'none';

  if (grid) {
    let gridData = JSON.parse(grid);
    drawGrid();
  }
  const card = localStorage.getItem("currentCard");
  if (card) {
    let currentCard = JSON.parse(card);
    console.log("Loaded card from localStorage:", currentCard);
    if (currentCard.flag) {
      alert("You have a ruins card to place!");
      document.getElementById("activeCardName").textContent = `Card: ${currentCard.id}`;
      currentCard.flag = true;

      // Set up terrain and shape
      setActiveShape(currentCard.shape[0]);
      let terrain = currentCard.terrainOptions[0];
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
      let placementLocked = false;
      let lastPlacedCells = [];
      drawGrid();
    } else {
      document.getElementById("ruinsCardName").textContent = "";
      document.getElementById("activeCardName").textContent = `Card: ${currentCard.id}`;

      setActiveShape(currentCard.shape[0]);
      let terrain = currentCard.terrainOptions[0];

      if (currentCard.type === "Monster") {
        alert("Monster card drawn! This isn't functional at the moment but might be in 2 weeks.");
        let terrain = "Monster";
        setActiveShape(currentCard.shape[0]);
        document.getElementById("ruinsCardName").textContent = "";
        document.getElementById("activeCardName").textContent = `Card: ${currentCard.id}`;
        document.getElementById('terrain-buttons').style.display = 'none';

        renderShapePreview(activeShape, terrain, currentCard.cost, seasonRemaining);
        let placementLocked = false;
        let lastPlacedCells = [];
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
      renderShapePreview(activeShape, terrain, currentCard.cost, seasonRemaining);
      let placementLocked = false;
      let lastPlacedCells = [];
      drawGrid();
    }
  }
});

document.getElementById("submitBtn").addEventListener("click", () => {
  console.log("Submitting grid:", gridData);
  // TODO: send gridData to backend for validation
  submitMove();
});

startBtn.addEventListener('click', async function () {
  try {
    const response = await fetch('https://cartographersstudy.onrender.com/api/reset-game', {
      method: 'POST'
    });
    const result = await response.json();
    console.log("Game reset:", result);

    drawCard();
  } catch (err) {
    console.error("Failed to reset game:", err);
    alert("Error resetting game: " + err.message);
  }
});

canvas.addEventListener("mousemove", (e) => {
  const rect = canvas.getBoundingClientRect();
  const x = Math.floor((e.clientX - rect.left) / cellSize);
  const y = Math.floor((e.clientY - rect.top) / cellSize);

  if (x !== hoverX || y !== hoverY) {
    setHover(x, y);
    drawGrid();
  }
});

canvas.addEventListener("click", () => {
  if (placementLocked) return;
  if (hoverX === null || hoverY === null) return;
  if (canPlaceAt(hoverX, hoverY)) {
    const placed = [];
    for (let dy = 0; dy < activeShape.length; dy++) {
      for (let dx = 0; dx < activeShape[0].length; dx++) {
        if (activeShape[dy][dx]) {
          const gx = hoverX + dx;
          const gy = hoverY + dy;
          gridData[gy][gx] = terrain;
          placed.push([gy, gx]);
        }
      }
    }
    setLastPlacedCells(placed);
    setPlacementLocked(true);
    drawGrid();
  }
});