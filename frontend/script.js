// Scroll Handling
function scrollToSection(id) {
    document.getElementById(id).scrollIntoView({ behavior: 'smooth' });
}

// Form Submission
document.getElementById('recommendationDetailParam').addEventListener('submit', async function (e) {
    e.preventDefault();

    // UI Helpers
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = document.getElementById('loadingSpinner');
    const resultsSection = document.getElementById('results');
    const resultsGrid = document.getElementById('resultsGrid');
    const resultCount = document.getElementById('resultCount');

    // State: Loading
    submitBtn.disabled = true;
    btnText.textContent = 'Analyzing...';
    spinner.classList.remove('d-none');

    // Get Inputs
    const weight = document.getElementById('weight').value;
    const strength = document.getElementById('strength').value;
    const waterResistant = document.getElementById('waterResistant').checked ? 1 : 0;

    const payload = {
        weight_capacity_kg: weight,
        strength: strength,
        water_resistance: waterResistant
    };

    try {
        // Fetch Data
        // Ideally should be /api/recommend if hosted on same origin, but using full URL for safety in dev
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        // Show Results Section
        resultsSection.classList.remove('d-none');
        scrollToSection('results'); // Scroll to results

        // Show AI Insight (Gemini)
        const insightBox = document.getElementById('aiInsightBox');
        if (data.aiInsight) {
            document.getElementById('aiInsightText').textContent = data.aiInsight;
            insightBox.classList.remove('d-none');
        } else {
            insightBox.classList.add('d-none');
        }

        // Clear previous
        resultsGrid.innerHTML = '';
        resultCount.textContent = data.count || 0;

        if (!data.recommendations || data.recommendations.length === 0) {
            resultsGrid.innerHTML = `
                <div class="col-12 text-center py-5">
                    <h4 class="text-muted">No materials match your exact criteria.</h4>
                    <p>Try lowering the strength requirement or checking other categories.</p>
                </div>
            `;
        } else {
            // Render Cards
            data.recommendations.forEach((item, index) => {
                // Determine rank styling
                let rankClass = '';
                if (index === 0) rankClass = 'rank-1';
                else if (index === 1) rankClass = 'rank-2';
                else if (index === 2) rankClass = 'rank-3';
                else rankClass = 'bg-dark text-white'; // Fallback

                const cardDelay = index * 0.1; // Stagger effect

                const cardHtml = `
                    <div class="col-md-6 col-lg-4">
                        <div class="result-card h-100 position-relative p-4 fade-in-up" style="animation-delay: ${cardDelay}s">
                            <div class="rank-badge ${rankClass} shadow">${index + 1}</div>
                            
                            <h5 class="fw-bold mb-1 pt-2">${item.material_name}</h5>
                            <p class="text-muted small mb-3">${item.description}</p>
                            
                            <div class="metrics mt-4">
                                <!-- Cost -->
                                <div class="d-flex justify-content-between mb-1">
                                    <small class="text-secondary fw-semibold">Estimated Cost</small>
                                    <span class="text-dark fw-bold">₹${item.predicted_cost}</span>
                                </div>
                                <div class="progress mb-3" style="height: 6px;">
                                    <div class="progress-bar bg-warning" role="progressbar" style="width: ${Math.min(item.predicted_cost * 2, 100)}%"></div>
                                </div>
                                
                                <!-- CO2 -->
                                <div class="d-flex justify-content-between mb-1">
                                    <small class="text-secondary fw-semibold">CO₂ Impact</small>
                                    <span class="text-dark fw-bold">${item.predicted_co2} kg</span>
                                </div>
                                <div class="progress mb-3" style="height: 6px;">
                                    <div class="progress-bar bg-danger" role="progressbar" style="width: ${Math.min(item.predicted_co2 * 10, 100)}%"></div>
                                </div>

                                <!-- Sustainability Score -->
                                <div class="d-flex justify-content-between align-items-end mt-3 p-3 bg-light-subtle rounded">
                                    <div class="text-start">
                                        <div class="small text-muted text-uppercase mb-1" style="font-size: 0.7rem;">Sustainability Score</div>
                                        <h3 class="mb-0 text-success fw-bold">${Math.round(item.sustainability_score)}<span class="fs-6 text-muted">/100</span></h3>
                                    </div>
                                    <i class="fa-solid fa-leaf text-success fa-2x mb-1 opacity-50"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                resultsGrid.innerHTML += cardHtml;
            });
        }

    } catch (error) {
        console.error('Error:', error);
        alert('Failed to connect to the EcoPackAI Brain. Ensure the backend is running.');
    } finally {
        // Reset Button
        submitBtn.disabled = false;
        btnText.textContent = 'Find Best Packaging';
        spinner.classList.add('d-none');
    }
});
