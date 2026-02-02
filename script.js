// DOM Elements
const form = document.getElementById('predictionForm');
const loading = document.getElementById('loading');
const placeholder = document.getElementById('placeholder');
const resultDisplay = document.getElementById('resultsDisplay');
const validationSummary = document.getElementById('validationSummary');
const validationList = document.getElementById('validationList');
const sampleValuesBtn = document.getElementById('sampleValuesBtn');

// Result elements
const predictedCost = document.getElementById('predictedCost');
const predictedCO2 = document.getElementById('predictedCO2');
const suggestionText = document.getElementById('suggestionText');

// Input elements
const strengthInputs = document.querySelectorAll('input[name="strength"]');
const weightInput = document.getElementById('weightCapacity');
const biodegradabilityInput = document.getElementById('biodegradability');
const recyclabilityInput = document.getElementById('recyclability');
const costEfficiencyInput = document.getElementById('costEfficiency');

// Display elements for range inputs
const strengthValue = document.getElementById('strengthValue');
const biodegradabilityValue = document.getElementById('biodegradabilityValue');
const recyclabilityValue = document.getElementById('recyclabilityValue');
const costEfficiencyValue = document.getElementById('costEfficiencyValue');

// Error elements
const strengthError = document.getElementById('strengthError');
const weightError = document.getElementById('weightError');
const biodegradabilityError = document.getElementById('biodegradabilityError');
const recyclabilityError = document.getElementById('recyclabilityError');
const costError = document.getElementById('costError');

// Strength mapping
const strengthMap = {
    '1': { label: 'Low', strength_mpa: 25 },
    '2': { label: 'Medium', strength_mpa: 40 },
    '3': { label: 'High', strength_mpa: 55 }
};

// Initialize range displays
updateStrengthDisplay();
updateBiodegradabilityDisplay();
updateRecyclabilityDisplay();
updateCostEfficiencyDisplay();

// Event Listeners
strengthInputs.forEach(input => {
    input.addEventListener('change', updateStrengthDisplay);
});

biodegradabilityInput.addEventListener('input', updateBiodegradabilityDisplay);
recyclabilityInput.addEventListener('input', updateRecyclabilityDisplay);
costEfficiencyInput.addEventListener('input', updateCostEfficiencyDisplay);

sampleValuesBtn.addEventListener('click', loadSampleValues);

// Update display functions
function updateStrengthDisplay() {
    const selected = document.querySelector('input[name="strength"]:checked');
    if (selected) {
        strengthValue.textContent = `${strengthMap[selected.value].label} (${selected.value})`;
    }
}

function updateBiodegradabilityDisplay() {
    biodegradabilityValue.textContent = biodegradabilityInput.value;
}

function updateRecyclabilityDisplay() {
    recyclabilityValue.textContent = `${recyclabilityInput.value}%`;
}

function updateCostEfficiencyDisplay() {
    costEfficiencyValue.textContent = costEfficiencyInput.value;
}

// Load sample values
function loadSampleValues() {
    // Set strength to High (3)
    document.getElementById('strength-high').checked = true;
    updateStrengthDisplay();
    
    // Set other values
    weightInput.value = '5.0';
    biodegradabilityInput.value = '7.5';
    recyclabilityInput.value = '75';
    costEfficiencyInput.value = '6.0';
    
    // Update displays
    updateBiodegradabilityDisplay();
    updateRecyclabilityDisplay();
    updateCostEfficiencyDisplay();
    
    // Clear any errors
    clearValidationErrors();
    validationSummary.style.display = 'none';
    
    // Show confirmation
    alert('Sample values loaded! Click "Analyze Material Sustainability" to run predictions.');
}

// Clear all validation errors
function clearValidationErrors() {
    strengthError.textContent = '';
    weightError.textContent = '';
    biodegradabilityError.textContent = '';
    recyclabilityError.textContent = '';
    costError.textContent = '';
}

// Validation functions
function validateStrength() {
    const selected = document.querySelector('input[name="strength"]:checked');
    if (!selected) {
        strengthError.textContent = 'Please select a material strength';
        return false;
    }
    strengthError.textContent = '';
    return true;
}

function validateWeight() {
    const weight = parseFloat(weightInput.value);
    if (isNaN(weight) || weight < 0.1 || weight > 50) {
        weightError.textContent = 'Weight must be between 0.1 and 50 kg';
        return false;
    }
    weightError.textContent = '';
    return true;
}

function validateBiodegradability() {
    const score = parseFloat(biodegradabilityInput.value);
    if (isNaN(score) || score < 1 || score > 10) {
        biodegradabilityError.textContent = 'Score must be between 1 and 10';
        return false;
    }
    biodegradabilityError.textContent = '';
    return true;
}

