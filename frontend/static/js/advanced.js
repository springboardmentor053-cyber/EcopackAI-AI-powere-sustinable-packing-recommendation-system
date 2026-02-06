// =======================
// CONFIG
// =======================
const API_BASE = "";
const API_KEY  = "dev-key-123";
const STORAGE_KEY = "ecoPackAI_product";

// ---------- helpers ----------
const $ = (id) => document.getElementById(id);

function getMaterialVisual(name=""){
  const s = (name || "").toLowerCase();

  if (s.includes("mushroom") || s.includes("mycel")) return { emoji:"🍄", label:"Mycelium Packaging" };
  if (s.includes("seaweed")) return { emoji:"🌿", label:"Seaweed Film" };
  if (s.includes("algae")) return { emoji:"🌊", label:"Algae-Based" };
  if (s.includes("bamboo")) return { emoji:"🎋", label:"Bamboo Fiber" };
  if (s.includes("banana")) return { emoji:"🍌", label:"Banana Fiber" };
  if (s.includes("hemp")) return { emoji:"🌱", label:"Hemp Fiber" };
  if (s.includes("jute")) return { emoji:"🧵", label:"Jute Fiber" };
  if (s.includes("kenaf")) return { emoji:"🌾", label:"Kenaf Fiber" };
  if (s.includes("rice husk")) return { emoji:"🌾", label:"Rice Husk Fiber" };
  if (s.includes("wheat straw")) return { emoji:"🌾", label:"Wheat Straw Fiber" };
  if (s.includes("sugarcane") || s.includes("bagasse")) return { emoji:"🍃", label:"Bagasse / Sugarcane Fiber" };
  if (s.includes("areca")) return { emoji:"🍂", label:"Areca Leaf" };
  if (s.includes("palm leaf") || (s.includes("palm") && s.includes("leaf"))) return { emoji:"🍃", label:"Palm Leaf" };
  if (s.includes("coconut") || s.includes("coir")) return { emoji:"🥥", label:"Coconut Coir Fiber" };
  if (s.includes("corn husk")) return { emoji:"🌽", label:"Corn Husk Fiber" };
  if (s.includes("cotton")) return { emoji:"🧶", label:"Cotton Wrap" };
  if (s.includes("wood wool") || s.includes("wood")) return { emoji:"🪵", label:"Wood-Based" };
  // --- Paper / board family ---
  if (s.includes("paper") || s.includes("cardboard") || s.includes("corrugated") || s.includes("linerboard") ||
      s.includes("boxboard") || s.includes("chipboard") || s.includes("sbs") || s.includes("sub") ||
      s.includes("glassine") || s.includes("greaseproof") || s.includes("grease-resistant") ||
      s.includes("sterile paper") || s.includes("paper pouches") || s.includes("paper seals") ||
      s.includes("mailer") || s.includes("mailers") || s.includes("envelopes") || s.includes("tray") || s.includes("trays")) {
    return { emoji:"📦", label:"Paper / Board" };
  }
  // --- Molded pulp / fiber trays / clamshells ---
  if (s.includes("pulp") || s.includes("molded fiber") || s.includes("molded")) return { emoji:"🧩", label:"Molded Fiber / Pulp" };

  // --- Bioplastics (PLA / PHA / PBS / Bio-PET / cellulose etc.) ---
  if (s.includes("pla") || s.includes("pha") || s.includes("pbs") || s.includes("bio-pet") || s.includes("bioplastic") ||
      s.includes("starch-based") || s.includes("cellulose") || s.includes("chitosan") || s.includes("bio-resin") ||
      s.includes("paper-laminated bioplastic") || s.includes("bio-based")) {
    return { emoji:"🌱", label:"Bioplastic / Bio-Polymer" };
  }

  // --- Films (plastic + barrier + multilayer) ---
  if (s.includes("film") || s.includes("wrap") || s.includes("shrink") || s.includes("stretch") || s.includes("evoh") ||
      s.includes("pvdc") || s.includes("blown") || s.includes("multilayer") || s.includes("modified atmosphere") ||
      s.includes("barrier film") || s.includes("barrier-coated")) {
    return { emoji:"🎞️", label:"Flexible Film" };
  }
  // --- Foams / cushioning ---
  if (s.includes("foam") || s.includes("eps") || s.includes("epp") || s.includes("paper bubble") || s.includes("air pillows") ||
      s.includes("inflatable") || s.includes("eps alternative")) {
    return { emoji:"🫧", label:"Cushioning / Foam" };
  }

  // --- Glass ---
  if (s.includes("glass") || s.includes("borosilicate") || s.includes("soda-lime") || s.includes("tempered") || s.includes("amber") || s.includes("flint")) {
    return { emoji:"🧪", label:"Glass" };
  }

  // --- Aluminum ---
  if (s.includes("aluminum") || s.includes("aluminium") || s.includes("foil") || s.includes("can")) {
    return { emoji:"🥫", label:"Aluminum" };
  }

  // --- Metals (steel / tinplate / brass / copper / closures) ---
  if (s.includes("steel") || s.includes("tinplate") || s.includes("brass") || s.includes("copper") || s.includes("metal")) {
    return { emoji:"🔩", label:"Metal" };
  }
  // --- Plastics (PET/PP/PE/PVC/ABS/PC/PA etc.) ---
  if (s.includes("plastic") || s.includes("pet") || s.includes("pp") || s.includes("pe") || s.includes("pvc") || s.includes("ps") ||
      s.includes("abs") || s.includes("polycarbonate") || s.includes("nylon") || s.includes("acetal") || s.includes("pom") ||
      s.includes("recycled hdpe") || s.includes("recycled ldpe") || s.includes("recycled pp") || s.includes("rpet") ||
      s.includes("hdpe") || s.includes("ldpe") || s.includes("thermoformed")) {
    return { emoji:"♻️", label:"Polymer / Plastic" };
  }

  // --- Specialty / thermal / cold-chain ---
  if (s.includes("cold pack") || s.includes("gel-based") || s.includes("thermal") || s.includes("insulated") || s.includes("vacuum insulated")) {
    return { emoji:"❄️", label:"Thermal / Cold-Chain" };
  }

  // --- Medical packaging ---
  if (s.includes("tyvek") || s.includes("medical")) return { emoji:"🩺", label:"Medical Packaging" };

  // Fallback (covers anything new)
  return { emoji:"📦", label:"Packaging Material" };

}

