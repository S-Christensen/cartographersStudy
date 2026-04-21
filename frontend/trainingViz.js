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
  "../ml_logs/model_trace_43.json",
  "/ml_logs/model_trace_43.json",
  "./ml_logs/model_trace_43.json",
];

const state = {
  payload: null,
  activeModelKey: "equal_weights",
  trace: [],
  stepIndex: 0,
  timer: null,
  speed: 6,
};

function $(id) {
  return document.getElementById(id);
}

const elements = {
  panel: $("trainingPanel"),
  modelSelect: $("trainingModelSelect"),
  loadSampleBtn: $("trainingLoadSampleBtn"),
  fileInput: $("trainingFileInput"),
  playPauseBtn: $("trainingPlayPauseBtn"),
  stepBtn: $("trainingStepBtn"),
  speedRange: $("trainingSpeedRange"),
  progress: $("trainingProgress"),
  status: $("trainingStatus"),
  seed: $("trainingSeed"),
  score: $("trainingScore"),
  stepValue: $("trainingStepValue"),
  season: $("trainingSeasonValue"),
  card: $("trainingCardValue"),
  move: $("trainingMoveValue"),
  coins: $("trainingCoinsValue"),
  time: $("trainingTimeValue"),
  grid: $("trainingGrid"),
  timeline: $("trainingTimeline"),
};

function setStatus(text) {
  elements.status.textContent = text;
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

function drawGrid(grid) {
  elements.grid.innerHTML = "";
  const cleanGrid = sanitizeGrid(grid);
  for (let y = 0; y < cleanGrid.length; y += 1) {
    for (let x = 0; x < cleanGrid[y].length; x += 1) {
      const cell = document.createElement("div");
      const key = cleanGrid[y][x];
      cell.className = "training-cell";
      cell.title = key;
      cell.style.backgroundColor = TERRAIN_COLORS[key] || "#2d2d2d";
      elements.grid.appendChild(cell);
    }
  }
}

function getModelData(payload, modelKey) {
  return payload?.results?.[modelKey] ?? null;
}

function stopPlayback() {
  if (state.timer !== null) {
    clearInterval(state.timer);
    state.timer = null;
  }
  elements.playPauseBtn.textContent = "Play";
}

function stepForward() {
  if (!state.trace.length) {
    return;
  }
  if (state.stepIndex >= state.trace.length - 1) {
    stopPlayback();
    return;
  }
  state.stepIndex += 1;
  renderCurrentStep();
}

function startPlayback() {
  if (!state.trace.length) {
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
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(10, height - 24);
  ctx.lineTo(width - 10, height - 24);
  ctx.stroke();

  const trace = state.trace;
  if (!trace.length) {
    return;
  }

  const stepWidth = (width - 20) / Math.max(1, trace.length - 1);
  for (let i = 0; i < trace.length; i += 1) {
    const step = trace[i];
    const x = 10 + i * stepWidth;
    const y = height - 24;

    if (step.is_first_deviation) {
      ctx.fillStyle = "#f04f4f";
    } else if (step.deviates_from_equal) {
      ctx.fillStyle = "#d9842b";
    } else {
      ctx.fillStyle = "#77ba66";
    }

    const r = i === state.stepIndex ? 5 : 3;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  }

  ctx.fillStyle = "#d2ba8a";
  ctx.font = "12px serif";
  ctx.fillText("Green = same as equal weights", 12, 16);
  ctx.fillText("Orange = deviation", 12, 32);
  ctx.fillText("Red = first deviation", 12, 48);
}

function renderCurrentStep() {
  if (!state.trace.length) {
    return;
  }

  const step = state.trace[state.stepIndex];
  elements.stepValue.textContent = `${state.stepIndex + 1} / ${state.trace.length}`;
  elements.season.textContent = SEASON_NAMES[step.season] || `S${step.season}`;
  elements.card.textContent = step.card?.id || "-";
  elements.move.textContent = step.move_type || "-";
  elements.coins.textContent = String(step.coins_after ?? "-");
  elements.time.textContent = String(step.season_time_after ?? "-");

  elements.progress.value = String(state.stepIndex);
  drawGrid(step.grid_after);
  renderTimeline();
}

function configureModel(payload, modelKey) {
  const modelData = getModelData(payload, modelKey);
  if (!modelData || !Array.isArray(modelData.trace)) {
    throw new Error(`Trace data missing for model '${modelKey}'.`);
  }

  stopPlayback();
  state.activeModelKey = modelKey;
  state.trace = modelData.trace;
  state.stepIndex = 0;

  elements.seed.textContent = String(payload.seed ?? "-");
  elements.score.textContent = String(modelData.score ?? "-");
  elements.progress.max = String(Math.max(0, state.trace.length - 1));
  elements.progress.value = "0";
  elements.progress.disabled = state.trace.length === 0;
  elements.playPauseBtn.disabled = state.trace.length === 0;
  elements.stepBtn.disabled = state.trace.length === 0;

  setStatus(`Loaded ${modelKey} (${state.trace.length} steps)`);
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
    configureModel(payload, elements.modelSelect.value);
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
      configureModel(payload, elements.modelSelect.value);
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

function init() {
  if (!elements.panel) {
    return;
  }

  elements.modelSelect.addEventListener("change", () => {
    if (!state.payload) {
      return;
    }
    try {
      configureModel(state.payload, elements.modelSelect.value);
    } catch (error) {
      setStatus("Selected model trace not available in file.");
      console.error(error);
    }
  });

  elements.loadSampleBtn.addEventListener("click", loadSampleTrace);

  elements.fileInput.addEventListener("change", (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    loadTraceFromFile(file);
  });

  elements.playPauseBtn.addEventListener("click", () => {
    if (!state.trace.length) {
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
    const nextIndex = Number(event.target.value || 0);
    state.stepIndex = Math.max(0, Math.min(nextIndex, state.trace.length - 1));
    stopPlayback();
    renderCurrentStep();
  });

  setStatus("Load a sample or JSON trace to start.");
  drawGrid(Array.from({ length: 11 }, () => Array(11).fill("0")));
  renderTimeline();
}

init();
