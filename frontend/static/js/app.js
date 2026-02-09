let comparisonChart = null;

document.addEventListener("DOMContentLoaded", function () {
  loadCategories();
  loadMaterials();
  resetUI();
});

function loadCategories() {
  fetch("/api/categories")
    .then(res => res.json())
    .then(data => {
      if (data.status !== "success") throw new Error("Category load failed");
      const select = document.getElementById("categorySelect");
      data.categories.forEach(cat => {
        const opt = document.createElement("option");
        opt.value = cat;
        opt.textContent = cat;
        select.appendChild(opt);
      });
    })
    .catch(() => showAlert("warning", "Unable to load product categories."));
}

function loadMaterials() {
  fetch("/api/materials")
    .then(res => res.json())
    .then(data => {
      if (data.status !== "success") throw new Error("Material load failed");
      const select = document.getElementById("currentMaterialSelect");
      data.materials.forEach(mat => {
        const opt = document.createElement("option");
        opt.value = mat;
        opt.textContent = mat;
        select.appendChild(opt);
      });
    })
    .catch(() => showAlert("warning", "Unable to load materials list."));
}

function runRecommendation() {
  hideAlert();
  resetResults();

  const category = document.getElementById("categorySelect").value.trim();
  const weight = parseFloat(document.getElementById("weightInput").value);
  const fragility = document.getElementById("fragilitySelect").value;
  const budgetRaw = document.getElementById("budgetInput").value.trim();
  const currentMaterial = document.getElementById("currentMaterialSelect").value;
  const topNRaw = parseInt(document.getElementById("topNSelect").value, 10);

  if (!category) {
    showAlert("warning", "Please select a product category.");
    return;
  }
  if (isNaN(weight) || weight <= 0) {
    showAlert("warning", "Please enter a valid product weight.");
    return;
  }

  const topN = [3, 5, 10].includes(topNRaw) ? topNRaw : 5;

  const payload = {
    category: category,
    weight: weight,
    top_n: topN,
    fragility_override: fragility,
    budget_limit: budgetRaw ? parseFloat(budgetRaw) : null
  };

  setLoading(true);

  fetch("/api/recommend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
    .then(res => res.json())
    .then(data => {
      if (data.status !== "success") throw new Error("Recommendation failed");
      displayResults(data.recommendations);

      if (currentMaterial) {
        return fetch("/api/compare", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            category: category,
            weight: weight,
            current_material: currentMaterial
          })
        })
          .then(res => res.json())
          .then(cmp => {
            if (cmp.status === "success") {
              displaySavings(cmp.comparison);
            }
          });
      }
    })
    .catch(err => {
      showAlert("error", err.message || "Something went wrong.");
    })
    .finally(() => {
      setLoading(false);
    });
}

function displayResults(recs) {
  if (!recs || !recs.length) {
    showAlert("warning", "No recommendations found.");
    return;
  }

  const grid = document.getElementById("materialsGrid");
  grid.innerHTML = "";

  recs.forEach((r, i) => {
    const card = document.createElement("div");
    card.className = "material-card" + (i === 0 ? " best" : "");
    card.innerHTML = `
      <strong>${r.material_name}</strong><br>
      Type: ${r.material_type}<br>
      Suitability: ${(r.suitability_score * 100).toFixed(1)}%<br>
      Predicted Cost: Rs.${r.predicted_cost_inr.toFixed(2)}<br>
      CO2 Impact: ${r.predicted_co2_kg.toFixed(4)} kg<br>
      Eco Score: ${r.eco_score.toFixed(3)}
    `;
    grid.appendChild(card);
  });

  const lowestCost = recs.reduce((a, b) =>
    b.predicted_cost_inr < a.predicted_cost_inr ? b : a
  );
  const lowestCO2 = recs.reduce((a, b) =>
    b.predicted_co2_kg < a.predicted_co2_kg ? b : a
  );
  const best = recs[0];

  document.getElementById("analyticsGrid").innerHTML = `
    <div class="analytics-box">Lowest Cost<br>${lowestCost.material_name} (Rs.${lowestCost.predicted_cost_inr.toFixed(2)})</div>
    <div class="analytics-box">Lowest CO2 Impact<br>${lowestCO2.material_name} (${lowestCO2.predicted_co2_kg.toFixed(4)} kg)</div>
    <div class="analytics-box">Best Overall Choice<br>${best.material_name}</div>
  `;

  renderChart(recs);
  buildTable(recs);

  document.getElementById("resultsSection").style.display = "block";
  document.getElementById("resultsSection").scrollIntoView({ behavior: "smooth" });
}

function renderChart(recs) {
  const ctx = document.getElementById("comparisonChart").getContext("2d");

  if (comparisonChart) comparisonChart.destroy();

  comparisonChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: recs.map(r => r.material_name),
      datasets: [
        {
          label: "Cost (INR)",
          data: recs.map(r => r.predicted_cost_inr),
          backgroundColor: "#4CAF50",
          yAxisID: "yCost"
        },
        {
          label: "CO2 Impact (kg)",
          data: recs.map(r => r.predicted_co2_kg),
          backgroundColor: "#FFC107",
          yAxisID: "yCO2"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        yCost: {
          position: "left",
          title: { display: true, text: "Cost (INR)" }
        },
        yCO2: {
          position: "right",
          title: { display: true, text: "CO2 Impact (kg)" },
          grid: { drawOnChartArea: false }
        }
      }
    }
  });
}

