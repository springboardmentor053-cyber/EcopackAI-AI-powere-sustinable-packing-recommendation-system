/* =============================================
   EcoPackAI - Product-Grade Dashboard Logic
   ============================================= */

let materialsChart = null;
let categoriesChart = null;
let co2Chart = null;

// Load dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
});

// Main function to load all dashboard data
function loadDashboard() {
    loadSummary();
    loadMaterialsChart();
    loadCategoriesChart();
    loadRecentActivity();
}

// Load summary cards and hero metric
function loadSummary() {
    fetch('/api/analytics/summary')
        .then(res => res.json())
        .then(data => {
            if (data.status !== 'success') throw new Error('Failed to load summary');
            
            const s = data.summary;
            
            // Hero metric - Total CO2 Saved
            const co2Saved = s.total_co2_saved_kg;
            document.getElementById('heroCO2Saved').textContent = co2Saved.toFixed(2);
            
            // Trees equivalent (1 tree absorbs ~0.022 kg CO2 per day)
            const treesEquiv = Math.round(co2Saved / 0.022);
            document.getElementById('treesEquivalent').textContent = treesEquiv.toLocaleString();
            
            // KPI Cards
            document.getElementById('totalRecommendations').textContent = s.total_recommendations;
            
            // Cost saved - handle negative
            const costSaved = s.total_cost_saved_inr;
            const costTrend = document.getElementById('costTrend');
            if (costSaved >= 0) {
                document.getElementById('totalCostSaved').textContent = '+' + costSaved.toFixed(0);
                costTrend.textContent = 'Savings';
                costTrend.className = 'kpi-trend positive';
                document.getElementById('costBar').className = 'kpi-bar-fill green';
            } else {
                document.getElementById('totalCostSaved').textContent = costSaved.toFixed(0);
                costTrend.textContent = 'Premium';
                costTrend.className = 'kpi-trend negative';
                document.getElementById('costBar').className = 'kpi-bar-fill orange';
            }
            
            // Suitability score
            const suitability = (s.avg_suitability_score * 100).toFixed(1);
            document.getElementById('avgSuitability').textContent = suitability + '%';
            document.getElementById('suitabilityBar').style.width = suitability + '%';
            
            // Categories served
            document.getElementById('categoriesServed').textContent = s.categories_served;
            document.getElementById('categoriesBar').style.width = (s.categories_served / 13 * 100) + '%';
            
        })
        .catch(err => {
            console.error('Summary error:', err);
            document.getElementById('heroCO2Saved').textContent = 'Error';
        });
}

// Load materials horizontal bar chart
function loadMaterialsChart() {
    fetch('/api/analytics/materials?limit=6')
        .then(res => res.json())
        .then(data => {
            if (data.status !== 'success') throw new Error('Failed to load materials');
            
            const materials = data.materials;
            const labels = materials.map(m => truncateLabel(m.material_name, 25));
            const counts = materials.map(m => m.recommendation_count);
            
            const ctx = document.getElementById('materialsChart').getContext('2d');
            
            if (materialsChart) materialsChart.destroy();
            
            materialsChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Recommendations',
                        data: counts,
                        backgroundColor: createGradient(ctx, '#059669', '#34D399'),
                        borderRadius: 6,
                        borderSkipped: false
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: '#1F2937',
                            titleFont: { size: 13, weight: '600' },
                            bodyFont: { size: 12 },
                            padding: 12,
                            cornerRadius: 8
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            grid: {
                                color: '#F3F4F6'
                            },
                            ticks: {
                                stepSize: 1,
                                font: { size: 11 }
                            }
                        },
                        y: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                font: { size: 11 }
                            }
                        }
                    }
                }
            });
        })
        .catch(err => {
            console.error('Materials chart error:', err);
        });
}

