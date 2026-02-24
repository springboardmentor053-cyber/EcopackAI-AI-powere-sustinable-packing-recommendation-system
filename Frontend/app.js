const form = document.getElementById("predictForm");
const resetBtn = document.getElementById("resetBtn");

const resultBox = document.getElementById("rankingCards");
const loaderBox = document.getElementById("loaderBox");
const errorBox = document.getElementById("errorBox");
const errorText = document.getElementById("errorText");

const predCost = document.getElementById("predCost");
const predCO2 = document.getElementById("predCO2");

async function handlePredictSubmit(e) {
  e.preventDefault();

  loaderBox.classList.remove("hidden");
  errorBox.classList.add("hidden");
  resultBox.innerHTML = "";

  const payload = {
    strength_mpa: parseFloat(document.getElementById("strength_mpa").value),
    cost_inr_per_kg: parseFloat(document.getElementById("cost_inr_per_kg").value),
    weight_capacity: parseFloat(document.getElementById("weight_capacity").value),
    recyclability_pct: parseFloat(document.getElementById("recyclability_pct").value),
    biodegradability_score: parseFloat(document.getElementById("biodegradability_score").value)
  };

  try {

    // ======================
    // PREDICT API
    // ======================
    const predictRes = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const predictData = await predictRes.json();

    if (!predictRes.ok) {
      throw new Error(predictData.error || "Prediction failed");
    }

    predCost.textContent =
      Number(predictData.predicted_cost).toFixed(2);

    predCO2.textContent =
      Number(predictData.predicted_co2).toFixed(2);

    // ======================
    // SUSTAINABILITY SCORE
    // ======================
    const recyclability = payload.recyclability_pct;
    const biodegradability = payload.biodegradability_score * 10;
    const co2Impact = 100 - (predictData.predicted_co2 * 20);

    let sustainabilityScore = Math.min(
      100,
      Math.max(0, (recyclability + biodegradability + co2Impact) / 3)
    );

    document.getElementById("sustainScore").textContent =
      sustainabilityScore.toFixed(0);

    document.getElementById("sustainMeter").style.width =
      sustainabilityScore + "%";

    // ======================
    // RECOMMEND API
    // ======================
    const recommendRes = await fetch("/recommend", {
      method: "POST"
    });

    const recommendData = await recommendRes.json();

    if (!recommendRes.ok) {
      throw new Error(recommendData.error || "Recommendation failed");
    }

    // ======================
    // SHOW TOP 5 CARDS
    // ======================
    if (recommendData.recommendations?.length > 0) {

      // ⭐ SAVE FOR DASHBOARD EXPORT
      localStorage.setItem(
        "top5Data",
        JSON.stringify(recommendData.recommendations)
      );

      recommendData.recommendations.forEach((item, index) => {

        resultBox.innerHTML += `
          <div class="material-card">
            <div class="rank">#${index + 1}</div>
            <h4>${item.material_type}</h4>
            <p>💰 ₹ ${Number(item.predicted_cost).toFixed(2)}</p>
            <p>🌍 ${Number(item.predicted_co2).toFixed(2)} kg/kg</p>
          </div>
        `;
      });
    }

    loaderBox.classList.add("hidden");

  } catch (err) {

    loaderBox.classList.add("hidden");
    errorBox.classList.remove("hidden");
    errorText.textContent = err.message;

    console.error("Prediction Error:", err);
  }
}

/* ======================
   EVENTS
====================== */

form.addEventListener("submit", handlePredictSubmit);

resetBtn.addEventListener("click", () => {
  form.reset();
  predCost.textContent = "--";
  predCO2.textContent = "--";
  resultBox.innerHTML = "";

  // optional reset sustainability UI
  document.getElementById("sustainScore").textContent = "--";
  document.getElementById("sustainMeter").style.width = "0%";
});