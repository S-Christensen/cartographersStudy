const TERRAIN_COLORS = {
  Forest: "#228B22",
  Village: "#8B0000",
  Water: "#1E90FF",
  Farm: "#DAA520",
  Mountain: "#A0522D",
  Monster: "#7a1f7a",
  Ruins: "#7f7f7f",
  "0": "#1f1813",
  0: "#1f1813",
};

const SEASON_NAMES = ["Spring", "Summer", "Autumn", "Winter"];
const SAMPLE_PATHS = [
  "../ml_logs/model_trace_716156.json",
  "/ml_logs/model_trace_716156.json",
  "./ml_logs/model_trace_716156.json",
  "../ml_logs/model_trace_43.json",
  "/ml_logs/model_trace_43.json",
  "./ml_logs/model_trace_43.json",
];

const MODEL_KEYS = ["equal_weights", "trained_color", "trained_position"];

const state = {
  payload: null,
  models: {
    equal_weights: { trace: [], data: null },
    trained_color: { trace: [], data: null },
    trained_position: { trace: [], data: null },
  },
  stepIndex: 0,
  timer: null,
  speed: 6,
};

function $(id) {
  return document.getElementById(id);
}

const elements = {
  toggleBtn: $("trainingToggleBtn"),
  panel: $("trainingPanel"),
  loadSampleBtn: $("trainingLoadSampleBtn"),
  fileInput: $("trainingFileInput"),
  playPauseBtn: $("trainingPlayPauseBtn"),
  stepBtn: $("trainingStepBtn"),
  speedRange: $("trainingSpeedRange"),
  progress: $("trainingProgress"),
  status: $("trainingStatus"),
  seed: $("trainingSeed"),
  stepValue: $("trainingStepValue"),
  season: $("trainingSeasonValue"),
  card: $("trainingCardValue"),
  move: $("trainingMoveValue"),
  timeline: $("trainingTimeline"),
};

// Create element references for each model's grid and score
const modelElements = {};
MODEL_KEYS.forEach((key) => {
  modelElements[key] = {
    grid: $(`trainingGrid-${key}`),
    score: $(`trainingScore-${key}`),
  };
});

function setStatus(text) {
  elements.status.textContent = text;
}

function setReplayPanelVisible(visible) {
  elements.panel.classList.toggle("is-hidden", !visible);
  if (elements.toggleBtn) {
    elements.toggleBtn.textContent = visible
      ? "Hide Model Training Replay"
      : "Show Model Training Replay";
  }
}

function sanitizeGrid(rawGrid) {
  if (!Array.isArray(rawGrid)) {
    return Array.from({ length: 11 }, () => Array(11).fill("0"));
  }
  return rawGrid.map((row) => {
    if (!Array.isArray(row)) {
      return Array(11).fill("0");
    }
    return row.map((cell) => String(cell));
  });
}

function drawGrid(gridElement, grid) {
  gridElement.innerHTML = "";
  const cleanGrid = sanitizeGrid(grid);
  for (let y = 0; y < cleanGrid.length; y += 1) {
    for (let x = 0; x < cleanGrid[y].length; x += 1) {
      const cell = document.createElement("div");
      const key = cleanGrid[y][x];
      cell.className = "training-cell";
      cell.title = key;
      cell.style.backgroundColor = TERRAIN_COLORS[key] || "#2d2d2d";
      gridElement.appendChild(cell);
    }
  }
}

function drawAllGrids(stepIndex) {
  MODEL_KEYS.forEach((modelKey) => {
    const trace = state.models[modelKey].trace;
    if (trace.length && stepIndex < trace.length) {
      const step = trace[stepIndex];
      drawGrid(modelElements[modelKey].grid, step.grid_after);
    }
  });
}

function stopPlayback() {
  if (state.timer !== null) {
    clearInterval(state.timer);
    state.timer = null;
  }
  elements.playPauseBtn.textContent = "Play";
}

