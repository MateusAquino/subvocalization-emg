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
    syncSelect("evaluate-network", networkList);
    syncTabs();
  });
}

function train_progress(epoch, loss, accuracy, val_loss, val_accuracy) {
  setTraining(epoch, loss, accuracy, val_loss, val_accuracy);
}

let lastPrediction = "";
function update_prediction(prediction, history) {
  const predictedWord = document.getElementById("evaluated-word");
  const word = parseWord(prediction, false);
  if (synthetizing && lastPrediction != word) eel.synthetize(word);
  if (keyboardPress && lastPrediction != word) eel.press_key(word);
  lastPrediction = word;
  predictedWord.innerText = word;
  history.map((word) => parseWord(word, false));
  setPredictionHistory(history);
}

eel.expose(log);
eel.expose(state);
eel.expose(error);
eel.expose(stream);
eel.expose(set_ports);
eel.expose(sync_files);
eel.expose(record_step);
eel.expose(train_progress);
eel.expose(update_prediction);
