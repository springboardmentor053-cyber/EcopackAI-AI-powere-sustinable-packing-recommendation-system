// =======================
// CONFIG
// =======================
const API_BASE = "http://127.0.0.1:5000";
const res = await fetch("/api/recommend", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-KEY": API_KEY,
  },
  body: JSON.stringify(payload),
});

const data = await res.json();

// =======================
// index.html page
// =======================
const form = document.getElementById("productForm");

if (form) {
  form.addEventListener("submit", function (e) {
    e.preventDefault();

    // If Bootstrap validation says invalid, stop
    if (!form.checkValidity()) return;

    const productData = {
      product_name: document.getElementById("product_name").value.trim(),
      product_category: document.getElementById("product_category").value.trim(),
      product_weight_kg: document.getElementById("product_weight_kg").value,
      fragility_level: document.getElementById("fragility_level").value,
      temperature_sensitive: document.getElementById("temperature_sensitive").value,
      required_strength_score: document.getElementById("required_strength_score").value,
      preferred_biodegradability_score: document.getElementById("preferred_biodegradability_score").value,
      max_packaging_cost_inr: document.getElementById("max_packaging_cost_inr").value,
    };

    localStorage.setItem("ecoPackAI_product", JSON.stringify(productData));
    window.location.href = "/results";
  });
}

// =======================
// results.html page
// =======================
const resultsTable = document.getElementById("resultsTable");

if (resultsTable) {
  const tbody = resultsTable.querySelector("tbody");
  const productSummary = document.getElementById("productSummary");
  const topRecommendation = document.getElementById("topRecommendation");

  const loadingBox = document.getElementById("loadingBox");
  const errorBox = document.getElementById("errorBox");

  const productData = JSON.parse(localStorage.getItem("ecoPackAI_product") || "{}");

  // Initial text
  if (productSummary) {
    productSummary.textContent = `Requested Product: ${productData.product_name || "N/A"} (loading details from API...)`;
  }

  function showError(message) {
    if (errorBox) {
      errorBox.textContent = message;
      errorBox.classList.remove("d-none");
    }
    if (loadingBox) loadingBox.classList.add("d-none");
  }

  function hideLoading() {
    if (loadingBox) loadingBox.classList.add("d-none");
  }

  async function loadRecommendations() {
    try {
      const res = await fetch(`${API_BASE}/api/recommend`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-KEY": API_KEY
        },
        body: JSON.stringify({
          product_name: productData.product_name
        }),
      });

      if (!res.ok) {
        const text = await res.text();
        console.error("Server response:", text);
        showError("Server error. Make sure Flask is running and API key is correct.");
        return;
      }

      const data = await res.json();

      if (data.error) {
        showError(data.error);
        return;
      }

      hideLoading();

      // Update product summary card
      if (productSummary && data.product) {
        const p = data.product;
        productSummary.textContent =
          `Product: ${p.product_name} | Category: ${p.product_category} | Weight: ${p.product_weight_kg} kg | Fragility: ${p.fragility_level || "N/A"} | Temp Sensitive: ${p.temperature_sensitive || "N/A"}`;
      }

      // Fill table
      tbody.innerHTML = "";
      data.recommendations.forEach((r) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="fw-semibold">${r.rank}</td>
          <td>${r.material_name}</td>
          <td>${Number(r.pred_cost_inr).toFixed(2)}</td>
          <td>${Number(r.pred_co2_kg).toFixed(3)}</td>
          <td>${Number(r.recyclability_percent).toFixed(0)}</td>
          <td>${Number(r.biodegradability_score).toFixed(0)}</td>
          <td>${Number(r.suitability_score).toFixed(4)}</td>
          <td>
            <span class="badge bg-success-subtle text-success border border-success-subtle">
              ${Number(r.environment_score).toFixed(2)}
            </span>
          </td>
        `;
        tbody.appendChild(tr);
      });

      // Top recommendation card
      if (topRecommendation && data.recommendations && data.recommendations.length > 0) {
        const top = data.recommendations[0];
        topRecommendation.innerHTML = `
          <div class="mb-2">
            <div class="fw-semibold">${top.material_name}</div>
            <div class="text-muted small">
              Cost: ₹${Number(top.pred_cost_inr).toFixed(2)} • CO₂: ${Number(top.pred_co2_kg).toFixed(3)} kg
            </div>
          </div>
          <div class="d-flex gap-2 flex-wrap">
            <span class="badge text-bg-primary">Recyclability: ${Number(top.recyclability_percent).toFixed(0)}%</span>
            <span class="badge text-bg-warning">Bio: ${Number(top.biodegradability_score).toFixed(0)}/10</span>
            <span class="badge text-bg-success">Env: ${Number(top.environment_score).toFixed(2)}</span>
          </div>
        `;
      }

    } catch (err) {
      console.error("API error:", err);
      showError("Failed to fetch recommendations. Is Flask running on 127.0.0.1:5000?");
    }
  }

  loadRecommendations();
}
