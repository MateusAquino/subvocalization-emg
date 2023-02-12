function stream(data) {
  if (data) addToCharts(data);
}

function log(message) {
  document.getElementById("output").innerText += `> ${message}\n`;
  var elem = document.getElementById("output");
  elem.scrollTop = elem.scrollHeight;
}

function state(message) {
  setState(message);
}

function error(message) {
  document.getElementById("error").innerText = message;
}

function set_ports(ports) {
  const portElement = document.getElementById("port");

  if (ports?.length == 1 && !portElement.value) portElement.value = ports[0];
  else if (ports?.length == 0) portElement.value = "Synthetic";

  ports.push("Synthetic");

  document.getElementById("ports").innerHTML = ports.map(
    (port) => `<option>${port}</option>`
  );
}

function record_step(word, loopCount, totalLoops) {
  setRecording(loopCount, totalLoops);
  document.getElementById("reading").innerText = parseWord(word);
}

function sync_files() {
  const saves = eel.list_saves()();
  const networks = eel.list_networks()();

  Promise.all([saves, networks]).then((values) => {
    const [saveList, networkList] = values;
    syncSelect(
      "recordings",
      saveList.map((save) => save.slice(0, -4))
    );
    syncSelect("networks", networkList);
  });
}

const tloss = document.getElementById("t-loss");
const tacc = document.getElementById("t-acc");
const tvloss = document.getElementById("t-vloss");
const tvacc = document.getElementById("t-vacc");
const vloss = document.getElementById("v-loss");
const vacc = document.getElementById("v-acc");
const progress = document.getElementById("train-progress");
function train_progress(epoch, loss, accuracy, val_loss, val_accuracy) {
  const epochs = document.getElementById("epochs").value;
  if (epoch == "train") {
    vloss.textContent = loss.toFixed(3);
    vacc.textContent = `${(accuracy * 100).toFixed(3)}%`;
  } else {
    tloss.textContent = loss.toFixed(3);
    tacc.textContent = `${(accuracy * 100).toFixed(3)}%`;
    tvloss.textContent = val_loss.toFixed(3);
    tvacc.textContent = `${(val_accuracy * 100).toFixed(3)}%`;
    progress.style.width = `${((epoch + 1) / epochs) * 100}%`;
    progress.textContent = `${epoch + 1}/${epochs}`;
  }
}

eel.expose(log);
eel.expose(state);
eel.expose(error);
eel.expose(stream);
eel.expose(set_ports);
eel.expose(sync_files);
eel.expose(record_step);
eel.expose(train_progress);
