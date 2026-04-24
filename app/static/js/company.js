// app/static/js/company.js

async function initCompanyPage() {
  const tickerElement = document.getElementById("companyTicker");
  if (!tickerElement) return;

  const ticker = tickerElement.value;

  // 1. Fetch Company Fundamentals (GET)
  const details = await fetchCompanyDetails(ticker);
  if (details) {
    displayHeader(details); // This was likely causing the crash!
    displayFundamentals(details.fundamentals);
  }

  // 2. Fetch Market Data & Price History (GET)
  const marketResponse = await fetchMarketData(ticker);

  if (marketResponse) {
    updateCurrentPrice(marketResponse.current_price);

    // Render chart if data exists
    if (marketResponse.history_dates && marketResponse.history_prices) {
      renderStockChart(
        marketResponse.history_dates,
        marketResponse.history_prices,
      );
    }
  }
}

/**
 * UI Painter: Header Section
 * Creates the breadcrumbs, title, and the price placeholder
 */
function displayHeader(data) {
  const container = document.getElementById("headerContainer");
  if (!container) return;

  container.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <nav aria-label="breadcrumb">
                    <ol class="breadcrumb">
                        <li class="breadcrumb-item"><a href="/dashboard">Dashboard</a></li>
                        <li class="breadcrumb-item active">${data.ticker}</li>
                    </ol>
                </nav>
                <h1 class="display-5 fw-bold mb-0">${data.name}</h1>
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

/**
 * UI Painter: Historical Table
 */
function displayFundamentals(fundamentals) {
  const tableBody = document.getElementById("fundamentalTableBody");
  if (!tableBody) return;

  tableBody.innerHTML = "";

  fundamentals.sort(
    (a, b) => new Date(b.report_date) - new Date(a.report_date),
  );

  fundamentals.forEach((f) => {
    const row = document.createElement("tr");

    const rev = f.revenue || 0;
    const net = f.net_income || 0;

    const displayRevenue =
      rev > 1000000 ? (rev / 1000000).toFixed(0) : rev.toFixed(0);
    const displayNetIncome =
      net > 1000000 ? (net / 1000000).toFixed(0) : net.toFixed(0);

    row.innerHTML = `
            <td>${f.report_date}</td>
            <td>${displayRevenue}M</td>
            <td class="${f.revenue_growth_percent >= 0 ? "text-success" : "text-danger"}">
                ${(f.revenue_growth_percent || 0).toFixed(2)}%
            </td>
            <td>${displayNetIncome}M</td>
            <td class="${f.profit_growth_percent >= 0 ? "text-success" : "text-danger"}">
                ${(f.profit_growth_percent || 0).toFixed(2)}%
            </td>
            <td>${(f.ebit_margin_percent || 0).toFixed(2)}%</td>
            <td>${(f.soliditet_percent || 0).toFixed(2)}%</td>
        `;
    tableBody.appendChild(row);
  });
}

/**
 * UI Painter: Chart.js Line Chart
 */
function renderStockChart(labels, prices) {
  const canvas = document.getElementById("stockChart");
  if (!canvas) return;

  new Chart(canvas.getContext("2d"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Price (SEK)",
          data: prices,
          borderColor: "#0d6efd",
          backgroundColor: "rgba(13, 110, 253, 0.1)",
          fill: true,
          tension: 0.2,
          pointRadius: 0, // Makes it look cleaner
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { ticks: { callback: (val) => val + " SEK" } },
      },
    },
  });
}

function updateCurrentPrice(price) {
  const priceDisplay = document.getElementById("currentPriceDisplay");
  if (priceDisplay && price) {
    priceDisplay.textContent = `${price.toFixed(2)} SEK`;
  }
}

document.addEventListener("DOMContentLoaded", initCompanyPage);
