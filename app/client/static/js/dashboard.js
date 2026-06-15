// app/static/js/dashboard.js

/**
 * Main function: Orchestrates the data fetching and initialization
 */
async function initDashboard() {
  const tableBody = document.getElementById("companyTableBody");

  // 1. Fetch data from the API (defined in api.js)
  const marketData = await fetchMarketSummary();

  // 2. Error Handling
  if (!marketData || marketData.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="5" class="text-center text-muted py-4">
          No Swedish Mid-Cap market data found.
        </td>
      </tr>
    `;
    updateStatus("Error loading data", "error");
    return;
  }

  // 3. Success: Update status and render the UI
  updateStatus(`${marketData.length} Companies`, "success");
  displayCompanies(marketData);
}

/**
 * Logic function: Clears the table and builds the rows
 * @param {Array} companies - The list of company objects from the API
 */
function displayCompanies(companies) {
  const tableBody = document.getElementById("companyTableBody");
  tableBody.innerHTML = ""; // Clear existing content / fallback loading states

  companies.forEach((company) => {
    const row = createTableRow(company);
    tableBody.appendChild(row);
  });
}

/**
 * UI function: Creates a single <tr> element representing a stock row
 * @param {Object} company - Individual company data
 */
function createTableRow(company) {
  const row = document.createElement("tr");
  row.className = "stock-row"; // Hover states and transitions handled cleanly by base.css

  // Determine financial performance styling dynamically using our new semantic tokens
  const ebitClass = company.ebit >= 0 ? "quant-up" : "quant-down";

  // Aligned numerical columns to 'text-end' to cleanly match the table head hierarchy
  row.innerHTML = `
    <td><strong>${company.ticker}</strong></td>
    <td>${company.name || "N/A"}</td>
    <td class="text-end">${company.revenue.toFixed(2)}</td>
    <td class="text-end ${ebitClass}">${company.ebit.toFixed(2)}</td>
    <td class="text-end">
      <a href="/company/${company.ticker}" class="btn btn-dark btn-sm">Analysis</a>
    </td>
  `;

  // Click handler for the whole row (excluding direct anchor triggers)
  row.addEventListener("click", (e) => {
    if (e.target.tagName !== "A") {
      window.location.href = `/company/${company.ticker}`;
    }
  });

  return row;
}

/**
 * Helper function: Updates the status badge using our decoupled CSS tokens
 * @param {string} text - The narrative indicator text
 * @param {'fetching' | 'success' | 'error'} state - Core application states
 */
function updateStatus(text, state) {
  const statusIndicator = document.getElementById("statusIndicator");
  if (!statusIndicator) return;

  statusIndicator.textContent = text;

  // Wipe old variations and apply clean, isolated design language classes
  statusIndicator.className = `badge status-${state}`;
}

// Start the app when the DOM is ready
document.addEventListener("DOMContentLoaded", initDashboard);
