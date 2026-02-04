let chartInstance = null;

/* =========================
   MAIN FETCH
========================= */
function getRecommendations() {
    const levelToNum = { Low: 3, Medium: 6, High: 9 };

    const payload = {
        product_category: document.getElementById("category").value,
        strength_score: levelToNum[document.getElementById("strength_score").value],
        weight_capacity_kg: Number(document.getElementById("weight_capacity_kg").value),
        biodegradability_score: levelToNum[document.getElementById("biodegradability_score").value],
        recyclability_percent: Number(document.getElementById("recyclability_percent").value),
        moisture_resistance: levelToNum[document.getElementById("moisture_resistance").value],
        heat_resistance: levelToNum[document.getElementById("heat_resistance").value]
    };

    document.getElementById("loader").classList.remove("hidden");

    fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
        .then(res => res.json())
        .then(data => {
            const materials = data.recommended_materials;

            populateTable(materials);
            drawChart(materials);
            showInsights(materials);
            updateKPIs(materials);

            const bestOverall = materials.reduce((a, b) =>
                b.eco_score > a.eco_score ? b : a
            );
            showAIReason(bestOverall);
        })
        .catch(err => console.error(err))
        .finally(() => {
            document.getElementById("loader").classList.add("hidden");
        });
}

/* =========================
   TABLE
========================= */
function populateTable(materials) {
    const tbody = document.getElementById("resultsBody");
    tbody.innerHTML = "";

    const minCost = Math.min(...materials.map(m => m.predicted_cost));
    const minCO2 = Math.min(...materials.map(m => m.predicted_co2));
    const bestEco = Math.max(...materials.map(m => m.eco_score));

    materials.forEach((m, index) => {
        const row = document.createElement("tr");

        if (m.eco_score === bestEco) row.classList.add("best-overall");

        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${m.material}</td>
            <td>${m.eco_score}</td>
            <td>${m.predicted_co2}</td>
            <td>${m.predicted_cost}</td>
            <td>${m.predicted_cost === minCost ? "Lowest Cost" : "-"}</td>
            <td>${m.predicted_co2 === minCO2 ? "Lowest CO₂" : "-"}</td>
        `;
        tbody.appendChild(row);
    });
}

/* =========================
   KPIs (SAFE)
========================= */
function updateKPIs(materials) {
    const avgEco = Math.round(
        materials.reduce((s, m) => s + m.eco_score, 0) / materials.length
    );
    const avgCO2 = Math.round(
        materials.reduce((s, m) => s + m.predicted_co2, 0) / materials.length
    );
    const avgCost = Math.round(
        materials.reduce((s, m) => s + m.predicted_cost, 0) / materials.length
    );

    setValue("avgEcoScore", avgEco);
    setValue("avgCO2", avgCO2);
    setValue("avgCost", avgCost);
}

/* =========================
   KPI SET (NO INFINITE LOOP)
========================= */
function setValue(id, value) {
    document.getElementById(id).innerText = value;
}

/* =========================
   AI REASONING
========================= */
function showAIReason(best) {
    document.getElementById("aiText").innerText =
        `${best.material} is recommended because it offers the best balance 
between sustainability and cost. It has a high eco score (${best.eco_score}), 
low CO₂ emissions (${best.predicted_co2}), and reasonable cost (${best.predicted_cost}).`;
}

/* =========================
   INSIGHT CARDS
========================= */
function showInsights(materials) {
    const lowestCost = materials.reduce((a, b) =>
        a.predicted_cost < b.predicted_cost ? a : b
    );
    const lowestCO2 = materials.reduce((a, b) =>
        a.predicted_co2 < b.predicted_co2 ? a : b
    );
    const bestOverall = materials.reduce((a, b) =>
        b.eco_score > a.eco_score ? b : a
    );

    document.getElementById("insightCost").innerText =
        `${lowestCost.material} has the lowest cost impact.`;

    document.getElementById("insightCO2").innerText =
        `${lowestCO2.material} produces the least CO₂ emissions.`;

    document.getElementById("insightBest").innerText =
        `${bestOverall.material} is the best overall sustainable option.`;
}

/* =========================
   CHART
========================= */
function drawChart(materials) {
    const ctx = document.getElementById("ecoChart").getContext("2d");

    if (chartInstance) chartInstance.destroy();

    chartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: materials.map(m => m.material),
            datasets: [
                {
                    label: "CO₂ Emissions",
                    data: materials.map(m => m.predicted_co2)
                },
                {
                    label: "Cost",
                    data: materials.map(m => m.predicted_cost)
                }
            ]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

/* =========================
   EXPORT CSV
========================= */
function exportCSV() {
    let csv = "Rank,Material,Eco Score,CO2,Cost\n";

    document.querySelectorAll("#resultsBody tr").forEach(row => {
        const cells = row.querySelectorAll("td");
        csv += `${cells[0].innerText},${cells[1].innerText},${cells[2].innerText},${cells[3].innerText},${cells[4].innerText}\n`;
    });

    downloadFile(csv, "EcoPack_AI_Report.csv", "text/csv");
}

/* =========================
   EXPORT PDF
========================= */
function exportPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    doc.text("EcoPack AI Sustainability Report", 14, 15);
    doc.autoTable({ html: "#resultsTable", startY: 20 });
    doc.save("EcoPack_AI_Report.pdf");
}

/* =========================
   DOWNLOAD HELPER
========================= */
function downloadFile(content, name, type) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([content], { type }));
    a.download = name;
    a.click();
}
/* =========================
   DARK MODE TOGGLE
========================= */
document.getElementById("darkToggle").addEventListener("click", () => {
    document.body.classList.toggle("dark");

    // Change button icon/text
    const btn = document.getElementById("darkToggle");
    if (document.body.classList.contains("dark")) {
        btn.innerText = "☀️ Light Mode";
        localStorage.setItem("theme", "dark");
    } else {
        btn.innerText = "🌙 Dark Mode";
        localStorage.setItem("theme", "light");
    }
});

/* =========================
   PERSIST THEME ON REFRESH
========================= */
(function loadTheme() {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
        document.body.classList.add("dark");
        document.getElementById("darkToggle").innerText = "☀️ Light Mode";
    }
})();
