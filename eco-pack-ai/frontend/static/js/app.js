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
    
    // Format the card with inline metrics
    card.innerHTML = `
      <strong>${r.material_name}</strong>
      <div class="material-metrics">
        <span class="metric"><span>SUITABILITY:</span> <strong>${(r.suitability_score * 100).toFixed(1)}%</strong></span>
        <span class="metric"><span>COST:</span> <strong>₹${r.predicted_cost_inr.toFixed(2)}</strong></span>
        <span class="metric"><span>CO₂ IMPACT:</span> <strong>${r.predicted_co2_kg.toFixed(4)} kg</strong></span>
        <span class="metric"><span>ECO SCORE:</span> <strong class="eco-score">${r.eco_score.toFixed(3)}</strong></span>
      </div>
    `;
    
    grid.appendChild(card);
  });

  // Calculate analytics
  const lowestCost = recs.reduce((a, b) =>
    b.predicted_cost_inr < a.predicted_cost_inr ? b : a
  );
  const lowestCO2 = recs.reduce((a, b) =>
    b.predicted_co2_kg < a.predicted_co2_kg ? b : a
  );
  const best = recs[0];

  // Update analytics grid
  document.getElementById("analyticsGrid").innerHTML = `
    <div class="analytics-box">
      <div class="label">LOWEST COST</div>
      <div class="value">${lowestCost.material_name}</div>
      <div class="sub">₹${lowestCost.predicted_cost_inr.toFixed(2)}</div>
    </div>
    <div class="analytics-box">
      <div class="label">LOWEST CO₂</div>
      <div class="value">${lowestCO2.material_name}</div>
      <div class="sub">${lowestCO2.predicted_co2_kg.toFixed(4)} kg</div>
    </div>
    <div class="analytics-box">
      <div class="label">BEST OVERALL</div>
      <div class="value">${best.material_name}</div>
      <div class="sub">Eco Score: ${best.eco_score.toFixed(3)}</div>
    </div>
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
          label: "Cost (₹)",
          data: recs.map(r => r.predicted_cost_inr),
          backgroundColor: "#1a7a4a",
          borderRadius: 6,
          yAxisID: "yCost"
        },
        {
          label: "CO₂ Impact (kg)",
          data: recs.map(r => r.predicted_co2_kg),
          backgroundColor: "#d97706",
          borderRadius: 6,
          yAxisID: "yCO2"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            usePointStyle: true,
            padding: 20,
            color: '#1f2937',
            font: { family: 'Inter', size: 12 }
          }
        }
      },
      scales: {
        yCost: {
          position: "left",
          title: { 
            display: true, 
            text: "Cost (₹)",
            color: '#4b5563',
            font: { family: 'Inter', weight: '500', size: 11 }
          },
          grid: { color: '#e5e7eb' },
          ticks: { color: '#1f2937' }
        },
        yCO2: {
          position: "right",
          title: { 
            display: true, 
            text: "CO₂ Impact (kg)",
            color: '#4b5563',
            font: { family: 'Inter', weight: '500', size: 11 }
          },
          grid: { drawOnChartArea: false },
          ticks: { color: '#1f2937' }
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
    tr.innerHTML = `
      <td><strong>${r.material_name}</strong></td>
      <td><span class="type-badge">${r.material_type}</span></td>
      <td>${(r.suitability_score * 100).toFixed(1)}%</td>
      <td>₹${r.predicted_cost_inr.toFixed(2)}</td>
      <td>${r.predicted_co2_kg.toFixed(4)} kg</td>
      <td><span class="eco-score">${r.eco_score.toFixed(3)}</span></td>
      <td><span class="rank-indicator">${i + 1}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function displaySavings(cmp) {
  document.getElementById("savingsSection").style.display = "block";

  document.getElementById("savingsMetrics").innerHTML = `
    <div class="analytics-box">
      <div class="label">CO₂ REDUCTION</div>
      <div class="value">${cmp.co2_reduction_percent.toFixed(1)}%</div>
      <div class="sub">${cmp.co2_savings_kg.toFixed(4)} kg saved</div>
    </div>
    <div class="analytics-box">
      <div class="label">COST SAVINGS</div>
      <div class="value">₹${cmp.cost_difference_inr.toFixed(2)}</div>
      <div class="sub">per unit</div>
    </div>
    <div class="analytics-box">
      <div class="label">ENVIRONMENTAL IMPACT</div>
      <div class="value">${cmp.recommended_eco_score.toFixed(3)}</div>
      <div class="sub">eco score</div>
    </div>
  `;

  document.getElementById("savingsDetails").innerHTML = `
    <div class="comparison-card current">
      <div class="label">CURRENT MATERIAL</div>
      <div class="value">${cmp.current_material}</div>
      <div class="details">
        <div>Cost: ₹${cmp.current_cost_inr.toFixed(2)}</div>
        <div>CO₂: ${cmp.current_co2_kg.toFixed(4)} kg</div>
      </div>
    </div>
    <div class="comparison-card recommended">
      <div class="label">RECOMMENDED</div>
      <div class="value">${cmp.recommended_material}</div>
      <div class="details">
        <div>Cost: ₹${cmp.recommended_cost_inr.toFixed(2)}</div>
        <div>CO₂: ${cmp.recommended_co2_kg.toFixed(4)} kg</div>
        <div>Eco Score: <span class="eco-score">${cmp.recommended_eco_score.toFixed(3)}</span></div>
      </div>
    </div>
  `;
}

/* ---------- UI HELPERS ---------- */
function setLoading(state) {
  const btn = document.getElementById("recommendBtn");
  btn.disabled = state;
  btn.innerHTML = state ? 
    '<span class="loading-spinner"></span> Analyzing...' : 
    'Run Recommendation Engine';
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