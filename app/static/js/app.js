document.addEventListener("DOMContentLoaded", () => {
  if (!window.DEPARTMENTS) return;

  const deps = window.DEPARTMENTS;
  let selected = deps[0];

  const cards = document.querySelectorAll(".dept-card");
  const input = document.getElementById("imageInput");
  const drop = document.getElementById("dropZone");
  const form = document.getElementById("predictForm");
  const btn = document.getElementById("analyzeBtn");

  function setDept(key) {
    selected = deps.find(d => d.key === key);
    cards.forEach(c => c.classList.toggle("selected", c.dataset.key === key));
    document.getElementById("departmentInfo").innerHTML =
      `<b>${selected.icon} ${selected.name_ka}</b><span>${selected.description}</span><small>Input: ${selected.input_size.join("×")} · ${selected.accepted_image}</small>`;
    input.value = "";
    document.getElementById("previewBox").classList.add("hidden");
    btn.disabled = true;
    resetResult();
  }

  function resetResult() {
    document.getElementById("resultBox").classList.add("hidden");
    document.getElementById("loadingResult").classList.add("hidden");
    document.getElementById("errorBox").classList.add("hidden");
    document.getElementById("emptyResult").classList.remove("hidden");
  }

  cards.forEach(c => c.addEventListener("click", () => setDept(c.dataset.key)));

  input.addEventListener("change", () => {
    const file = input.files[0];
    if (!file) return;
    document.getElementById("previewImage").src = URL.createObjectURL(file);
    document.getElementById("fileName").textContent = file.name;
    document.getElementById("fileSize").textContent = `${(file.size/1024/1024).toFixed(2)} MB`;
    document.getElementById("previewBox").classList.remove("hidden");
    btn.disabled = false;
    resetResult();
  });

  ["dragover","dragenter"].forEach(evt => drop.addEventListener(evt, e => {
    e.preventDefault(); drop.classList.add("drag");
  }));
  ["dragleave","drop"].forEach(evt => drop.addEventListener(evt, e => {
    e.preventDefault(); drop.classList.remove("drag");
  }));
  drop.addEventListener("drop", e => {
    const file = e.dataTransfer.files[0];
    const dt = new DataTransfer(); dt.items.add(file); input.files = dt.files;
    input.dispatchEvent(new Event("change"));
  });

  form.addEventListener("submit", async e => {
    e.preventDefault();
    if (!input.files.length) return;

    document.getElementById("emptyResult").classList.add("hidden");
    document.getElementById("resultBox").classList.add("hidden");
    document.getElementById("errorBox").classList.add("hidden");
    document.getElementById("loadingResult").classList.remove("hidden");
    btn.disabled = true;

    const fd = new FormData();
    fd.append("image", input.files[0]);

    try {
      const res = await fetch(`/api/v1/predict/${selected.key}`, {method:"POST", body:fd});
      const data = await res.json();
      if (!res.ok || !data.success) throw new Error(data.error || "შეცდომა");

      document.getElementById("loadingResult").classList.add("hidden");
      document.getElementById("resultBox").classList.remove("hidden");
      document.getElementById("prediction").textContent = data.display_prediction;
      document.getElementById("confidence").textContent = `${data.confidence}%`;
      document.getElementById("uncertain").classList.toggle("hidden", !data.uncertain);
      document.getElementById("pdfLink").href = `/report/${data.analysis_id}.pdf`;

      const list = document.getElementById("probabilities");
      list.innerHTML = "";
      data.top_predictions.forEach(p => {
        list.innerHTML += `<div class="prob-row"><div><span>${p.display_label}</span><b>${p.probability}%</b></div><div class="bar"><i style="width:${p.probability}%"></i></div></div>`;
      });
    } catch(err) {
      document.getElementById("loadingResult").classList.add("hidden");
      const box = document.getElementById("errorBox");
      box.textContent = err.message; box.classList.remove("hidden");
    } finally {
      btn.disabled = false;
    }
  });

  setDept(selected.key);
});
