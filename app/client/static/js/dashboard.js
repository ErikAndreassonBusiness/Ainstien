// app/static/js/dashboard.js

/**
 * Main function: Orchestrates the data fetching and initialization
 */
async function initDashboard() {
  const tableBody = document.getElementById("companyTableBody");
  const statusIndicator = document.getElementById("statusIndicator");

  // 1. Fetch data from the API (defined in api.js)
  const marketData = await fetchMarketSummary();

  // 2. Error Handling
  if (!marketData || marketData.length === 0) {
    tableBody.innerHTML =
      '<tr><td colspan="6" class="text-center">No data found.</td></tr>';
    updateStatus("Error", "bg-danger");
    return;
  }

  // 3. Success: Update status and render the UI
  updateStatus(`${marketData.length} Companies`, "bg-dark");
  displayCompanies(marketData);
}

/**
 * Logic function: Clears the table and builds the rows
 * @param {Array} companies - The list of company objects from the API
 */
function displayCompanies(companies) {
  const tableBody = document.getElementById("companyTableBody");
  tableBody.innerHTML = ""; // Clear existing content

  companies.forEach((company) => {
    const row = createTableRow(company);
    tableBody.appendChild(row);
  });
}

/**
 * UI function: Creates a single <tr> element
 * @param {Object} company - Individual company data
 */
function createTableRow(company) {
  const row = document.createElement("tr");
  row.className = "stock-row cursor-pointer";

  // Color coding logic
  const growthClass =
    company.revenue_growth >= 0 ? "text-success" : "text-danger";

  row.innerHTML = `
        <td><strong>${company.ticker}</strong></td>
        <td>${company.name || "N/A"}</td>
        <td class="${growthClass}">${company.revenue_growth.toFixed(2)}%</td>
        <td>${company.ebit_margin.toFixed(2)}%</td>
        <td class="text-end">
            <a href="/company/${company.ticker}" class="btn btn-sm btn-outline-dark">Analysis</a>
        </td>
    `;

  // Click handler for the whole row
  row.addEventListener("click", (e) => {
    // Don't trigger if the user specifically clicks the "Analysis" button
    if (e.target.tagName !== "A") {
      window.location.href = `/company/${company.ticker}`;
    }
  });

  return row;
}

/**
 * Helper function: Updates the status badge
 */
function updateStatus(text, colorClass) {
  const statusIndicator = document.getElementById("statusIndicator");
  if (statusIndicator) {
    statusIndicator.textContent = text;
    statusIndicator.className = `badge ${colorClass}`;
  }
}

// Start the app when the DOM is ready
document.addEventListener("DOMContentLoaded", initDashboard);
