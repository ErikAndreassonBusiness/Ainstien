var stockChartInstance = stockChartInstance || null;

// ========== For the Analyse buttons on dashboard ========
document.addEventListener("DOMContentLoaded", function () {
  // Select all rows with the class 'stock-row'
  const rows = document.querySelectorAll(".stock-row");

  rows.forEach((row) => {
    row.addEventListener("click", function (e) {
      // Check if the click was on the button itself or a link
      // If it was, let the browser handle it normally.
      if (e.target.tagName === "A" || e.target.tagName === "BUTTON") {
        return;
      }

      // Otherwise, get the URL from the data attribute and navigate
      const url = this.getAttribute("data-url");
      if (url) {
        window.location.href = url;
      }
    });
  });
});

// ============== For the Live Market Charts =============
document.addEventListener("DOMContentLoaded", function () {
  const ctx = document.getElementById("stockChart");
  if (!ctx) return;

  try {
    const labelsRaw = document.getElementById("chartLabelsData").textContent;
    const valuesRaw = document.getElementById("chartValuesData").textContent;

    const labels = JSON.parse(labelsRaw);
    const dataPoints = JSON.parse(valuesRaw);

    if (stockChartInstance !== null) {
      stockChartInstance.destroy();
    }

    if (dataPoints.length === 0) {
      console.warn("Ainstien: History data is empty for this ticker.");
      return;
    }

    // Render the chart
    stockChartInstance = new Chart(ctx.getContext("2d"), {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Closing Price",
            data: dataPoints,
            borderColor: "#0d6efd",
            backgroundColor: "rgba(13, 110, 253, 0.1)",
            fill: true,
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { display: false },
          y: { ticks: { callback: (val) => val + " kr" } },
        },
      },
    });
    console.log("Ainstien: Chart rendered successfully!");
  } catch (error) {
    console.error("Ainstien: Logic error:", error);
  }
});
