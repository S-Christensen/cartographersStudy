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
  setActiveShape,
  setHover,
  setLastPlacedCells,
  setPlacementLocked,
  submitMove,
  terrain
} from './game.js';

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

document.getElementById("submitBtn").addEventListener("click", () => {
  console.log("Submitting grid:", gridData);
  submitMove();
});

startBtn.addEventListener('click', async function () {
  try {
    const response = await fetch('https://cartographersstudy.onrender.com/api/reset-game', {
      method: 'POST'
    });
    const result = await response.json();
    console.log("Game reset:", result);
    const valid = await fetch('https://cartographersstudy.onrender.com/api/create-player', { method: "POST" });
    const { playerToken } = await valid.json();
    localStorage.setItem("playerToken", playerToken);

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