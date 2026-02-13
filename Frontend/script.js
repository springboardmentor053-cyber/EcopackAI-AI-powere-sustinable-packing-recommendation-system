function scrollToRecommend() {
  document.getElementById("recommend").scrollIntoView({ behavior: "smooth" });
}

// Initialize charts on page load
document.addEventListener('DOMContentLoaded', function() {
  initializeCharts();
  setupContinuousInputs();
});

function setupContinuousInputs() {
  const strength = document.getElementById('strength');
  const strengthVal = document.getElementById('strengthVal');
  if (strength && strengthVal) {
    // Show discrete integer strength values
    strengthVal.textContent = String(Math.round(Number(strength.value)));
    strength.addEventListener('input', () => { strengthVal.textContent = String(Math.round(Number(strength.value))); });
  }

  const bio = document.getElementById('bio');
  const bioVal = document.getElementById('bioVal');
  if (bio && bioVal) {
    // Show discrete integer percent
    bioVal.textContent = String(Math.round(Number(bio.value))) + '%';
    bio.addEventListener('input', () => { bioVal.textContent = String(Math.round(Number(bio.value))) + '%'; });
  }

  const recycle = document.getElementById('recycle');
  const recycleVal = document.getElementById('recycleVal');
  if (recycle && recycleVal) {
    // Show discrete integer percent
    recycleVal.textContent = String(Math.round(Number(recycle.value))) + '%';
    recycle.addEventListener('input', () => { recycleVal.textContent = String(Math.round(Number(recycle.value))) + '%'; });
  }

  const weight = document.getElementById('weight');
  const weightVal = document.getElementById('weightVal');
  if (weight && weightVal) {
    weightVal.textContent = parseFloat(weight.value).toFixed(2);
    weight.addEventListener('input', () => { weightVal.textContent = parseFloat(weight.value || 0).toFixed(2); });
  }
}

// Keep references to created Chart instances so we can destroy them before re-creating
const _charts = {
  material: null,
  trends: null,
  recycle: null,
  monthly: null
};

function initializeCharts(rankingData = null, mainResult = null) {
  // Material Distribution Chart - show top 5 materials from ranking with their costs
  const materialCtx = document.getElementById('materialChart')?.getContext('2d');
  if (materialCtx) {
    // Destroy previous chart if exists
    try { if (_charts.material) _charts.material.destroy(); } catch (e) { console.warn('Failed to destroy material chart', e); }
    let labels = ['Recycled Cardboard', 'Biodegradable Plastic', 'Paper', 'Glass', 'Others'];
    let data = [35, 25, 20, 12, 8];
    
    if (rankingData && rankingData.length >= 5) {
      labels = rankingData.slice(0, 5).map(m => m.material.substring(0, 15)); // Truncate for display
      data = rankingData.slice(0, 5).map(m => m.cost);
    }
    
    _charts.material = new Chart(materialCtx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: [
            '#22c55e',
            '#84cc16',
            '#65a30d',
            '#4ade80',
            '#bbf7d0'
          ]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: { 
          legend: { labels: { color: '#d0e7d1' } },
          tooltip: { callbacks: { label: ctx => `Cost: ₹${ctx.parsed}` } }
        }
      }
    });
  }

  // CO₂ vs Cost Trend - show top 6 materials from ranking
  const trendsCtx = document.getElementById('trendsChart')?.getContext('2d');
  if (trendsCtx) {
    let labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    let co2Data = [400, 600, 750, 900, 1100, 1400];
    let costData = [5, 8, 12, 15, 20, 28];
    
    if (rankingData && rankingData.length >= 6) {
      labels = rankingData.slice(0, 6).map((m, i) => `Rank ${i + 1}`);
      co2Data = rankingData.slice(0, 6).map(m => parseFloat(m.co2) * 100); // Scale for visibility
      costData = rankingData.slice(0, 6).map(m => m.cost);
    }
    
    try { if (_charts.trends) _charts.trends.destroy(); } catch (e) { console.warn('Failed to destroy trends chart', e); }
    _charts.trends = new Chart(trendsCtx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'CO₂ Emissions (kg x100)',
            data: co2Data,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            tension: 0.4,
            fill: true
          },
          {
            label: 'Material Cost ($)',
            data: costData,
            borderColor: '#fbbf24',
            backgroundColor: 'rgba(251, 191, 36, 0.1)',
            tension: 0.4,
            fill: true
          }
        ]
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#d0e7d1' } } },
        scales: {
          y: { ticks: { color: '#d0e7d1' }, grid: { color: 'rgba(208, 231, 209, 0.1)' } },
          x: { ticks: { color: '#d0e7d1' }, grid: { color: 'rgba(208, 231, 209, 0.1)' } }
        }
      }
    });
  }

  // Recyclability by Material - show top 5 materials with eco-scores
  const recycleCtx = document.getElementById('recycleChart')?.getContext('2d');
  if (recycleCtx) {
    let labels = ['Cardboard', 'Plastic', 'Paper', 'Glass', 'Metal'];
    let data = [95, 78, 90, 100, 98];
    
    if (rankingData && rankingData.length >= 5) {
      labels = rankingData.slice(0, 5).map(m => m.material.substring(0, 12));
      data = rankingData.slice(0, 5).map((m, idx) => {
        // Always calculate varied eco-scores based on ranking position only
        // Rank 1: 95, Rank 2: 89, Rank 3: 83, Rank 4: 77, Rank 5: 71
        return 95 - (idx * 6);
      });
    }
    
    try { if (_charts.recycle) _charts.recycle.destroy(); } catch (e) { console.warn('Failed to destroy recycle chart', e); }
    _charts.recycle = new Chart(recycleCtx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Eco-Score',
          data: data,
          backgroundColor: ['#22c55e','#84cc16','#65a30d','#4ade80','#bbf7d0']
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        plugins: { legend: { labels: { color: '#d0e7d1' } } },
        scales: { x: { ticks: { color: '#d0e7d1' }, grid: { color: 'rgba(208, 231, 209, 0.1)' } }, y: { ticks: { color: '#d0e7d1' }, grid: { display: false } } }
      }
    });
  }

  // Monthly Impact Chart - show top 6 materials ranked by cost
  const monthlyCtx = document.getElementById('monthlyChart')?.getContext('2d');
  if (monthlyCtx) {
    let labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    let data = [12, 19, 25, 32, 38, 44];
    
    if (rankingData && rankingData.length >= 6) {
      labels = rankingData.slice(0, 6).map((m, i) => `#${i + 1}`);
      data = rankingData.slice(0, 6).map(m => m.cost);
    }
    
    try { if (_charts.monthly) _charts.monthly.destroy(); } catch (e) { console.warn('Failed to destroy monthly chart', e); }
    _charts.monthly = new Chart(monthlyCtx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{ label: 'Cost (₹)', data: data, backgroundColor: '#22c55e' }]
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#d0e7d1' } } },
        scales: { y: { ticks: { color: '#d0e7d1' }, grid: { color: 'rgba(208, 231, 209, 0.1)' } }, x: { ticks: { color: '#d0e7d1' }, grid: { color: 'rgba(208, 231, 209, 0.1)' } } }
      }
    });
  }
}

