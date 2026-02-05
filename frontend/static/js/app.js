document.getElementById("recommendForm").addEventListener("submit", function(e) {
    e.preventDefault();

    const statusEl = document.getElementById("resultStatus");
    const button = document.getElementById("recommendBtn");
    const tbody = document.querySelector("#resultTable tbody");

  
    statusEl.className = "alert alert-warning";
    statusEl.innerHTML = '<i class="bi bi-hourglass-split"></i> Analyzing materials and generating recommendations...';
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
    tbody.innerHTML = "";

    const data = [{
        material_type: "glass", 
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
    .then(res => {
        if (!res.ok) {
            throw new Error("Request failed. Please try again.");
        }
        return res.json();
    })
    .then(payload => {
        const results = payload?.data;
        if (!Array.isArray(results) || results.length === 0) {
            statusEl.className = "alert alert-warning";
            statusEl.innerHTML = '<i class="bi bi-exclamation-triangle"></i> No results returned. Try adjusting your inputs.';
            return;
        }

        
        statusEl.className = "alert alert-success";
        statusEl.innerHTML = `<i class="bi bi-check-circle"></i> Successfully analyzed ${results.length} materials. Top recommendations shown below.`;

        const materialIcons = {
            'glass': '🥃',
            'plastic': '🧴',
            'metal': '🥫',
            'paper': '📄',
            'bagasse': '🌾',
            'bamboo': '🎋',
            'jute': '🧺'
        };

        results.forEach((r, index) => {
            const rank = index + 1;
            const rankClass = rank === 1 ? 'rank-1' : '';
            
            let rankBadgeClass = 'rank-badge';
            if (rank === 1) rankBadgeClass += ' gold';
            else if (rank === 2) rankBadgeClass += ' silver';
            else if (rank === 3) rankBadgeClass += ' bronze';

            const icon = materialIcons[r.material_type.toLowerCase()] || '📦';
            
            
            const costInRupees = (r.predicted_cost * 500).toFixed(2);
            const co2 = r.predicted_co2.toFixed(3);
            const score = r.rank_score.toFixed(4);
            
           
            const scorePercent = (r.rank_score * 100).toFixed(1);

            const row = `
                <tr class="${rankClass}">
                    <td><span class="${rankBadgeClass}">${rank}</span></td>
                    <td><span class="material-icon">${icon}</span><strong>${r.material_type.charAt(0).toUpperCase() + r.material_type.slice(1)}</strong></td>
                    <td>₹${costInRupees}</td>
                    <td>${co2} kg</td>
                    <td>
                        <div class="d-flex align-items-center">
                            <div class="progress flex-grow-1 me-2" style="height: 20px;">
                                <div class="progress-bar bg-success" role="progressbar" 
                                     style="width: ${scorePercent}%" 
                                     aria-valuenow="${scorePercent}" 
                                     aria-valuemin="0" 
                                     aria-valuemax="100">
                                </div>
                            </div>
                            <span>${score}</span>
                        </div>
                    </td>
                </tr>
            `;

            tbody.innerHTML += row;
        });
    })
    .catch(() => {
        statusEl.className = "alert alert-danger";
        statusEl.innerHTML = '<i class="bi bi-x-circle"></i> Something went wrong. Please check your inputs and try again.';
    })
    .finally(() => {
        button.disabled = false;
        button.innerHTML = '<i class="bi bi-magic"></i> Generate Recommendations';
    });
});