function validateRecyclability() {
    const percent = parseFloat(recyclabilityInput.value);
    if (isNaN(percent) || percent < 0 || percent > 100) {
        recyclabilityError.textContent = 'Percentage must be between 0 and 100';
        return false;
    }
    recyclabilityError.textContent = '';
    return true;
}

function validateCostEfficiency() {
    const score = parseFloat(costEfficiencyInput.value);
    if (isNaN(score) || score < 1 || score > 10) {
        costError.textContent = 'Score must be between 1 and 10';
        return false;
    }
    costError.textContent = '';
    return true;
}

// Validate all inputs
function validateAllInputs() {
    const validations = [
        { valid: validateStrength(), field: 'Material Strength' },
        { valid: validateWeight(), field: 'Weight Capacity' },
        { valid: validateBiodegradability(), field: 'Biodegradability Score' },
        { valid: validateRecyclability(), field: 'Recyclability Percentage' },
        { valid: validateCostEfficiency(), field: 'Cost Efficiency Score' }
    ];
    
    const invalidFields = validations.filter(v => !v.valid).map(v => v.field);
    
    if (invalidFields.length > 0) {
        validationList.innerHTML = '';
        invalidFields.forEach(field => {
            const li = document.createElement('li');
            li.textContent = field;
            validationList.appendChild(li);
        });
        validationSummary.style.display = 'block';
        return false;
    }
    
    validationSummary.style.display = 'none';
    return true;
}

// Map UI data to backend API format
function mapToBackendData() {
    const selectedStrength = document.querySelector('input[name="strength"]:checked');
    
    // Default mapping based on the example you provided
    // In a real application, you would have more sophisticated mapping logic
    const strengthValue = selectedStrength ? strengthMap[selectedStrength.value].strength_mpa : 40;
    
    // Map cost efficiency score to cost per unit
    // Higher efficiency = lower cost (inverse relationship)
    const costEfficiency = parseFloat(costEfficiencyInput.value);
    const costPerUnit = 100 - (costEfficiency * 7); // Scale factor
    
    return {
        strength_mpa: strengthValue,
        biodegradability_score: parseFloat(biodegradabilityInput.value),
        recyclability_percent: parseFloat(recyclabilityInput.value),
        flexibility: "Medium", // Default value for demo
        cost_per_unit: Math.max(costPerUnit, 10), // Ensure minimum cost
        co2_emission_score: 26 // Default value for demo
    };
}

// Get CO2 indicator class
function getCO2Indicator(co2Value) {
    if (co2Value < 3) return 'low';
    if (co2Value < 7) return 'medium';
    return 'high';
}

// Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(value);
}

// Form submission
form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (!validateAllInputs()) {
        validationSummary.scrollIntoView({ behavior: 'smooth' });
        return;
    }
    
    // Hide previous results and show loading
    placeholder.style.display = 'none';
    resultDisplay.style.display = 'none';
    validationSummary.style.display = 'none';
    loading.style.display = 'block';
    
    try {
        // Map UI data to backend format
        const apiData = mapToBackendData();
        
        console.log('Sending data to backend:', apiData);
        
        // Make API call to Flask backend
        const response = await fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(apiData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const result = await response.json();
        
        console.log('Received response from backend:', result);
        
        // Hide loading
        loading.style.display = 'none';
        
        // Check for errors in response
        if (result.error) {
            throw new Error(result.error);
        }
        
        // Display results
        predictedCost.textContent = formatCurrency(result.predicted_cost);
        predictedCO2.textContent = `${result.predicted_co2.toFixed(2)} kg`;
        
        // Add CO2 indicator
        const co2Indicator = document.createElement('span');
        co2Indicator.className = `co2-indicator ${getCO2Indicator(result.predicted_co2)}`;
        co2Indicator.textContent = getCO2Indicator(result.predicted_co2).toUpperCase();
        predictedCO2.appendChild(co2Indicator);
        
        // Display suggestion
        suggestionText.textContent = result.suggestion || 'No specific recommendation available.';
        
        // Show results
        resultDisplay.style.display = 'block';
        resultDisplay.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('Error during prediction:', error);
        
        // Hide loading
        loading.style.display = 'none';
        
        // Show error in placeholder
        placeholder.style.display = 'block';
        placeholder.innerHTML = `
            <i class="fas fa-exclamation-triangle" style="color:#E74C3C;font-size:3rem;"></i>
            <h3>Error Loading Predictions</h3>
            <p>${error.message}</p>
            <p style="margin-top:20px;font-size:0.9rem;">
                Make sure your Flask backend is running at <code>http://127.0.0.1:5000</code>
            </p>
            <button onclick="loadSampleValues()" class="sample-btn" style="margin-top:15px;">
                <i class="fas fa-redo"></i> Try Sample Values
            </button>
        `;
    }
});

// Initialize with sample values on first load (optional)
window.addEventListener('load', function() {
    console.log('Material Sustainability Analyzer UI loaded');
    console.log('Make sure Flask backend is running at http://127.0.0.1:5000');
});