function safeNum(x, d=2){
  const n = Number(x);
  return Number.isFinite(n) ? n.toFixed(d) : "—";
}

function show(el){ if(el) el.style.display = ""; }
function hide(el){ if(el) el.style.display = "none"; }
function setText(el, txt){ if(el) el.textContent = txt; }

function downloadBlob(filename, content, type="text/plain"){
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename;
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
}

function toCsv(rows){
  if(!rows || !rows.length) return "";
  const headers = Object.keys(rows[0]);
  const esc = (v) => `"${String(v ?? "").replaceAll('"','""')}"`;
  const lines = [
    headers.join(","),
    ...rows.map(r => headers.map(h => esc(r[h])).join(","))
  ];
  return lines.join("\n");
}

function wrapLabel(label, maxCharsPerLine=22){
  const s = String(label || "");
  if (s.length <= maxCharsPerLine) return s;

  const words = s.split(" ");
  const lines = [];
  let line = "";

  for (const w of words){
    const test = (line ? line + " " : "") + w;
    if (test.length > maxCharsPerLine){
      if (line) lines.push(line);
      line = w;
    } else {
      line = test;
    }
  }
  if (line) lines.push(line);
  if (!lines.length) return s.slice(0, maxCharsPerLine) + "…";
  return lines;
}

