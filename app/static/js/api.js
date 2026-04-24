const host = "/api";
/**
 * Fetches summary metrics for the dashboard table.
 */
async function fetchMarketSummary() {
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
