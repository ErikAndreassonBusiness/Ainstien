// app/static/js/company.js

let stockChartInstance = null;

/**
 * Orchestrates rendering pipelines for individual equity profiles
 */
async function initCompanyPage() {
  displayLoading();
  const tickerEl = document.getElementById("companyTicker");
  if (!tickerEl) return;
  const ticker = tickerEl.value;

  // Pipeline A: Core Fundamentals Data Engine
  try {
    const companyData = await fetchCompanyDetails(ticker);
    if (companyData) {
      displayHeader(companyData);
      displayFundamentals(companyData.history);
    }
  } catch (error) {
    console.error("Table dataset engine failure:", error);
    document.getElementById("headerContainer").innerHTML = `
      <div class="alert alert-warning border-0 shadow-sm">
        <h5 class="fw-bold m-0">Error loading historical data entries for ${ticker}</h5>
      </div>
    `;
  }

  // Pipeline B: Real-Time Market Valuation & Linear Charts
  try {
    const marketData = await fetchMarketData(ticker);
    if (marketData) {
      const priceEl = document.getElementById("currentPriceDisplay");
      if (priceEl && marketData.current_price) {
        priceEl.textContent = `${marketData.current_price.toFixed(2)} SEK`;
      }

      if (marketData.history_dates && marketData.history_prices) {
        renderStockChart(marketData.history_dates, marketData.history_prices);
      }
    }
  } catch (error) {
    console.error("Historical market timeline failure:", error);
  }
}

/**
 * Render standard structural loading framework
 */
function displayLoading() {
  const container = document.getElementById("headerContainer");
  if (!container) return;

  container.innerHTML = `
    <div class="text-center py-5">
      <div class="spinner-border text-secondary mb-3" role="status"></div>
      <p class="text-muted text-sm tracking-wider text-uppercase">Loading engine datasets...</p>
    </div>
  `;
}

/**
 * Builds the application navigation profile elements
 */
function displayHeader(company) {
  const container = document.getElementById("headerContainer");
  if (!container) return;

  container.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb mb-2">
            <li class="breadcrumb-item"><a href="/dashboard" class="text-decoration-none text-muted">Dashboard</a></li>
            <li class="breadcrumb-item active fw-bold text-dark" aria-current="page">${company.ticker}</li>
          </ol>
        </nav>
        <h1 class="display-6 fw-bold text-dark mb-0">${company.name || "N/A"}</h1>
        <div class="mt-2">
          <span class="badge bg-dark text-xs font-monospace px-2 py-1">${company.ticker}</span>
        </div>
      </div>
      <div class="text-end">
        <h2 id="currentPriceDisplay" class="quant-up fw-bold mb-2">... SEK</h2>
        <button class="btn btn-dark btn-sm shadow-sm" onclick="window.print()">Export Profile PDF</button>
      </div>
    </div>
  `;
}

/**
 * Generates cell matrices for income and balance sheets
 */
function displayFundamentals(history) {
  const incomeBody = document.getElementById("incomeTableBody");
  const balanceBody = document.getElementById("balanceTableBody");

  if (!incomeBody || !balanceBody) return;

  incomeBody.innerHTML = "";
  balanceBody.innerHTML = "";

  if (!history || history.length === 0) {
    incomeBody.innerHTML =
      '<tr><td colspan="6" class="text-center text-muted py-3">No metrics mapped.</td></tr>';
    balanceBody.innerHTML =
      '<tr><td colspan="12" class="text-center text-muted py-3">No metrics mapped.</td></tr>';
    return;
  }

  // Sort descending (Newest reporting sequences up front)
  history.sort((a, b) => new Date(b.report_date) - new Date(a.report_date));

  history.forEach((report) => {
    const f = report.fundamentals || {};

    // Numerical scale parsing utility (Formats raw fields into Millions scale strings)
    const mil = (val) => {
      if (val === null || val === undefined) return "0";
      const parsedValue = Math.abs(val) > 1000000 ? val / 1000000 : val;
      return Number(parsedValue).toLocaleString("en-US", {
        maximumFractionDigits: 0,
      });
    };

    // Income statement table structure updates
    const incomeRow = document.createElement("tr");
    incomeRow.innerHTML = `
      <td class="fw-bold text-dark">${report.report_date}</td>
      <td class="text-end">${mil(f.revenue)}M</td>
      <td class="text-end">${mil(f.depreciation)}M</td>
      <td class="text-end">${mil(f.ebitda)}M</td>
      <td class="text-end">${mil(f.ebit)}M</td>
      <td class="text-end ${f.net_income >= 0 ? "quant-up" : "quant-down"}">${mil(f.net_income)}M</td>
    `;
    incomeBody.appendChild(incomeRow);

    // Balance sheet structural cell row injection matrix
    const balanceRow = document.createElement("tr");
    balanceRow.innerHTML = `
      <td class="fw-bold text-dark">${report.report_date}</td>
      <td class="text-end">${mil(f.total_assets)}M</td>
      <td class="text-end">${mil(f.current_assets)}M</td>
      <td class="text-end">${mil(f.fixed_assets)}M</td>
      <td class="text-end">${mil(f.cash)}M</td>
      <td class="text-end">${mil(f.inventory)}M</td>
      <td class="text-end">${mil(f.account_receiveables)}M</td>
      <td class="text-end fw-semibold">${mil(f.total_equity)}M</td>
      <td class="text-end">${mil(f.short_term_debt)}M</td>
      <td class="text-end">${mil(f.long_term_debt)}M</td>
    `;
    balanceBody.appendChild(balanceRow);
  });
}

/**
 * Renders the linear time-series chart via Canvas APIs
 */
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
          label: "Price Evolution",
          data: prices,
          borderColor: "#0056b3", // Synchronized cleanly with your core --ainstien-blue token
          backgroundColor: "rgba(0, 86, 179, 0.04)",
          fill: true,
          tension: 0.15,
          pointRadius: 0,
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { ticks: { callback: (value) => `${value} SEK` } },
      },
    },
  });
}

document.addEventListener("DOMContentLoaded", initCompanyPage);
