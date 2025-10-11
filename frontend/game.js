const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const gridSize = 11;
const cellSize = canvas.width / gridSize;
let gridData = Array(gridSize * gridSize).fill(null);

function drawGrid() {
  for (let y = 0; y < gridSize; y++) {
    for (let x = 0; x < gridSize; x++) {
      const index = y * gridSize + x;
      ctx.fillStyle = getColor(gridData[index]);
      ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
      ctx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
    }
  }
}
function getColor(value) {
  if (value === "forest") return "#228B22";
  if (value === "water") return "#1E90FF";
  return "#1e1e1e";
}
drawGrid();