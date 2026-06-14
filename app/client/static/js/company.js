// app/static/js/company.js

let stockChartInstance = null;

async function initCompanyPage() {
  displayLoading(); // Display a loading sign until data is fetched.
  const tickerEl = document.getElementById("companyTicker");
  if (!tickerEl) return;
  const ticker = tickerEl.value;

  // Fetch & Display Fundamentals (The Table)
  try {
    const companyData = await fetchCompanyDetails(ticker);
    if (companyData) {
      displayHeader(companyData);
      displayFundamentals(companyData.history);
    }
  } catch (error) {
    console.error("Table failed to load:", error);
    document.getElementById("headerContainer").innerHTML =
      "<h3>Error loading company details</h3>";
  }

  // Fetch & Display Market Data (The Chart)
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

function displayLoading() {
  // Get container to fill
  let loadingContainerHTML = document.getElementById("headerContainer");

  let loadingContainer = ``;
  loadingContainer += `<div class="text-center py-5">`;
  loadingContainer += `<div class="spinner-border text-primary" role="status"></div>`;
  loadingContainer += `<p>Loading company data...</p>`;
  loadingContainer += `</div></div>`;

  loadingContainerHTML.innerHTML = loadingContainer; // convert to HTML
}

function displayHeader(company) {
  let containerHeaderHTML = document.getElementById("headerContainer");

  //Build the HTML stucture
  let containerHeader = ``;
  containerHeader += `<div class="d-flex justify-content-between align-items-center mb-4">`;
  containerHeader += `<div>`; //to have the stock name to the left

  //Return button to dashboard
  containerHeader += ` <nav aria-label="breadcrumb">`;
  containerHeader += `<ol class="breadcrumb">`;
  containerHeader += `<li class="breadcrumb-item"><a href="/dashboard">Dashboard</a></li>`;
  containerHeader += `<li class="breadcrumb-item active">${company.ticker}</li>`;
  containerHeader += `</ol>`;
  containerHeader += `</nav>`;

  // DIsplay company info
  containerHeader += ` <h1 class="display-5 fw-bold mb-0">${company.name || "N/A"}</h1>`;
  containerHeader += `<div class="mt-2">`;
  containerHeader += `<span class="badge bg-dark">${company.ticker}</span>`;
  containerHeader += `</div>`;
  containerHeader += `</div>`;
  containerHeader += `<div class="text-end">`;
  containerHeader += `<h2 id="currentPriceDisplay" class="text-success fw-bold mb-1">... SEK</h2>`;
  containerHeader += `<button class="btn btn-outline-primary btn-sm" onclick="window.print()">Export PDF</button>`;
  containerHeader += `</div>`;
  containerHeader += ` </div>`;

  containerHeaderHTML.innerHTML = containerHeader;
}

function displayFundamentals(history) {
  const incomeBody = document.getElementById("incomeTableBody");
  const balanceBody = document.getElementById("balanceTableBody");

  if (!incomeBody || !balanceBody) return;

  // Clear old entries
  incomeBody.innerHTML = "";
  balanceBody.innerHTML = "";

  if (!history || history.length === 0) {
    incomeBody.innerHTML =
      '<tr><td colspan="6" class="text-center">No data available.</td></tr>';
    balanceBody.innerHTML =
      '<tr><td colspan="12" class="text-center">No data available.</td></tr>';
    return;
  }

  // Sort descending by date (newest first)
  history.sort((a, b) => new Date(b.report_date) - new Date(a.report_date));

  history.forEach((report) => {
    const f = report.fundamentals || {};

    // Formatting helper
    const mil = (val) =>
      val !== null && val !== undefined
        ? val > 1000000
          ? (val / 1000000).toFixed(0)
          : val.toFixed(0)
        : "0";

    // ---- Create Income Row ----
    const incomeRow = document.createElement("tr");
    incomeRow.innerHTML = `
        <td class="fw-bold">${report.report_date}</td>
        <td>${mil(f.revenue)}M</td>
        <td>${mil(f.depreciation)}M</td>
        <td>${mil(f.ebitda)}M</td>
        <td>${mil(f.ebit)}M</td>
        <td class="fw-bold text-primary">${mil(f.net_income)}M</td>
    `;
    incomeBody.appendChild(incomeRow);

    // ---- Create Balance Sheet Row ----
    const balanceRow = document.createElement("tr");
    balanceRow.innerHTML = `
        <td class="fw-bold">${report.report_date}</td>
        <td>${mil(f.total_assets)}M</td>
        <td>${mil(f.current_assets)}M</td>
        <td>${mil(f.fixed_assets)}M</td>
        <td>${mil(f.cash)}M</td>
        <td>${mil(f.inventory)}M</td>
        <td>${mil(f.account_receiveables)}M</td>
        <td>${mil(f.goodwill)}M</td>
        <td class="fw-bold text-success">${mil(f.total_equity)}M</td>
        <td>${mil(f.total_debt)}M</td>
        <td>${mil(f.short_term_debt)}M</td>
        <td>${mil(f.long_term_debt)}M</td>
    `;
    balanceBody.appendChild(balanceRow);
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

// Executes the JS script
document.addEventListener("DOMContentLoaded", initCompanyPage);
