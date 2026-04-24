// app/static/js/company.js
var stockChartInstance = stockChartInstance || null;

document.addEventListener("DOMContentLoaded", async function () {
  const ctx = document.getElementById("stockChart");
  const tickerInput = document.getElementById("companyTicker");

  if (!ctx || !tickerInput) return;

  const ticker = tickerInput.value;
  const loader = document.getElementById("chartLoader");

  // Call function from api.js
  const data = await fetchMarketData(ticker);

  if (data) {
    if (loader) loader.style.display = "none";
    renderStockChart(ctx, data.history_dates, data.history_prices);
  } else {
    if (loader)
      loader.innerHTML = '<p class="text-danger">Kunde inte ladda graffen.</p>';
  }
});

function renderStockChart(canvasElement, labels, prices) {
  if (stockChartInstance !== null) {
    stockChartInstance.destroy();
  }

  stockChartInstance = new Chart(canvasElement.getContext("2d"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Stängningskurs",
          data: prices,
          borderColor: "#0d6efd",
          backgroundColor: "rgba(13, 110, 253, 0.1)",
          fill: true,
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { display: false },
        y: { ticks: { callback: (val) => val + " kr" } },
      },
    },
  });
}
