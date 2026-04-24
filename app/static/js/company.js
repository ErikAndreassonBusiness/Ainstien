// app/static/js/company.js

let stockChartInstance = null;

async function initCompanyPage() {
  const tickerEl = document.getElementById("companyTicker");
  if (!tickerEl) return;
  const ticker = tickerEl.value;

  // 1. Fetch & Display Fundamentals (The Table)
  try {
    const details = await fetchCompanyDetails(ticker);
    if (details) {
      displayHeader(details);
      displayFundamentals(details.fundamentals);
    }
  } catch (error) {
    console.error("Table failed to load:", error);
    document.getElementById("headerContainer").innerHTML =
      "<h3>Error loading company details</h3>";
  }

  // 2. Fetch & Display Market Data (The Chart)
  try {
    const marketData = await fetchMarketData(ticker);
    if (marketData) {
      // Update price in the header we just created
      const priceEl = document.getElementById("currentPriceDisplay");
      if (priceEl && marketData.current_price) {
        priceEl.textContent = `${marketData.current_price.toFixed(2)} SEK`;
      }

      if (marketData.history_dates && marketData.history_prices) {
        renderStockChart(marketData.history_dates, marketData.history_prices);
      }
    }
  } catch (error) {
    console.error("Chart failed to load:", error);
  }
}

function displayHeader(data) {
  const container = document.getElementById("headerContainer");
  // This replaces the "Loading..." spinner with the actual UI
  container.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <nav aria-label="breadcrumb">
                    <ol class="breadcrumb">
                        <li class="breadcrumb-item"><a href="/dashboard">Dashboard</a></li>
                        <li class="breadcrumb-item active">${data.ticker}</li>
                    </ol>
                </nav>
                <h1 class="display-5 fw-bold mb-0">${data.name || "N/A"}</h1>
                <div class="mt-2">
                    <span class="badge bg-dark">${data.ticker}</span>
                </div>
            </div>
            <div class="text-end">
                <h2 id="currentPriceDisplay" class="text-success fw-bold mb-1">... SEK</h2>
                <button class="btn btn-outline-primary btn-sm" onclick="window.print()">Export PDF</button>
            </div>
        </div>
    `;
}

function displayFundamentals(fundamentals) {
  const tableBody = document.getElementById("fundamentalTableBody");
  if (!tableBody) return;
  tableBody.innerHTML = "";

  if (!fundamentals || fundamentals.length === 0) {
    tableBody.innerHTML =
      '<tr><td colspan="7" class="text-center">No fundamental data available.</td></tr>';
    return;
  }

  // Sort descending by date
  fundamentals.sort(
    (a, b) => new Date(b.report_date) - new Date(a.report_date),
  );

  fundamentals.forEach((f) => {
    const row = document.createElement("tr");

    // Helper to safely handle nulls and formatting
    const fmt = (val) =>
      val !== null && val !== undefined ? val.toFixed(2) : "0.00";
    const mil = (val) =>
      val !== null && val !== undefined
        ? val > 1000000
          ? (val / 1000000).toFixed(0)
          : val.toFixed(0)
        : "0";

    row.innerHTML = `
            <td>${f.report_date}</td>
            <td>${mil(f.revenue)}M</td>
            <td class="${f.revenue_growth_percent >= 0 ? "text-success" : "text-danger"}">${fmt(f.revenue_growth_percent)}%</td>
            <td>${mil(f.net_income)}M</td>
            <td class="${f.profit_growth_percent >= 0 ? "text-success" : "text-danger"}">${fmt(f.profit_growth_percent)}%</td>
            <td>${fmt(f.ebit_margin_percent)}%</td>
            <td>${fmt(f.soliditet_percent)}%</td>
        `;
    tableBody.appendChild(row);
  });
}

function renderStockChart(labels, prices) {
  const canvas = document.getElementById("stockChart");
  if (!canvas) return;

  if (stockChartInstance) {
    stockChartInstance.destroy();
  }

  stockChartInstance = new Chart(canvas.getContext("2d"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Price",
          data: prices,
          borderColor: "#0d6efd",
          backgroundColor: "rgba(13, 110, 253, 0.1)",
          fill: true,
          tension: 0.2,
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
    },
  });
}

document.addEventListener("DOMContentLoaded", initCompanyPage);
