// Recordings tab
const addWord = document.querySelector("#add-word");
const deleteWord = document.querySelector("#delete-word");
const addFallback = document.querySelector("#add-fallback");
const deleteFallback = document.querySelector("#delete-fallback");
const deleteRecording = document.querySelector("#delete-recording");

addWord.onclick = () => {
  addToList("[name=words]", "#word");
};
deleteWord.onclick = () => {
  deleteFromList("[name=words]");
};
addFallback.onclick = () => {
  addToList("[name=fallbacks]", "#fallback");
};
deleteFallback.onclick = () => {
  deleteFromList("[name=fallbacks]");
};
deleteRecording.onclick = () => {
  deleteFromList("[name=recordings]");
};

// Neural Network tab
const networkTab = document.getElementById("network-tab");
const ratioSlider = document.getElementById("trainingratio");
const ratioPercent = document.getElementById("trainingratio-percent");
const includedSelect = document.getElementById("included");
const excludedSelect = document.getElementById("excluded");
const includeBtn = document.getElementById("btn-include");
const excludeBtn = document.getElementById("btn-exclude");

networkTab.onclick = () => {
  const recordings = Array.from(
    document.querySelector("[name=recordings]").options
  ).map((option) => option.value);
  const included = Array.from(includedSelect.options);
  const excluded = Array.from(excludedSelect.options);
  const existingOptions = included
    .map((option) => option.value)
    .concat(excluded.map((option) => option.value));
  const toAdd = recordings.filter((el) => !existingOptions.includes(el));
  const toRemoveIncluded = included.filter(
    (option) => !recordings.includes(option.value)
  );
  const toRemoveExcluded = excluded.filter(
    (option) => !recordings.includes(option.value)
  );
  toAdd.forEach((el) => excludedSelect.add(new Option(el, el)));
  toRemoveIncluded.forEach((option) => includedSelect.removeChild(option));
  toRemoveExcluded.forEach((option) => excludedSelect.removeChild(option));
};

includeBtn.onclick = () => {
  const excluded = document.querySelectorAll(`#excluded option:checked`);
  Array.from(excluded).map((option) => {
    const newOption = new Option(option.value, option.value);
    excludedSelect.removeChild(option);
    includedSelect.add(newOption);
  });
};

excludeBtn.onclick = () => {
  const included = document.querySelectorAll(`#included option:checked`);
  Array.from(included).map((option) => {
    const newOption = new Option(option.value, option.value);
    includedSelect.removeChild(option);
    excludedSelect.add(newOption);
  });
};

ratioSlider.oninput = () => {
  ratioPercent.innerText = `${ratioSlider.value}%`;
  ratioSlider.style.setProperty("--ratio", ratioSlider.value);
};

const deleteNetwork = document.querySelector("#delete-network");
deleteNetwork.onclick = () => {
  deleteFromList("[name=networks]");
};

// Functions
function addToList(selector, inputSelector) {
  const select = document.querySelector(selector);
  const input = document.querySelector(inputSelector);
  const newOption = new Option(input.value, input.value);
  select.add(newOption);
  input.value = "";
}

function deleteFromList(selector) {
  const select = document.querySelector(selector);
  const selected = document.querySelectorAll(`${selector} option:checked`);
  Array.from(selected).map((option) => {
    if (selector === "[name=recordings]") eel.delete_save(option.value);
    else if (selector === "[name=networks]") eel.delete_network(option.value);
    select.removeChild(option);
  });
}

var synthetizing = false;
function toggleSynthetize(value) {
  synthetizing = value;
}

var keyboardPress = false;
function toggleKeyboard(value) {
  keyboardPress = value;
}
