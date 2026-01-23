const bio = document.getElementById("biodegradability_score");
const recycle = document.getElementById("recyclability_percent");

bio.oninput = () => document.getElementById("bioVal").innerText = bio.value;
recycle.oninput = () =>
    document.getElementById("recycleVal").innerText = recycle.value + "%";

let chart;

function predict() {
    const payload = {
        strength_encoded: Number(document.getElementById("strength_encoded").value),
        weight_capacity: Number(document.getElementById("weight_capacity").value),
        biodegradability_score: Number(bio.value),
        recyclability_percent: Number(recycle.value),
        cost_efficiency_score: Number(
            document.getElementById("cost_efficiency_score").value
        )
    };

    fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("cost").innerText =
            "₹ " + data.predicted_cost.toFixed(2) + " / kg";

        document.getElementById("co2").innerText =
            data.predicted_co2.toFixed(3) + " kg";

        drawChart(data.predicted_cost, data.predicted_co2);
        document.getElementById("status").innerText = "";
    })
    .catch(() => {
        document.getElementById("status").innerText =
            "Backend not responding. Please check Flask server.";
    });
}

function drawChart(cost, co2) {
    const ctx = document.getElementById("impactChart");

    if (chart) chart.destroy();

    chart = new Chart(ctx, {
        type: "scatter",
        data: {
            datasets: [{
                label: "Current Configuration",
                data: [{ x: cost, y: co2 }],
                backgroundColor: "#2ecc71",
                pointRadius: 8
            }]
        },
        options: {
            scales: {
                x: { title: { display: true, text: "Cost (₹/kg)" } },
                y: { title: { display: true, text: "CO₂ (kg)" } }
            }
        }
    });
}
