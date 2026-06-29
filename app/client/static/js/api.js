const host = "/api";

// ========== Main Functions ===========

/**
 * POST from DB
 */
async function post(data_to_get, endpoint) {
  const response = await fetch("/api/" + endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data_to_get),
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
 * Special fetch to force the browser to update
 */
async function fetchDataDiagnostics(data) {
  try {
    console.log("1. Sending diagnostics request with data:", data);

    const response = await fetch("/api/diagnostics", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const result = await response.json();
    console.log("2. Received response from backend:", result);

    if (result.status === "success") {
      console.log("3. Backend reported success. Checking HTML elements...");

      const distImg = document.getElementById("target-dist-img");
      const outliersImg = document.getElementById("outliers-img");
      const heatmapImg = document.getElementById("heatmap-img");

      console.log("Elements found in HTML:", {
        "target-dist-img": !!distImg,
        "outliers-img": !!outliersImg,
        "heatmap-img": !!heatmapImg,
      });

      if (distImg && result.images?.target_distribution) {
        distImg.src = result.images.target_distribution;
        console.log("Updated target-dist-img src to:", distImg.src);
      }
      if (outliersImg && result.images?.outliers_scaled) {
        outliersImg.src = result.images.outliers_scaled;
        console.log("Updated outliers-img src to:", outliersImg.src);
      }
      if (heatmapImg && result.images?.correlation_matrix) {
        heatmapImg.src = result.images.correlation_matrix;
        console.log("Updated heatmap-img src to:", heatmapImg.src);
      }
    } else {
      console.error("Backend returned success=false:", result.message);
    }
  } catch (error) {
    console.error("Network or execution error:", error);
  }
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
