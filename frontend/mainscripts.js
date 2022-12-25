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
  });

  charts.push(chart);
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

function startSession() {
  port = document.getElementById("port").value;
  eel.start_session(port);
}

function stopSession() {
  eel.stop_session();
}

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");

function setState(state) {
  document.getElementById("error").innerText = "";
  document.getElementById("state").innerText = state;

  if (state == "Idle" || state == "Error") {
    startBtn.style.display = "initial";
    stopBtn.style.display = "none";
    startBtn.disabled = false;
  } else if (state == "Starting") {
    startBtn.disabled = true;
  } else if (state == "Running") {
    startBtn.disabled = false;
    startBtn.style.display = "none";
    stopBtn.style.display = "initial";
  }
}

eel.setup();