function buildTable(recs) {
  const tbody = document.getElementById("summaryTbody");
  tbody.innerHTML = "";

  recs.forEach((r, i) => {
    const tr = document.createElement("tr");
    if (i === 0) tr.className = "best-row";
    tr.innerHTML = `
      <td>${r.material_name}</td>
      <td>${r.material_type}</td>
      <td>${(r.suitability_score * 100).toFixed(1)}%</td>
      <td>Rs.${r.predicted_cost_inr.toFixed(2)}</td>
      <td>${r.predicted_co2_kg.toFixed(4)}</td>
      <td>${r.eco_score.toFixed(3)}</td>
      <td>#${i + 1}</td>
    `;
    tbody.appendChild(tr);
  });
}

function displaySavings(cmp) {
  document.getElementById("savingsSection").style.display = "block";

  // Check if same material
  if (cmp.same_material) {
    document.getElementById("savingsMetrics").innerHTML = `
      <div class="analytics-box" style="grid-column: span 3; background: #E3F2FD; border-color: #90CAF9;">
        You're already using the optimal material for this product!
      </div>
    `;
    document.getElementById("savingsDetails").innerHTML = `
      <div class="material-card best" style="grid-column: span 2;">
        <strong>CURRENT & RECOMMENDED</strong><br>
        ${cmp.current_material}<br>
        Cost: Rs.${cmp.current_cost_inr.toFixed(2)}<br>
        CO2: ${cmp.current_co2_kg.toFixed(4)} kg<br>
        Eco Score: ${cmp.recommended_eco_score.toFixed(3)}
      </div>
    `;
    return;
  }

  // Rest of your existing code...
  document.getElementById("savingsMetrics").innerHTML = `
    <div class="analytics-box">${cmp.co2_reduction_percent.toFixed(1)}% CO2 Reduction</div>
    <div class="analytics-box">${cmp.co2_savings_kg.toFixed(4)} kg CO2 Saved</div>
    <div class="analytics-box">Rs.${cmp.cost_difference_inr.toFixed(2)} Cost Saved</div>
  `;

  document.getElementById("savingsDetails").innerHTML = `
    <div class="material-card">
      <strong>CURRENT</strong><br>
      ${cmp.current_material}<br>
      Cost: Rs.${cmp.current_cost_inr.toFixed(2)}<br>
      CO2: ${cmp.current_co2_kg.toFixed(4)}
    </div>
    <div class="material-card best">
      <strong>RECOMMENDED</strong><br>
      ${cmp.recommended_material}<br>
      Cost: Rs.${cmp.recommended_cost_inr.toFixed(2)}<br>
      CO2: ${cmp.recommended_co2_kg.toFixed(4)}<br>
      Eco Score: ${cmp.recommended_eco_score.toFixed(3)}
    </div>
  `;
}


function displaySavings(cmp) {
  document.getElementById("savingsSection").style.display = "block";

  document.getElementById("savingsMetrics").innerHTML = `
    <div class="analytics-box">${cmp.co2_reduction_percent.toFixed(1)}% CO2 Reduction</div>
    <div class="analytics-box">${cmp.co2_savings_kg.toFixed(4)} kg CO2 Saved</div>
    <div class="analytics-box">Rs.${cmp.cost_difference_inr.toFixed(2)} Cost Saved</div>
  `;

  document.getElementById("savingsDetails").innerHTML = `
    <div class="material-card">
      <strong>CURRENT</strong><br>
      ${cmp.current_material}<br>
      Cost: Rs.${cmp.current_cost_inr.toFixed(2)}<br>
      CO2: ${cmp.current_co2_kg.toFixed(4)}
    </div>
    <div class="material-card best">
      <strong>RECOMMENDED</strong><br>
      ${cmp.recommended_material}<br>
      Cost: Rs.${cmp.recommended_cost_inr.toFixed(2)}<br>
      CO2: ${cmp.recommended_co2_kg.toFixed(4)}<br>
      Eco Score: ${cmp.recommended_eco_score.toFixed(3)}
    </div>
  `;
}

/* ---------- UI HELPERS ---------- */
function setLoading(state) {
  const btn = document.getElementById("recommendBtn");
  btn.disabled = state;
  btn.textContent = state ? "Analyzing..." : "Run Recommendation Engine";
}

function showAlert(type, msg) {
  const box = document.getElementById("alertBox");
  box.textContent = msg;
  box.style.display = "block";
  box.className = "alert-box " + type;
}

function hideAlert() {
  const box = document.getElementById("alertBox");
  box.style.display = "none";
  box.textContent = "";
}

function resetResults() {
  document.getElementById("resultsSection").style.display = "none";
  document.getElementById("savingsSection").style.display = "none";
}

function resetUI() {
  hideAlert();
  resetResults();
}