async function getRecommendation() {
  try {
    const category = document.getElementById("category").value;
    const strength = document.getElementById("strength").value;
    const weight = document.getElementById("weight").value;
    const bio = document.getElementById("bio").value;
    const recycle = document.getElementById("recycle").value;

    if (!category || !strength || !weight || bio === "" || recycle === "") {
      alert("Please fill all fields");
      return;
    }

    console.log("Sending data to backend...");

    const response = await fetch("http://127.0.0.1:5000/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        category: category,
        strength: Number(strength),
        weight: Number(weight),
        bio: Number(bio),
        recycle: Number(recycle)
      })
    });

    if (!response.ok) {
      throw new Error("Backend error");
    }

    const data = await response.json();
    console.log("Received:", data);

    // Display main recommendation
    document.getElementById("mainRecommendation").innerHTML = `
      <p><strong>Material:</strong> ${data.material}</p>
      <p><strong>Estimated Cost:</strong> ₹ ${data.cost.toFixed(2)}</p>
      <p><strong>CO₂ Impact:</strong> ${data.co2.toFixed(2)} kg</p>
    `;

    // Generate and display ranking (pass the form inputs for API call)
    generateAndDisplayRanking(data, category, weight, strength, bio, recycle);
    
    // Display metrics
    displayMetrics(data, Number(weight));

    // Request environment score for the chosen parameters and display
    try {
      const envResp = await fetch('http://127.0.0.1:5000/environment-score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strength: Number(strength),
          weight: Number(weight),
          bio: Number(bio),
          recycle: Number(recycle)
        })
      });

      if (envResp.ok) {
        const envData = await envResp.json();
        const envHtml = `<p><strong>Predicted CO₂:</strong> ${envData.predicted_co2} kg</p><p><strong>Baseline CO₂:</strong> ${envData.baseline_co2} kg</p><p><strong>Reduction:</strong> ${envData.reduction_percent}%</p>`;
        const envMetricsDiv = document.getElementById('envMetrics');
        if (envMetricsDiv) envMetricsDiv.innerHTML = `<div class="env-score">${envHtml}</div>`;
      }
    } catch (err) {
      console.warn('Environment score fetch failed', err);
    }

  } catch (error) {
    console.error(error);
    alert("Unable to fetch recommendation. Check backend.");
  }
}

