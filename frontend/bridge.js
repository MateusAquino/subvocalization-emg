function stream(data) {
  if (data) addToCharts(data);
}

function log(message) {
  document.getElementById("output").innerText += message + "\n";
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

eel.expose(log);
eel.expose(state);
eel.expose(error);
eel.expose(stream);
eel.expose(set_ports);
