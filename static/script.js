let costCo2Chart = null;
let sustainabilityChart = null;

async function getRecommendations() {

  const payload = {
    strength_level: document.getElementById("strength_level").value,
    product_weight_g: Number(document.getElementById("product_weight_g").value),
    biodegradability_score: Number(document.getElementById("biodegradability_score").value),
    recyclability_pct: Number(document.getElementById("recyclability_pct").value)
  };


  const cardsDiv = document.getElementById("cards");
  cardsDiv.innerHTML = "Running model...";

  try {
    const res = await fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    const recs = data.recommendations || [];

    cardsDiv.innerHTML = "";

    if (recs.length === 0) {
      cardsDiv.innerHTML = "<p>No materials found.</p>";
      return;
    }

    // ---- Cards ----
    recs.forEach(r => {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <h3>${r.material_type}</h3>
        <p><b>Category:</b> ${r.material_category}</p>
        <p><b>Predicted Cost:</b> ${r.predicted_cost_inr_per_kg} INR/kg</p>
        <p><b>CO₂ Impact:</b> ${r.predicted_co2_impact}</p>
      `;
      cardsDiv.appendChild(card);
    });

    // ---- Chart 1: Cost vs CO₂ ----
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
            { label: "Cost (INR/kg)", data: cost, backgroundColor: "#22c55e" },
            { label: "CO₂ Impact", data: co2, backgroundColor: "#facc15" }
          ]
        }
      }
    );

    // ---- Chart 2: Sustainability Radar ----
    const avgBio = recs.reduce((a,b)=>a+b.biodegradability_score,0)/recs.length;
    const avgRec = recs.reduce((a,b)=>a+b.recyclability_pct,0)/recs.length;

    if (sustainabilityChart) sustainabilityChart.destroy();

    sustainabilityChart = new Chart(
      document.getElementById("sustainabilityChart"),
      {
        type: "radar",
        data: {
          labels: ["Biodegradability", "Recyclability"],
          datasets: [{
            label: "Avg Sustainability Profile",
            data: [avgBio, avgRec],
            backgroundColor: "rgba(34,197,94,0.3)",
            borderColor: "#22c55e"
          }]
        }
      }
    );

  } catch (err) {
    cardsDiv.innerHTML = "Backend connection failed.";
  }
}
