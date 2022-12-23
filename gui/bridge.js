function log(message) {
  document.getElementById("output").innerText += message + "\n"
}

function error(message) {
  document.getElementById("error").innerText = message
}

eel.expose(log);
eel.expose(error);