// Load categories doughnut chart and CO2 bar chart
function loadCategoriesChart() {
    fetch('/api/analytics/categories')
        .then(res => res.json())
        .then(data => {
            if (data.status !== 'success') throw new Error('Failed to load categories');
            
            const categories = data.categories;
            const labels = categories.map(c => truncateLabel(c.category_name, 20));
            const counts = categories.map(c => c.recommendation_count);
            const co2Saved = categories.map(c => c.total_co2_saved);
            
            // Doughnut chart for category distribution
            const ctxPie = document.getElementById('categoriesChart').getContext('2d');
            
            if (categoriesChart) categoriesChart.destroy();
            
            const colors = [
                '#059669', '#10B981', '#34D399', '#6EE7B7', '#A7F3D0',
                '#3B82F6', '#60A5FA', '#93C5FD',
                '#8B5CF6', '#A78BFA',
                '#F59E0B', '#FBBF24', '#FCD34D'
            ];
            
            categoriesChart = new Chart(ctxPie, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: counts,
                        backgroundColor: colors.slice(0, labels.length),
                        borderWidth: 2,
                        borderColor: '#fff',
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '65%',
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                boxWidth: 10,
                                padding: 8,
                                font: { size: 10 },
                                usePointStyle: true,
                                pointStyle: 'circle'
                            }
                        },
                        tooltip: {
                            backgroundColor: '#1F2937',
                            titleFont: { size: 12, weight: '600' },
                            bodyFont: { size: 11 },
                            padding: 10,
                            cornerRadius: 6
                        }
                    }
                }
            });
            
            // CO2 Impact bar chart
            const ctxCO2 = document.getElementById('co2Chart').getContext('2d');
            
            if (co2Chart) co2Chart.destroy();
            
            co2Chart = new Chart(ctxCO2, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'CO₂ Saved (kg)',
                        data: co2Saved,
                        backgroundColor: co2Saved.map(v => v >= 0 ? '#059669' : '#EF4444'),
                        borderRadius: 4,
                        borderSkipped: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: '#1F2937',
                            callbacks: {
                                label: function(context) {
                                    const value = context.raw;
                                    return value >= 0 
                                        ? `Saved: ${value.toFixed(3)} kg CO₂`
                                        : `Increased: ${Math.abs(value).toFixed(3)} kg CO₂`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            grid: {
                                color: '#F3F4F6'
                            },
                            ticks: {
                                font: { size: 11 },
                                callback: function(value) {
                                    return value.toFixed(1);
                                }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                font: { size: 9 },
                                maxRotation: 45,
                                minRotation: 45
                            }
                        }
                    }
                }
            });
            
            // Update impact insights
            updateImpactInsights(categories);
        })
        .catch(err => {
            console.error('Categories chart error:', err);
        });
}

// Update impact insights section
function updateImpactInsights(categories) {
    const insights = document.getElementById('impactInsights');
    
    // Find best and worst performers
    const sorted = [...categories].sort((a, b) => b.total_co2_saved - a.total_co2_saved);
    const best = sorted[0];
    const worst = sorted[sorted.length - 1];
    const total = categories.reduce((sum, c) => sum + c.recommendation_count, 0);
    
    insights.innerHTML = `
        <div class="insight-box">
            <div class="insight-label">Highest Impact Category</div>
            <div class="insight-value positive">${truncateLabel(best.category_name, 20)}</div>
        </div>
        <div class="insight-box ${worst.total_co2_saved < 0 ? 'negative' : 'neutral'}">
            <div class="insight-label">Needs Attention</div>
            <div class="insight-value ${worst.total_co2_saved < 0 ? 'negative' : ''}">${truncateLabel(worst.category_name, 20)}</div>
        </div>
        <div class="insight-box neutral">
            <div class="insight-label">Total Categories Analyzed</div>
            <div class="insight-value">${categories.length} industries</div>
        </div>
    `;
}

// Load recent activity feed
function loadRecentActivity() {
    fetch('/api/analytics/recent?limit=8')
        .then(res => res.json())
        .then(data => {
            if (data.status !== 'success') throw new Error('Failed to load recent');
            
            const activityList = document.getElementById('activityList');
            
            if (data.recommendations.length === 0) {
                activityList.innerHTML = '<div class="loading-placeholder">No recommendations yet</div>';
                return;
            }
            
            let html = '';
            data.recommendations.forEach(rec => {
                const badgeClass = rec.co2_saved === null ? 'neutral' : 
                                   (rec.co2_saved > 0 ? 'positive' : 'negative');
                const badgeText = rec.co2_saved === null ? 'N/A' : 
                                  (rec.co2_saved > 0 ? '+' + rec.co2_saved.toFixed(2) + ' kg' : rec.co2_saved.toFixed(2) + ' kg');
                
                html += `
                    <div class="activity-item">
                        <div class="activity-icon">📦</div>
                        <div class="activity-content">
                            <div class="activity-title">${rec.material} → ${truncateLabel(rec.category, 25)}</div>
                            <div class="activity-meta">${rec.timestamp} · ${rec.weight_kg} kg · ${(rec.suitability * 100).toFixed(0)}% match</div>
                        </div>
                        <div class="activity-badge ${badgeClass}">${badgeText}</div>
                    </div>
                `;
            });
            
            activityList.innerHTML = html;
            
            // Update insights
            updateQuickInsights(data.recommendations);
        })
        .catch(err => {
            console.error('Recent activity error:', err);
            document.getElementById('activityList').innerHTML = 
                '<div class="loading-placeholder">Failed to load activity</div>';
        });
}

