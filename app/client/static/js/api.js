const host = "/api";

// ========== Main Functions ===========

/**
 * POST from DB
 */
async function post(data_to_get, endpoint) {
  const response = await fetch("/api/" + endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data_to_get }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
}

/**
 * GET to DB
 */
async function get(endpoint) {
  const response = await fetch("/api/" + endpoint, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
}

/**
 * Fetches summary metrics for the dashboard table.
 */
async function fetchCompaniesSummary() {
  try {
    return get("market-summary");
  } catch (error) {
    console.error("Kunde inte hämta marknadsdata:", error);
    return null;
  }
}

/**
 * Fetches market data for a specific stock ticker.
 * This include a stock chart, currrent price and industry
 */
async function fetchMarketData(ticker) {
  try {
    return get(`market-data/${ticker}`);
  } catch (error) {
    console.error("Kunde inte hämta marknadsdata:", error);
    return null;
  }
}

/**
 * Fetches the full company details (Fundamentals + Info)
 */
async function fetchCompanyDetails(ticker) {
  try {
    return get(`/company-details/${ticker}`);
  } catch (error) {
    console.error("API Error (Company Details):", error);
    return null;
  }
}

// ========================= Model Engine API Calls =========================

/**
 * Dispatches request for multidimensional variance (Correlation Matrix)
 */
async function fetchCorrelationMatrix(features) {
  return post(features, "correlation-matrix");
}

/**
 * Dispatches core payload for Machine Learning algorithms
 */
async function runModels(modelSettings) {
  return post(modelSettings, "run-models");
}

/**
 * Fetches the available fundamental and metric feature lists from the database.
 */
async function fetchFeatureNames() {
  try {
    return get("feature-names");
  } catch (error) {
    console.error("API Error (Feature Names):", error);
    return null;
  }
}

/**
 * Fetches the registered valid predictive objective target settings.
 */
async function fetchTargetNames() {
  try {
    return get("target-names");
  } catch (error) {
    console.error("API Error (Target Names):", error);
    return null;
  }
}
