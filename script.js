function scrollToRecommend() {
  document.getElementById("recommend").scrollIntoView({ behavior: "smooth" });
}

// Initialize charts on page load
document.addEventListener('DOMContentLoaded', function() {
  initializeCharts();
});

function initializeCharts() {
  // Material Distribution Chart (Pie)
  const materialCtx = document.getElementById('materialChart').getContext('2d');
  new Chart(materialCtx, {
    type: 'doughnut',
    data: {
      labels: ['Recycled Cardboard', 'Biodegradable Plastic', 'Paper', 'Glass', 'Others'],
      datasets: [{
        data: [35, 25, 20, 12, 8],
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
        legend: {
          labels: { color: '#d0e7d1' }
        }
      }
    }
  });

  // CO₂ vs Cost Savings Trend (Line)
  const trendsCtx = document.getElementById('trendsChart').getContext('2d');
  new Chart(trendsCtx, {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [
        {
          label: 'CO₂ Saved (kg)',
          data: [400, 600, 750, 900, 1100, 1400],
          borderColor: '#22c55e',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Cost Savings (₹000s)',
          data: [5, 8, 12, 15, 20, 28],
          borderColor: '#fbbf24',
          backgroundColor: 'rgba(251, 191, 36, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          labels: { color: '#d0e7d1' }
        }
      },
      scales: {
        y: {
          ticks: { color: '#d0e7d1' },
          grid: { color: 'rgba(208, 231, 209, 0.1)' }
        },
        x: {
          ticks: { color: '#d0e7d1' },
          grid: { color: 'rgba(208, 231, 209, 0.1)' }
        }
      }
    }
  });

  // Recyclability by Material (Bar)
  const recycleCtx = document.getElementById('recycleChart').getContext('2d');
  new Chart(recycleCtx, {
    type: 'bar',
    data: {
      labels: ['Cardboard', 'Plastic', 'Paper', 'Glass', 'Metal'],
      datasets: [{
        label: 'Recyclability (%)',
        data: [95, 78, 90, 100, 98],
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
      indexAxis: 'y',
      responsive: true,
      plugins: {
        legend: {
          labels: { color: '#d0e7d1' }
        }
      },
      scales: {
        x: {
          ticks: { color: '#d0e7d1' },
          grid: { color: 'rgba(208, 231, 209, 0.1)' }
        },
        y: {
          ticks: { color: '#d0e7d1' },
          grid: { display: false }
        }
      }
    }
  });

  // Monthly Impact Chart (Bar)
  const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
  new Chart(monthlyCtx, {
    type: 'bar',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [
        {
          label: 'Materials Upgraded',
          data: [12, 19, 25, 32, 38, 44],
          backgroundColor: '#22c55e'
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          labels: { color: '#d0e7d1' }
        }
      },
      scales: {
        y: {
          ticks: { color: '#d0e7d1' },
          grid: { color: 'rgba(208, 231, 209, 0.1)' }
        },
        x: {
          ticks: { color: '#d0e7d1' },
          grid: { color: 'rgba(208, 231, 209, 0.1)' }
        }
      }
    }
  });
}

async function getRecommendation() {
  try {
    const strength = document.getElementById("strength").value;
    const weight = document.getElementById("weight").value;
    const bio = document.getElementById("bio").value;
    const recycle = document.getElementById("recycle").value;

    if (!strength || !weight || bio === "" || recycle === "") {
      alert("Please fill all fields");
      return;
    }

    console.log("Sending data to backend...");

    const response = await fetch("http://127.0.0.1:5000/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
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

    document.getElementById("result").innerHTML = `
      <h3>AI Recommendation</h3>
      <p><strong>Material:</strong> ${data.material}</p>
      <p><strong>Estimated Cost:</strong> ₹ ${data.cost}</p>
      <p><strong>CO₂ Impact:</strong> ${data.co2} kg</p>
    `;
  } catch (error) {
    console.error(error);
    alert("Unable to fetch recommendation. Check backend.");
  }
}










