/* ===========================
   EcoPackAI Dashboard Logic
   =========================== */

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

// Load summary cards
function loadSummary() {
    fetch('/api/analytics/summary')
        .then(res => res.json())
        .then(data => {
            if (data.status !== 'success') throw new Error('Failed to load summary');
            
            const s = data.summary;
            
            document.getElementById('totalRecommendations').textContent = s.total_recommendations;
            document.getElementById('totalCO2Saved').textContent = s.total_co2_saved_kg.toFixed(2);
            document.getElementById('categoriesServed').textContent = s.categories_served;
            document.getElementById('avgEcoScore').textContent = s.avg_eco_score.toFixed(3);
        })
        .catch(err => {
            console.error('Summary error:', err);
            document.getElementById('totalRecommendations').textContent = 'Error';
        });
}

// Load materials bar chart
function loadMaterialsChart() {
    fetch('/api/analytics/materials?limit=10')
        .then(res => res.json())
        .then(data => {
            if (data.status !== 'success') throw new Error('Failed to load materials');
            
            const materials = data.materials;
            const labels = materials.map(m => m.material_name);
            const counts = materials.map(m => m.recommendation_count);
            const ecoScores = materials.map(m => m.avg_eco_score);
            
            const ctx = document.getElementById('materialsChart').getContext('2d');
            
            if (materialsChart) materialsChart.destroy();
            
            materialsChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Recommendation Count',
                        data: counts,
                        backgroundColor: '#4CAF50',
                        borderRadius: 6
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
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

// Load categories charts (pie + CO2 bar)
function loadCategoriesChart() {
    fetch('/api/analytics/categories')
        .then(res => res.json())
        .then(data => {
            if (data.status !== 'success') throw new Error('Failed to load categories');
            
            const categories = data.categories;
            const labels = categories.map(c => c.category_name);
            const counts = categories.map(c => c.recommendation_count);
            const co2Saved = categories.map(c => c.total_co2_saved);
            
            // Pie chart for recommendation distribution
            const ctxPie = document.getElementById('categoriesChart').getContext('2d');
            
            if (categoriesChart) categoriesChart.destroy();
            
            const colors = [
                '#2E8B57', '#3CB371', '#66CDAA', '#8FBC8F', '#98FB98',
                '#90EE90', '#00FA9A', '#00FF7F', '#7CFC00', '#32CD32',
                '#228B22', '#006400', '#556B2F'
            ];
            
            categoriesChart = new Chart(ctxPie, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: counts,
                        backgroundColor: colors.slice(0, labels.length),
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                boxWidth: 12,
                                padding: 10,
                                font: {
                                    size: 11
                                }
                            }
                        }
                    }
                }
            });
            
            // Bar chart for CO2 savings
            const ctxCO2 = document.getElementById('co2Chart').getContext('2d');
            
            if (co2Chart) co2Chart.destroy();
            
            co2Chart = new Chart(ctxCO2, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Total CO2 Saved (kg)',
                        data: co2Saved,
                        backgroundColor: co2Saved.map(v => v >= 0 ? '#4CAF50' : '#E57373'),
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'CO2 Saved (kg)'
                            }
                        }
                    }
                }
            });
        })
        .catch(err => {
            console.error('Categories chart error:', err);
        });
}

// Load recent activity table
function loadRecentActivity() {
    fetch('/api/analytics/recent?limit=10')
        .then(res => res.json())
        .then(data => {
            if (data.status !== 'success') throw new Error('Failed to load recent');
            
            const tbody = document.getElementById('activityTableBody');
            
            if (data.recommendations.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="loading-text">No recommendations yet</td></tr>';
                return;
            }
            
            let html = '';
            data.recommendations.forEach(rec => {
                const co2SavedClass = rec.co2_saved === null ? 'neutral' : 
                                      (rec.co2_saved > 0 ? 'positive' : 'negative');
                const co2SavedText = rec.co2_saved === null ? '-' : 
                                     (rec.co2_saved > 0 ? '+' : '') + rec.co2_saved.toFixed(4);
                
                html += `
                    <tr>
                        <td>${rec.timestamp || '-'}</td>
                        <td>${rec.category}</td>
                        <td>${rec.weight_kg} kg</td>
                        <td>${rec.material}</td>
                        <td>${(rec.suitability * 100).toFixed(1)}%</td>
                        <td>Rs.${rec.cost_inr.toFixed(2)}</td>
                        <td>${rec.co2_kg.toFixed(4)} kg</td>
                        <td class="${co2SavedClass}">${co2SavedText}</td>
                    </tr>
                `;
            });
            
            tbody.innerHTML = html;
        })
        .catch(err => {
            console.error('Recent activity error:', err);
            document.getElementById('activityTableBody').innerHTML = 
                '<tr><td colspan="8" class="loading-text">Failed to load data</td></tr>';
        });
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
            const headers = ['Timestamp', 'Category', 'Weight (kg)', 'Material', 'Suitability', 
                           'Cost (INR)', 'CO2 (kg)', 'CO2 Saved (kg)', 'Cost Saved (INR)'];
            
            let csv = headers.join(',') + '\n';
            
            data.recommendations.forEach(rec => {
                const row = [
                    rec.timestamp || '',
                    `"${rec.category}"`,
                    rec.weight_kg,
                    `"${rec.material}"`,
                    rec.suitability,
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
            a.download = `ecopackai_report_${new Date().toISOString().split('T')[0]}.csv`;
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