// =======================
// Wizard page logic
// =======================
const wizardForm = $("wizardForm");
if (wizardForm){
  const cost = $("priority_cost"), eco = $("priority_eco"), dur = $("priority_dur");
  const wCost = $("wCost"), wEco = $("wEco"), wDur = $("wDur");
  const liveSummary = $("liveSummary");

  const refresh = () => {
    if(cost && wCost) wCost.textContent = cost.value;
    if(eco && wEco) wEco.textContent = eco.value;
    if(dur && wDur) wDur.textContent = dur.value;

    const pn = $("product_name")?.value?.trim() || "—";
    const wt = $("product_weight_kg")?.value || "—";
    const fr = $("fragility_level")?.value || "—";
    const ts = $("temperature_sensitive")?.value || "—";

    if(liveSummary){
      liveSummary.innerHTML = `
        <div><span class="small-muted">Product:</span> <b>${pn}</b></div>
        <div><span class="small-muted">Weight:</span> <b>${wt}</b></div>
        <div><span class="small-muted">Fragility:</span> <b>${fr}</b></div>
        <div><span class="small-muted">Temp Sensitive:</span> <b>${ts}</b></div>
        <div class="mt-2 small-muted">Priorities → Cost ${cost.value}%, Eco ${eco.value}%, Durability ${dur.value}%</div>
      `;
    }
  };

  ["input","change"].forEach(evt=>{
    cost?.addEventListener(evt, refresh);
    eco?.addEventListener(evt, refresh);
    dur?.addEventListener(evt, refresh);
    $("product_name")?.addEventListener(evt, refresh);
    $("product_weight_kg")?.addEventListener(evt, refresh);
    $("fragility_level")?.addEventListener(evt, refresh);
    $("temperature_sensitive")?.addEventListener(evt, refresh);
  });
  refresh();

  wizardForm.addEventListener("submit", (e)=>{
    e.preventDefault();

    const productData = {
      product_name: $("product_name").value.trim(),
      product_category: $("product_category").value.trim(),
      product_weight_kg: $("product_weight_kg").value,
      fragility_level: $("fragility_level").value,
      temperature_sensitive: $("temperature_sensitive").value,
      required_strength_score: $("required_strength_score").value,
      preferred_biodegradability_score: $("preferred_biodegradability_score").value,
      max_packaging_cost_inr: $("max_packaging_cost_inr").value,
      priorities: {
        cost: Number($("priority_cost").value),
        eco: Number($("priority_eco").value),
        dur: Number($("priority_dur").value),
      }
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(productData));
    window.location.href = "/results";
  });
}

