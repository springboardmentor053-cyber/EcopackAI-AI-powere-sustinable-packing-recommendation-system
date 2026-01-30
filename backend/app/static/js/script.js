document.addEventListener('DOMContentLoaded', () => {
    // Initialize Tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })

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
        form.addEventListener('submit', (e) => handleFormSubmit(e, false));
    }

    const aiBtn = document.getElementById('aiSubmitBtn');
    if (aiBtn) {
        aiBtn.addEventListener('click', (e) => handleFormSubmit(e, true));
    }
});

async function handleFormSubmit(event, forceAI = false) {
    if (event) event.preventDefault();

    // UI Elements
    const submitBtn = document.getElementById('submitBtn');
    const aiBtn = document.getElementById('aiSubmitBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsSection = document.getElementById('resultsSection');
    const tbody = document.getElementById('resultsTableBody');
    const loadingText = loadingSpinner.querySelector('.loading-text');

    // Reset UI
    submitBtn.disabled = true;
    if (aiBtn) aiBtn.disabled = true;

    if (forceAI) {
        if (aiBtn) aiBtn.innerHTML = '🤖 Thinking...';
        loadingText.innerText = 'Consulting Gemini AI for sustainable options...';
    } else {
        submitBtn.innerHTML = 'Analyzing...';
        loadingText.innerText = 'Analyzing material properties & CO₂ impact...';
    }

    resultsSection.style.display = 'none';
    loadingSpinner.style.display = 'block';
    tbody.innerHTML = ''; // Clear previous results

    // Gather Data
    const category = document.getElementById('category').value;
    const weight = document.getElementById('weight').value;
    const fragility = document.getElementById('fragility').value;
    const waterResistant = document.getElementById('waterResistant').checked;

    // Basic Validation
    if (!category || !weight) {
        showNotification("Please fill in all required fields.", "warning");
        loadingSpinner.style.display = 'none';
        submitBtn.disabled = false;
        if (aiBtn) aiBtn.disabled = false;
        submitBtn.innerHTML = '<span class="fs-4">✨ Get Recommendations</span>';
        if (aiBtn) aiBtn.innerHTML = '<span class="fs-4">🤖 Ask Gemini AI</span>';
        return;
    }

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
                water_resistant: waterResistant,
                force_gemini: forceAI
            })
        });

        const data = await response.json();

        if (response.ok && data.recommended_materials && data.recommended_materials.length > 0) {
            renderResults(data.recommended_materials);
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
        if (aiBtn) aiBtn.disabled = false;

        submitBtn.innerHTML = '<span class="fs-4">✨ Get Recommendations</span>';
        if (aiBtn) aiBtn.innerHTML = '<span class="fs-4">🤖 Ask Gemini AI</span>';
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
        const score = parseFloat(item.final_rank_score || 0).toFixed(1);
        const cost = item.estimated_cost; // Already formatted
        const co2 = item.co2_impact;      // Already formatted text
        const origin = item.manufacturing_place || 'Global';
        const weightCap = item.weight_capacity_kg;

        row.innerHTML = `
            <td>
                <div class="d-flex align-items-center">
                    <span class="material-icon me-2">📦</span>
                    ${item.material_name}
                </div>
            </td>
            <td>
                <div class="suitability-badge">
                   ${score}/100
                </div>
            </td>
            <td><span class="metric-value">${cost}</span></td>
            <td><span class="metric-value text-warning">${co2}</span></td>
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
