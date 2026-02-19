function scrollToRecommend() {
  document.getElementById("recommend").scrollIntoView({ behavior: "smooth" });
}

document.addEventListener('DOMContentLoaded', function() {
  initializeCharts();
  setupContinuousInputs();
});

function setupContinuousInputs() {
  const strength = document.getElementById('strength');
  const strengthVal = document.getElementById('strengthVal');
  if (strength && strengthVal) {
    strengthVal.textContent = String(Math.round(Number(strength.value)));
    strength.addEventListener('input', () => { strengthVal.textContent = String(Math.round(Number(strength.value))); });
  }

  const bio = document.getElementById('bio');
  const bioVal = document.getElementById('bioVal');
  if (bio && bioVal) {
    bioVal.textContent = String(Math.round(Number(bio.value))) + '%';
    bio.addEventListener('input', () => { bioVal.textContent = String(Math.round(Number(bio.value))) + '%'; });
  }

  const recycle = document.getElementById('recycle');
  const recycleVal = document.getElementById('recycleVal');
  if (recycle && recycleVal) {
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

const _charts = {
  material: null,
  trends: null,
  recycle: null,
  monthly: null
};

function initializeCharts(rankingData = null, mainResult = null) {
  // ── Material Distribution ───────────────────────────────────────────────────
  const materialCtx = document.getElementById('materialChart')?.getContext('2d');
  if (materialCtx) {
    try { if (_charts.material) _charts.material.destroy(); } catch (e) {}
    let labels = ['Recycled Cardboard', 'Biodegradable Plastic', 'Paper', 'Glass', 'Others'];
    let data   = [35, 25, 20, 12, 8];

    if (rankingData && rankingData.length >= 5) {
      labels = rankingData.slice(0, 5).map(m => m.material.substring(0, 15));
      data   = rankingData.slice(0, 5).map(m => m.cost);
    }

    _charts.material = new Chart(materialCtx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: ['#22c55e','#84cc16','#65a30d','#4ade80','#bbf7d0']
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

  // ── CO₂ vs Cost Trend ──────────────────────────────────────────────────────
  const trendsCtx = document.getElementById('trendsChart')?.getContext('2d');
  if (trendsCtx) {
    let labels  = ['Jan','Feb','Mar','Apr','May','Jun'];
    let co2Data = [400, 600, 750, 900, 1100, 1400];
    let costData = [5, 8, 12, 15, 20, 28];

    if (rankingData && rankingData.length >= 6) {
      labels   = rankingData.slice(0, 6).map((m, i) => `Rank ${i + 1}`);
      co2Data  = rankingData.slice(0, 6).map(m => parseFloat(m.co2) * 100);
      costData = rankingData.slice(0, 6).map(m => m.cost);
    }

    try { if (_charts.trends) _charts.trends.destroy(); } catch (e) {}
    _charts.trends = new Chart(trendsCtx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'CO₂ Emissions (kg x100)',
            data: co2Data,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239,68,68,0.1)',
            tension: 0.4,
            fill: true
          },
          {
            label: 'Material Cost (₹)',          // ✅ FIX: ₹ instead of $
            data: costData,
            borderColor: '#fbbf24',
            backgroundColor: 'rgba(251,191,36,0.1)',
            tension: 0.4,
            fill: true
          }
        ]
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#d0e7d1' } } },
        scales: {
          y: { ticks: { color: '#d0e7d1' }, grid: { color: 'rgba(208,231,209,0.1)' } },
          x: { ticks: { color: '#d0e7d1' }, grid: { color: 'rgba(208,231,209,0.1)' } }
        }
      }
    });
  }

  // ── Recyclability by Material ───────────────────────────────────────────────
  const recycleCtx = document.getElementById('recycleChart')?.getContext('2d');
  if (recycleCtx) {
    let labels = ['Cardboard','Plastic','Paper','Glass','Metal'];
    let data   = [95, 78, 90, 100, 98];

    if (rankingData && rankingData.length >= 5) {
      labels = rankingData.slice(0, 5).map(m => m.material.substring(0, 15));

      // Use CO₂ values inverted, then min-max normalize to 40–100 range
      // so bars are always clearly visible even when values are close together
      const co2Values = rankingData.slice(0, 5).map(m => parseFloat(m.co2));
      const minCo2    = Math.min(...co2Values);
      const maxCo2    = Math.max(...co2Values);
      const range     = maxCo2 - minCo2 || 1; // avoid divide-by-zero

      // Lower CO₂ → higher eco-friendliness score, spread across 40–100%
      data = co2Values.map(v => {
        const normalized = (maxCo2 - v) / range; // 0 (worst) to 1 (best)
        return parseFloat((40 + normalized * 60).toFixed(1)); // map to 40–100
      });
    }

    try { if (_charts.recycle) _charts.recycle.destroy(); } catch (e) {}
    _charts.recycle = new Chart(recycleCtx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Eco-Friendliness Score (lower CO₂ = higher)',
          data,
          backgroundColor: ['#22c55e','#84cc16','#65a30d','#4ade80','#bbf7d0']
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        plugins: { legend: { labels: { color: '#d0e7d1' } } },
        scales: {
          x: {
            ticks: { color: '#d0e7d1', callback: v => v + '%' },
            grid: { color: 'rgba(208,231,209,0.1)' },
            max: 100
          },
          y: { ticks: { color: '#d0e7d1' }, grid: { display: false } }
        }
      }
    });
  }

  // ── Monthly Impact ─────────────────────────────────────────────────────────
  const monthlyCtx = document.getElementById('monthlyChart')?.getContext('2d');
  if (monthlyCtx) {
    let labels = ['Jan','Feb','Mar','Apr','May','Jun'];
    let data   = [12, 19, 25, 32, 38, 44];

    if (rankingData && rankingData.length >= 6) {
      labels = rankingData.slice(0, 6).map((m, i) => `#${i + 1}`);
      data   = rankingData.slice(0, 6).map(m => m.cost);
    }

    try { if (_charts.monthly) _charts.monthly.destroy(); } catch (e) {}
    _charts.monthly = new Chart(monthlyCtx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Cost (₹)',                      // ✅ FIX: ₹ instead of $
          data,
          backgroundColor: '#22c55e'
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#d0e7d1' } } },
        scales: {
          y: {
            ticks: {
              color: '#d0e7d1',
              callback: v => '₹' + v                // ✅ FIX: ₹ prefix on axis
            },
            grid: { color: 'rgba(208,231,209,0.1)' }
          },
          x: { ticks: { color: '#d0e7d1' }, grid: { color: 'rgba(208,231,209,0.1)' } }
        }
      }
    });
  }
}

