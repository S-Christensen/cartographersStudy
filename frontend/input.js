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

// Drag/drop logic placeholder
canvas.addEventListener("click", (e) => {
  const x = Math.floor(e.offsetX / cellSize);
  const y = Math.floor(e.offsetY / cellSize);
  placeShapeAt(x, y);
});

function placeShapeAt(x, y) {
  for (let dy = 0; dy < activeShape.length; dy++) {
    for (let dx = 0; dx < activeShape[0].length; dx++) {
      if (activeShape[dy][dx]) {
        const gx = x + dx;
        const gy = y + dy;
        if (gx < gridSize && gy < gridSize) {
          gridData[gy][gx] = terrain;
        }
      }
    }
  }
  drawGrid();
}

document.getElementById("submitBtn").addEventListener("click", () => {
  console.log("Submitting grid:", gridData);
  // TODO: send gridData to backend for validation
});