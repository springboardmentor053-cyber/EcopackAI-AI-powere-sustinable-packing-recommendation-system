document.getElementById("recommendForm").addEventListener("submit", function(e) {
    e.preventDefault();

    const data = [{
        material_type: "glass", // dummy, backend overrides
        strength: Number(document.getElementById("strength").value),
        weight_capacity: Number(document.getElementById("weight_capacity").value),
        biodegradability_score: Number(document.getElementById("bio_score").value),
        recyclability_percentage: Number(document.getElementById("recycle_score").value),
        fragility_level: Number(document.getElementById("fragility_level").value),
        shipping_type: document.getElementById("shipping_type").value
    }];

    fetch("/api/recommend", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(results => {

        const tbody = document.querySelector("#resultTable tbody");
        tbody.innerHTML = "";

        results.forEach((r, index) => {

            const highlight = index === 0 ? "table-success fw-bold" : "";

            const row = `
                <tr class="${highlight}">
                    <td>${r.material_type}</td>
                    <td>${r.predicted_cost.toFixed(3)}</td>
                    <td>${r.predicted_co2.toFixed(3)}</td>
                    <td>${r.rank_score.toFixed(3)}</td>
                </tr>
            `;

            tbody.innerHTML += row;
        });
    });
});
