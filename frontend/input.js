import {
  activeShape,
  canPlaceAt,
  drawGrid,
  gridData,
  lastPlacedCells,
  placementLocked,
  setLastPlacedCells,
  setPlacementLocked,
  terrain
} from './game.js';

document.addEventListener("keydown", (e) => {
  if (e.key === "q") rotateLeft();
  if (e.key === "e") rotateRight();
  if (e.key === "f") flipShape();
});

function rotateLeft() {
  activeShape = rotateMatrix(activeShape, -1);
  drawGrid();
}

function rotateRight() {
  activeShape = rotateMatrix(activeShape, 1);
  drawGrid();
}

function flipShape() {
  activeShape = activeShape.map(row => [...row].reverse());
  drawGrid();
}

function rotateMatrix(matrix, direction) {
  const rotated = direction === 1
    ? matrix[0].map((_, i) => matrix.map(row => row[i]).reverse())
    : matrix[0].map((_, i) => matrix.map(row => row[row.length - 1 - i]));
  return rotated;
}

function placeShapeAt(x, y) {
  if (placementLocked || !canPlaceAt(x, y)) return;

  const placed = [];

  for (let dy = 0; dy < activeShape.length; dy++) {
    for (let dx = 0; dx < activeShape[0].length; dx++) {
      if (activeShape[dy][dx]) {
        const gx = x + dx;
        const gy = y + dy;
        if (gx < gridSize && gy < gridSize) {
          gridData[gy][gx] = terrain;
          placed.push([gy, gx]);
        }
      }
    }
  }

  setLastPlacedCells(placed);
  setPlacementLocked(true);
  drawGrid();
}

document.getElementById("submitBtn").addEventListener("click", () => {
  console.log("Submitting grid:", gridData);
  // TODO: send gridData to backend for validation
});

let hoverX = null;
let hoverY = null;

canvas.addEventListener("mousemove", (e) => {
  const rect = canvas.getBoundingClientRect();
  const x = Math.floor((e.clientX - rect.left) / cellSize);
  const y = Math.floor((e.clientY - rect.top) / cellSize);

  if (x !== hoverX || y !== hoverY) {
    hoverX = x;
    hoverY = y;
    drawGrid(); // triggers preview
  }
});

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