// Update performance metrics panel
function updateQuickInsights(recommendations) {
    const insightsList = document.getElementById('insightsList');
    
    // Calculate metrics
    const totalRecs = recommendations.length;
    const withSavings = recommendations.filter(r => r.co2_saved && r.co2_saved > 0).length;
    const savingsRate = totalRecs > 0 ? ((withSavings / totalRecs) * 100).toFixed(0) : 0;
    
    // Most recommended material
    const materials = {};
    recommendations.forEach(r => {
        materials[r.material] = (materials[r.material] || 0) + 1;
    });
    const sortedMaterials = Object.entries(materials).sort((a, b) => b[1] - a[1]);
    const topMaterial = sortedMaterials[0];
    
    // Average suitability
    const avgSuitability = recommendations.length > 0 
        ? (recommendations.reduce((sum, r) => sum + r.suitability, 0) / recommendations.length * 100).toFixed(0)
        : 0;
    
    // Total CO2 from recent
    const totalCO2Recent = recommendations.reduce((sum, r) => sum + (r.co2_saved || 0), 0).toFixed(2);
    
    // Categories coverage
    const uniqueCategories = new Set(recommendations.map(r => r.category)).size;
    
    insightsList.innerHTML = `
        <div class="metric-item">
            <div class="metric-row">
                <span class="metric-label">CO₂ Positive Rate</span>
                <span class="metric-value ${savingsRate >= 50 ? 'positive' : 'negative'}">${savingsRate}%</span>
            </div>
            <div class="metric-bar">
                <div class="metric-bar-fill ${savingsRate >= 50 ? 'green' : 'red'}" style="width: ${savingsRate}%"></div>
            </div>
        </div>
        <div class="metric-item">
            <div class="metric-row">
                <span class="metric-label">Top Material</span>
                <span class="metric-value small">${topMaterial ? topMaterial[0].split(' ')[0] : 'N/A'}</span>
            </div>
            <div class="metric-subtext">${topMaterial ? topMaterial[1] + ' recommendations' : ''}</div>
        </div>
        <div class="metric-item">
            <div class="metric-row">
                <span class="metric-label">Avg Match Score</span>
                <span class="metric-value">${avgSuitability}%</span>
            </div>
            <div class="metric-bar">
                <div class="metric-bar-fill purple" style="width: ${avgSuitability}%"></div>
            </div>
        </div>
        <div class="metric-item">
            <div class="metric-row">
                <span class="metric-label">Recent CO₂ Impact</span>
                <span class="metric-value ${parseFloat(totalCO2Recent) >= 0 ? 'positive' : 'negative'}">${totalCO2Recent} kg</span>
            </div>
        </div>
    `;
}

// Helper: Create gradient for charts
function createGradient(ctx, color1, color2) {
    const gradient = ctx.createLinearGradient(0, 0, 400, 0);
    gradient.addColorStop(0, color1);
    gradient.addColorStop(1, color2);
    return gradient;
}

// Helper: Truncate long labels
function truncateLabel(label, maxLength) {
    if (label.length <= maxLength) return label;
    return label.substring(0, maxLength - 3) + '...';
}

// Export to CSV
function exportToCSV() {
    fetch('/api/analytics/recent?limit=100')
        .then(res => res.json())
        .then(data => {
            if (data.status !== 'success' || data.recommendations.length === 0) {
                alert('No data to export');
                return;
            }
            
            // Build CSV content
            const headers = ['Timestamp', 'Category', 'Weight (kg)', 'Material', 'Suitability %', 
                           'Cost (INR)', 'CO2 (kg)', 'CO2 Saved (kg)', 'Cost Saved (INR)'];
            
            let csv = headers.join(',') + '\n';
            
            data.recommendations.forEach(rec => {
                const row = [
                    rec.timestamp || '',
                    `"${rec.category}"`,
                    rec.weight_kg,
                    `"${rec.material}"`,
                    (rec.suitability * 100).toFixed(1),
                    rec.cost_inr,
                    rec.co2_kg,
                    rec.co2_saved || '',
                    rec.cost_saved || ''
                ];
                csv += row.join(',') + '\n';
            });
            
            // Download file
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `ecopackai_sustainability_report_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        })
        .catch(err => {
            console.error('Export error:', err);
            alert('Failed to export data');
        });
}