// At the very top, keep your instance tracker
var stockChartInstance = stockChartInstance || null;

// ========== For the Analyse buttons on dashboard ========
document.addEventListener("DOMContentLoaded", function () {
  const rows = document.querySelectorAll(".stock-row");
  rows.forEach((row) => {
    row.addEventListener("click", function (e) {
      if (e.target.tagName === "A" || e.target.tagName === "BUTTON") return;
      const url = this.getAttribute("data-url");
      if (url) window.location.href = url;
    });
  });
});

// ============== For the Live Market Charts =============
document.addEventListener("DOMContentLoaded", async function () {
  const ctx = document.getElementById("stockChart");
  const tickerInput = document.getElementById("companyTicker");

  // Only run if we are on the company details page
  if (!ctx || !tickerInput) return;

  const ticker = tickerInput.value;
  const loader = document.getElementById("chartLoader");

  // 1. Fetch data from your new api.js function
  const data = await fetchMarketData(ticker);

  if (data) {
    // 2. Hide loader if it exists
    if (loader) loader.style.display = "none";

    // 3. Call the new render function
    renderStockChart(ctx, data.history_dates, data.history_prices);

    // 4. (Optional) Update the Sector/Industry label if you have one
    const categoryLabel = document.getElementById("categoryInfoLabel");
    if (categoryLabel) categoryLabel.textContent = data.category_info;
  } else {
    if (loader)
      loader.innerHTML = '<p class="text-danger">Kunde inte ladda graffen.</p>';
  }
});

/**
 * NEW: The renderStockChart function
 * Handles the Chart.js creation and destruction
 */
function renderStockChart(canvasElement, labels, prices) {
  if (prices.length === 0) {
    console.warn("Ainstien: Ingen historik hittades för denna ticker.");
    return;
  }

  // Destroy previous instance to avoid "Canvas already in use" error
  if (stockChartInstance !== null) {
    stockChartInstance.destroy();
  }

  // Create new chart and store it in the global variable
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
        y: {
          ticks: {
            callback: (val) => val + " kr",
          },
        },
      },
    },
  });
  console.log("Ainstien: Chart rendered successfully via API!");
}