async function getRecommendation() {
  try {
    const category = document.getElementById("category").value;
    const strength = document.getElementById("strength").value;
    const weight   = document.getElementById("weight").value;
    const bio      = document.getElementById("bio").value;
    const recycle  = document.getElementById("recycle").value;

    if (!category || !strength || !weight || bio === "" || recycle === "") {
      alert("Please fill all fields");
      return;
    }

    const response = await fetch("http://127.0.0.1:5000/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        category, strength: Number(strength), weight: Number(weight),
        bio: Number(bio), recycle: Number(recycle)
      })
    });

    if (!response.ok) throw new Error("Backend error");

    const data = await response.json();

    document.getElementById("mainRecommendation").innerHTML = `
      <p><strong>Material:</strong> ${data.material}</p>
      <p><strong>Estimated Cost:</strong> ₹ ${data.cost.toFixed(2)}</p>
      <p><strong>CO₂ Impact:</strong> ${data.co2.toFixed(2)} kg</p>
    `;

    generateAndDisplayRanking(data, category, weight, strength, bio, recycle);
    displayMetrics(data, Number(weight));

    try {
      const envResp = await fetch('http://127.0.0.1:5000/environment-score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strength: Number(strength), weight: Number(weight), bio: Number(bio), recycle: Number(recycle) })
      });
      if (envResp.ok) {
        const envData = await envResp.json();
        const envMetricsDiv = document.getElementById('envMetrics');
        if (envMetricsDiv) {
          envMetricsDiv.innerHTML = `
            <div class="env-score">
              <p><strong>Predicted CO₂:</strong> ${envData.predicted_co2} kg</p>
              <p><strong>Baseline CO₂:</strong> ${envData.baseline_co2} kg</p>
              <p><strong>Reduction:</strong> ${envData.reduction_percent}%</p>
            </div>`;
        }
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
  async function tryFetch(host) {
    return await fetch(`${host}/ranked-materials/${encodeURIComponent(category)}`, {
      method: 'POST', mode: 'cors',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ strength: Number(strength), weight: Number(weight), bio: Number(bio), recycle: Number(recycle) })
    });
  }

  let rankResp = null;
  try {
    rankResp = await tryFetch('http://127.0.0.1:5000');
  } catch (err1) {
    try { rankResp = await tryFetch('http://localhost:5000'); } catch (err2) { throw err2; }
  }

  if (rankResp && rankResp.ok) {
    const rankData  = await rankResp.json();
    const materials = rankData.materials || [];
    renderRankingTable(materials);
    initializeCharts(materials, mainResult);
  } else {
    const fallback = [{ rank:1, material: mainResult.material, cost: mainResult.cost, co2: mainResult.co2, eco_score: 50 }];
    renderRankingTable(fallback);
    initializeCharts(fallback, mainResult);
  }
}

