const bioSlider = document.getElementById("biodegradability_score");
const recycleSlider = document.getElementById("recyclability_percent");

bioSlider.oninput = () => {
    document.getElementById("bioVal").innerText = bioSlider.value;
};

recycleSlider.oninput = () => {
    document.getElementById("recycleVal").innerText = recycleSlider.value + "%";
};

function predict() {
    const payload = {
        strength_encoded: Number(document.getElementById("strength_encoded").value),
        weight_capacity: Number(document.getElementById("weight_capacity").value),
        biodegradability_score: Number(bioSlider.value),
        recyclability_percent: Number(recycleSlider.value),
        cost_efficiency_score: Number(document.getElementById("cost_efficiency_score").value)
    };

    fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("cost").innerText =
            "₹ " + data.predicted_cost.toFixed(2) + " / kg";

        document.getElementById("co2").innerText =
            data.predicted_co2.toFixed(3) + " kg / kg";

        document.getElementById("status").innerText = "";
    })
    .catch(() => {
        document.getElementById("status").innerText =
            "Backend not responding. Check Flask server.";
    });
}