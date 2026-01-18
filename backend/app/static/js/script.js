document.addEventListener('DOMContentLoaded', () => {
    // Theme Toggle Logic
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;
    const savedTheme = localStorage.getItem('theme');

    if (savedTheme === 'light') {
        html.setAttribute('data-theme', 'light');
        if (themeToggle) themeToggle.innerHTML = '☀️';
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';

            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            themeToggle.innerHTML = newTheme === 'light' ? '☀️' : '🌙';
        });
    }

    // Form Handling
    const form = document.getElementById('recommendationForm');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
});

async function handleFormSubmit(event) {
    event.preventDefault();

    // UI Elements
    const submitBtn = document.getElementById('submitBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsSection = document.getElementById('resultsSection');
    const tbody = document.getElementById('resultsTableBody');

    // Reset UI
    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Analyzing...';
    resultsSection.style.display = 'none';
    loadingSpinner.style.display = 'block';
    tbody.innerHTML = ''; // Clear previous results

    // Gather Data
    const category = document.getElementById('category').value;
    const weight = document.getElementById('weight').value;
    const fragility = document.getElementById('fragility').value;
    const waterResistant = document.getElementById('waterResistant').checked;

    try {
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_category: category,
                weight_kg: weight,
                fragility: fragility,
                water_resistant: waterResistant
            })
        });

        const data = await response.json();

        if (response.ok && data.recommendations && data.recommendations.length > 0) {
            renderResults(data.recommendations);
        } else {
            // Show toast or alert for no results
            showNotification(data.message || "No recommendations found.", "warning");
        }

    } catch (error) {
        console.error('Error:', error);
        showNotification("Failed to connect to the server. Please check your connection.", "error");
    } finally {
        loadingSpinner.style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Get Recommendations';
    }
}

function renderResults(recommendations) {
    const tbody = document.getElementById('resultsTableBody');
    const resultsSection = document.getElementById('resultsSection');

    recommendations.forEach((item, index) => {
        const row = document.createElement('tr');
        row.className = 'result-row';
        row.style.animationDelay = `${index * 100}ms`; // Staggered animation

        // Format Numbers
        const score = parseFloat(item.final_rank_score).toFixed(1);
        const cost = parseFloat(item.predicted_cost_inr).toFixed(2);
        const co2 = parseFloat(item.predicted_co2_score).toFixed(2);
        const origin = item.manufacturing_place || 'Global';
        const weightCap = item.weight_capacity_kg;

        row.innerHTML = `
            <td>
                <div class="d-flex align-items-center">
                    <span class="material-icon me-2">📦</span>
                    ${item.material_type}
                </div>
            </td>
            <td>
                <div class="suitability-badge">
                   ${score}/100
                </div>
            </td>
            <td><span class="metric-value">₹${cost}</span></td>
            <td><span class="metric-value text-warning">${co2} CO₂</span></td>
            <td>${origin}</td>
            <td>${weightCap} kg</td>
        `;
        tbody.appendChild(row);
    });

    resultsSection.style.display = 'block';

    // Smooth scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

function resetForm() {
    const form = document.getElementById('recommendationForm');
    const resultsSection = document.getElementById('resultsSection');

    if (form) form.reset();
    if (resultsSection) {
        resultsSection.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            resultsSection.style.display = 'none';
            resultsSection.style.animation = '';
        }, 300);
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showNotification(message, type = 'info') {
    // Simple alert for now, can be upgraded to a toast
    alert(message);
}