function stepForward() {
  const maxSteps = Math.max(
    ...MODEL_KEYS.map((key) => state.models[key].trace.length)
  );
  if (!maxSteps) {
    return;
  }
  if (state.stepIndex >= maxSteps - 1) {
    stopPlayback();
    return;
  }
  state.stepIndex += 1;
  renderCurrentStep();
}

function startPlayback() {
  const maxSteps = Math.max(
    ...MODEL_KEYS.map((key) => state.models[key].trace.length)
  );
  if (!maxSteps) {
    return;
  }
  stopPlayback();
  elements.playPauseBtn.textContent = "Pause";
  const intervalMs = Math.max(40, Math.round(1400 / state.speed));
  state.timer = setInterval(stepForward, intervalMs);
}

function renderTimeline() {
  const canvas = elements.timeline;
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  ctx.clearRect(0, 0, width, height);

  ctx.strokeStyle = "#66512f";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(10, height - 30);
  ctx.lineTo(width - 10, height - 30);
  ctx.stroke();

  // Get the maximum trace length to establish scale
  const maxSteps = Math.max(
    ...MODEL_KEYS.map((key) => state.models[key].trace.length)
  );
  if (!maxSteps) {
    return;
  }

  // Draw timeline for each model
  const modelColors = {
    equal_weights: "#8866ff",
    trained_color: "#ff8866",
    trained_position: "#66ff88",
  };

  const rowHeight = (height - 60) / 3;

  MODEL_KEYS.forEach((modelKey, idx) => {
    const trace = state.models[modelKey].trace;
    const startY = 20 + idx * rowHeight;

    // Draw model label
    ctx.fillStyle = "#d2ba8a";
    ctx.font = "11px serif";
    ctx.fillText(modelKey, 12, startY + 12);

    // Draw trace line
    ctx.strokeStyle = modelColors[modelKey];
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(10, startY + 18);
    ctx.lineTo(width - 10, startY + 18);
    ctx.stroke();

    // Draw step indicators and deviations
    const stepWidth = (width - 20) / Math.max(1, maxSteps - 1);
    for (let i = 0; i < trace.length; i += 1) {
      const step = trace[i];
      const x = 10 + i * stepWidth;

      if (step.is_first_deviation) {
        ctx.fillStyle = "#f04f4f";
      } else if (step.deviates_from_equal) {
        ctx.fillStyle = "#d9842b";
      } else {
        ctx.fillStyle = modelColors[modelKey];
      }

      const r = i === state.stepIndex ? 4 : 2.5;
      ctx.beginPath();
      ctx.arc(x, startY + 18, r, 0, Math.PI * 2);
      ctx.fill();
    }
  });

  // Draw legend at bottom
  ctx.fillStyle = "#d2ba8a";
  ctx.font = "10px serif";
  const legendStart = height - 18;
  ctx.fillText("● Green=baseline  ● Orange=deviation  ● Red=first deviation", 12, legendStart);

  // Draw current position indicator
  if (maxSteps > 1) {
    const x = 10 + (state.stepIndex / (maxSteps - 1)) * (width - 20);
    ctx.strokeStyle = "#c9a94d";
    ctx.lineWidth = 2;
    ctx.globalAlpha = 0.6;
    ctx.beginPath();
    ctx.moveTo(x, 5);
    ctx.lineTo(x, height - 25);
    ctx.stroke();
    ctx.globalAlpha = 1.0;
  }
}

function renderCurrentStep() {
  const maxSteps = Math.max(
    ...MODEL_KEYS.map((key) => state.models[key].trace.length)
  );
  if (!maxSteps) {
    return;
  }

  // Use the first model's step as reference for shared metadata
  const referenceTrace = state.models.equal_weights.trace;
  const step = referenceTrace[state.stepIndex] || {};

  elements.stepValue.textContent = `${state.stepIndex + 1} / ${maxSteps}`;
  elements.season.textContent = SEASON_NAMES[step.season] || `S${step.season}`;
  elements.card.textContent = step.card?.id || "-";
  elements.move.textContent = step.move_type || "-";

  elements.progress.value = String(state.stepIndex);
  drawAllGrids(state.stepIndex);
  renderTimeline();
}

