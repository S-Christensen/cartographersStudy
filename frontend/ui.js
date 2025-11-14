import { activeShape, currentCard, drawGrid, seasonRemaining, setActiveShape, setTerrain, terrain } from './game.js';

export function showShapeButtons(shapes) {
  const container = document.getElementById('shape-buttons');
  container.innerHTML = '';

  shapes.forEach((shape, index) => {
    const btn = document.createElement('button');
    if (index === 0) btn.textContent = 'Shape + Coin';
    else btn.textContent = `Shape`;
    btn.addEventListener('click', () => {
      setActiveShape(shape);
      renderShapePreview(shape, terrain, currentCard.cost, seasonRemaining);
      drawGrid();
    });
    container.appendChild(btn);
  });
}

export function getColor(terrain) {
  const colors = {
    Forest: "#228B22",
    Village: "#8B0000",
    Water: "#1E90FF",
    Farm: "#DAA520",
    Mountain: "#a0522d",
    Monster: "#800080"
  };
  return colors[terrain] || "#000000";
}

export function renderShapePreview(shape, terrain, cost = null, seasonRemaining = null) {
  const preview = document.getElementById("shapePreview");
  preview.innerHTML = "";

  if (cost !== null || seasonRemaining !== null) {
    const costLabel = document.createElement("div");
    costLabel.className = "shape-cost";

    let text = "";
    if (cost !== null) text += `Card Cost: ${cost}`;
    if (seasonRemaining !== null) text += ` | Season Remaining: ${seasonRemaining}`;

    costLabel.textContent = text;
    preview.appendChild(costLabel);
  }

  shape.forEach(row => {
    const rowDiv = document.createElement("div");
    rowDiv.className = "shape-row";
    row.forEach(cell => {
      const div = document.createElement("div");
      div.className = "shape-cell";
      if (cell) div.style.backgroundColor = getColor(terrain);
      rowDiv.appendChild(div);
    });
    preview.appendChild(rowDiv);
  });
}

function formatName(name) {
  if (typeof name !== "string") return "Unknown";
  return name
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, match => match.toUpperCase());
}

export function renderScoringCards(scoreNames, currentSeason) {
  if (!Array.isArray(scoreNames) || scoreNames.length === 0) return;
  const container = document.getElementById("scoringDisplay");
  container.innerHTML = "";
  const letters = 'ABCD';

  const cardWidth = 682;
  const cardHeight = 948;

  scoreNames.forEach((card, index) => {
    const div = document.createElement("div");
    div.className = "scoring-card";
    if (index !== currentSeason && index !== (currentSeason + 1) % 4) {
      div.classList.add("inactive");
    }
    const green = ["sentinelWood", "greenbough", "treetower", "stonesideForest"];
    const blue = ["canalLake", "magesValley", "goldenGranary", "shoresideExpanse"];
    const red = ["wildholds", "greatCity", "greengoldPlains", "shieldgate"];
    const misc = ["borderlands", "lostBarony", "brokenRoad", "cauldrons"];
    
    let file;
    let scoreIndex;
    if (green.includes(card)) {
      file = "src/green.png";
      scoreIndex = green.indexOf(card);
    } else if (blue.includes(card)) {
      file = "src/blue.png";
      scoreIndex = blue.indexOf(card);
    } else if (red.includes(card)) {
      file = "src/red.png";
      scoreIndex = red.indexOf(card);
    } else {
      file = "src/misc.png";
      scoreIndex = misc.indexOf(card);
    }

    let row, col;
    if (scoreIndex < 3) {
      row = 0;
      col = scoreIndex;
    } else {
      row = 1;
      col = 0;
    }

    const offsetX = -(col * cardWidth);
    const offsetY = -(row * cardHeight);

    const label = document.createElement("span");
    label.textContent = `${letters[index]}: ${formatName(card)}`;
    div.appendChild(label);

    const preview = document.createElement("div");
    preview.className = "scoring-preview";
    preview.style.backgroundImage = `url("${file}")`;
    preview.style.backgroundPosition = `${offsetX}px ${offsetY}px`;
    div.appendChild(preview);
    container.appendChild(div);
  });
}

  export function showTerrainButtons(allowedTerrains) {
    const container = document.getElementById('terrain-buttons');
    container.innerHTML = '';
    allowedTerrains.forEach(type => {
      const btn = document.createElement('button');
      btn.textContent = type.charAt(0).toUpperCase() + type.slice(1);
      btn.className = 'terrain-btn ' + type;
      btn.dataset.color = type;
      btn.addEventListener('click', () => {
        setTerrain(type);
        renderShapePreview(activeShape, type, currentCard.cost, seasonRemaining);
      });
      container.appendChild(btn);
    });
  }

export function highlightCurrentSeason(seasonId) {
    const seasons = ['spring', 'summer', 'autumn', 'winter'];
  document.querySelectorAll('.season').forEach(div => {
    div.classList.remove('current-season');
  });
  const current = document.getElementById(seasons[seasonId]);
  if (current) current.classList.add('current-season');
}

export function updateCoinTracker(coinsEarned) {
  const coins = document.querySelectorAll(".coin");
  coins.forEach((coin, index) => {
    if (index < coinsEarned) {
      coin.classList.add("active");
    } else {
      coin.classList.remove("active");
    }
  });
}
/*
export function updateSeasonScores(endData) {
    if (!endData || endData.season === undefined) {
        console.warn("updateSeasonScores called without valid endData");
        return;
    }

    if (!endData.breakdown) {
        console.warn("No breakdown returned (likely game over).");
        return;
    }

    const seasonNames = ["spring", "summer", "autumn", "winter"];
    const seasonFinishedIndex = (endData.season - 1 + 4) % 4;
    const seasonFinishedName = seasonNames[seasonFinishedIndex];

    const seasonDiv = document.getElementById(seasonFinishedName);
    if (!seasonDiv) return;

    const breakdown = endData.breakdown;

    Object.entries(breakdown).forEach(([key, value]) => {
        if (key === "total") return;

        const row = seasonDiv.querySelector(`.breakdown-row[data-key="${key}"] span`);
        if (row) {
            row.textContent = value;
        }
    });

    // Update total points
    const totalDiv = document.getElementById("totalPoints");
    if (totalDiv) {
        totalDiv.textContent = `Total: ${endData.total}`;
    }

    // Highlight the new season
    const newSeasonName = seasonNames[endData.season];
    highlightCurrentSeason(newSeasonName);
}*/