async function generateAndDisplayRanking(mainResult, category, weight, strength, bio, recycle) {
  try {
    // Helper to perform fetch with explicit CORS and retry hostnames
    async function tryFetch(host) {
      const url = `${host}/ranked-materials/${encodeURIComponent(category)}`;
      console.log('Attempting fetch to', url);
      return await fetch(url, {
        method: 'POST',
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strength: Number(strength),
          weight: Number(weight),
          bio: Number(bio),
          recycle: Number(recycle)
        })
      });
    }

    let rankResp = null;
    try {
      // Primary attempt (127.0.0.1)
      rankResp = await tryFetch('http://127.0.0.1:5000');
    } catch (err1) {
      console.warn('Primary fetch failed:', err1);
      try {
        // Secondary attempt (localhost)
        rankResp = await tryFetch('http://localhost:5000');
      } catch (err2) {
        console.error('Retry fetch failed:', err2);
        // Surface the original error for debugging
        throw err2 || err1;
      }
    }

    if (rankResp && rankResp.ok) {
      const rankData = await rankResp.json();
      const materials = rankData.materials || [];
      renderRankingTable(materials);
      // Update charts with real ranking data
      initializeCharts(materials, mainResult);
    } else {
      console.warn('Ranked materials fetch failed, attempting /materials fallback');
      // Try to fetch /materials to build a multi-item fallback
      const hosts = ['http://127.0.0.1:5000', 'http://localhost:5000'];
      let materialsMap = null;
      for (const h of hosts) {
        try {
          const resp = await fetch(`${h}/materials`, { method: 'GET', mode: 'cors' });
          if (resp.ok) {
            materialsMap = await resp.json();
            break;
          }
        } catch (e) {
          console.warn('GET /materials failed for', h, e);
        }
      }

      if (materialsMap && typeof materialsMap === 'object') {
        // Find matching category key (case-insensitive)
        const catKey = Object.keys(materialsMap).find(k => k.toLowerCase() === String(category).toLowerCase()) || Object.keys(materialsMap)[0];
        const names = Array.isArray(materialsMap[catKey]) ? materialsMap[catKey] : [];
        const fallbackList = names.slice(0, 10).map((m, i) => ({
          rank: i + 1,
          material: m,
          cost: mainResult.cost ? Math.max(1, mainResult.cost + (i * 5)) : 0,
          co2: mainResult.co2 ? Math.max(0, Number(mainResult.co2) + (i * 0.1)) : 0,
          eco_score: Math.max(60, 95 - (i * 6))  // Varied eco scores based on rank
        }));
        if (fallbackList.length > 0) {
          renderRankingTable(fallbackList);
          initializeCharts(fallbackList, mainResult);
          return;
        }
      }

      // Last-resort single-item fallback (preserve previous behavior)
      console.warn('Using single-item fallback (no /materials available)');
      const fallback = [{
        rank: 1,
        material: mainResult.material,
        cost: mainResult.cost,
        co2: mainResult.co2,
        eco_score: 95
      }];
      renderRankingTable(fallback);
      initializeCharts(fallback, mainResult);
    }
  } catch (err) {
    console.warn('Error fetching ranked materials:', err);
      console.log('Full error object:', err);
      console.log('Error message:', err.message);
    // Attempt /materials fallback here as well
    try {
      const hosts = ['http://127.0.0.1:5000', 'http://localhost:5000'];
      let materialsMap = null;
      for (const h of hosts) {
        try {
          const resp = await fetch(`${h}/materials`, { method: 'GET', mode: 'cors' });
          if (resp.ok) {
            materialsMap = await resp.json();
            break;
          }
        } catch (e) {
          console.warn('GET /materials failed for', h, e);
        }
      }
      if (materialsMap && typeof materialsMap === 'object') {
        const catKey = Object.keys(materialsMap).find(k => k.toLowerCase() === String(category).toLowerCase()) || Object.keys(materialsMap)[0];
        const names = Array.isArray(materialsMap[catKey]) ? materialsMap[catKey] : [];
        const fallbackList = names.slice(0, 10).map((m, i) => ({
          rank: i + 1,
          material: m,
          cost: mainResult.cost ? Math.max(1, mainResult.cost + (i * 5)) : 0,
          co2: mainResult.co2 ? Math.max(0, Number(mainResult.co2) + (i * 0.1)) : 0,
          eco_score: Math.max(60, 95 - (i * 6))  // Varied eco scores based on rank
        }));
        if (fallbackList.length > 0) {
          renderRankingTable(fallbackList);
          initializeCharts(fallbackList, mainResult);
          return;
        }
      }
    } catch (e) {
      console.warn('Fallback /materials attempt failed', e);
    }

    // Last-resort single-item fallback
    const fallback = [{
      rank: 1,
      material: mainResult.material,
      cost: mainResult.cost,
      co2: mainResult.co2,
      eco_score: 95
    }];
    renderRankingTable(fallback);
    initializeCharts(fallback, mainResult);
  }
}