function configureModels(payload) {
  if (!payload?.results) {
    throw new Error("Invalid payload: missing results.");
  }

  setReplayPanelVisible(true);
  stopPlayback();

  // Load all three models
  MODEL_KEYS.forEach((modelKey) => {
    const modelData = payload.results[modelKey];
    if (!modelData || !Array.isArray(modelData.trace)) {
      console.warn(`Model ${modelKey} trace not available.`);
      state.models[modelKey] = { trace: [], data: null };
    } else {
      state.models[modelKey].trace = modelData.trace;
      state.models[modelKey].data = modelData;
      modelElements[modelKey].score.textContent = String(modelData.score ?? "-");
    }
  });

  state.stepIndex = 0;

  const maxSteps = Math.max(
    ...MODEL_KEYS.map((key) => state.models[key].trace.length)
  );

  elements.seed.textContent = String(payload.seed ?? "-");
  elements.progress.max = String(Math.max(0, maxSteps - 1));
  elements.progress.value = "0";
  elements.progress.disabled = maxSteps === 0;
  elements.playPauseBtn.disabled = maxSteps === 0;
  elements.stepBtn.disabled = maxSteps === 0;

  setStatus(
    maxSteps > 0 ? `Loaded all models (${maxSteps} steps)` : "No trace data available."
  );
  renderCurrentStep();
}

async function fetchFirstAvailable(paths) {
  let lastError = null;
  for (const path of paths) {
    try {
      const response = await fetch(path);
      if (!response.ok) {
        continue;
      }
      return await response.json();
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError || new Error("No sample trace file found.");
}

async function loadSampleTrace() {
  setStatus("Loading sample trace...");
  try {
    const payload = await fetchFirstAvailable(SAMPLE_PATHS);
    state.payload = payload;
    configureModels(payload);
  } catch (error) {
    setStatus("Sample trace unavailable; use Load JSON.");
    console.error("Failed to load sample trace:", error);
  }
}

function loadTraceFromFile(file) {
  const reader = new FileReader();
  setStatus("Reading local trace file...");

  reader.onload = () => {
    try {
      const payload = JSON.parse(String(reader.result));
      state.payload = payload;
      configureModels(payload);
    } catch (error) {
      setStatus("Invalid JSON file.");
      console.error("Invalid trace JSON:", error);
    }
  };

  reader.onerror = () => {
    setStatus("Failed to read file.");
  };

  reader.readAsText(file);
}

function initializeReplayToggle() {
  setReplayPanelVisible(false);
  if (!elements.toggleBtn) {
    return;
  }
  elements.toggleBtn.addEventListener("click", () => {
    const shouldShow = elements.panel.classList.contains("is-hidden");
    setReplayPanelVisible(shouldShow);
  });
}

function init() {
  if (!elements.panel) {
    return;
  }

  initializeReplayToggle();

  elements.loadSampleBtn.addEventListener("click", loadSampleTrace);

  elements.fileInput.addEventListener("change", (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    loadTraceFromFile(file);
  });

  elements.playPauseBtn.addEventListener("click", () => {
    const maxSteps = Math.max(
      ...MODEL_KEYS.map((key) => state.models[key].trace.length)
    );
    if (!maxSteps) {
      return;
    }
    if (state.timer === null) {
      startPlayback();
    } else {
      stopPlayback();
    }
  });

  elements.stepBtn.addEventListener("click", () => {
    stopPlayback();
    stepForward();
  });

  elements.speedRange.addEventListener("input", (event) => {
    state.speed = Number(event.target.value || 6);
    if (state.timer !== null) {
      startPlayback();
    }
  });

  elements.progress.addEventListener("input", (event) => {
    const maxSteps = Math.max(
      ...MODEL_KEYS.map((key) => state.models[key].trace.length)
    );
    const nextIndex = Number(event.target.value || 0);
    state.stepIndex = Math.max(0, Math.min(nextIndex, maxSteps - 1));
    stopPlayback();
    renderCurrentStep();
  });

  setStatus("Load a sample or JSON trace to start.");
  drawAllGrids(0);
  renderTimeline();
}

init();