function renderRankingTable(rankings) {
  const table = document.getElementById("rankingTable");
  if (!table) return;
  table.innerHTML = "";

  if (!rankings || !Array.isArray(rankings) || rankings.length === 0) {
    table.innerHTML = `<tr><td>-</td><td>No ranked materials available</td><td>-</td><td>-</td></tr>`;
    return;
  }

  const maxToShow = Math.min(rankings.length, 3);
  for (let i = 0; i < maxToShow; i++) {
    const item     = rankings[i];
    const rank     = item.rank || (i + 1);
    const material = item.material || 'Unknown';
    const cost     = typeof item.cost === 'number' ? item.cost.toFixed(2) : (item.cost ? Number(item.cost).toFixed(2) : '-');
    const co2      = typeof item.co2  === 'number' ? item.co2.toFixed(2)  : (item.co2  ? Number(item.co2).toFixed(2)  : '-');
    const row      = document.createElement("tr");
    row.innerHTML  = `<td>${rank}</td><td>${material}</td><td>₹ ${cost}</td><td>${co2} kg</td>`;
    table.appendChild(row);
  }
}

function displayMetrics(result, weight) {
  const costSavings    = (result.cost * 0.15).toFixed(2);
  const co2Reduction   = ((result.co2 * 0.20) * 100 / result.co2).toFixed(1);
  const materialScore  = Math.min(100, result.cost > 0 ? 100 : 0).toFixed(0);
  const metricsContainer = document.getElementById("metricsContainer");
  if (!metricsContainer) return;

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
    </div>`;
}

// ── Toast ──────────────────────────────────────────────────────────────────────
function showToast(message, type = 'success', duration = 4000) {
  const container = document.querySelector('.toast-container') || (() => {
    const div = document.createElement('div');
    div.className = 'toast-container';
    document.body.appendChild(div);
    return div;
  })();

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  const icons = { success:'✓', error:'✕', warning:'⚠', info:'ℹ' };
  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || '•'}</span>
    <span class="toast-message">${message}</span>
    <button class="toast-close" onclick="this.parentElement.remove()">✕</button>`;
  container.appendChild(toast);

  if (duration > 0) {
    setTimeout(() => {
      toast.classList.add('removing');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }
}

function downloadBlob(blob, filename) {
  if (!blob || blob.size === 0) { showToast('Error: Downloaded file is empty.', 'error'); return; }
  const url = URL.createObjectURL(blob);
  const a   = document.createElement('a');
  a.style.display = 'none';
  a.href     = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(url); }, 5000);
}

async function exportExcel() {
  const btn = document.getElementById('exportExcelBtn');
  try {
    if (btn) btn.disabled = true;
    showToast('Generating Excel report...', 'info', 2000);
    const resp = await fetch('http://127.0.0.1:5000/dashboard/export/excel');
    if (!resp.ok) {
      const error = await resp.json().catch(() => ({ error: `Server error ${resp.status}` }));
      showToast('Export failed: ' + (error.error || 'Unknown error'), 'error');
      return;
    }
    const blob = await resp.blob();
    if (blob.size === 0) { showToast('Export failed: Server returned an empty file.', 'error'); return; }
    downloadBlob(new Blob([blob], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }), 'Sustainability_Report.xlsx');
    showToast('Excel report downloaded successfully!', 'success');
  } catch (e) {
    showToast('Unable to export Excel. Check server connection.', 'error');
  } finally {
    setTimeout(() => { if (btn) btn.disabled = false; }, 3000);
  }
}

async function exportPDF() {
  const btn = document.getElementById('exportPdfBtn');
  try {
    if (btn) btn.disabled = true;
    showToast('Generating PDF report...', 'info', 2000);
    const resp = await fetch('http://127.0.0.1:5000/dashboard/export/pdf');
    if (!resp.ok) {
      const error = await resp.json().catch(() => ({ error: `Server error ${resp.status}` }));
      showToast('Export failed: ' + (error.error || 'Unknown error'), 'error');
      return;
    }
    const blob = await resp.blob();
    if (blob.size === 0) { showToast('Export failed: Server returned an empty file.', 'error'); return; }
    downloadBlob(new Blob([blob], { type: 'application/pdf' }), 'Sustainability_Report.pdf');
    showToast('PDF report downloaded successfully!', 'success');
  } catch (e) {
    showToast('Unable to export PDF. Check server connection.', 'error');
  } finally {
    setTimeout(() => { if (btn) btn.disabled = false; }, 3000);
  }
}