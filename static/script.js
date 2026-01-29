let costCo2Chart = null;

async function getRecommendations() {

  const payload = {
    strength_level: document.getElementById("strength_level").value,
    product_weight_g: Number(document.getElementById("product_weight_g").value),
    biodegradability_score: Number(document.getElementById("biodegradability_score").value),
    recyclability_pct: Number(document.getElementById("recyclability_pct").value)
  };

  const cardsDiv = document.getElementById("cards");
  cardsDiv.innerHTML = "Loading...";

  const res = await fetch("/api/recommend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await res.json();
    if (!res.ok) {
    cardsDiv.innerHTML = `<p style="color:red;">API Error: ${data.message || data.error}</p>`;
    return;
  }

  const recs = data.recommendations || [];

  cardsDiv.innerHTML = "";

  if (recs.length === 0) {
    cardsDiv.innerHTML = "<p>No materials found.</p>";
    return;
  }

  // Render cards
  recs.forEach(r => {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <h3>${r.material_type}</h3>
      <p><b>Category:</b> ${r.material_category}</p>
      <p><b>Predicted Cost:</b> ₹${r.predicted_cost_inr_per_kg.toFixed(2)}</p>
      <p><b>CO₂ Impact:</b> ${r.predicted_co2_impact.toFixed(3)}</p>
    `;
    cardsDiv.appendChild(card);
  });

  // KPIs
  const lowestCost = recs.reduce((a,b) =>
    a.predicted_cost_inr_per_kg < b.predicted_cost_inr_per_kg ? a : b
  );

  const lowestCO2 = recs.reduce((a,b) =>
    a.predicted_co2_impact < b.predicted_co2_impact ? a : b
  );

  document.getElementById("kpiLowestCost").textContent =
    `${lowestCost.material_type} (₹${lowestCost.predicted_cost_inr_per_kg.toFixed(2)})`;

  document.getElementById("kpiLowestCO2").textContent =
    `${lowestCO2.material_type} (${lowestCO2.predicted_co2_impact.toFixed(3)})`;

  document.getElementById("kpiBestOverall").textContent =
    recs[0].material_type;

  // Populate comparison table
  const tbody = document.querySelector("#comparisonTable tbody");
  tbody.innerHTML = "";

  recs.forEach((r, index) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${r.material_type}</td>
      <td>₹${r.predicted_cost_inr_per_kg.toFixed(2)}</td>
      <td>${r.predicted_co2_impact.toFixed(3)}</td>
      <td>#${index + 1}</td>
    `;
    tbody.appendChild(row);
  });


  // Chart
  const labels = recs.map(r => r.material_type);
  const cost = recs.map(r => r.predicted_cost_inr_per_kg);
  const co2 = recs.map(r => r.predicted_co2_impact);

  if (costCo2Chart) costCo2Chart.destroy();

  costCo2Chart = new Chart(
    document.getElementById("costCo2Chart"),
    {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Cost (INR/kg)",
            data: cost,
            backgroundColor: "#22c55e",
            yAxisID: "yCost"
          },
          {
            label: "CO₂ Impact",
            data: co2,
            backgroundColor: "#facc15",
            yAxisID: "yCo2"
          }
        ]
      },
      options: {
        maintainAspectRatio: false,
        scales: {
          yCost: { position: "left" },
          yCo2: { position: "right", grid: { drawOnChartArea: false } }
        }
      }
    }
  );
}
