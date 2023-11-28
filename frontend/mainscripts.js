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
let charts = [];

// EMG Charts
function newCharts() {
  console.log("Creating charts");
  if (charts) charts.forEach((chart) => chart.destroy());
  charts = [];
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
            beginAtZero: false,
            stacked: true,
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
}

newCharts();
let lastDataLength = 0;
function addToCharts(data) {
  if (data[0].length < 15) return;
  if (data[0].length < lastDataLength) newCharts();
  lastDataLength = data[0].length;
  for (let idx = 0; idx < 8; idx++) {
    curve = [];
    for (let i = 15; i < data[idx].length; i++) {
      channelData = data[idx][i];
      curve.push({ x: i - 15, y: channelData });
    }
    charts[idx].data.datasets[0].data = curve;
    charts[idx].update("none");
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
  syncTabs();
}

function syncTabs() {
  const state = document.getElementById("state").innerText;
  const recordings = Array.from(document.getElementById("recordings").options);
  const networks = Array.from(document.getElementById("networks").options);
  const emgTab = document.getElementById("emg-tab");
  const recordingTab = document.getElementById("recording-tab");
  const networkTab = document.getElementById("network-tab");
  const evaluatorTab = document.getElementById("evaluator-tab");
  enableTabIf(recordingTab, state == "Running");
  enableTabIf(networkTab, recordings.length >= 1);
  enableTabIf(evaluatorTab, state == "Running" && networks.length >= 1);
  const activeTab = document.querySelector(".nav-link.active");
  if (activeTab.classList.contains("disabled")) emgTab.click();
}

function enableTabIf(tab, condition) {
  if (condition) tab.classList.remove("disabled");
  else tab.classList.add("disabled");
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
  const wpm = document.getElementById("wpm").value;
  const period = document.getElementById("period").value;
  const saveasrec = document.getElementById("saveasrec").value;
  const oneStream = document.getElementById("oneStream").checked;
  const includeSilence = document.getElementById("includeSilence").checked;
  const includeFallback = document.getElementById("includeFallback").checked;
  const words = Array.from(document.getElementById("lang").options).map(
    (e) => e.text
  );
  eel.start_recording(
    saveasrec,
    wpm,
    period,
    oneStream,
    includeSilence,
    includeFallback,
    words
  );
}

function stopRecording() {
  eel.stop_recording();
}

function setRecording(loopCount, totalLoops) {
  const active = loopCount != totalLoops;
  loopCount += 1;
  document
    .getElementById("window-recording")
    .style.setProperty("display", active ? "flex" : "none", "important");
  document
    .getElementById("window-main")
    .style.setProperty("display", active ? "none" : "block", "important");
  document
    .getElementById("progress")
    .style.setProperty("--progress", loopCount / totalLoops);
  document.getElementById("percentage").innerText = Math.trunc(
    (loopCount / totalLoops) * 100
  );
}

function parseWord(word, renderFallback = true) {
  const fallbacks = Array.from(
    document.getElementById("fallbacks").options
  ).map((e) => e.text);

  if (word == "$PREPARE") return prepare();
  else if (word == "$SILENCE") return " ";
  else if (renderFallback && word == "$FALLBACK")
    return fallbacks[Math.floor(Math.random() * fallbacks.length)];
  else if (word == "$FALLBACK") return "<fallback>";
  else return word;
}

function prepare() {
  const percentage = document.getElementById("percentage");
  setTimeout(() => (percentage.innerText = "3"), 0000);
  setTimeout(() => (percentage.innerText = "2"), 1000);
  setTimeout(() => (percentage.innerText = "1"), 2000);
  return "Prepare...";
}

function showFallbacks(checkbox) {
  const active = checkbox.checked;
  if (active)
    document.getElementById("fallbacks-section").classList.remove("d-none");
  else document.getElementById("fallbacks-section").classList.add("d-none");
}

function syncSelect(selectId, list) {
  const select = document.getElementById(selectId);
  const options = Array.from(select.options);
  const existing = options.map((option) => option.value);
  const toAdd = list.filter((el) => !existing.includes(el));
  const toRemove = options.filter((option) => !list.includes(option.value));
  toAdd.forEach((el) => select.add(new Option(el, el)));
  toRemove.forEach((option) => select.removeChild(option));
}

function startTraining() {
  const saveasnet = document.getElementById("saveasnet").value;
  const ratio = document.getElementById("trainingratio").value;
  const batch_size = document.getElementById("batch_size").value;
  const epochs = document.getElementById("epochs").value;
  const channels = document.getElementById("channels").value;
  const windowSize = document.getElementById("windowSize").value;
  const options = document.getElementById("included").options;
  const includedRecords = Array.from(options).map((option) => option.value);
  if (!includedRecords.length) return;
  document.getElementById("train-btn").disabled = true;

  eel.start_training(
    saveasnet,
    ratio,
    includedRecords,
    batch_size,
    epochs,
    channels,
    windowSize
  );
}

const tloss = document.getElementById("t-loss");
const tacc = document.getElementById("t-acc");
const vloss = document.getElementById("v-loss");
const vacc = document.getElementById("v-acc");
const progress = document.getElementById("train-progress");

function setTraining(epoch, loss, accuracy, val_loss, val_accuracy) {
  const epochs = document.getElementById("epochs").value;
  if (epoch == "train") {
    vloss.textContent = loss.toFixed(3);
    vacc.textContent = `${(accuracy * 100).toFixed(3)}%`;
  } else {
    tloss.textContent = loss.toFixed(3);
    tacc.textContent = `${(accuracy * 100).toFixed(3)}%`;
    vloss.textContent = val_loss.toFixed(3);
    vacc.textContent = `${(val_accuracy * 100).toFixed(3)}%`;
    progress.style.width = `${((epoch + 1) / epochs) * 100}%`;
    progress.textContent = `${epoch + 1}/${epochs}`;
  }
  if (epoch + 1 == epochs)
    document.getElementById("train-btn").disabled = false;
}

function toggleEvaluation() {
  const networkId = document.getElementById("evaluate-network").value;
  const historyCount = document.getElementById("history-count").value;
  const refreshRate = document.getElementById("refresh-rate").value;
  const startPredictingBtn = document.getElementById("predict-btn");
  if (startPredictingBtn.innerText.includes("Start")) {
    eel.start_predicting(networkId, historyCount, refreshRate);
    startPredictingBtn.classList.remove("btn-success");
    startPredictingBtn.classList.add("btn-danger");
    startPredictingBtn.innerText = "Stop predicting";
  } else {
    eel.stop_predicting();
    startPredictingBtn.classList.remove("btn-danger");
    startPredictingBtn.classList.add("btn-success");
    startPredictingBtn.innerText = "Start classification stream";
  }
}

let historyTbody = document.getElementById("evaluated-history");
function setPredictionHistory(history) {
  const tbody = document.createElement("tbody");
  history.forEach((row, index) => {
    const tr = document.createElement("tr");
    const th = document.createElement("th");
    const td = document.createElement("td");
    th.scope = "row";
    th.innerText = index + 1;
    td.innerText = row;
    tr.appendChild(th);
    tr.appendChild(td);
    tbody.appendChild(tr);
  });

  historyTbody.parentElement.replaceChild(tbody, historyTbody);
  historyTbody = tbody;
}

// Bootstrap
const tooltipTriggerList = document.querySelectorAll(
  '[data-bs-toggle="tooltip"]'
);
const tooltipList = [...tooltipTriggerList].map(
  (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl)
);

// Eel Bridge setup
eel.setup();
