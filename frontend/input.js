import {
  activeShape,
  canPlaceAt,
  canvas,
  cellSize,
  drawCard,
  drawGrid,
  fetchSession,
  gridData,
  hoverX,
  hoverY,
  placementLocked,
  setActiveShape,
  setGameStarted,
  setHover,
  setLastPlacedCells,
  setPlacementLocked,
  showGameControls,
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
  submitBtn.disabled=true;
  undoBtn.disabled=true;
  submitMove();
});

document.getElementById("reset-button").addEventListener("click", () => {
  console.log("Wiping local storage");
  localStorage.clear();
});

roomCodeInput.addEventListener('input', function () {
  joinBtn.disabled = roomCodeInput.value.trim() === '';
});

joinBtn.addEventListener('click', async function () {
  const code = roomCodeInput.value.trim();
  const roomSize = parseInt(document.getElementById("roomSizeInput").value, 10);''

  if (!code || !roomSize) {
    alert("Please enter a room code and room size!");
    return;
  }

  try {
    alert("Joining game with room code:", code, "room size:", roomSize);
    joinBtn.disabled = true;
    /*
    const response = await fetch('https://cartographersstudy.onrender.com/api/reset-game', {
      method: 'POST'
    });
    const result = await response.json();
    console.log("Game reset:", result);
    */

    // Create player
    const valid = await fetch('https://cartographersstudy.onrender.com/api/create-player', {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ roomCode: code, roomSize})
    });
    const { playerToken } = await valid.json();
    localStorage.setItem("playerToken", playerToken);
    localStorage.setItem("roomCode", code);

    showGameControls();
    setGameStarted(true);
    fetchSession();
    document.getElementById("scoringContainer").style.display = "";
    /*
    alert("Waiting for others to join.")
    let locked = true
    while (locked) {
      const temp = await fetch('https://cartographersstudy.onrender.com/api/busywait' , {
        method: "POST",
        headers: { "Content-Type": "application/json", 'Authorization': `Bearer ${playerToken}` },
        body: JSON.stringify({ roomCode: code})
      });
      const temp2 = await temp.json()
      locked = temp2.locked;
    }*/

    drawCard();
  } catch (err) {
    console.error("Failed to join game:", err);
    alert("Error joining game: " + err.message);
    joinBtn.disabled = false;
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
    submitBtn.disabled = false;
    undoBtn.disabled = false;
  }
});