/* =============================================
   EcoPackAI - Recommendations Page Logic
   ============================================= */

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
      <span style="color: #6B7280; font-size: 0.85rem;">Type: ${r.material_type}</span><br><br>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.9rem;">
        <div><strong>Suitability:</strong> ${(r.suitability_score * 100).toFixed(1)}%</div>
        <div><strong>Cost:</strong> Rs.${r.predicted_cost_inr.toFixed(2)}</div>
        <div><strong>CO₂:</strong> ${r.predicted_co2_kg.toFixed(4)} kg</div>
        <div><strong>Eco Score:</strong> ${r.eco_score.toFixed(3)}</div>
      </div>
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
    <div class="analytics-box">
      <div style="font-size: 0.75rem; opacity: 0.8; margin-bottom: 4px;">LOWEST COST</div>
      <div style="font-size: 1.1rem;">${lowestCost.material_name}</div>
      <div style="font-size: 0.85rem; margin-top: 4px;">Rs.${lowestCost.predicted_cost_inr.toFixed(2)}</div>
    </div>
    <div class="analytics-box">
      <div style="font-size: 0.75rem; opacity: 0.8; margin-bottom: 4px;">LOWEST CO₂</div>
      <div style="font-size: 1.1rem;">${lowestCO2.material_name}</div>
      <div style="font-size: 0.85rem; margin-top: 4px;">${lowestCO2.predicted_co2_kg.toFixed(4)} kg</div>
    </div>
    <div class="analytics-box" style="background: linear-gradient(135deg, #059669, #047857); color: white; border-color: transparent;">
      <div style="font-size: 0.75rem; opacity: 0.9; margin-bottom: 4px;">BEST OVERALL</div>
      <div style="font-size: 1.1rem;">${best.material_name}</div>
      <div style="font-size: 0.85rem; margin-top: 4px;">${(best.suitability_score * 100).toFixed(1)}% Match</div>
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
          label: "Cost (INR)",
          data: recs.map(r => r.predicted_cost_inr),
          backgroundColor: "#059669",
          borderRadius: 4,
          yAxisID: "yCost"
        },
        {
          label: "CO₂ Impact (kg)",
          data: recs.map(r => r.predicted_co2_kg),
          backgroundColor: "#F59E0B",
          borderRadius: 4,
          yAxisID: "yCO2"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            padding: 20
          }
        },
        tooltip: {
          backgroundColor: '#1F2937',
          titleFont: { size: 13, weight: '600' },
          bodyFont: { size: 12 },
          padding: 12,
          cornerRadius: 8
        }
      },
      scales: {
        yCost: {
          position: "left",
          title: { 
            display: true, 
            text: "Cost (INR)",
            font: { size: 11, weight: '600' }
          },
          grid: { color: '#F3F4F6' }
        },
        yCO2: {
          position: "right",
          title: { 
            display: true, 
            text: "CO₂ Impact (kg)",
            font: { size: 11, weight: '600' }
          },
          grid: { drawOnChartArea: false }
        },
        x: {
          grid: { display: false },
          ticks: { font: { size: 10 } }
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
      <td>${r.material_type}</td>
      <td>${(r.suitability_score * 100).toFixed(1)}%</td>
      <td>Rs.${r.predicted_cost_inr.toFixed(2)}</td>
      <td>${r.predicted_co2_kg.toFixed(4)} kg</td>
      <td>${r.eco_score.toFixed(3)}</td>
      <td><span style="background: ${i === 0 ? '#059669' : '#E5E7EB'}; color: ${i === 0 ? 'white' : '#374151'}; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">#${i + 1}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function displaySavings(cmp) {
  document.getElementById("savingsSection").style.display = "block";

  // Check if same material
  if (cmp.same_material) {
    document.getElementById("savingsMetrics").innerHTML = `
      <div class="analytics-box" style="grid-column: span 3; background: linear-gradient(135deg, #DBEAFE, #BFDBFE); border-color: #93C5FD; color: #1E40AF;">
        <svg style="width: 24px; height: 24px; margin-bottom: 8px; stroke: currentColor;" viewBox="0 0 24 24" fill="none" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
        <div style="font-weight: 600;">You're already using the optimal material!</div>
        <div style="font-size: 0.85rem; opacity: 0.8; margin-top: 4px;">No changes needed for this product category</div>
      </div>
    `;
    document.getElementById("savingsDetails").innerHTML = `
      <div class="material-card best" style="grid-column: span 2;">
        <strong>CURRENT & RECOMMENDED</strong><br>
        ${cmp.current_material}<br><br>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; font-size: 0.9rem;">
          <div><strong>Cost:</strong> Rs.${cmp.current_cost_inr.toFixed(2)}</div>
          <div><strong>CO₂:</strong> ${cmp.current_co2_kg.toFixed(4)} kg</div>
          <div><strong>Eco Score:</strong> ${cmp.recommended_eco_score.toFixed(3)}</div>
        </div>
      </div>
    `;
    return;
  }

  // Different materials - show comparison
  const co2Positive = cmp.co2_savings_kg >= 0;
  const costPositive = cmp.cost_difference_inr >= 0;

  document.getElementById("savingsMetrics").innerHTML = `
    <div class="analytics-box" style="background: ${co2Positive ? 'linear-gradient(135deg, #ECFDF5, #D1FAE5)' : 'linear-gradient(135deg, #FEF2F2, #FECACA)'}; border-color: ${co2Positive ? '#6EE7B7' : '#FCA5A5'}; color: ${co2Positive ? '#047857' : '#DC2626'};">
      <div style="font-size: 0.75rem; opacity: 0.8; margin-bottom: 4px;">CO₂ REDUCTION</div>
      <div style="font-size: 1.5rem; font-weight: 700;">${cmp.co2_reduction_percent.toFixed(1)}%</div>
    </div>
    <div class="analytics-box" style="background: ${co2Positive ? 'linear-gradient(135deg, #ECFDF5, #D1FAE5)' : 'linear-gradient(135deg, #FEF2F2, #FECACA)'}; border-color: ${co2Positive ? '#6EE7B7' : '#FCA5A5'}; color: ${co2Positive ? '#047857' : '#DC2626'};">
      <div style="font-size: 0.75rem; opacity: 0.8; margin-bottom: 4px;">CO₂ SAVED</div>
      <div style="font-size: 1.5rem; font-weight: 700;">${cmp.co2_savings_kg.toFixed(4)} kg</div>
    </div>
    <div class="analytics-box" style="background: ${costPositive ? 'linear-gradient(135deg, #ECFDF5, #D1FAE5)' : 'linear-gradient(135deg, #FFFBEB, #FEF3C7)'}; border-color: ${costPositive ? '#6EE7B7' : '#FCD34D'}; color: ${costPositive ? '#047857' : '#B45309'};">
      <div style="font-size: 0.75rem; opacity: 0.8; margin-bottom: 4px;">COST ${costPositive ? 'SAVED' : 'PREMIUM'}</div>
      <div style="font-size: 1.5rem; font-weight: 700;">Rs.${Math.abs(cmp.cost_difference_inr).toFixed(2)}</div>
    </div>
  `;

  document.getElementById("savingsDetails").innerHTML = `
    <div class="material-card">
      <div style="font-size: 0.7rem; font-weight: 700; color: #6B7280; margin-bottom: 8px;">CURRENT MATERIAL</div>
      <strong>${cmp.current_material}</strong><br><br>
      <div style="font-size: 0.9rem;">
        <div style="margin-bottom: 6px;"><strong>Cost:</strong> Rs.${cmp.current_cost_inr.toFixed(2)}</div>
        <div><strong>CO₂:</strong> ${cmp.current_co2_kg.toFixed(4)} kg</div>
      </div>
    </div>
    <div class="material-card best">
      <div style="font-size: 0.7rem; font-weight: 700; color: #047857; margin-bottom: 8px;">RECOMMENDED MATERIAL</div>
      <strong>${cmp.recommended_material}</strong><br><br>
      <div style="font-size: 0.9rem;">
        <div style="margin-bottom: 6px;"><strong>Cost:</strong> Rs.${cmp.recommended_cost_inr.toFixed(2)}</div>
        <div style="margin-bottom: 6px;"><strong>CO₂:</strong> ${cmp.recommended_co2_kg.toFixed(4)} kg</div>
        <div><strong>Eco Score:</strong> ${cmp.recommended_eco_score.toFixed(3)}</div>
      </div>
    </div>
  `;
}

/* ---------- UI HELPERS ---------- */
function setLoading(state) {
  const btn = document.getElementById("recommendBtn");
  btn.disabled = state;
  if (state) {
    btn.innerHTML = `
      <svg class="btn-icon" style="animation: spin 1s linear infinite;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"/>
      </svg>
      Analyzing...
    `;
  } else {
    btn.innerHTML = `
      <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
      </svg>
      Run Recommendation Engine
    `;
  }
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

// Add CSS animation for loading spinner
const style = document.createElement('style');
style.textContent = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;
document.head.appendChild(style);