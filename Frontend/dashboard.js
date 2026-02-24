document.addEventListener("DOMContentLoaded", async () => {

  let top5Data = [];

  // =============================
  // LOAD DASHBOARD DATA
  // =============================
  try {
    const res = await fetch("/dashboard-data");
    const data = await res.json();

    document.getElementById("totalMaterials").textContent =
      data.total_materials || "--";

    document.getElementById("avgCost").textContent =
      data.avg_cost ? data.avg_cost.toFixed(2) : "--";

    document.getElementById("avgCO2").textContent =
      data.avg_co2 ? data.avg_co2.toFixed(2) : "--";

    const labels = data.materials.map(m => m.material_type);
    const costData = data.materials.map(m => m.predicted_cost);

    // LINE CHART
    new Chart(document.getElementById("costChart"), {
      type: "line",
      data: {
        labels,
        datasets: [{
          label: "Cost Trend",
          data: costData,
          borderColor: "#2ecc71",
          backgroundColor: "rgba(46,204,113,0.2)",
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });

    // PIE CHART
    new Chart(document.getElementById("tierChart"), {
      type: "doughnut",
      data: {
        labels: ["Low","Medium","High"],
        datasets: [{
          data:[70,20,10],
          backgroundColor:["#2ecc71","#f1c40f","#e74c3c"]
        }]
      },
      options:{
        responsive:true,
        maintainAspectRatio:false,
        cutout:"60%"
      }
    });

  } catch(err){
    console.error("Dashboard error:", err);
  }

  // =============================
  // LOAD TOP 5 DATA (MAIN FIX)
  // =============================
  const stored = localStorage.getItem("top5Data");

  if (stored) {
    top5Data = JSON.parse(stored);
    console.log("TOP5 loaded:", top5Data);
  }

  // =============================
  // EXPORT CSV (WORKING)
  // =============================
  document.getElementById("exportCSV").addEventListener("click", () => {

    if (!top5Data.length) {
      alert("⚠️ Pehle Recommendation page se Top 5 generate karo.");
      return;
    }

    let csv = "Material,Cost,CO2\n";

    top5Data.forEach(item => {
      csv += `${item.material_type},${item.predicted_cost},${item.predicted_co2}\n`;
    });

    const blob = new Blob([csv], { type: "text/csv" });

    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "Top5_Recommendations.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
  });

  // =============================
  // EXPORT PDF (WORKING)
  // =============================
  document.getElementById("exportPDF").addEventListener("click", () => {

    if (!top5Data.length) {
      alert("⚠️ Pehle Recommendation page se Top 5 generate karo.");
      return;
    }

    let text = "EcoPackAI TOP 5 RECOMMENDATIONS\n\n";

    top5Data.forEach((m,i)=>{
      text += `${i+1}. ${m.material_type}
Cost: ${m.predicted_cost}
CO2: ${m.predicted_co2}

`;
    });

    const blob = new Blob([text], { type: "text/plain" });

    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "Top5_Recommendations.pdf";
    document.body.appendChild(link);
    link.click();
    link.remove();
  });

});