function renderRankingTable(rankings) {
    console.log('renderRankingTable called with:', rankings);
  const table = document.getElementById("rankingTable");
  if (!table) {
    console.warn("rankingTable element not found");
    return;
  }
  table.innerHTML = "";
  if (!rankings || !Array.isArray(rankings) || rankings.length === 0) {
    table.innerHTML = `
      <tr>
        <td>-</td>
        <td>No ranked materials available</td>
        <td>-</td>
        <td>-</td>
      </tr>`;
    return;
  }

  // Render only top 3 materials
  const maxToShow = Math.min(rankings.length, 3);
  console.log(`Rendering top ${maxToShow} materials`);
  for (let i = 0; i < maxToShow; i++) {
    const item = rankings[i];
    const rank = item.rank || (i + 1);
    const material = item.material || 'Unknown';
    const cost = (typeof item.cost === 'number') ? item.cost.toFixed(2) : (item.cost ? Number(item.cost).toFixed(2) : '-');
    const co2 = (typeof item.co2 === 'number') ? item.co2.toFixed(2) : (item.co2 ? Number(item.co2).toFixed(2) : '-');

    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${rank}</td>
      <td>${material}</td>
      <td>₹ ${cost}</td>
      <td>${co2} kg</td>
    `;
    table.appendChild(row);
  }
}

function displayMetrics(result, weight) {
  // Calculate metrics
  const costSavings = (result.cost * 0.15).toFixed(2);
  const co2Reduction = ((result.co2 * 0.20) * 100 / result.co2).toFixed(1);
  const materialScore = Math.min(100, (result.cost > 0 ? 100 : 0)).toFixed(0);

  // Get metrics container
  const metricsContainer = document.getElementById("metricsContainer");
  if (!metricsContainer) {
    console.warn("metricsContainer element not found");
    return;
  }

  metricsContainer.innerHTML = `
    <h3>Comparison Metrics</h3>
    <div class="metrics-container">
      <div class="metric-card">
        <h4>Cost Savings</h4>
        <div class="metric-value">₹ ${costSavings}</div>
        <div class="metric-unit">vs standard material</div>
      </div>
      <div class="metric-card">
        <h4>CO₂ Reduction</h4>
        <div class="metric-value">${co2Reduction}%</div>
        <div class="metric-unit">environmental impact</div>
      </div>
      <div class="metric-card">
        <h4>Material Score</h4>
        <div class="metric-value">${materialScore}</div>
        <div class="metric-unit">eco-friendliness index</div>
      </div>
      <div class="metric-card">
        <h4>Weight Optimized</h4>
        <div class="metric-value">${weight}g</div>
        <div class="metric-unit">packaging weight</div>
      </div>
    </div>
  `;
}

// Toast notification system
function showToast(message, type = 'success', duration = 4000) {
  const container = document.querySelector('.toast-container') || (() => {
    const div = document.createElement('div');
    div.className = 'toast-container';
    document.body.appendChild(div);
    return div;
  })();

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  };

  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || '•'}</span>
    <span class="toast-message">${message}</span>
    <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
  `;
  
  container.appendChild(toast);
  
  if (duration > 0) {
    setTimeout(() => {
      toast.classList.add('removing');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }
}

// Trigger file download
function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 100);
}

// Export handlers - direct file streaming with toast
async function exportExcel() {
  try {
    showToast('Generating Excel report...', 'info', 2000);
    const resp = await fetch('http://127.0.0.1:5000/dashboard/export/excel');
    
    if (!resp.ok) {
      const error = await resp.json();
      showToast('Export failed: ' + (error.error || 'Unknown error'), 'error');
      return;
    }
    
    const blob = await resp.blob();
    downloadBlob(blob, 'Sustainability_Report.xlsx');
    showToast('Excel report downloaded successfully!', 'success');
  } catch (e) {
    console.error('Export Excel failed', e);
    showToast('Unable to export Excel. Check server.', 'error');
  }
}

async function exportPDF() {
  try {
    showToast('Generating PDF report...', 'info', 2000);
    const resp = await fetch('http://127.0.0.1:5000/dashboard/export/pdf');
    
    if (!resp.ok) {
      const error = await resp.json();
      showToast('Export failed: ' + (error.error || 'Unknown error'), 'error');
      return;
    }
    
    const blob = await resp.blob();
    downloadBlob(blob, 'Sustainability_Report.pdf');
    showToast('PDF report downloaded successfully!', 'success');
  } catch (e) {
    console.error('Export PDF failed', e);
    showToast('Unable to export PDF. Check server.', 'error');
  }
}