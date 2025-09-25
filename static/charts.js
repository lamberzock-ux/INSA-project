async function loadMetrics() {
    const res = await fetch("/api/metrics");
    const data = await res.json();

    const ctx = document.getElementById("metricsChart").getContext("2d");
    new Chart(ctx, {
        type: "line",
        data: {
            labels: data.timestamps.reverse(),
            datasets: [{
                label: "Events",
                data: data.values.reverse(),
                borderColor: "#0ff",
                backgroundColor: "rgba(0,255,255,0.2)",
            }]
        }
    });
}

async function loadAlerts() {
    const res = await fetch("/api/alerts");
    const alerts = await res.json();
    const table = document.getElementById("alertsTable");

    alerts.forEach(alert => {
        let row = `<tr><td>${alert.time}</td><td>${alert.type}</td><td>${alert.severity}</td></tr>`;
        table.innerHTML += row;
    });
}

loadMetrics();
loadAlerts();
