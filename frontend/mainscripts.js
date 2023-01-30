const colors = [
  "#df5f5f",
  "#df9d5f",
  "#d7df5f",
  "#79df5f",
  "#5fdfbf",
  "#5f61df",
  "#a55fdf",
  "#df5faa",
];
const charts = [];

// EMG Charts
for (let idx = 0; idx < 8; idx++) {
  const ctx = document.getElementById(`stream-${idx + 1}`);

  const chart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: [
        {
          data: [],
          borderWidth: 2,
          backgroundColor: colors[idx],
          borderColor: colors[idx],
        },
      ],
    },
    options: {
      indexAxis: "x",
      showLine: true,
      animation: false,
      parsing: false,
      normalized: true,
      maintainAspectRatio: false,
      responsive: true,
      plugins: {
        decimation: {
          algorithm: "lttb",
          samples: 500,
          threshold: 500,
          enabled: true,
        },
        legend: { display: false },
        tooltips: { enabled: false },
      },
      elements: { point: { radius: 0 } },
      scales: {
        x: {
          type: "linear",
          beginAtZero: true,
          min: 0,
          max: 2499,
          ticks: { display: false },
        },
        y: {
          ticks: { display: false },
          beginAtZero: true,
          min: -3000,
          max: 3000,
        },
      },
    },
  });

  ctx.addEventListener("wheel", (event) => {
    const delta = Math.sign(event.deltaY);
    zoom(chart, delta);
    event.preventDefault();
  });

  charts.push(chart);
}

function addToCharts(data) {
  for (let idx = 0; idx < 8; idx++) {
    curve = [];
    for (let i = 0; i < data[idx].length; i++) {
      channelData = data[idx][i];
      curve.push({ x: i, y: channelData });
    }
    charts[idx].data.datasets[0].data = curve;
    charts[idx].update();
  }
}

const startingSpinner = document.getElementById("startingSpinner");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");

function setState(state) {
  document.getElementById("error").innerText = "";
  document.getElementById("state").innerText = state;

  if (state == "Idle" || state == "Error") {
    startBtn.style.display = "initial";
    stopBtn.style.display = "none";
    startingSpinner.style.display = "none";
    startBtn.disabled = false;
  } else if (state == "Starting") {
    startBtn.disabled = true;
    startingSpinner.style.display = "inline-block";
  } else if (state == "Running") {
    startBtn.disabled = false;
    startingSpinner.style.display = "none";
    startBtn.style.display = "none";
    stopBtn.style.display = "initial";
  }
}

// Action buttons
function startSession() {
  const port = document.getElementById("port").value;
  eel.start_session(port);
}

function stopSession() {
  eel.stop_session();
}

function zoomAll(delta) {
  charts.forEach((chart) => zoom(chart, -delta));
}

function zoom(chart, delta) {
  // reset zoom
  if (delta == 0) {
    chart.options.scales.y.max = 3000;
    chart.options.scales.y.min = -3000;
    return;
  }

  // zoom in: +15% | zoom out: -20
  let scroll = 0;
  if (delta < 0) scroll = -delta * 15 * (chart.options.scales.y.max / 100);
  else scroll = -delta * 20;
  if ((scroll > 0 && chart.options.scales.y.max > 5) || scroll <= 0) {
    chart.options.scales.y.max -= scroll;
    chart.options.scales.y.min += scroll;
  }
}

function startRecording() {
  const wps = document.getElementById("wps").value;
  const period = document.getElementById("period").value;
  const includeSilence = document.getElementById("includeSilence").checked;
  const includeFallback = document.getElementById("includeFallback").checked;
  const words = Array.from(document.getElementById("lang").options).map(e => e.text)
  eel.start_recording(wps, period, includeSilence, includeFallback, words)
}

function setRecording(loopCount, totalLoops) {
  const active = loopCount != totalLoops;
  document.getElementById("window-recording").style.setProperty("display", active ? "flex" : "none", "important")
  document.getElementById("window-main").style.setProperty("display", active ? "none" : "block", "important")
  document.getElementById("progress").style.setProperty("--progress", loopCount/totalLoops)
  document.getElementById("percentage").innerText = Math.trunc(loopCount/totalLoops*100)
}

function parseWord(word) {
  const fallbacks = Array.from(document.getElementById("fallbacks").options).map(e => e.text);

  if (word == "$PREPARE") return prepare();
  else if (word == "$SILENCE") return " ";
  else if (word == "$FALLBACK") return fallbacks[Math.floor(Math.random() * fallbacks.length)];
  else return word;
}

function prepare() {
  setTimeout(() => document.getElementById("percentage").innerText = "3", 0000)
  setTimeout(() => document.getElementById("percentage").innerText = "2", 1000)
  setTimeout(() => document.getElementById("percentage").innerText = "1", 2000)
  return "Prepare...";
}

function showFallbacks(checkbox) {
  const active = checkbox.checked
  if (active) document.getElementById("fallbacks-section").classList.remove("d-none")
  else document.getElementById("fallbacks-section").classList.add("d-none")
}

// Bootstrap
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

// Events
(() => {
  const ratioSlider = document.getElementById("trainingratio");
  const ratioPercent = document.getElementById("trainingratio-percent");
  
  ratioSlider.oninput = () => {
    ratioPercent.innerText = `${ratioSlider.value}%`;
    ratioSlider.style.setProperty("--ratio", ratioSlider.value)
  }
})()

// Eel Bridge setup
eel.setup();