// =======================
// Results dashboard logic
// =======================
const tbody = $("tbody");
if (tbody){
  const loadingBox = $("loadingBox");
  const errorBox = $("errorBox");

  const productSummary = $("productSummary");
  const kpiRow = $("kpiRow");
  const chartsRow = $("chartsRow");
  const resultsBlock = $("resultsBlock");

  const searchBox = $("searchBox");
  const modeSelect = $("modeSelect");
  const sortSelect = $("sortSelect");
  const countSelect = $("countSelect"); // ✅ NEW dropdown

  const btnApplyFilters = $("btnApplyFilters");
  const btnResetFilters = $("btnResetFilters");

  let chartCost, chartCo2, chartScatter;

  let productData = null;
  let recsOriginal = [];
  let recsCurrent = [];

  const showError = (msg) => {
    if(errorBox){
      errorBox.classList.remove("d-none");
      errorBox.innerHTML = `<div class="fw-semibold" style="color:#FF5C7A;">Error</div><div class="small-muted">${msg}</div>`;
    }
    hide(loadingBox);
  };

  const buildCards = (recs) => {
    const cardsArea = $("cardsArea");
    if(!cardsArea) return;
    cardsArea.innerHTML = "";

    recs.slice(0,3).forEach((r, idx)=>{
      const col = document.createElement("div");
      col.className = "col-lg-4";
      const img = getMaterialVisual(r.material_name);

      col.innerHTML = `
        <div class="card p-3 h-100 material-card">
          <div class="material-img mb-3">
            <div class="text-center">
              <div style="font-size:28px;">${img.emoji}</div>
              <div class="small-muted mt-1">${img.label}</div>
            </div>
          </div>

          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="small-muted">Recommendation #${idx+1}</div>
              <div class="fw-bold mt-1">${r.material_name}</div>
              <div class="small-muted mt-1">Eco Score: <b>${safeNum(r.environment_score,2)}</b></div>
            </div>
            <span class="badge badge-eco">${safeNum(r.recyclability_percent,0)}% Recyclable</span>
          </div>

          <div class="d-flex gap-2 flex-wrap mt-3">
            <span class="material-chip">Bio: ${safeNum(r.biodegradability_score,0)}/10</span>
            <span class="material-chip">CO₂: ${safeNum(r.pred_co2_kg,3)} kg</span>
            <span class="material-chip">₹${safeNum(r.pred_cost_inr,2)}</span>
          </div>

          <div class="small-muted mt-3">
            Why it’s high: strong eco score + good cost/CO₂ trade-off.
          </div>
        </div>
      `;
      cardsArea.appendChild(col);
    });
  };

  const buildTable = (recs) => {
    tbody.innerHTML = "";
    recs.forEach((r)=>{
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><input type="checkbox" class="form-check-input compareCheck" data-material="${r.material_name}"></td>
        <td class="fw-bold">${r.rank}</td>
        <td>${r.material_name}</td>
        <td>₹${safeNum(r.pred_cost_inr,2)}</td>
        <td>${safeNum(r.pred_co2_kg,3)}</td>
        <td>${safeNum(r.recyclability_percent,0)}%</td>
        <td>${safeNum(r.biodegradability_score,0)}/10</td>
        <td>${safeNum(r.suitability_score,4)}</td>
        <td><span class="badge badge-eco">${safeNum(r.environment_score,2)}</span></td>
      `;
      tbody.appendChild(tr);
    });
  };

  const renderCharts = (recs) => {
    const labels = recs.map(r => String(r.material_name || "—"));
    const cost = recs.map(r => Number(r.pred_cost_inr));
    const co2  = recs.map(r => Number(r.pred_co2_kg));

    // COST (horizontal bar)
    const elCost = $("chartCost");
    if (elCost && window.Chart){
      chartCost?.destroy();
      chartCost = new Chart(elCost, {
        type: "bar",
        data: { labels, datasets: [{ label: "Predicted Cost (INR)", data: cost }] },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: "y",
          scales: {
            x: { title: { display: true, text: "Cost (INR)" } },
            y: {
              ticks: {
                autoSkip: false,
                callback: function(value){
                  const lab = this.getLabelForValue(value);
                  return wrapLabel(lab, 22);
                }
              }
            }
          },
          plugins: { tooltip: { callbacks: { title: (items) => items?.[0]?.label || "" } } }
        }
      });
    }

    // CO2 (horizontal bar)
    const elCo2 = $("chartCo2");
    if (elCo2 && window.Chart){
      chartCo2?.destroy();
      chartCo2 = new Chart(elCo2, {
        type: "bar",
        data: { labels, datasets: [{ label: "Predicted CO₂ (kg)", data: co2 }] },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: "y",
          scales: {
            x: { title: { display: true, text: "CO₂ (kg)" } },
            y: {
              ticks: {
                autoSkip: false,
                callback: function(value){
                  const lab = this.getLabelForValue(value);
                  return wrapLabel(lab, 22);
                }
              }
            }
          },
          plugins: { tooltip: { callbacks: { title: (items) => items?.[0]?.label || "" } } }
        }
      });
    }

    // TRADEOFF (scatter)
    const elScatter = $("chartScatter");
    if (elScatter && window.Chart){
      chartScatter?.destroy();
      chartScatter = new Chart(elScatter, {
        type: "scatter",
        data: {
          datasets: [{
            label: "Materials",
            data: recs.map(r => ({
              x: Number(r.pred_cost_inr),
              y: Number(r.pred_co2_kg),
              material: String(r.material_name || "")
            })),
            pointRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { title: { display:true, text:"Cost (INR)" } },
            y: { title: { display:true, text:"CO₂ (kg)" } }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: (ctx) => {
                  const d = ctx.raw || {};
                  return `${d.material} • ₹${safeNum(d.x,2)} • CO₂ ${safeNum(d.y,3)} kg`;
                }
              }
            }
          }
        }
      });
    }
  };

  const applyWhatIfRerank = (recs, priorities) => {
    const maxCost = Math.max(...recs.map(r=>Number(r.pred_cost_inr)||0)) || 1;

    const wCost = (priorities?.cost ?? 50) / 100;
    const wEco  = (priorities?.eco  ?? 50) / 100;
    const wDur  = (priorities?.dur  ?? 50) / 100;

    return recs.map(r=>{
      const costScore = 1 - (Number(r.pred_cost_inr)/maxCost);
      const ecoScore  = (Number(r.environment_score)/100);
      const durScore  = Math.min(1, Number(r.suitability_score));

      const newScore = (wCost*costScore) + (wEco*ecoScore) + (wDur*durScore);
      return { ...r, whatif_score: newScore };
    }).sort((a,b)=>b.whatif_score - a.whatif_score)
      .map((r, i)=>({ ...r, rank: i+1 }));
  };

  const updateKpis = (recs) => {
    const top = recs[0];
    setText($("kpiBest"), top?.material_name || "—");
    setText($("kpiCost"), top ? `₹${safeNum(top.pred_cost_inr,2)}` : "—");
    setText($("kpiCo2"),  top ? `${safeNum(top.pred_co2_kg,3)}` : "—");
    setText($("kpiEco"),  top ? `${safeNum(top.environment_score,2)}` : "—");
  };

  const renderAll = (recs) => {
    recsCurrent = recs;
    updateKpis(recs);
    buildCards(recs);
    buildTable(recs);
    renderCharts(recs);
  };

  function applyFiltersAndRender(){
    const q = (searchBox?.value || "").toLowerCase().trim();
    const mode = modeSelect?.value || "balanced";
    const sort = sortSelect?.value || "rank";

    let filtered = [...recsOriginal];

    if(q){
      filtered = filtered.filter(r => (r.material_name || "").toLowerCase().includes(q));
    }

    if(mode === "eco"){
      filtered.sort((a,b)=> Number(b.environment_score) - Number(a.environment_score));
    } else if(mode === "cheap"){
      filtered.sort((a,b)=> Number(a.pred_cost_inr) - Number(b.pred_cost_inr));
    } else if(mode === "lowco2"){
      filtered.sort((a,b)=> Number(a.pred_co2_kg) - Number(b.pred_co2_kg));
    } else {
      filtered.sort((a,b)=> Number(a.rank) - Number(b.rank));
    }

    filtered = filtered.map((r, i)=> ({...r, rank: i+1}));

    if(sort === "env")  filtered.sort((a,b)=> Number(b.environment_score) - Number(a.environment_score));
    if(sort === "cost") filtered.sort((a,b)=> Number(a.pred_cost_inr) - Number(b.pred_cost_inr));
    if(sort === "co2")  filtered.sort((a,b)=> Number(a.pred_co2_kg) - Number(b.pred_co2_kg));

    filtered = filtered.map((r, i)=> ({...r, rank: i+1}));

    // ✅ NEW: show N recommendations (max 20)
    const nWanted = Math.max(1, Math.min(Number(countSelect?.value || 10), filtered.length));
    filtered = filtered.slice(0, nWanted).map((r, i)=> ({...r, rank: i+1}));

    renderAll(filtered);
  }

  function exportCsv(){
    const csv = toCsv(recsCurrent.map(r=>({
      rank: r.rank,
      material: r.material_name,
      pred_cost_inr: safeNum(r.pred_cost_inr,2),
      pred_co2_kg: safeNum(r.pred_co2_kg,3),
      recyclability_percent: safeNum(r.recyclability_percent,0),
      biodegradability_score: safeNum(r.biodegradability_score,0),
      suitability_score: safeNum(r.suitability_score,4),
      environment_score: safeNum(r.environment_score,2),
    })));
    downloadBlob("ecopackai_recommendations.csv", csv, "text/csv");
  }

  function exportPdf(){
    try{
      const { jsPDF } = window.jspdf;
      const doc = new jsPDF();

      doc.setFontSize(16);
      doc.text("EcoPackAI Recommendation Report", 14, 18);

      doc.setFontSize(10);
      doc.text(`Product: ${productData?.product_name || "—"}`, 14, 26);
      doc.text(`Category: ${productData?.product_category || "—"}`, 14, 32);
      doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 38);

      const rows = recsCurrent.map(r => ([
        String(r.rank),
        r.material_name,
        `₹${safeNum(r.pred_cost_inr,2)}`,
        `${safeNum(r.pred_co2_kg,3)}`,
        `${safeNum(r.recyclability_percent,0)}%`,
        `${safeNum(r.biodegradability_score,0)}/10`,
        `${safeNum(r.environment_score,2)}`
      ]));

      doc.autoTable({
        startY: 46,
        head: [["Rank","Material","Pred Cost","Pred CO₂","Recyclability","Bio","Eco Score"]],
        body: rows,
        styles: { fontSize: 9 },
        headStyles: { fillColor: [15, 60, 35] }
      });

      doc.save("EcoPackAI_Recommendation_Report.pdf");
    }catch(err){
      console.error(err);
      alert("PDF export failed. Make sure jsPDF scripts are loaded.");
    }
  }

  function compareSelected(){
    const checks = Array.from(document.querySelectorAll(".compareCheck:checked"));
    const names = checks.map(c => c.getAttribute("data-material"));
    const selected = recsCurrent.filter(r => names.includes(r.material_name));
    localStorage.setItem("ecoPackAI_compare", JSON.stringify(selected));
    window.location.href = "/comparison";
  }

  async function load(){
    try{
      productData = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
      if(!productData.product_name){
        showError("No product input found. Please go back and enter inputs.");
        return;
      }

      // ✅ Always ask backend for up to 20 so dropdown can show up to 20
      const res = await fetch(`${API_BASE}/api/recommend`, {
        method:"POST",
        headers:{
          "Content-Type":"application/json",
          "X-API-KEY": API_KEY
        },
        body: JSON.stringify({
          product_name: productData.product_name,
          top_n: 20
        })
      });

      if(!res.ok){
        showError("Server error. Check Flask is running and API key is correct.");
        return;
      }

      const data = await res.json();

      if(data.error){
        showError(data.error);
        return;
      }

      hide(loadingBox);

      const p = data.product || {};
      setText(productSummary, `Product: ${p.product_name} • Category: ${p.product_category} • Weight: ${p.product_weight_kg} kg`);

      const recs0 = data.recommendations || [];
      recsOriginal = applyWhatIfRerank(recs0, productData.priorities);

      show(kpiRow); show(chartsRow); show(resultsBlock);

      // listeners
      $("btnExportCsv")?.addEventListener("click", exportCsv);
      $("btnExportPdf")?.addEventListener("click", exportPdf);
      $("btnCompare")?.addEventListener("click", compareSelected);

      btnApplyFilters?.addEventListener("click", applyFiltersAndRender);
      btnResetFilters?.addEventListener("click", ()=>{
        if(searchBox) searchBox.value = "";
        if(modeSelect) modeSelect.value = "balanced";
        if(sortSelect) sortSelect.value = "rank";
        if(countSelect) countSelect.value = "10";
        applyFiltersAndRender();
      });

      // ✅ live update when dropdown changes
      countSelect?.addEventListener("change", applyFiltersAndRender);

      applyFiltersAndRender();

    }catch(e){
      console.error(e);
      showError("Failed to fetch recommendations. Is Flask running on 127.0.0.1:5000?");
    }
  }

  load();
}
