// -------------------- DASHBOARD (PREDICT) --------------------
const form = document.getElementById("predictForm");
const resetBtn = document.getElementById("resetBtn");

const resultBox = document.getElementById("resultBox");
const loaderBox = document.getElementById("loaderBox");
const errorBox = document.getElementById("errorBox");
const errorText = document.getElementById("errorText");

const predCost = document.getElementById("predCost");
const predCO2 = document.getElementById("predCO2");

function hidePredictBoxes() {
  if (resultBox) resultBox.style.display = "none";
  if (loaderBox) loaderBox.style.display = "none";
  if (errorBox) errorBox.style.display = "none";
}

function setDefaultPredict() {
  if (predCost) predCost.textContent = "--";
  if (predCO2) predCO2.textContent = "--";
}

async function handlePredictSubmit(e) {
  e.preventDefault();

  hidePredictBoxes();
  if (loaderBox) loaderBox.style.display = "flex";

  const payload = {
    strength_mpa: parseFloat(document.getElementById("strength_mpa").value),
    cost_inr_per_kg: parseFloat(document.getElementById("cost_inr_per_kg").value),
    weight_capacity: parseFloat(document.getElementById("weight_capacity").value),
    recyclability_pct: parseFloat(document.getElementById("recyclability_pct").value),
    biodegradability_score: parseFloat(document.getElementById("biodegradability_score").value)
  };

  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (loaderBox) loaderBox.style.display = "none";

    if (!res.ok) {
      if (errorText) errorText.textContent = data.error || "Server error!";
      if (errorBox) errorBox.style.display = "block";
      return;
    }

    if (predCost) predCost.textContent = Number(data.predicted_cost).toFixed(2);
    if (predCO2) predCO2.textContent = Number(data.predicted_co2).toFixed(2);

    if (resultBox) resultBox.style.display = "block";
  } catch (err) {
    if (loaderBox) loaderBox.style.display = "none";
    if (errorText) errorText.textContent = "Connection failed! Check Flask terminal.";
    if (errorBox) errorBox.style.display = "block";
    console.log(err);
  }
}

function setupDashboard() {
  if (!form) return;

  form.addEventListener("submit", handlePredictSubmit);

  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      form.reset();
      hidePredictBoxes();
      setDefaultPredict();
    });
  }
}

// -------------------- MATERIALS PAGE --------------------
async function loadMaterials() {
  const tbody = document.getElementById("materialsBody");
  const loader = document.getElementById("loaderBox");
  const errorBox = document.getElementById("errorBox");
  const errorText = document.getElementById("errorText");
  const rowCount = document.getElementById("rowCount");

  if (!tbody) return;

  loader.style.display = "flex";
  errorBox.style.display = "none";

  try {
    const res = await fetch("/api/materials");
    const data = await res.json();

    if (!res.ok) {
      loader.style.display = "none";
      errorText.textContent = data.error || "Failed to load materials";
      errorBox.style.display = "block";
      return;
    }

    tbody.innerHTML = "";

    data.materials.forEach((m) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${m.material_id ?? "-"}</td>
        <td>${m.material_type ?? "-"}</td>
        <td>${m.strength_mpa ?? "-"}</td>
        <td>${m.weight_capacity ?? "-"}</td>
        <td>${m.co2_emission_kg_per_kg ?? "-"}</td>
        <td>${m.biodegradability_score ?? "-"}</td>
        <td>${m.recyclability_pct ?? "-"}</td>
        <td>${m.cost_inr_per_kg ?? "-"}</td>
        <td>${m.material_category ?? "-"}</td>
      `;
      tbody.appendChild(tr);
    });

    rowCount.textContent = `Rows: ${data.materials.length}`;
    loader.style.display = "none";
  } catch (err) {
    loader.style.display = "none";
    errorText.textContent = "Server connection failed!";
    errorBox.style.display = "block";
    console.log(err);
  }
}

function setupSearch() {
  const searchInput = document.getElementById("searchInput");
  const tbody = document.getElementById("materialsBody");

  if (!searchInput || !tbody) return;

  searchInput.addEventListener("input", () => {
    const query = searchInput.value.toLowerCase();
    const rows = tbody.querySelectorAll("tr");

    rows.forEach((row) => {
      const rowText = row.innerText.toLowerCase();
      row.style.display = rowText.includes(query) ? "" : "none";
    });
  });
}

function setupRefresh() {
  const refreshBtn = document.getElementById("refreshBtn");
  if (!refreshBtn) return;

  refreshBtn.addEventListener("click", () => {
    loadMaterials();
  });
}

function setupMaterialsPage() {
  const tbody = document.getElementById("materialsBody");
  if (!tbody) return;

  loadMaterials();
  setupSearch();
  setupRefresh();
}

// -------------------- INIT --------------------
document.addEventListener("DOMContentLoaded", () => {
  setupDashboard();
  setupMaterialsPage();
});
