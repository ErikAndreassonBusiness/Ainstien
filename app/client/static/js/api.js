const host = "/api";
/**
 * Fetches summary metrics for the dashboard table.
 */
async function fetchCompaniesSummary() {
  try {
    const route = `${host}/market-summary`;

    const response = await fetch(route, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error("Kunde inte hämta marknadsöversikt.");
    }

    return await response.json();
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
    // Construct the route using the host constant
    const route = `${host}/market-data/${ticker}`;

    const response = await fetch(route, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Kunde inte hämta marknadsdata för ${ticker}`);
    }

    // Return the JSON data directly
    return await response.json();
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
    const route = `${host}/company-details/${ticker}`;

    const response = await fetch(route, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Kunde inte hämta detaljer för ${ticker}`);
    }

    return await response.json();
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
  const response = await fetch("/api/correlation-matrix", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ features }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
}

/**
 * Dispatches core payload for Machine Learning algorithms
 */
async function runModels(modelSettings) {
  const response = await fetch("/api/run-models", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(modelSettings),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
}

/**
 * Fetches the available fundamental and metric feature lists from the database.
 */
async function fetchFeatureNames() {
  try {
    const response = await fetch(`${host}/feature-names`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    if (!response.ok) {
      throw new Error(
        `Failed to fetch feature configurations. Status: ${response.status}`,
      );
    }
    return await response.json();
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
    const response = await fetch(`${host}/target-names`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    if (!response.ok) {
      throw new Error(
        `Failed to fetch target parameters. Status: ${response.status}`,
      );
    }
    return await response.json();
  } catch (error) {
    console.error("API Error (Target Names):", error);
    return null;
  }
}
